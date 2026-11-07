# QC 2 - Instructional quality

**Lesson:** HTTP Requests and Responses

**Objective:** Explain GET and POST methods and distinguish between 2xx, 4xx, and 5xx response status categories.

_Note: the lesson was changed after this check ran._

## Summary

The 45-minute lesson solidly covers the core objective of explaining GET vs. POST and distinguishing 2xx, 4xx, and 5xx status codes through balanced instruction, realistic mini-scenarios, and a well-aligned workplace ticketing exercise. However, the schedule totals 47–48 minutes rather than 45, and distractor options in the quiz introduce HTTP concepts not covered in the lesson.

## Objective coverage

| Part | Explained | Practised | Assessed |
|---|---|---|---|
| Explain GET method | yes | yes | yes |
| Explain POST method | yes | yes | yes |
| Distinguish 2xx status category | yes | yes | yes |
| Distinguish 4xx status category | yes | yes | yes |
| Distinguish 5xx status category | yes | yes | yes |

## Scores

- **alignment:** 5/5 - Instruction, practice scenarios, workplace ticket, and assessment questions map directly to GET, POST, and 2xx/4xx/5xx categories.
- **clarity:** 5/5 - Explanations are concise, technically precise with RFC citations, and use clear contrast between client and server responsibilities.
- **structure and pacing:** 4/5 - The flow is logical and scaffolds well, but total segment durations add up to 47–48 minutes instead of the allocated 45 minutes.
- **examples:** 5/5 - Practical, concrete examples such as product searches, login/registration, and payment checkout provide strong mental models.
- **practical application:** 5/5 - The Jira-style engineering ticket provides genuine, job-relevant practice in triage and API contract design.
- **cognitive load:** 4/5 - Cognitive load is well managed overall, though introducing unmentioned methods (PUT, CONNECT) and categories (3xx) in quiz options creates unnecessary noise.

**Highest impact fix:** Trim the section timings by 2–3 minutes (e.g., reducing the hook to 2 min and ticket to 10 min) to fit the strict 45-minute schedule, and replace unintroduced distractors in the quiz with familiar terms.

## Issues

### T1 (medium, ignored)
- **Section:** Timings / Structure
- **Text:** "Real-world hook (3 min) ... Concept 1: (10 min) ... Try it (2-3 minutes) ... Concept 2: (10 min) ... Try it (2‑3 minutes) ... Mini task (12 min) ... Knowledge check (7 min) ... Recap (3 min)"
- **Problem:** The sum of listed section timings is between 47 and 49 minutes, which exceeds the designated 45-minute total lesson limit.
- **Suggested fix:** Adjust timings: Real-world hook (2 min), Concept 1 + Try it (10 min total), Concept 2 + Try it (10 min total), Mini task (11 min), Knowledge check (9 min), Recap (3 min) to total exactly 45 minutes.
- **Found by:** AI review

### T2 (low, ignored)
- **Section:** Knowledge check
- **Text:** "c) PUT  
   d) CONNECT"
- **Problem:** Question 1 introduces PUT and CONNECT as multiple-choice options, which were neither defined nor mentioned anywhere in the lesson.
- **Suggested fix:** Replace with concepts touched upon in the lesson or common non-verbs, such as 'c) FETCH' and 'd) STATUS'.
- **Found by:** AI review

### T3 (low, applied)
- **Section:** Knowledge check
- **Text:** "b) 3xx"
- **Problem:** Question 3 introduces the 3xx status category in the options, but 3xx redirection was not taught in Concept 2.
- **Suggested fix:** Replace option b with another plausible category option or explicitly state in Concept 2 that 3xx handles redirection, e.g., keep choices limited to 2xx, 4xx, 5xx, or 1xx.
- **Found by:** AI review
