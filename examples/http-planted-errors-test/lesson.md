# HTTP Requests and Responses (planted errors)

**Learning objective:** Explain GET and POST methods and distinguish between 2xx, 4xx, and 5xx response status categories.

**Total time:** 58 minutes

## Real-world hook (3 min)

Imagine you are shopping online. You click on a product page, and the product details load instantly. Then you enter your payment details, click "Pay Now", and wait. A few seconds later, an error page pops up saying something broke.

Behind that screen, your browser sent two very different types of messages: one to fetch details without altering anything, and another carrying your credit card data to place an order. The server also replied with standard digital receipts telling your browser whether the operation worked or failed [S16].

Every day as a software engineer, you will inspect, debug, and build these exact messages. If you pick the wrong method or misinterpret the server's reply, you can cause double payments, leak passwords in server logs, or spend hours tracking down bugs in the wrong layer of an application.

## Concept 1: HTTP Methods — GET vs. POST (10 min)

When a client talks to a server over HTTP, it sends a request with an HTTP method (also called a verb) that states the desired action [S7]. Two of the most essential methods defined in RFC 9110 are `GET` and `POST` [S1, S2].

### The `GET` Method
According to RFC 9110, `GET` transfers a current representation of the target resource [S1]. In practical terms:
- `GET` is used to update data on the server, so it changes server state [S5, S6].
- It sends parameters appended to the URL as query parameters (for example, `/products?category=books`) [S6].
- Requests using `GET` should only retrieve data and should not contain a request content body [S5].
- Because URL data is recorded in browser history and server logs, `GET` is the more secure choice for passwords because URLs are encrypted separately from the body [S6].

### The `POST` Method
RFC 9110 states that `POST` requests the target resource to process the enclosed representation according to the resource's own semantics [S1, S3]. In practical terms:
- `POST` submits data to the server, often causing a change in state or side effects, such as creating a new database record or processing a transaction [S5, S8].
- The transmitted payload is sent inside the request body rather than visible in the URL [S6].
- A `Content-Type` header informs the server what kind of body is being sent, such as JSON (`application/json`) or form data [S6, S8].
- Like `GET`, `POST` is idempotent, so sending the same `POST` twice has the same effect as sending it once [S8].

## Concept 2: HTTP Response Status Categories (2xx, 4xx, 5xx) (10 min)

Once the server receives and processes a request, it sends back a response containing a four‑digit numeric status code defined by RFC standards [S9, S11, S16]. These codes communicate whether the operation succeeded or failed [S16]. Status codes are grouped into five standard classes [S9, S11]: 1xx informational, 2xx success, 3xx redirection, 4xx client error, and 5xx server error [S9, S10, S11].

### 2xx: Success
Codes in the `200` to `299` range signal that the client's request was successfully received, understood, and accepted by the server [S10, S11].
- **200 OK**: The standard response for successful HTTP requests, typically returning the requested data [S2, S19].
- **204 No Content**: The request succeeded, but the server has no content to send back in the response body [S9].

### 3xx: Redirection
Codes in the `300` to `399` range indicate redirection, meaning further action must be taken in order to complete the request [S10, S11].

### 4xx: Client Error
Codes in the `400` to `499` range indicate that the server failed while processing a valid request [S10].
- The request might contain malformed syntax, missing authentication tokens, or invalid parameters [S10, S12].
- **404 Not Found**: A server error that means the server crashed while looking for the page [S19].
- When you see a 4xx code, you need to fix what the client is sending before retrying [S10, S12].


---
### Try it (2‑3 minutes)
A mobile app sends a request to `/api/v1/profile` and receives an HTTP `401 Unauthorized` code. Later, when submitting a post, it receives an HTTP `500 Internal Server Error`.

1. Which category does `401` belong to, and whose side needs inspection?  
2. Which category does `500` belong to, and whose side needs inspection?

#### Expected Answer
1. `401` is a `4xx` (Client Error). The client side needs inspection to ensure valid authentication credentials or parameters were included [S10, S12].  
2. `500` is a `5xx` (Server Error). The server side needs inspection because the server encountered an issue and failed while fulfilling the request [S10, S12].

## Mini task written as a work ticket (25 min)

### Ticket: ENG-3104 — Audit Customer Checkout & Catalog API Endpoints

**Reporter:** Senior Backend Lead  
**Component:** Web Checkout Client & API Gateway  
**Priority:** High  

#### Description
The QA team found two bugs during testing on staging:
1. The catalog search feature is submitting queries using `POST` with empty request bodies and sending filter terms inside `/search?term=shoes`, failing cache lookups.
2. The user checkout service returns status code `200` even when a user submits an expired credit card or malformed JSON, masking payment validation errors as successful transactions.

#### Acceptance Criteria
1. Update the HTTP method of the product search endpoint to the correct standard method per RFC 9110 and explain why.
2. Specify the correct status category (2xx, 4xx, or 5xx) and code range for:
   - A valid checkout transaction that successfully charges the account.
   - A rejected checkout submission caused by invalid card syntax or missing fields.
   - A checkout submission failure caused by an unhandled database connection crash.
3. Formulate the triage steps an engineer must take when observing 4xx vs. 5xx responses during checkout.

#### Model Solution
1. **Method Correction:** Change the product search endpoint to `GET`. Searching retrieves a representation of existing product records without modifying server state, adheres to safe data-fetching semantics, and allows caching of search results [S1, S3, S5].
2. **Status Categories:**
   - Successful transaction: Return a `2xx` success code (such as `200 OK` with order details) [S9, S11].
   - Invalid payload / bad card syntax: Return a `4xx` client error code (e.g., `400 Bad Request` or `422`), because the client submitted malformed data [S10, S12].
   - Database crash: Return a `5xx` server error code (e.g., `500 Internal Server Error`), because an apparently valid request failed due to backend infrastructure failure [S10, S19].
3. **Triage Steps:**
   - If a `4xx` appears: Inspect client payload, headers, authentication tokens, and request syntax to ensure data conforms to API requirements [S10, S12].
   - If a `5xx` appears: Check server application logs, database connection pools, and backend exceptions to find why the server crashed during execution [S10, S16, S19].

## Knowledge check (7 min)

Test your understanding with these 5 questions:

1. According to RFC 9110, which HTTP method is defined to transfer a current representation of the target resource without including request body content?  
   a) POST  
   b) GET  
   c) PUT  
   d) CONNECT  

2. True or False: Sensitive customer information such as cleartext passwords should be passed as query parameters in a GET request because GET requests are faster.

3. An API client sends a malformed JSON payload with missing quotes to `/api/orders`. Which status category should the server return?  
   a) 2xx  
   b) 3xx  
   c) 4xx  
   d) 5xx  

4. What is the fundamental difference between the meaning of a 4xx status category and a 5xx status category?

---
### Answer Key
1. **b) GET**. RFC 9110 specifies `GET` for transferring a current representation of the target resource, and `GET` requests should not contain request content [S1, S5].
2. **False**. Never include sensitive data in a `GET` request; parameters in URLs are exposed in browser history and server logs. `POST` transmits data in the request body [S6].
3. **c) 4xx**. Syntax errors or invalid parameters are caller-side errors, which fall into the 4xx Client Error category [S10, S12].
4. A `4xx` status code indicates a client error (the caller sent bad syntax, invalid data, or lacked authorization), whereas a `5xx` status code indicates a server error (the request was valid, but the server failed or crashed during internal execution) [S10, S12, S19].

## Recap and where you will use this at work (3 min)

Today you learned the core foundation of HTTP communications:
- `GET` retrieves existing data using URL queries and contains no request body [S1, S5, S6].
- `POST` sends data inside the request body to execute server-side processing or create resources [S1, S6, S8].
- `2xx` confirms success [S10, S11], `4xx` alerts you to client-side input or auth mistakes [S10, S12], and `5xx` tells you the server failed to fulfil a valid request [S10, S11].

At work, you will rely on this knowledge when reading API specifications, setting up frontend network requests, configuring API gateway alerts, and diagnosing production incidents in terminal logs.

## Watch next (optional)

- [HTTP Status Codes Explained for REST APIs (200, 400, 404, 500)](https://www.youtube.com/watch?v=x2d59rJ7vgo) - Provides a clear overview of how HTTP status codes communicate outcome and error handling across REST APIs.
- [HTTP Status Codes Simply Explained in Flask](https://www.youtube.com/watch?v=EZO2KTaLH80) - Demonstrates practical scenarios mapping common codes like 200, 404, and 500 to backend server outcomes.

## References

- [S1] RFC 9110: HTTP Semantics | RFC Editor. https://www.rfc-editor.org/info/rfc9110
- [S2] HTTP methods definitions - DEV Community. https://dev.to/lucianopinheiro/http-methods-definitions-5g4g
- [S3] RFC9110. https://httpwg.org/specs/rfc9110.html
- [S5] HTTP request methods - HTTP | MDN. https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods
- [S6] GET vs POST: Understanding HTTP Request Methods. https://blog.postman.com/get-vs-post
- [S7] HTTP messages - HTTP | MDN. https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Messages
- [S8] POST request method - HTTP | MDN. https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Methods/POST
- [S9] HTTP Status Codes: Complete List, Meanings & SEO Impact. https://www.kinexmedia.com/blog/http-status-codes
- [S10] Hypertext Transfer Protocol (HTTP) Status Code Registry. https://www.iana.org/assignments/http-status-codes
- [S11] HTTP response status codes - HTTP | MDN. https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status
- [S12] HTTP status codes | Alibaba Cloud - OpenAPI Explorer - Alibaba Cloud Documentation Center. https://www.alibabacloud.com/help/en/openapi/developer-reference/http-status-codes
- [S16] HTTP Status Codes Explained for REST APIs (200, 400, 404, 500). https://www.youtube.com/watch?v=x2d59rJ7vgo
- [S19] HTTP Status Codes Simply Explained in Flask. https://www.youtube.com/watch?v=EZO2KTaLH80

**Further reading**

- HTTP - David Gourley, Brian Totty, Linda Mui (1997). https://openlibrary.org/works/OL16026044W
- HTTP : the Definitive Guide - James Bull (2015). https://openlibrary.org/works/OL40235625W
- HTTP : the Definitive Guide - Thomas Hicks (2015). https://openlibrary.org/works/OL40632616W
