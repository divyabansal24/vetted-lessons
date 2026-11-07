# SQL Joins

**Learning objective:** Explain INNER, LEFT, RIGHT and FULL OUTER joins and choose the correct join for a given query.

**Total time:** 45 minutes

## Real-world hook (3 min)

Imagine you run an online retail store. You have two tables: `customers` and `orders`. Marketing asks for a report of all customer names alongside their order amounts so they can send thank-you notes.

If you use the wrong query, customers who signed up yesterday but have not placed an order yet might vanish completely from your list. Or worse, orphaned test orders without an associated customer account might break your automated emailing pipeline. Combining data across relational tables requires picking the exact join type that matches your business requirements [S6, S10].

## Concept 1 with a quick try-it (10 min)

Relational databases split data across tables to avoid duplication. The explicit `JOIN ... ON` syntax links two tables using a match condition [S7]. In SQL, the table specified after `FROM` is the "left" table, and the table specified after `JOIN` is the "right" table [S6].

### 1. INNER JOIN
An `INNER JOIN` returns only the rows where the join condition succeeds on both sides [S5, S6]. If a row in the left table has no matching row in the right table, it is dropped entirely [S5, S6]. Writing `JOIN ... ON` defaults to `INNER JOIN` across major SQL engines [S5].

```sql
SELECT customers.name, orders.amount
FROM customers
INNER JOIN orders ON customers.id = orders.customer_id;
```

### 2. LEFT OUTER JOIN
A `LEFT JOIN` (or `LEFT OUTER JOIN`—the word `OUTER` is optional [S5]) preserves every single row from the left table [S5, S7]. First, matching rows are joined; then, for any left row that has no match on the right, the right-side columns are filled with `NULL` [S5, S7, S8].

```sql
SELECT customers.name, orders.amount
FROM customers
LEFT JOIN orders ON customers.id = orders.customer_id;
```
Use `INNER JOIN` when you only want complete records with matching pairs, and `LEFT JOIN` when you must retain all records from the base table regardless of whether related data exists [S10].

### Try it (2-3 minutes)
You have a `users` table with 3 rows: Alice (id: 1), Bob (id: 2), and Charlie (id: 3). You have a `posts` table with 1 row: written by user_id 1.
1. How many rows will an `INNER JOIN` on `users.id = posts.user_id` return?
2. How many rows will a `LEFT JOIN` with `users` on the left return?

**Expected Answer:**
1. `INNER JOIN` returns 1 row (Alice and her post).
2. `LEFT JOIN` returns 3 rows (Alice with her post, Bob with `NULL` post columns, and Charlie with `NULL` post columns).

## Concept 2 with a quick try-it (10 min)

### 1. RIGHT OUTER JOIN
A `RIGHT OUTER JOIN` is the converse of a left join [S5]. It retains every row from the right table (the table after `JOIN`), filling in `NULL` for any columns from the left table where no match exists [S5, S6, S11]. In day-to-day engineering, `RIGHT JOIN` is rarely used; developers usually reverse table order in the `FROM` clause and write a `LEFT JOIN` instead to keep queries intuitive to read [S6, S9].

```sql
SELECT customers.name, orders.amount
FROM customers
RIGHT JOIN orders ON customers.id = orders.customer_id;
```

### 2. FULL OUTER JOIN
A `FULL OUTER JOIN` preserves all rows from both tables [S6, S8, S10]. It connects rows where the join predicate matches, and for any unmatched rows from either side, it fills the missing columns with `NULL` [S6, S8, S11]. Note that database engine support differs; for example, PostgreSQL and SQL Server support `FULL OUTER JOIN`, whereas MySQL does not natively support the syntax [S8].

```sql
SELECT customers.name, orders.amount
FROM customers
FULL OUTER JOIN orders ON customers.id = orders.customer_id;
```

### How to choose the right join:
- Want only rows with matches on both sides? Use **`INNER JOIN`** [S6, S10].
- Want all base records from your starting table plus optional extras? Use **`LEFT JOIN`** [S6, S10].
- Want all records from the secondary table? Use **`RIGHT JOIN`** (or swap to `LEFT JOIN`) [S6, S9].
- Auditing discrepancies or retaining everything from both tables? Use **`FULL OUTER JOIN`** [S6, S10].

### Try it (2-3 minutes)
**Question 1:**
You have `departments` (HR, Engineering, Legal) and `contractors` (Dave in HR, Eve in Design). Design does not match any current department, and Legal has no contractors.
Which join returns all departments AND all contractors, keeping Dave matched with HR, Eve with a `NULL` department, and Legal with a `NULL` contractor?

**Expected Answer:**
`FULL OUTER JOIN` (or `FULL JOIN`). It preserves unmatched rows from both tables, populating missing sides with `NULL` [S6, S8].

**Question 2:**
Rewrite the following `LEFT JOIN` query as a `RIGHT JOIN` query to practice the syntax [S6, S9]:

```sql
SELECT orders.amount, customers.name
FROM orders
LEFT JOIN customers ON orders.customer_id = customers.id;
```

**Expected Answer:**
```sql
SELECT orders.amount, customers.name
FROM customers
RIGHT JOIN orders ON orders.customer_id = customers.id;
```

## Mini task written as a work ticket (12 min)

### Ticket: ENG-4082 – Audit Merchant Onboarding and Terminals

**Background:**
Operations needs an audit report of merchants and hardware payment terminals. Some merchants have multiple terminals, some new merchants have zero terminals, and some legacy hardware terminals in warehouse storage have no assigned merchant.

**Task Requirements:**
1. Produce a query for the monthly billing team showing all active pairings: return merchant name and terminal serial number, but exclude any merchants without terminals and any unassigned terminals.
2. Produce a query for Merchant Support listing **all** merchants and their terminal serial numbers (if assigned) so reps can see which merchants still need hardware dispatched.
3. Produce an inventory reconciliation query that returns all merchants and all terminals, capturing unmatched merchants as well as orphaned terminals in one view.

**Schema:**
- `merchants` (`merchant_id`, `name`)
- `terminals` (`terminal_id`, `serial_number`, `merchant_id`)

**Step-by-Step Implementation:**
1. For Requirement 1, use an `INNER JOIN` because only matched records on both sides are valid for billing [S10].
2. For Requirement 2, use a `LEFT JOIN` with `merchants` as the left table to preserve all merchant accounts even if they have no terminals [S5, S7].
3. For Requirement 3, use a `FULL OUTER JOIN` to capture every record from both tables, filling missing fields with `NULL` [S6, S8].

**Model Solution:**
```sql
-- 1. Active pairings only (Billing)
SELECT m.name, t.serial_number
FROM merchants m
INNER JOIN terminals t ON m.merchant_id = t.merchant_id;

-- 2. All merchants, including those without terminals (Support)
SELECT m.name, t.serial_number
FROM merchants m
LEFT JOIN terminals t ON m.merchant_id = t.merchant_id;

-- 3. Inventory audit: all merchants and all terminals (Reconciliation)
SELECT m.name, t.serial_number
FROM merchants m
FULL OUTER JOIN terminals t ON m.merchant_id = t.merchant_id;
```

## Knowledge check (7 min)

1. What is the default join type if you write `SELECT * FROM table_a JOIN table_b ON ...`?
   a) `LEFT JOIN`
   b) `FULL OUTER JOIN`
   c) `INNER JOIN`
   d) `CROSS JOIN`

2. In a `LEFT OUTER JOIN`, what appears in the right table's columns when a left-table row has no match?
   a) An empty string `""`
   b) `NULL`
   c) `0`
   d) The row is excluded

3. Why do most production teams prefer `LEFT JOIN` over `RIGHT JOIN`?

4. A manager asks for a list of all products that have never been ordered. You write:
```sql
SELECT p.product_name
FROM products p
LEFT JOIN order_items oi ON p.product_id = oi.product_id
WHERE oi.product_id IS NULL;
```
Why does this work?

5. True or False: A `FULL OUTER JOIN` drops rows if they do not find a matching key in the opposing table.

---

### Answer Key
1. **c) `INNER JOIN`** - In standard SQL and engines like PostgreSQL, `INNER` is the default when writing `JOIN` without a qualifier [S5, S6].
2. **b) `NULL`** - When a row from the left table has no match on the right, SQL substitutes `NULL` values for the right table's columns [S5, S7].
3. Code readability. Reading top-to-bottom and left-to-right makes it easier to keep the primary entity in the `FROM` clause; any `RIGHT JOIN` can be rewritten as a `LEFT JOIN` simply by reversing table order [S6, S9].
4. A `LEFT JOIN` keeps all products and injects `NULL` for `order_items` attributes whenever a product has no matching order [S5, S7]. Filtering by `WHERE oi.product_id IS NULL` isolates exactly those unmatched products.
5. **False** - A `FULL OUTER JOIN` keeps all rows from both tables, filling `NULL` wherever a match is missing rather than dropping rows [S6, S8].

## Recap and where you will use this at work (3 min)

You now understand how to combine relational datasets using the four fundamental SQL joins:
- `INNER JOIN`: Filters down to only matching records across both tables [S5, S6].
- `LEFT JOIN`: Retains all rows from the primary left table, appending matching data or `NULL`s [S5, S7].
- `RIGHT JOIN`: Retains all rows from the right table, which is functionally equivalent to swapping table order with a `LEFT JOIN` [S5, S6].
- `FULL OUTER JOIN`: Keeps all records from both sides, exposing unmatched data with `NULL`s [S6, S8].

At work, choosing the wrong join leads to subtle logic bugs: reports with undercounted revenue, dropped user signups, or silent `NULL` pointer errors in application services. You will use `INNER JOIN` for transactional lookups, `LEFT JOIN` for user profile dashboards, and `FULL OUTER JOIN` when reconciling data during migrations or system audits.

## Watch next (optional)

- [SQL Joins Explained | INNER, LEFT, RIGHT & FULL OUTER JOIN Tutorial](https://www.youtube.com/watch?v=p5XV1m0bDBo) - Provides a clean, beginner-friendly walkthrough showing how aliases, column selection, and NULL handling behave across INNER, LEFT, RIGHT, and FULL joins.
- [SQL JOINS Tutorial for beginners | Practice SQL Queries using JOINS - Part 1](https://www.youtube.com/watch?v=0OQJDd3QqQM) - Walks through practical query writing step-by-step for complete beginners learning table joins.
- [SQL Joins Basics (Visually Explained) | INNER, LEFT, RIGHT, FULL | #SQL Course 8](https://www.youtube.com/watch?v=aY7z4HcHm5M) - Uses clear visual diagrams to illustrate how set intersections and join types map to matched and unmatched data rows.

## References

- [S5] PostgreSQL: Documentation: 18: 7.2. Table Expressions. https://www.postgresql.org/docs/current/queries-table-expressions.html
- [S6] SQL Joins Explained: INNER, LEFT, RIGHT & FULL. https://www.codingtemple.com/blog/sql-joins-explained
- [S7] PostgreSQL: Documentation: 18: 2.6. Joins Between Tables. https://www.postgresql.org/docs/current/tutorial-join.html
- [S8] SQL Joins Explained – INNER, LEFT, RIGHT, and FULL JOIN Diagrams | DbSchema. https://dbschema.com/blog/tutorials/sql-joins-explained
- [S9] MySQL :: MySQL 9.7 Reference Manual :: 15.2.13.2 JOIN Clause. https://dev.mysql.com/doc/en/join.html
- [S10] SQL JOINs Demystified: A Complete Guide to Inner, Left, Right & Full Joins – IT Exams Training – Pass4Sure. https://www.pass4sure.com/blog/sql-joins-demystified-a-complete-guide-to-inner-left-right-full-joins
- [S11] MySQL JOIN types - INNER JOIN, SELF JOIN, CROSS JOIN, FULL OUTER JOIN: LEFT and RIGHT. https://www.devart.com/dbforge/mysql/studio/mysql-joins.html
