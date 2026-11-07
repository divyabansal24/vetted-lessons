import os
import re
import json
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent / "saved"


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:50] or "lesson"


def new_state(title, objective):
    slug = slugify(title)
    if (BASE / slug).exists():
        slug = f"{slug}-{datetime.now().strftime('%H%M%S')}"
    return {
        "slug": slug,
        "title": title,
        "objective": objective,
        "created": datetime.now().isoformat(timespec="seconds"),
        "research": None,
        "lesson": None,
        "lesson_generated": None,
        "older_versions": [],
        "qc1": None,
        "qc2": None,
        "errors": {},
        "rev": 0,
        "widget": 0,
    }


def save(state):
    folder = BASE / state["slug"]
    folder.mkdir(parents=True, exist_ok=True)
    state["updated"] = datetime.now().isoformat(timespec="seconds")
    tmp = folder / "state.tmp"
    tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, folder / "state.json")


def load(slug):
    return json.loads((BASE / slug / "state.json").read_text(encoding="utf-8"))


def list_saved():
    if not BASE.exists():
        return []
    out = []
    for f in sorted(BASE.glob("*/state.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            steps = [n for n, k in (("lesson", "lesson"), ("QC1", "qc1"), ("QC2", "qc2")) if data.get(k)]
            when = (data.get("updated") or data.get("created", ""))[11:16]
            out.append({"slug": data["slug"], "title": data["title"], "label": f"{data['title']} ({when}, {', '.join(steps) or 'new'})"})
        except Exception:
            continue
    return out


def write_exports(state, files):
    folder = BASE / state["slug"] / "export"
    folder.mkdir(parents=True, exist_ok=True)
    for name, text in files.items():
        (folder / name).write_text(text, encoding="utf-8")
    return folder
