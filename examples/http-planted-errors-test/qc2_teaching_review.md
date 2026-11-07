# QC 2 - Instructional quality

**Lesson:** HTTP Requests and Responses (planted errors)

**Objective:** Explain GET and POST methods and distinguish between 2xx, 4xx, and 5xx response status categories.

## Summary

The lesson introduces core HTTP concepts (GET/POST and 2xx/4xx/5xx status codes), supported by a realistic work ticket exercise. However, it contains severe factual errors regarding GET security, POST idempotency, 4xx definition, and GET state modification.

## Objective coverage

| Part | Explained | Practised | Assessed |
|---|---|---|---|
| Explain GET method | yes | yes | yes |
| Explain POST method | yes | yes | yes |
| Distinguish between 2xx response status category | yes | yes | yes |
| Distinguish between 4xx response status category | yes | yes | yes |
| Distinguish between 5xx response status category | yes | yes | yes |

## Scores

- **alignment:** 3/5 - The exercises and assessment align well with the objective, but severe factual errors in the instructional content misalign with actual technical standards.
- **clarity:** 2/5 - Contradictory and incorrect technical statements severely impair learning clarity.
- **structure and pacing:** 4/5 - Good logical structure with hook, concept breakdown, practice scenario, and assessment.
- **examples:** 4/5 - The scenario ticket (ENG-3104) is highly practical and realistic for a backend developer role.
- **practical application:** 4/5 - The mini task work ticket provides excellent real-world application.
- **cognitive load:** 3/5 - The amount of content is appropriate, but processing contradictory statements increases confusion.

**Highest impact fix:** Fix the critical technical misconceptions in Concept 1 and Concept 2 (GET state changes, GET password security, POST idempotency, 4xx definition) so learners receive accurate HTTP foundational knowledge.

## Issues

### T1 (high, open)
- **Problem:** The lesson adds up to 58 minutes, not 45.
- **Suggested fix:** Change the minutes of the sections so they add up to 45, or trim content.
- **Found by:** rule check

### T2 (high, open)
- **Section:** Concept 1: HTTP Methods — GET vs. POST
- **Text:** "GET is used to update data on the server, so it changes server state"
- **Problem:** Factual error: GET requests are safe and read-only; they should not modify server state.
- **Suggested fix:** GET is used to retrieve data from the server and should not modify server state.
- **Found by:** AI review

### T3 (high, open)
- **Section:** Concept 1: HTTP Methods — GET vs. POST
- **Text:** "GET is the more secure choice for passwords because URLs are encrypted separately from the body"
- **Problem:** Factual error: GET places parameters in the URL, exposing them in history, logs, and headers. POST is far more secure for sensitive data.
- **Suggested fix:** GET should never be used for sensitive data like passwords because URL parameters are stored in server logs and browser history.
- **Found by:** AI review

### T4 (high, open)
- **Section:** Concept 1: HTTP Methods — GET vs. POST
- **Text:** "Like GET, POST is idempotent"
- **Problem:** Factual error: POST is non-idempotent by default.
- **Suggested fix:** Unlike GET, POST is non-idempotent; submitting the same POST request multiple times may result in duplicate operations (such as double charges).
- **Found by:** AI review

### T5 (high, open)
- **Section:** Concept 2: HTTP Response Status Categories (2xx, 4xx, 5xx)
- **Text:** "4xx: Client Error ... indicate that the server failed while processing a valid request"
- **Problem:** Factual error: 4xx indicates an issue caused by the client (invalid request, bad syntax, missing auth), not a server failure.
- **Suggested fix:** 4xx: Client Error status codes indicate that the request contains bad syntax, invalid parameters, or cannot be fulfilled due to client-side issues.
- **Found by:** AI review

### T6 (medium, open)
- **Section:** Concept 1: HTTP Methods — GET vs. POST
- **Problem:** The concept is explained but the student never applies it here.
- **Suggested fix:** End the section with a short Try it exercise and its answer.
- **Found by:** rule check

### T7 (medium, open)
- **Section:** Concept 2: HTTP Response Status Categories (2xx, 4xx, 5xx)
- **Text:** "404 Not Found: A server error that means the server crashed"
- **Problem:** Factual error: 404 means the requested resource was not found on the server, not that the server crashed.
- **Suggested fix:** 404 Not Found: Indicates that the requested resource could not be found on the server.
- **Found by:** AI review

### T8 (medium, open)
- **Section:** Concept 2: HTTP Response Status Categories (2xx, 4xx, 5xx)
- **Text:** "5xx: Server Error"
- **Problem:** The lesson omits a dedicated text section defining 5xx, despite naming 5xx in the objective and using it in exercises.
- **Suggested fix:** Add a subsection: '### 5xx: Server Error\nCodes in the 500 to 599 range indicate that the server encountered an internal error or failure while attempting to fulfill a valid request (e.g., 500 Internal Server Error).'
- **Found by:** AI review

### T9 (low, open)
- **Section:** Knowledge check (7 min)
- **Text:** "Test your understanding with these 5 questions:"
- **Problem:** The section header claims there are 5 questions, but only 4 are listed.
- **Suggested fix:** Update the header text to: 'Test your understanding with these 4 questions:'
- **Found by:** AI review
