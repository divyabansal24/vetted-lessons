import re
from llm import ask

PLAN = [
    ("hook", "Real-world hook", 3),
    ("concept1", "Concept 1 with a quick try-it", 10),
    ("concept2", "Concept 2 with a quick try-it", 10),
    ("task", "Mini task written as a work ticket", 12),
    ("quiz", "Knowledge check", 7),
    ("recap", "Recap and where you will use this at work", 3),
]


def source_text(sources, size=1200):
    blocks = []
    for s in sources:
        body = (s.get("content") or "")[:size]
        blocks.append(f"[{s['id']}] {s['type']}, reliability {s['reliability']}: {s['title']} ({s['url']})\n{body}")
    return "\n\n".join(blocks)


def lesson_text(sections):
    return "\n\n".join(f"## {s['title']} ({s['minutes']} min)\n{s['content']}" for s in sections)


def generate(title, objective, research):
    sources = research["sources"]
    plan = "\n".join(f"{i}. {name} - {mins} minutes" for i, (_, name, mins) in enumerate(PLAN, 1))
    prompt = f"""You are writing one lesson for a work-integrated computer science programme.
Students learn by doing: every idea is taught and then applied straight away, and the lesson connects to real engineering work.

Lesson title: {title}
Learning objective: {objective}

The lesson must take exactly 45 minutes and follow this plan:
{plan}

Rules:
- Base facts on the sources below and cite them inline like [S3]. Only cite a source if its text supports the point.
- If you need a point the sources do not cover, write it without a citation. It will be checked later.
- Write for a first or second year student: plain words, short paragraphs, concrete examples.
- Each concept section ends with a "Try it" exercise that takes 2-3 minutes, followed by the expected answer.
- The work ticket describes a realistic problem at a company, lists the steps to solve it, and ends with a model solution.
- The knowledge check has exactly 5 numbered questions (mix of multiple choice and short answer), then an answer key that explains each answer.
- Every part of the learning objective must be explained, practised and tested somewhere in the lesson.
- Use Markdown inside "content". Do not repeat the section title inside "content".
- From the YouTube sources, pick up to 3 that fit the lesson best and give one line on why each is worth watching.

Sources:
{source_text(sources)}

Return JSON only:
{{"sections": [{{"title": "...", "minutes": 3, "content": "..."}}], "videos": [{{"id": "S9", "why": "..."}}]}}
"sections" must have exactly {len(PLAN)} items in the order of the plan."""
    data = ask(prompt, as_json=True)
    parts = data.get("sections", [])
    if len(parts) != len(PLAN):
        raise RuntimeError(f"The model returned {len(parts)} sections instead of {len(PLAN)}. Please try again.")
    sections = []
    for (kind, name, mins), p in zip(PLAN, parts):
        try:
            minutes = int(p.get("minutes", mins))
        except (TypeError, ValueError):
            minutes = mins
        sections.append({
            "kind": kind,
            "title": (p.get("title") or name).strip(),
            "minutes": minutes,
            "content": (p.get("content") or "").strip(),
        })
    video_ids = {s["id"] for s in sources if s["type"] == "video"}
    videos = [v for v in data.get("videos", []) if v.get("id") in video_ids][:3]
    if not videos:
        videos = [{"id": s["id"], "why": "Extra explanation of the topic."} for s in sources if s["type"] == "video"][:2]
    return {"sections": sections, "videos": videos}


def cited(text):
    found = set()
    for group in re.findall(r"\[(S\d+(?:\s*,\s*S\d+)*)\]", text):
        found.update(x.strip() for x in group.split(","))
    return found


def to_markdown(state):
    lesson = state["lesson"]
    sources = state["research"]["sources"]
    by_id = {s["id"]: s for s in sources}
    total = sum(int(s["minutes"]) for s in lesson["sections"])
    out = [
        f"# {state['title']}",
        "",
        f"**Learning objective:** {state['objective']}",
        "",
        f"**Total time:** {total} minutes",
        "",
    ]
    for s in lesson["sections"]:
        out += [f"## {s['title']} ({s['minutes']} min)", "", s["content"], ""]

    if lesson.get("videos"):
        out += ["## Watch next (optional)", ""]
        for v in lesson["videos"]:
            src = by_id.get(v["id"])
            if src:
                out.append(f"- [{src['title']}]({src['url']}) - {v.get('why', '')}")
        out.append("")

    used = sorted(cited(lesson_text(lesson["sections"])), key=lambda x: int(x[1:]))
    out += ["## References", ""]
    for i in used:
        if i in by_id:
            s = by_id[i]
            out.append(f"- [{i}] {s['title']}. {s['url']}")
    books = [s for s in sources if s["type"] == "book" and s["id"] not in used]
    if books:
        out += ["", "**Further reading**", ""]
        out += [f"- {b['title']}. {b['url']}" for b in books[:3]]
    return "\n".join(out) + "\n"
