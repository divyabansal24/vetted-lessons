import os
import re
import time
import requests
from concurrent.futures import ThreadPoolExecutor, wait
from urllib.parse import urlparse, parse_qs
from tavily import TavilyClient
from youtube_transcript_api import YouTubeTranscriptApi
from llm import ask

TRUSTED = [
    "rfc-editor.org", "ietf.org", "developer.mozilla.org", "w3.org", "docs.python.org",
    "postgresql.org", "docs.oracle.com", "learn.microsoft.com", "owasp.org", "sqlite.org",
    "dev.mysql.com", "nodejs.org", "kubernetes.io", "docs.github.com", "httpwg.org",
]
MEDIUM = [
    "wikipedia.org", "geeksforgeeks.org", "freecodecamp.org", "w3schools.com",
    "digitalocean.com", "ibm.com", "aws.amazon.com", "realpython.com", "cloudflare.com",
    "khanacademy.org", "programiz.com", "javatpoint.com", "tutorialspoint.com",
    "blog.postman.com", "oreilly.com",
]


def tavily():
    key = os.getenv("TAVILY_API_KEY", "").strip()
    if not key:
        raise RuntimeError("TAVILY_API_KEY is missing. Add it to the .env file.")
    return TavilyClient(api_key=key)


def rate(url):
    host = urlparse(url).netloc.lower()
    if host.endswith(".edu") or host.endswith(".gov") or host.endswith(".ac.in"):
        return "high"
    if any(host == d or host.endswith("." + d) for d in TRUSTED):
        return "high"
    if any(host == d or host.endswith("." + d) for d in MEDIUM):
        return "medium"
    if host.startswith("docs.") or "/docs/" in url:
        return "medium"
    return "low"


def make_queries(title, objective):
    prompt = f"""A teacher is preparing a lesson.
Title: {title}
Learning objective: {objective}

Write search queries to research it.
- "web": 3 different Google-style queries that together cover every part of the objective. Prefer wording that finds official documentation and standards.
- "video": 1 query for a YouTube explainer video.
- "books": 1 short query (2-4 words) to find textbooks on the topic.

Return JSON only: {{"web": ["...", "...", "..."], "video": "...", "books": "..."}}"""
    return ask(prompt, as_json=True)


def search_web(queries):
    found = {}
    t = tavily()
    for q in queries:
        res = t.search(query=q, max_results=4, exclude_domains=["youtube.com"])
        for r in res.get("results", []):
            url = r.get("url", "")
            if url and url not in found:
                found[url] = {
                    "type": "web",
                    "title": r.get("title") or url,
                    "url": url,
                    "content": (r.get("content") or "")[:1500],
                    "reliability": rate(url),
                    "query": q,
                }
    return list(found.values())


def video_id(url):
    p = urlparse(url)
    if "youtu.be" in p.netloc:
        return p.path.strip("/") or None
    if "youtube.com" in p.netloc and p.path == "/watch":
        return parse_qs(p.query).get("v", [None])[0]
    return None


def transcript(vid):
    try:
        parts = YouTubeTranscriptApi().fetch(vid, languages=["en", "en-IN", "en-US", "hi"])
        return " ".join(p.text for p in parts)
    except Exception:
        return ""


def search_videos(query):
    res = tavily().search(query=query, max_results=6, include_domains=["youtube.com"])
    found = []
    for r in res.get("results", []):
        vid = video_id(r.get("url", ""))
        if vid and vid not in [v for v, _ in found]:
            found.append((vid, r))
    found = found[:4]

    pool = ThreadPoolExecutor(max_workers=4)
    jobs = {vid: pool.submit(transcript, vid) for vid, _ in found}
    wait(list(jobs.values()), timeout=25)
    pool.shutdown(wait=False, cancel_futures=True)

    out = []
    for vid, r in found:
        job = jobs[vid]
        text = job.result() if job.done() else ""
        out.append({
            "type": "video",
            "title": r.get("title") or vid,
            "url": f"https://www.youtube.com/watch?v={vid}",
            "content": text[:2500] if text else (r.get("content") or "")[:800],
            "has_transcript": bool(text),
            "reliability": "medium" if text else "low",
            "query": query,
        })
    return out


COMMON = {"the", "and", "for", "with", "explain", "between", "guide", "introduction", "request", "requests",
          "response", "responses", "method", "methods", "basics", "fundamentals", "how", "what", "using"}
TECH = {"computer", "computers", "computing", "programming", "software", "internet", "network", "networks",
        "networking", "web", "database", "databases", "sql", "protocol", "protocols", "data", "information",
        "technology", "java", "python", "javascript", "html", "algorithms", "engineering"}


def words(text):
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if len(w) > 2}


def relevant(title, subjects, wanted):
    hits = wanted & words(title)
    key_hits = hits - COMMON
    tech = bool(TECH & words(" ".join(subjects) + " " + title))
    return bool(key_hits) and (len(hits) >= 2 or tech or not subjects)


def search_books(query, topic=""):
    res = requests.get(
        "https://openlibrary.org/search.json",
        params={"q": query, "limit": 25, "language": "eng", "fields": "title,author_name,first_publish_year,key,subject"},
        timeout=20,
    )
    res.raise_for_status()
    wanted = words(query + " " + topic)
    out = []
    for d in res.json().get("docs", []):
        title = d.get("title", "Untitled")
        if not relevant(title, d.get("subject", [])[:30], wanted):
            continue
        authors = ", ".join(d.get("author_name", [])[:3]) or "Unknown author"
        year = d.get("first_publish_year", "n.d.")
        out.append({
            "type": "book",
            "title": f"{title} - {authors} ({year})",
            "url": "https://openlibrary.org" + d.get("key", ""),
            "content": f"Book: {title} by {authors}, first published {year}. Catalogue record only, full text not read.",
            "reliability": "medium",
            "query": query,
        })
        if len(out) == 5:
            break
    return out


def log(step, start):
    print(f"[research] {step} done in {time.time() - start:.1f}s", flush=True)


def run(title, objective):
    warnings = []
    t = time.time()
    try:
        plan = make_queries(title, objective)
        web_q = [q for q in plan.get("web", []) if q][:3] or [title]
        video_q = plan.get("video") or f"{title} explained"
        book_q = plan.get("books") or title
    except Exception as e:
        warnings.append(f"Could not plan search queries, used the title instead. ({str(e)[:160]})")
        web_q = [title, f"{title} {objective}"[:150], f"{title} official documentation"]
        video_q, book_q = f"{title} explained", " ".join(title.split()[:2])
        plan = {"web": web_q, "video": video_q, "books": book_q}
    log("query planning", t)

    web, videos, books = [], [], []
    t = time.time()
    try:
        web = search_web(web_q)
    except Exception as e:
        warnings.append(f"Web search failed: {e}")
    log("web search", t)
    t = time.time()
    try:
        videos = search_videos(video_q)
        if videos and not any(v["has_transcript"] for v in videos):
            warnings.append("No video transcripts could be read, so videos are listed as extra viewing only.")
    except Exception as e:
        warnings.append(f"YouTube search failed: {e}")
    log("youtube", t)
    t = time.time()
    try:
        books = search_books(book_q, title)
        if not books and book_q != title:
            books = search_books(title, title)
        if not books:
            warnings.append("No books matched the topic closely enough, so none are listed.")
    except Exception as e:
        warnings.append(f"Book search failed: {e}")
    log("books", t)

    sources = web + books + videos
    if not sources:
        details = " | ".join(w[:200] for w in warnings) or "no details"
        raise RuntimeError(f"Research found nothing. Details: {details}")
    for n, s in enumerate(sources, 1):
        s["id"] = f"S{n}"
    return {"queries": plan, "sources": sources, "warnings": warnings}
