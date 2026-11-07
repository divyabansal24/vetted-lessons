# Vetted

Researched lessons, checked twice.

Vetted is a lesson creation tool for instructors. You give it a lesson title and a learning objective. It researches websites, books and YouTube, writes a 45-minute lesson with citations, and then checks the lesson with two separate quality control layers before the instructor reviews, edits and exports it.

Built for the AI Research Intern task (Program Design team).

## What it does

1. **Research** – searches the web (Tavily), YouTube (Tavily + `youtube-transcript-api` for captions) and books (Open Library). Every source gets an id (S1, S2...) and a reliability rating: high for standards and official docs (RFCs, MDN, PostgreSQL docs, .edu), medium for well-known tutorial sites and vendor docs, low for blogs.
2. **Lesson** – writes a 45-minute lesson in a teach-then-apply structure:

   | Section | Minutes |
   |---|---|
   | Real-world hook | 3 |
   | Concept 1 + Try it | 10 |
   | Concept 2 + Try it | 10 |
   | Mini task written as a work ticket | 12 |
   | Knowledge check (5 questions + answer key) | 7 |
   | Recap and where you will use this at work | 3 |

   Facts are cited inline like `[S3]`. Relevant YouTube videos are added as optional viewing, and a reference list is built from the sources the lesson actually cites.
3. **QC 1 – Research and factual accuracy** – a separate AI review lists every factual claim, finds which sources really support it, and marks it supported / weak / unsupported / wrong. Code then adds:
   - a confidence level from the number of supporting sources (3+ high, 1–2 medium, 0 none)
   - a flag when a claim is backed only by low-reliability sources
   - a flag when the lesson cites a source id that does not exist
4. **QC 2 – Instructional quality** – a separate AI review splits the objective into parts and checks each one is explained, practised and assessed, scores alignment, clarity, pacing, examples, practical application and cognitive load, and lists issues with a highest-impact fix. Code adds fixed checks: total time is 45 minutes, every concept has a Try it, the quiz has 5 questions, no section is too thin.
5. **Review, edit, export** – the instructor edits any section (saved automatically), applies or ignores each QC issue, previews the final lesson, and downloads the lesson, both QC reports and the source list as Markdown files or one zip.

## Error handling

- Empty or too-short inputs are blocked before anything runs.
- Every step saves to `saved/<lesson>/state.json` straight away, so a crash or a failed call never loses research, the lesson or edits. The AI-generated version is kept separately, and up to 5 older versions are kept when a lesson is regenerated.
- Any failed step shows the reason and can be retried with the same button.
- If one research source fails (web, YouTube or books) the others still run and a warning is shown.
- YouTube captions get at most 25 seconds; slower videos are kept as links only.
- AI calls have timeouts, retries, and fall back across several Gemini models and then Groq.
- If research is rerun after a lesson exists, the app warns that citations may now point to different sources.
- If the lesson is edited after a QC check, the report is marked as out of date.

## Live demo

A hosted copy runs on Streamlit Community Cloud: **LIVE_LINK**

The full experience is the local version (see Setup). The hosted copy is for a quick look, and has these limits:

- **Saved lessons are not permanent.** Free hosting resets its storage when the app restarts or goes to sleep, so download anything you want to keep from the Preview and export tab.
- **It sleeps when nobody uses it.** The first visit after a break can take up to a minute to wake up.
- **YouTube transcripts may be missing.** YouTube often blocks caption requests from cloud servers, so videos may show "Transcript: no" and are listed as extra viewing only.
- **Free AI limits are shared.** It runs on free Gemini and Groq tiers with daily limits. If they run out, the step shows a clear message and can be retried later.
- **Each step takes 20 seconds to a couple of minutes,** because every step makes one or more AI calls.

## Setup

Needs Python 3.10+.

```
git clone <this repo>
cd vetted-lessons
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS / Linux
pip install -r requirements.txt
copy .env.example .env          # Windows  (cp on macOS / Linux)
```

Put your keys in `.env`:

| Key | Where to get it | Needed |
|---|---|---|
| `GEMINI_API_KEY` | aistudio.google.com | yes |
| `TAVILY_API_KEY` | app.tavily.com | yes |
| `GROQ_API_KEY` | console.groq.com | optional backup |

Check everything works, then start the app:

```
python check_setup.py
streamlit run app.py
```

It opens at http://localhost:8501.

## Project files

| File | Job |
|---|---|
| `app.py` | Streamlit screens and the step-by-step flow |
| `research.py` | Web, YouTube and book search, source reliability rating |
| `lesson.py` | Lesson generation and the Markdown export |
| `qc.py` | QC 1, QC 2, applying fixes, report export |
| `llm.py` | AI calls with timeouts, retries and provider fallback |
| `store.py` | Saving and loading lessons |
| `check_setup.py` | Checks the API keys and services |

## Testing

The `examples/` folder has the real exported output (lesson, both QC reports and the source list) for each run below, so you can see the results without running the app.

Two lessons were generated and checked:

1. **HTTP Requests and Responses** – *Explain GET and POST methods and distinguish between 2xx, 4xx, and 5xx response status categories.* (sample from the brief)
2. **SQL Joins** – *Explain INNER, LEFT, RIGHT and FULL OUTER joins and choose the correct join for a given query.*

### Manual fact check

I checked both lessons myself against RFC 9110 (HTTP Semantics) and the PostgreSQL / MySQL documentation.

- HTTP: GET/POST semantics, query string vs body, the five status classes, 401 as a client error and 422 as a valid code were correct. I found two problems QC 1 had marked as supported: the 204 line quoted RFC 9110 using the wording of the older RFC 7231 ("payload" instead of "content"), and 500 was described as a "server crash" instead of RFC 9110's "unexpected condition". I fixed both in the editor.
- SQL: all four join definitions, MySQL not supporting FULL OUTER JOIN, and the `LEFT JOIN ... WHERE ... IS NULL` pattern were correct. QC 1 caught a real nuance (a bare `JOIN` without `ON` acts as a `CROSS JOIN` in MySQL) and QC 2 caught that RIGHT JOIN was explained but never practised. Both fixes were applied.

### Do the QC layers catch real mistakes?

I took the HTTP lesson and planted 10 known mistakes, then ran both QC layers on it without telling them what was planted.

| # | Planted mistake | Type | Caught by | Result |
|---|---|---|---|---|
| P1 | GET changes server state | fact | QC 1 | caught |
| P2 | POST is idempotent | fact | QC 1 | caught |
| P3 | GET is more secure for passwords | fact | QC 1 | caught |
| P4 | 404 is a server error | fact | QC 1 | caught |
| P5 | Status codes are four digits | fact | QC 1 | caught |
| P6 | 4xx means the server failed | fact | QC 1 | caught |
| P7 | 5xx never explained | teaching | QC 2 (AI review) | caught |
| P8 | Concept 1 has no Try it | teaching | QC 2 (rule check) | caught |
| P9 | Timings add up to 58 minutes | teaching | QC 2 (rule check) | caught |
| P10 | POST question removed from the quiz | teaching | QC 2 | partly caught |

**Result: QC 1 caught 6/6 factual errors with no false alarms. QC 2 caught 3 of the 4 teaching problems fully and 1 partly.** QC 2 also repeated five of the factual errors, which overlaps with QC 1 but is not wrong.

What the test showed and what I changed:

- In the first run QC 1 marked all 6 claims as wrong, but only 5 became issues the instructor could act on. I added a rule so every claim marked wrong always gets an issue, with a keyword check so it does not create duplicates.
- For P10, QC 2 noticed the quiz had only 4 questions but suggested changing the heading to "4 questions" instead of adding the missing POST question, and its coverage table wrongly said POST was assessed. My rule check should have caught this but counted the numbered answer key lines as questions. I fixed the rule to count only the questions.
- On the two real lessons, QC 1 also raised a few false alarms: true claims flagged because the AI matched them to blogs instead of the official docs, so I ignored them after checking.

## Problems I ran into and what I changed

- **Off-topic books.** The first research run returned Anne Frank's diary for an HTTP lesson. Open Library search is loose, so a book now has to share a real topic word with the lesson and, if it only matches one word, carry a computing subject tag.
- **Official spec rated low.** httpwg.org (the HTTP working group's copy of RFC 9110) was rated low, so I added it to the trusted list and rated vendor documentation sites as medium.
- **Gemini overloaded.** During testing the Gemini free tier returned "503 high demand" for every model and later hit its 20 requests a day limit. The app now rotates through several Gemini models, waits and retries, and finally falls back to Groq.
- **Citations missing from the reference list.** The lesson often cites `[S5, S6]` together and my first version only read single citations. Fixed, and the fake-citation check now covers grouped citations too.
- **QC rules tested with planted mistakes.** See the table above: two rule bugs were found and fixed this way.
- **QC 2 false alarms.** QC 2 flagged the `[S3]` citation tags as clutter and kept miscounting the Try it minutes as extra time. I told the reviewer which things are intentional, and since the app already computes the total minutes exactly, the code now drops AI timing complaints when the rule check confirms 45 minutes.

## Design decisions

- **QC runs as separate AI calls from generation**, and each reviewer is told it did not write the lesson, so the checker does not share the writer's assumptions.
- **Rules where things can be calculated, AI where judgment is needed.** Minutes, question counts, citation ids and source counts are checked by code, because the AI got them wrong in testing.
- **The instructor stays in charge.** Every QC issue can be applied or ignored, and an applied fix only rewrites one section. Fixes rewrite the whole section, so it is worth rereading it afterwards.
- **No keys needed for books and videos.** Open Library and Tavily's YouTube search avoid extra Google Cloud setup.

## Limitations

- QC 1 reads only an excerpt (about 1,200 characters) of each source, so it can miss support that appears further down a page. The instructor can overrule it.
- AI QC reduces errors but does not replace a human check, as the manual fact check above shows.
- Books are listed from catalogue records only; their text is not read.
- YouTube sometimes blocks caption requests, in which case videos are listed as extra viewing only.

## Credits

- Source-count confidence idea inspired by [klausners/course-builder](https://github.com/klausners/course-builder) (MIT). Idea only, no code used.
- Instructional audit ideas (prioritised fixes, highest-impact fix) inspired by [Gowtham-Pentela/lectureforge-ai](https://github.com/Gowtham-Pentela/lectureforge-ai). Idea only, no code used.
- Lesson structure (teach then apply in the same session, work-style tasks) based on Kalvium's public description of how it teaches. No Kalvium content used.
- Built with Streamlit, Google Gemini API, Groq API, Tavily, youtube-transcript-api and the Open Library API.
- AI assistance: Claude was used to help write and debug code, as the brief allows.
