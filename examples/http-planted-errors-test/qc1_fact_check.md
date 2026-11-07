# QC 1 - Research and factual accuracy

**Lesson:** HTTP Requests and Responses (planted errors)

**Objective:** Explain GET and POST methods and distinguish between 2xx, 4xx, and 5xx response status categories.

## Summary

The lesson introduces basic HTTP concepts (GET vs. POST and 2xx, 4xx, 5xx status code categories). However, it contains several critical factual errors, including false assertions that GET updates data on the server, GET encrypts parameters separately, POST is idempotent, 4xx represents a server failure, 404 is a server crash, and status codes are four-digit numbers.

## Claims checked

| Claim | Status | Sources | Confidence | Best source |
|---|---|---|---|---|
| GET is used to update data on the server and changes server state. | wrong | - | none | - |
| GET sends parameters appended to the URL as query parameters. | supported | S6 | medium | medium |
| Requests using GET should only retrieve data and should not contain request content body. | supported | S5 | medium | high |
| GET is the more secure choice for passwords because URLs are encrypted separately from the body. | wrong | - | none | - |
| POST submits data to the server, often causing a change in state or side effects. | supported | S5, S8 | medium | high |
| The payload in a POST request is sent inside the request body. | supported | S6, S8 | medium | high |
| POST is idempotent. | wrong | - | none | - |
| HTTP status codes are four-digit numeric codes. | wrong | - | none | - |
| Codes in the 400 to 499 range indicate that the server failed while processing a valid request. | wrong | - | none | - |
| 404 Not Found means the server crashed while looking for the page. | wrong | - | none | - |

## Issues

### F1 (high, open)
- **Section:** Concept 1: HTTP Methods — GET vs. POST (10 min)
- **Text:** "GET is used to update data on the server, so it changes server state"
- **Problem:** Factual error. GET requests should be read-only and safe, not used to update data or alter server state.
- **Suggested fix:** Change text to: 'GET is used to retrieve data from the server without modifying server state.'
- **Found by:** AI review

### F2 (high, open)
- **Section:** Concept 1: HTTP Methods — GET vs. POST (10 min)
- **Text:** "GET is the more secure choice for passwords because URLs are encrypted separately from the body"
- **Problem:** Factual error and dangerous security misconception. URL query parameters are logged in plain text on servers and browser history, and HTTPS encrypts the entire HTTP request (headers, URL, body) together.
- **Suggested fix:** Change text to: 'GET should never be used for sensitive data like passwords because query parameters remain stored in browser history and server access logs. POST is preferred for sensitive submissions.'
- **Found by:** AI review

### F3 (high, open)
- **Section:** Concept 1: HTTP Methods — GET vs. POST (10 min)
- **Text:** "Like GET, POST is idempotent, so sending the same POST twice has the same effect as sending it once"
- **Problem:** Factual error. POST is non-idempotent; repeated POST requests may create duplicate resources or side effects.
- **Suggested fix:** Change text to: 'Unlike GET, POST is non-idempotent, meaning sending identical POST requests multiple times may produce additional side effects, such as creating duplicate orders.'
- **Found by:** AI review

### F4 (high, open)
- **Section:** Concept 2: HTTP Response Status Categories (2xx, 4xx, 5xx) (10 min)
- **Text:** "Codes in the 400 to 499 range indicate that the server failed while processing a valid request."
- **Problem:** Factual error. 4xx indicates client error (invalid syntax, bad parameters, unauthorized access), not server failure.
- **Suggested fix:** Change text to: 'Codes in the 400 to 499 range indicate client errors, meaning the request contains bad syntax, missing parameters, or invalid permissions.'
- **Found by:** AI review

### F5 (high, open)
- **Section:** Concept 2: HTTP Response Status Categories (2xx, 4xx, 5xx) (10 min)
- **Text:** "404 Not Found: A server error that means the server crashed while looking for the page"
- **Problem:** Factual error. 404 Not Found means the requested resource could not be found on the server, not that the server crashed.
- **Suggested fix:** Change text to: '404 Not Found: A client error indicating that the server could not find the requested resource or URL.'
- **Found by:** AI review

### F6 (medium, open)
- **Section:** Concept 2: HTTP Response Status Categories (2xx, 4xx, 5xx) (10 min)
- **Text:** "response containing a four‑digit numeric status code"
- **Problem:** Factual error. HTTP status codes are three-digit numbers.
- **Suggested fix:** Change 'four-digit' to 'three-digit'.
- **Found by:** AI review
