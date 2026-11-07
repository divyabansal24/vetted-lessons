import os
import time
from dotenv import load_dotenv

load_dotenv()

print("Checking Gemini...")
try:
    from google import genai
    from google.genai import types
    c = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY", "").strip(),
        http_options=types.HttpOptions(timeout=60000),
    )
    first = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()
    for model in [first, "gemini-3.5-flash", "gemini-3.1-flash-lite"]:
        print(f"  Trying {model}...", flush=True)
        start = time.time()
        try:
            res = c.models.generate_content(model=model, contents="Reply with the word ok")
            print(f"    Works in {time.time() - start:.1f}s, replied: {(res.text or '').strip()}")
        except Exception as e:
            print(f"    Failed after {time.time() - start:.1f}s: {str(e)[:200]}")
except Exception as e:
    print("  Problem:", e)

print("Checking Groq...")
try:
    import llm
    if os.getenv("GROQ_API_KEY", "").strip():
        print("  Works, replied:", llm.ask_groq("Reply with the word ok", False))
    else:
        print("  No GROQ_API_KEY in .env, skipped")
except Exception as e:
    print("  Problem:", e)

print("Checking Tavily...")
try:
    from tavily import TavilyClient
    t = TavilyClient(api_key=os.getenv("TAVILY_API_KEY", "").strip())
    res = t.search(query="HTTP status codes", max_results=1)
    print("  Works, first result:", res["results"][0]["url"])
except Exception as e:
    print("  Problem:", e)

print("Checking Open Library...")
try:
    import requests
    r = requests.get("https://openlibrary.org/search.json", params={"q": "computer networks", "limit": 1}, timeout=20)
    print("  Works, found:", r.json()["docs"][0]["title"])
except Exception as e:
    print("  Problem:", e)
