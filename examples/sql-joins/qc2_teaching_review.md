# QC 2 - Instructional quality

**Lesson:** SQL Joins

**Objective:** Explain INNER, LEFT, RIGHT and FULL OUTER joins and choose the correct join for a given query.

_Note: the lesson was changed after this check ran._

## Summary

The lesson provides a clear, accurate, and well-structured introduction to SQL joins. It uses effective real-world analogies and practical exercises that align well with the learning objectives. The progression from simple joins to more complex ones is logical, and the inclusion of a 'work ticket' scenario provides excellent context for application. The primary weakness is the lack of explicit practice for RIGHT JOIN, which is mentioned but not exercised.

## Objective coverage

| Part | Explained | Practised | Assessed |
|---|---|---|---|
| Explain INNER JOIN | yes | yes | yes |
| Explain LEFT JOIN | yes | yes | yes |
| Explain RIGHT JOIN | yes | no | yes |
| Explain FULL OUTER JOIN | yes | yes | yes |
| Choose the correct join for a given query | yes | yes | yes |

## Scores

- **alignment:** 5/5 - The content directly maps to the stated learning objectives.
- **clarity:** 5/5 - Explanations are concise, accurate, and use helpful terminology.
- **structure and pacing:** 4/5 - The flow is logical, though the mini task might take longer than 12 minutes for a novice learner.
- **examples:** 5/5 - The retail store and merchant/terminal examples are relatable and effective.
- **practical application:** 4/5 - Excellent application, though RIGHT JOIN is neglected in practice.
- **cognitive load:** 5/5 - The content is chunked well, preventing information overload.

**Highest impact fix:** Add a specific practice question to the 'Concept 2' section or the 'Mini task' that requires the learner to write a RIGHT JOIN query, even if the lesson notes that it is rarely used in production, to ensure they can identify and construct it when encountered.

## Issues

### T1 (medium, ignored)
- **Problem:** Objective part "Explain RIGHT JOIN" is not practised.
- **Suggested fix:** Add what is missing for "Explain RIGHT JOIN": an exercise
- **Found by:** rule check

### T2 (medium, applied)
- **Section:** Concept 2
- **Text:** "RIGHT JOIN is rarely used"
- **Problem:** While it is good practice to teach that RIGHT JOIN is rare, the learner is never asked to write one, meaning they may not be able to identify or use it if they encounter it in legacy code.
- **Suggested fix:** Add a short 'Try it' question: 'Rewrite the following LEFT JOIN query as a RIGHT JOIN query to practice the syntax'.
- **Found by:** AI review
