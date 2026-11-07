import io
import html
import zipfile
import streamlit as st
from dotenv import load_dotenv

import store
import research
import lesson
import qc

load_dotenv()
st.set_page_config(page_title="Vetted", layout="wide")
st.markdown(
    """
    <style>
    .block-container {max-width: 1120px; padding-top: 1.6rem;}
    h1 {font-size: 1.75rem; margin: 0.2rem 0 0 0;}
    .brand {display: flex; align-items: baseline; gap: 0.7rem; margin-bottom: 1.2rem;
            border-bottom: 1px solid rgba(128,128,128,0.25); padding-bottom: 0.7rem;}
    .brand b {font-size: 1.25rem; letter-spacing: 0.02em; color: #3fb68b;}
    .brand span {color: #8a948f; font-size: 0.9rem;}
    .muted {color: #8a948f; font-size: 0.93rem; margin-top: 0.3rem;}
    .steps {display: flex; gap: 0.5rem; margin: 1rem 0 0.6rem 0; flex-wrap: wrap;}
    .step {flex: 1; min-width: 120px; padding: 0.55rem 0.8rem; border-radius: 8px;
           border: 1px solid rgba(128,128,128,0.3); font-size: 0.88rem; color: #8a948f;}
    .step.done {border-color: #3fb68b; color: #3fb68b; background: rgba(63,182,139,0.08);}
    .step.next {border-color: #e0b341; color: #e0b341;}
    .step small {display: block; font-size: 0.75rem; opacity: 0.85;}
    .tag {display: inline-block; padding: 0.08rem 0.5rem; border-radius: 999px; font-size: 0.75rem;
          margin-right: 0.35rem; border: 1px solid; font-weight: 600;}
    .tag.high {color: #e5534b; border-color: #e5534b;}
    .tag.medium {color: #e0b341; border-color: #e0b341;}
    .tag.low {color: #8a948f; border-color: #8a948f;}
    .tag.open {color: #e8ece9; border-color: rgba(128,128,128,0.5);}
    .tag.applied {color: #3fb68b; border-color: #3fb68b;}
    .tag.ignored {color: #8a948f; border-color: rgba(128,128,128,0.4);}
    .tag.src {color: #6ea8fe; border-color: #6ea8fe;}
    .how {border: 1px solid rgba(128,128,128,0.3); border-radius: 10px; padding: 0.9rem 1rem; height: 100%;}
    .how b {color: #3fb68b;}
    </style>
    """,
    unsafe_allow_html=True,
)


def tag(text, kind):
    return f'<span class="tag {kind}">{html.escape(str(text))}</span>'


def steps_bar(state):
    items = [
        ("Research", bool(state["research"])),
        ("Lesson", bool(state["lesson"])),
        ("QC 1 · facts", bool(state["qc1"])),
        ("QC 2 · teaching", bool(state["qc2"])),
        ("Export", bool(state["qc1"] and state["qc2"])),
    ]
    out, marked = [], False
    for n, (name, ok) in enumerate(items, 1):
        if ok:
            cls, note = "done", "done"
        elif not marked:
            cls, note, marked = "next", "next step", True
        else:
            cls, note = "", "waiting"
        out.append(f'<div class="step {cls}"><small>Step {n} · {note}</small>{name}</div>')
    st.markdown(f'<div class="steps">{"".join(out)}</div>', unsafe_allow_html=True)


def get():
    return st.session_state.get("state")


def put(state):
    st.session_state["state"] = state
    store.save(state)


def run_step(state, step, message, fn):
    try:
        with st.spinner(message):
            fn()
        state["errors"].pop(step, None)
        put(state)
        return True
    except Exception as e:
        state["errors"][step] = str(e)
        put(state)
        return False


def show_error(state, step):
    err = state["errors"].get(step)
    if err:
        st.error(f"This step failed: {err}\n\nYour saved work is safe. Click the button again to retry.")


def edit(i, field, key):
    state = get()
    value = st.session_state[key]
    state["lesson"]["sections"][i][field] = int(value) if field == "minutes" else value
    state["rev"] += 1
    put(state)


with st.sidebar:
    st.markdown("### New lesson")
    with st.form("new_lesson", clear_on_submit=False):
        title = st.text_input("Lesson title")
        objective = st.text_area("Learning objective", height=110)
        start = st.form_submit_button("Start new lesson")
    if start:
        if not title.strip() or not objective.strip():
            st.error("Please fill in both the lesson title and the learning objective.")
        elif len(objective.strip()) < 15:
            st.error("The learning objective is too short. Say what the student should be able to do.")
        else:
            put(store.new_state(title.strip(), objective.strip()))
            st.rerun()

    saved = store.list_saved()
    if saved:
        st.divider()
        pick = st.selectbox("Saved lessons", saved, format_func=lambda s: s.get("label", s["title"]))
        if st.button("Open"):
            st.session_state["state"] = store.load(pick["slug"])
            st.rerun()


state = get()
if not state:
    st.markdown('<div class="brand"><b>Vetted</b><span>Researched lessons, checked twice.</span></div>', unsafe_allow_html=True)
    st.title("Create a 45-minute lesson")
    st.markdown('<p class="muted">Enter a lesson title and a learning objective in the sidebar to start, or open a saved lesson.</p>', unsafe_allow_html=True)
    cols = st.columns(4)
    cards = [
        ("1. Research", "Websites, books and YouTube, each source rated for reliability."),
        ("2. Lesson", "Teach then apply: hook, two concepts with Try it, a work ticket, a quiz and a recap."),
        ("3. Two QC layers", "QC 1 checks every claim against the sources. QC 2 checks the teaching against the objective."),
        ("4. Review and export", "Edit any section, apply or ignore each fix, preview and download."),
    ]
    for col, (head, text) in zip(cols, cards):
        col.markdown(f'<div class="how"><b>{head}</b><br>{text}</div>', unsafe_allow_html=True)
    st.stop()

st.markdown('<div class="brand"><b>Vetted</b><span>Researched lessons, checked twice.</span></div>', unsafe_allow_html=True)
st.title(state["title"])
st.markdown(f'<p class="muted">Objective: {html.escape(state["objective"])}</p>', unsafe_allow_html=True)
steps_bar(state)

tabs = st.tabs(["1. Research", "2. Lesson", "3. QC 1 - Facts", "4. QC 2 - Teaching", "5. Preview and export"])

with tabs[0]:
    r = state["research"]
    if st.button("Run research again" if r else "Run research"):
        def step():
            state["research"] = research.run(state["title"], state["objective"])
            if state["lesson"]:
                state["research_changed"] = True
        if run_step(state, "research", "Searching websites, books and YouTube...", step):
            st.rerun()
    show_error(state, "research")
    if r:
        for w in r["warnings"]:
            st.warning(w)
        q = r["queries"]
        st.markdown(f"**Search queries:** {', '.join(q.get('web', []))} · video: {q.get('video', '')} · books: {q.get('books', '')}")
        for kind, label in [("web", "Websites"), ("book", "Books"), ("video", "YouTube videos")]:
            rows = [s for s in r["sources"] if s["type"] == kind]
            st.subheader(f"{label} ({len(rows)})")
            if not rows:
                st.write("None found.")
                continue
            table = []
            for s in rows:
                row = {"ID": s["id"], "Title": s["title"], "Reliability": s["reliability"], "Link": s["url"]}
                if kind == "video":
                    row["Transcript"] = "yes" if s.get("has_transcript") else "no"
                table.append(row)
            st.dataframe(table, hide_index=True, width="stretch",
                         column_config={"Link": st.column_config.LinkColumn("Link")})

with tabs[1]:
    if not state["research"]:
        st.info("Run research first.")
    else:
        L = state["lesson"]
        if st.button("Generate a new lesson" if L else "Generate lesson"):
            def step():
                if state["lesson"]:
                    state["older_versions"] = ([state["lesson"]] + state["older_versions"])[:5]
                state["lesson"] = lesson.generate(state["title"], state["objective"], state["research"])
                state["lesson_generated"] = {"sections": [dict(s) for s in state["lesson"]["sections"]],
                                             "videos": list(state["lesson"]["videos"])}
                state["rev"] += 1
                state["widget"] += 1
                state["research_changed"] = False
            if run_step(state, "lesson", "Writing the lesson...", step):
                st.rerun()
        show_error(state, "lesson")
        if state.get("research_changed"):
            st.warning("Research was run again after this lesson was written, so its [S] citations may point to the wrong sources. Generate a new lesson.")
        L = state["lesson"]
        if L:
            total = sum(int(s["minutes"]) for s in L["sections"])
            if total == 45:
                st.success("Total time: 45 minutes")
            else:
                st.warning(f"Total time: {total} minutes. It should be 45.")
            st.caption("Changes save on their own when you click outside a box.")
            w = state["widget"]
            for i, s in enumerate(L["sections"]):
                with st.expander(f"{s['title']} ({s['minutes']} min)"):
                    c1, c2 = st.columns([4, 1])
                    c1.text_input("Title", value=s["title"], key=f"t{i}_{w}",
                                  on_change=edit, args=(i, "title", f"t{i}_{w}"))
                    c2.number_input("Minutes", min_value=0, max_value=45, value=int(s["minutes"]),
                                    key=f"m{i}_{w}", on_change=edit, args=(i, "minutes", f"m{i}_{w}"))
                    st.text_area("Content", value=s["content"], height=320, key=f"c{i}_{w}",
                                 on_change=edit, args=(i, "content", f"c{i}_{w}"))
            if state["lesson_generated"] and st.button("Undo all edits and go back to the AI version"):
                state["lesson"] = {"sections": [dict(s) for s in state["lesson_generated"]["sections"]],
                                   "videos": list(state["lesson_generated"]["videos"])}
                state["rev"] += 1
                state["widget"] += 1
                put(state)
                st.rerun()


def show_issues(state, report, name):
    sections = state["lesson"]["sections"]
    titles = [s["title"] for s in sections]
    open_count = sum(1 for i in report["issues"] if i["status"] == "open")
    st.subheader(f"Issues ({open_count} open of {len(report['issues'])})")
    for issue in report["issues"]:
        with st.container(border=True):
            source = "rule check" if issue["origin"] == "rule" else "AI review"
            st.markdown(f"<b>{issue['id']}</b> &nbsp;" + tag(issue["severity"], issue["severity"]) + tag(issue["status"], issue["status"]) + tag(source, "src"), unsafe_allow_html=True)
            if issue["section"]:
                st.markdown(f"Section: {issue['section']}")
            if issue["quote"]:
                st.markdown(f"> {issue['quote']}")
            st.markdown(f"**Problem:** {issue['problem']}")
            st.markdown(f"**Suggested fix:** {issue['fix']}")
            if issue["status"] != "open":
                continue
            key = f"{name}_{issue['id']}"
            idx = qc.match_section(issue["section"], sections)
            target = st.selectbox("Apply to section", range(len(titles)), index=idx,
                                  format_func=lambda j: titles[j], key=f"sel_{key}")
            c1, c2, _ = st.columns([1, 1, 4])
            if c1.button("Apply fix", key=f"apply_{key}"):
                def step():
                    new = qc.apply_fix(state, target, issue)
                    state["lesson"]["sections"][target]["content"] = new
                    issue["status"] = "applied"
                    state["rev"] += 1
                    state["widget"] += 1
                if run_step(state, f"fix_{key}", "Rewriting that section...", step):
                    st.rerun()
            if c2.button("Ignore", key=f"ignore_{key}"):
                issue["status"] = "ignored"
                put(state)
                st.rerun()
            show_error(state, f"fix_{key}")


with tabs[2]:
    if not state["lesson"]:
        st.info("Generate the lesson first.")
    else:
        if st.button("Run QC 1 again" if state["qc1"] else "Run QC 1"):
            def step():
                state["qc1"] = qc.fact_check(state)
            if run_step(state, "qc1", "Checking every claim against the sources...", step):
                st.rerun()
        show_error(state, "qc1")
        rep = state["qc1"]
        if rep:
            if rep["rev"] != state["rev"]:
                st.warning("The lesson has changed since this check ran. Run QC 1 again to check the latest version.")
            st.write(rep["summary"])
            stat_cols = st.columns(4)
            for col, key in zip(stat_cols, ["supported", "weak", "unsupported", "wrong"]):
                col.metric(f"Claims {key}", rep["stats"].get(key, 0))
            st.caption("Confidence comes from how many sources back a claim: 3 or more is high, 1 to 2 is medium, 0 is none.")
            st.dataframe([
                {"Claim": c["claim"], "Status": c["status"], "Sources": ", ".join(c["sources"]) or "-",
                 "Confidence": c["confidence"], "Best source": c["best_source"], "Note": c["note"]}
                for c in rep["claims"]
            ], hide_index=True, width="stretch")
            show_issues(state, rep, "qc1")

with tabs[3]:
    if not state["lesson"]:
        st.info("Generate the lesson first.")
    else:
        if st.button("Run QC 2 again" if state["qc2"] else "Run QC 2"):
            def step():
                state["qc2"] = qc.teaching_check(state)
            if run_step(state, "qc2", "Reviewing the lesson as an instructional designer...", step):
                st.rerun()
        show_error(state, "qc2")
        rep = state["qc2"]
        if rep:
            if rep["rev"] != state["rev"]:
                st.warning("The lesson has changed since this check ran. Run QC 2 again to check the latest version.")
            st.write(rep["summary"])
            if rep.get("highest_impact_fix"):
                st.info(f"Highest impact fix: {rep['highest_impact_fix']}")
            yes = lambda v: "yes" if v else "no"
            st.markdown("**Objective coverage**")
            st.dataframe([
                {"Part": p.get("part", ""), "Explained": yes(p.get("explained")),
                 "Practised": yes(p.get("practised")), "Assessed": yes(p.get("assessed")), "Note": p.get("note", "")}
                for p in rep["objective_parts"]
            ], hide_index=True, width="stretch")
            scores = [(k, v) for k, v in rep["scores"].items() if isinstance(v, dict)]
            if scores:
                cols = st.columns(len(scores))
                for col, (k, v) in zip(cols, scores):
                    col.metric(k.replace("_", " "), f"{v.get('score', '-')}/5", help=v.get("reason", ""))
            show_issues(state, rep, "qc2")

with tabs[4]:
    if not state["lesson"]:
        st.info("Generate the lesson first.")
    else:
        md = lesson.to_markdown(state)
        files = {"lesson.md": md}
        if state["qc1"]:
            files["qc1_fact_check.md"] = qc.report_markdown(state, state["qc1"], "qc1")
        if state["qc2"]:
            files["qc2_teaching_review.md"] = qc.report_markdown(state, state["qc2"], "qc2")
        refs = "\n".join(f"{s['id']}\t{s['type']}\t{s['reliability']}\t{s['title']}\t{s['url']}"
                         for s in state["research"]["sources"])
        files["sources.tsv"] = "id\ttype\treliability\ttitle\turl\n" + refs + "\n"

        c1, c2, c3 = st.columns(3)
        c1.download_button("Download lesson (.md)", md, file_name=f"{state['slug']}.md")
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
            for name, text in files.items():
                z.writestr(name, text)
        c2.download_button("Download everything (.zip)", buf.getvalue(), file_name=f"{state['slug']}.zip")
        if c3.button("Save export to disk"):
            folder = store.write_exports(state, files)
            st.success(f"Saved to {folder}")
        if not state["qc1"] or not state["qc2"]:
            st.caption("Run both QC layers to include their reports in the export.")
        st.divider()
        st.markdown(md)
