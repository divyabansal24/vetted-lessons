import re
from llm import ask
from lesson import source_text, lesson_text, cited

RANK = {"high": 3, "medium": 2, "low": 1}
SEVERITY = {"high": 0, "medium": 1, "low": 2}


def tidy(issue, origin="ai"):
    sev = str(issue.get("severity", "medium")).lower()
    return {
        "severity": sev if sev in SEVERITY else "medium",
        "section": issue.get("section", ""),
        "quote": issue.get("quote", ""),
        "problem": issue.get("problem", ""),
        "fix": issue.get("fix", ""),
        "origin": origin,
        "status": "open",
    }


def number(issues, prefix):
    issues.sort(key=lambda i: SEVERITY[i["severity"]])
    for n, i in enumerate(issues, 1):
        i["id"] = f"{prefix}{n}"
    return issues


STOP = {"the", "and", "for", "that", "this", "with", "are", "was", "from", "because", "while", "which", "used"}


def keywords(text):
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if len(w) > 2 and w not in STOP}


def covered(claim, issues):
    want = keywords(claim)
    if not want:
        return True
    for i in issues:
        have = keywords(f"{i.get('quote', '')} {i.get('problem', '')} {i.get('fix', '')}")
        if len(want & have) / len(want) >= 0.6:
            return True
    return False


def fact_check(state):
    sources = state["research"]["sources"]
    by_id = {s["id"]: s for s in sources}
    text = lesson_text(state["lesson"]["sections"])
    prompt = f"""You are a strict fact checker. Review this lesson before students see it. You did not write it.

Lesson title: {state['title']}
Learning objective: {state['objective']}

Step 1. List every factual claim that matters for learning: definitions, rules, numbers, how something behaves. Skip opinions and instructions to the student.
For each claim give:
- "section": the section title it is in
- "claim": the claim in one short sentence
- "sources": ids of sources below whose text actually supports it. Read the text, do not trust the lesson's own citation.
- "status": "supported", "weak" (partly supported or vague), "unsupported" (no source supports it) or "wrong" (false, or a source contradicts it)
- "note": one short line explaining the status

Step 2. List issues: false or misleading statements, claims that need a source, sources that are unreliable or off topic, contradictions between sections, and gaps that would leave a student with a wrong idea.
Use your own knowledge as well as the sources to catch false statements.
Each issue: "severity" (high, medium or low), "section", "quote" (a few exact words from the lesson), "problem", "fix" (the corrected text or a concrete action).

Sources:
{source_text(sources)}

Lesson:
{text}

Return JSON only:
{{"summary": "...", "claims": [...], "issues": [...]}}"""
    data = ask(prompt, as_json=True)

    claims = []
    for c in data.get("claims", []):
        ids = [i for i in c.get("sources", []) if i in by_id]
        count = len(ids)
        best = max((RANK[by_id[i]["reliability"]] for i in ids), default=0)
        claims.append({
            "section": c.get("section", ""),
            "claim": c.get("claim", ""),
            "status": str(c.get("status", "unsupported")).lower(),
            "sources": ids,
            "source_count": count,
            "confidence": "high" if count >= 3 else "medium" if count >= 1 else "none",
            "best_source": {3: "high", 2: "medium", 1: "low", 0: "-"}[best],
            "note": c.get("note", ""),
        })

    issues = [tidy(i) for i in data.get("issues", [])]
    for c in claims:
        if c["status"] == "wrong" and not covered(c["claim"], issues):
            issues.append(tidy({
                "severity": "high",
                "section": c["section"],
                "quote": c["claim"],
                "problem": f"QC 1 marked this claim as wrong: {c['note'] or c['claim']}",
                "fix": "Correct the statement using the cited official sources.",
            }, "rule"))
        if c["status"] in ("supported", "weak") and c["best_source"] == "low":
            issues.append(tidy({
                "severity": "medium",
                "section": c["section"],
                "problem": f"\"{c['claim']}\" is only backed by low-reliability sources.",
                "fix": "Cite official documentation or a standard for this point, or soften the wording.",
            }, "rule"))
        if c["status"] == "supported" and c["source_count"] == 0:
            issues.append(tidy({
                "severity": "low",
                "section": c["section"],
                "problem": f"\"{c['claim']}\" has no supporting source in the research.",
                "fix": "Add a citation or run research again with a narrower query.",
            }, "rule"))
    for bad in sorted(cited(text) - set(by_id), key=lambda x: int(x[1:])):
        issues.append(tidy({
            "severity": "high",
            "problem": f"The lesson cites [{bad}], which is not one of the research sources.",
            "fix": f"Remove [{bad}] or replace it with a real source id.",
        }, "rule"))

    stats = {}
    for c in claims:
        stats[c["status"]] = stats.get(c["status"], 0) + 1
    return {
        "summary": data.get("summary", ""),
        "claims": claims,
        "stats": stats,
        "issues": number(issues, "F"),
        "rev": state["rev"],
    }


def teaching_check(state):
    sections = state["lesson"]["sections"]
    issues = []

    total = sum(int(s["minutes"]) for s in sections)
    if total != 45:
        issues.append(tidy({
            "severity": "high",
            "problem": f"The lesson adds up to {total} minutes, not 45.",
            "fix": "Change the minutes of the sections so they add up to 45, or trim content.",
        }, "rule"))
    for s in sections:
        if len(s["content"].strip()) < 150:
            issues.append(tidy({
                "severity": "medium",
                "section": s["title"],
                "problem": "This section is very short for the time it is given.",
                "fix": "Add an explanation, an example or a step the student can follow.",
            }, "rule"))
        if s.get("kind") in ("concept1", "concept2") and "try it" not in s["content"].lower():
            issues.append(tidy({
                "severity": "medium",
                "section": s["title"],
                "problem": "The concept is explained but the student never applies it here.",
                "fix": "End the section with a short Try it exercise and its answer.",
            }, "rule"))
    quiz = next((s for s in sections if s.get("kind") == "quiz"), None)
    questions = re.split(r"(?i)answer key|answers\b", quiz["content"])[0] if quiz else ""
    if quiz and len(re.findall(r"(?m)^\s*(?:\*\*)?(?:Q\s*)?\d+[.)]", questions)) < 5:
        issues.append(tidy({
            "severity": "medium",
            "section": quiz["title"],
            "problem": "The knowledge check has fewer than 5 questions.",
            "fix": "Add questions until there are 5, each tied to part of the objective.",
        }, "rule"))

    prompt = f"""You are an instructional designer reviewing a 45-minute lesson. You did not write it. Be honest and specific.

Lesson title: {state['title']}
Learning objective: {state['objective']}

Things that are on purpose, do not report them:
- Inline tags like [S3] are source citations required for fact checking and the reference list.
- "Try it" exercises are part of their section's minutes, not extra time. The section minutes add up to {total}, and the app checks the total itself, so do not report the total time.

1. Split the learning objective into its separate parts (for example each method, term or category it names).
   For each part: "part", "explained" (true/false), "practised" (true/false, there is an exercise or task on it), "assessed" (true/false, a quiz question tests it), "note".
2. Score from 1 to 5 with a one line reason: "alignment", "clarity", "structure_and_pacing", "examples", "practical_application", "cognitive_load" (5 means the load is well managed).
3. "highest_impact_fix": the one change that would most improve learning.
4. "issues": parts of the objective that are not taught, practised or tested; unclear explanations; missing or weak examples; practice that does not match the objective; timings that will not work; too much at once; quiz questions that do not test the objective or have a wrong answer.
   Each issue: "severity" (high, medium or low), "section", "quote" (a few exact words), "problem", "fix" (concrete, ideally the new text).

Lesson:
{lesson_text(sections)}

Return JSON only:
{{"summary": "...", "objective_parts": [...], "scores": {{"alignment": {{"score": 4, "reason": "..."}}}}, "highest_impact_fix": "...", "issues": [...]}}"""
    data = ask(prompt, as_json=True)

    parts = data.get("objective_parts", [])
    for p in parts:
        missing = [w for w in ("explained", "practised", "assessed") if not p.get(w)]
        if missing:
            issues.append(tidy({
                "severity": "high" if "explained" in missing else "medium",
                "problem": f"Objective part \"{p.get('part', '')}\" is not {', '.join(missing)}.",
                "fix": f"Add what is missing for \"{p.get('part', '')}\": " + ", ".join(
                    {"explained": "an explanation", "practised": "an exercise", "assessed": "a quiz question"}[m] for m in missing),
            }, "rule"))
    for i in data.get("issues", []):
        text = f"{i.get('problem', '')} {i.get('fix', '')}".lower()
        if total == 45 and "45" in text and "min" in text:
            print("[qc2] dropped an AI timing complaint, the rule check already confirms 45 minutes", flush=True)
            continue
        issues.append(tidy(i))

    return {
        "summary": data.get("summary", ""),
        "objective_parts": parts,
        "scores": data.get("scores", {}),
        "highest_impact_fix": data.get("highest_impact_fix", ""),
        "issues": number(issues, "T"),
        "rev": state["rev"],
    }


def match_section(name, sections):
    name = (name or "").lower().strip()
    if not name:
        return 0
    for i, s in enumerate(sections):
        if s["title"].lower() == name:
            return i
    for i, s in enumerate(sections):
        if name in s["title"].lower() or s["title"].lower() in name:
            return i
    return 0


def apply_fix(state, index, issue):
    section = state["lesson"]["sections"][index]
    prompt = f"""Rewrite one section of a lesson to fix a review comment.

Lesson title: {state['title']}
Learning objective: {state['objective']}
Section: {section['title']} ({section['minutes']} minutes)

Review comment:
Problem: {issue['problem']}
Quoted text: {issue.get('quote', '')}
Suggested fix: {issue['fix']}

Keep everything that is not affected the same, keep the style and length roughly the same, and keep citations like [S2].
Only use facts the sources support.

Sources:
{source_text(state['research']['sources'], 600)}

Current section:
{section['content']}

Return only the new section content in Markdown, without the section title."""
    return ask(prompt)


def report_markdown(state, report, kind):
    title = "QC 1 - Research and factual accuracy" if kind == "qc1" else "QC 2 - Instructional quality"
    out = [f"# {title}", "", f"**Lesson:** {state['title']}", "", f"**Objective:** {state['objective']}", ""]
    if report.get("rev") != state["rev"]:
        out += ["_Note: the lesson was changed after this check ran._", ""]
    out += ["## Summary", "", report.get("summary", ""), ""]

    if kind == "qc1":
        out += ["## Claims checked", ""]
        out += ["| Claim | Status | Sources | Confidence | Best source |", "|---|---|---|---|---|"]
        for c in report["claims"]:
            out.append(f"| {c['claim']} | {c['status']} | {', '.join(c['sources']) or '-'} | {c['confidence']} | {c['best_source']} |")
        out.append("")
    else:
        out += ["## Objective coverage", "", "| Part | Explained | Practised | Assessed |", "|---|---|---|---|"]
        for p in report["objective_parts"]:
            yes = lambda v: "yes" if v else "no"
            out.append(f"| {p.get('part', '')} | {yes(p.get('explained'))} | {yes(p.get('practised'))} | {yes(p.get('assessed'))} |")
        out += ["", "## Scores", ""]
        for name, v in report["scores"].items():
            if isinstance(v, dict):
                out.append(f"- **{name.replace('_', ' ')}:** {v.get('score', '-')}/5 - {v.get('reason', '')}")
        if report.get("highest_impact_fix"):
            out += ["", f"**Highest impact fix:** {report['highest_impact_fix']}"]
        out.append("")

    out += ["## Issues", ""]
    for i in report["issues"]:
        out.append(f"### {i['id']} ({i['severity']}, {i['status']})")
        if i["section"]:
            out.append(f"- **Section:** {i['section']}")
        if i["quote"]:
            out.append(f"- **Text:** \"{i['quote']}\"")
        out.append(f"- **Problem:** {i['problem']}")
        out.append(f"- **Suggested fix:** {i['fix']}")
        out.append(f"- **Found by:** {'rule check' if i['origin'] == 'rule' else 'AI review'}")
        out.append("")
    return "\n".join(out)
