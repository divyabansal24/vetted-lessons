# QC 1 - Research and factual accuracy

**Lesson:** SQL Joins

**Objective:** Explain INNER, LEFT, RIGHT and FULL OUTER joins and choose the correct join for a given query.

_Note: the lesson was changed after this check ran._

## Summary

The lesson accurately describes the behavior, standard syntax, and use cases of INNER, LEFT, RIGHT, and FULL OUTER joins in SQL. Most claims are well-supported by the provided documentation from PostgreSQL, MySQL, and SQL standard excerpts. A minor clarification regarding MySQL's handling of the bare JOIN keyword vs standard SQL should be noted for complete technical accuracy.

## Claims checked

| Claim | Status | Sources | Confidence | Best source |
|---|---|---|---|---|
| In SQL, the table specified after FROM is the left table and the table specified after JOIN is the right table. | supported | S6 | medium | low |
| An INNER JOIN returns only rows where the join condition succeeds on both sides. | supported | S5, S6 | medium | high |
| Writing JOIN without a qualifier defaults to INNER JOIN. | supported | S5, S6 | medium | high |
| In LEFT OUTER JOIN, the word OUTER is optional. | supported | S1, S5 | medium | high |
| A LEFT JOIN preserves every row from the left table, filling right-side columns with NULL when there is no match. | supported | S5, S7, S8 | high | high |
| A RIGHT JOIN keeps all rows from the right table, substituting NULL for unmatched left-table columns. | supported | S5, S6, S11 | high | high |
| A RIGHT JOIN produces identical results to a LEFT JOIN with the table order swapped. | supported | S6, S9 | medium | high |
| FULL OUTER JOIN retains all rows from both tables, filling unmatched columns with NULL. | supported | S6, S8, S11 | high | low |
| PostgreSQL and SQL Server support FULL OUTER JOIN natively, whereas MySQL does not. | supported | S8 | medium | low |

## Issues

### F1 (medium, ignored)
- **Section:** Concept 1 with a quick try-it (10 min)
- **Problem:** "In SQL, the table specified after FROM is the left table and the table specified after JOIN is the right table." is only backed by low-reliability sources.
- **Suggested fix:** Cite official documentation or a standard for this point, or soften the wording.
- **Found by:** rule check

### F2 (medium, ignored)
- **Section:** Concept 2 with a quick try-it (10 min)
- **Problem:** "FULL OUTER JOIN retains all rows from both tables, filling unmatched columns with NULL." is only backed by low-reliability sources.
- **Suggested fix:** Cite official documentation or a standard for this point, or soften the wording.
- **Found by:** rule check

### F3 (medium, ignored)
- **Section:** Concept 2 with a quick try-it (10 min)
- **Problem:** "PostgreSQL and SQL Server support FULL OUTER JOIN natively, whereas MySQL does not." is only backed by low-reliability sources.
- **Suggested fix:** Cite official documentation or a standard for this point, or soften the wording.
- **Found by:** rule check

### F4 (low, applied)
- **Section:** Concept 1 with a quick try-it (10 min)
- **Text:** "Writing simply `JOIN` defaults to `INNER JOIN`"
- **Problem:** While true in standard SQL and PostgreSQL, in MySQL a bare `JOIN` without an `ON` clause is treated as equivalent to `CROSS JOIN`.
- **Suggested fix:** Clarify that writing `JOIN ... ON` defaults to `INNER JOIN` across major SQL engines.
- **Found by:** AI review
