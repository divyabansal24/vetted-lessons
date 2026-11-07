# QC 1 - Research and factual accuracy

**Lesson:** HTTP Requests and Responses

**Objective:** Explain GET and POST methods and distinguish between 2xx, 4xx, and 5xx response status categories.

## Summary

The lesson accurately describes HTTP GET and POST methods, distinguishing their semantic use, payload placement, and safety implications, along with the classification of 2xx, 4xx, and 5xx HTTP response status code categories. The factual claims are strongly backed by RFC 9110 and standard HTTP references, with only minor non-critical omissions regarding 3xx inclusion relative to stated objectives.

## Claims checked

| Claim | Status | Sources | Confidence | Best source |
|---|---|---|---|---|
| GET and POST are HTTP methods defined in RFC 9110. | supported | S1, S2 | medium | high |
| GET requests transfer a current representation of the target resource. | supported | S1, S2, S3 | high | high |
| GET is used to retrieve data without modifying server state and should not contain request content. | supported | S5, S6 | medium | high |
| GET requests append parameters to the URL as query parameters. | supported | S6 | medium | medium |
| Sensitive data such as passwords should never be sent in a GET request. | supported | S6 | medium | medium |
| POST requests the target resource to process the enclosed representation according to the resource's own semantics. | supported | S1, S3 | medium | high |
| POST sends its data payload in the request body rather than the URL. | supported | S6, S8 | medium | high |
| The Content-Type header informs the server of the body's media type. | supported | S6, S8 | medium | high |
| Successive identical POST requests may result in additional side effects like duplicate resource creation. | supported | S8 | medium | high |
| HTTP status codes are three-digit numbers categorized into five classes: 1xx, 2xx, 3xx, 4xx, and 5xx. | supported | S9, S10, S11 | high | high |
| 2xx codes indicate that the action was successfully received, understood, and accepted. | supported | S10, S11 | medium | high |
| 204 No Content indicates the request succeeded but has no response body to return. | supported | S9, S10 | medium | low |
| 4xx codes indicate client error where the request contains bad syntax or cannot be fulfilled. | supported | S10, S11, S12 | high | high |
| 5xx codes indicate the server failed to fulfill an apparently valid request. | supported | S10, S11, S12 | high | high |

## Issues

### F1 (medium, ignored)
- **Section:** Concept 2: HTTP Response Status Categories (2xx, 4xx, 5xx) (10 min)
- **Problem:** "204 No Content indicates the request succeeded but has no response body to return." is only backed by low-reliability sources.
- **Suggested fix:** Cite official documentation or a standard for this point, or soften the wording.
- **Found by:** rule check

### F2 (low, ignored)
- **Section:** Concept 2: HTTP Response Status Categories (2xx, 4xx, 5xx) (10 min)
- **Text:** "3xx: Redirection Codes in the 300 to 399 range indicate redirection"
- **Problem:** The learning objective explicitly targets 2xx, 4xx, and 5xx categories, but 3xx is introduced briefly without mention in the objectives or recap.
- **Suggested fix:** Either update the learning objective to include 3xx or keep 3xx explicitly framed as an aside note.
- **Found by:** AI review
