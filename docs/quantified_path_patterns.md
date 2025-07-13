Here's a summary of the **Neo4j Cypher Manual on Variable‑Length Patterns**, tailored for an AI‑coding agent:

---

## 1. Quantified Path Patterns

* Enables matching of path segments whose exact length is unknown or variable — useful for hierarchical traversals or connecting nodes at varying depths. ([Graph Database & Analytics][1])
* Syntax: wrap a repeated sub‑pattern in parentheses and follow with a quantifier:

  ```
  ((:Stop)-[:NEXT]->(:Stop)){min,max}
  ```
* Matches any repetition between `min` and `max`, inclusive. Internally equivalent to a union of fixed‑length expansions. ([Graph Database & Analytics][2], [Graph Database & Analytics][1])
* Useful for collapsing multiple fixed-length MATCH clauses into one concise pattern. ([Graph Database & Analytics][3])

## 2. Quantified Relationships

* A shortcut when repeating a single relationship type between two node patterns. Example:

  ```
  (a)-[:NEXT*1..10]->(b)
  ```
* Equivalent to a quantified path pattern consisting of a single relationship repeated. ([Graph Database & Analytics][1])
* More concise and clearer, though limits placement of predicates relative to quantified pattern bounds. ([Graph Database & Analytics][1])

## 3. Group Variables

* Variables declared inside quantified patterns become **group variables** outside.
* Internally, each repetition introduces fresh variable instances that bind to the same nodes/relationships via implicit equijoins. Externally, these variables are exposed as **lists**. ([Graph Database & Analytics][2])
* Example:

  ```cypher
  MATCH ((x)-[r:R]->(z WHERE z.h > x.h)){2,3}
  RETURN [n IN x | n.h] AS x_h, [n IN z | n.h] AS z_h
  ```

  Produces lists of x and z values from each repetition. ([Graph Database & Analytics][2])

## 4. Rules & Constraints

* The quantified sub‑pattern must include at least one relationship (i.e., minimum length > 0). ([Graph Database & Analytics][2])
* No nesting of quantified path patterns (e.g., you cannot nest `{2,3}` inside another quantified block). ([Graph Database & Analytics][2])
* Relationships may not be traversed more than once in a match; nodes can repeat. ([Graph Database & Analytics][2])
* `WHERE` clauses referencing group-variable internals (e.g. list content) must be inside the quantified pattern; otherwise those variables operate as lists, not scalars. ([Graph Database & Analytics][2])

## 5. Variable‑Length Relationships (Legacy, pre‑5.9)

* The older `[*min..max]` syntax was used to indicate relationship repetition (e.g., `[:KNOWS*2..3]`).
* This variant differs in quantifier semantics, where clauses could not reference internals of the repeated pattern via `WHERE`.
* Still supported but not GQL‑conformant and lacks certain expressiveness. ([graphaware.com][4], [Graph Database & Analytics][1])

## 🧠 Quick Reference for AI Coding Agent

| Feature                     | Preferred Syntax                                                        | Use Case                                       |
| --------------------------- | ----------------------------------------------------------------------- | ---------------------------------------------- |
| Repeat arbitrary sub-paths  | `((pattern)){min,max}`                                                  | Hierarchical traversal or variable-depth paths |
| Repeat same relationship    | `()-[:TYPE*min..max]->()`                                               | Succinct single-edge repetition                |
| List of nodes/relationships | Use variables inside quantified pattern; return with list comprehension | Compute aggregated metrics along the path      |
| Add filters inside pattern  | Place `WHERE` inside quantified parentheses                             | Constrain each instance before grouping        |

---

### ✅ When crafting Cypher generative or analysis tasks:

* Prefer **quantified path patterns** for structured repeatable path logic.
* Use **quantified relationships** for simple single-edge repetitions.
* Treat variables inside quantified patterns as templates; when returned they yield lists via group variables.
* Always enforce upper bounds (e.g. `{1,5}`) to avoid exhaustive graph expansion. ([Graph Database & Analytics][5], [Graph Database & Analytics][1], [Stack Overflow][6], [Graph Database & Analytics][2])

Let me know if you want runnable example templates or transformation rules for code generation!

[1]: https://neo4j.com/docs/cypher-manual/current/patterns/variable-length-patterns/?utm_source=chatgpt.com "Variable-length patterns - Cypher Manual - Neo4j"
[2]: https://neo4j.com/docs/cypher-manual/current/patterns/reference/?utm_source=chatgpt.com "Syntax and semantics - Cypher Manual - Neo4j"
[3]: https://neo4j.com/docs/cypher-manual/4.3/syntax/patterns/?utm_source=chatgpt.com "Patterns - Cypher Manual - Neo4j"
[4]: https://graphaware.com/blog/neo4j-cypher-variable-length-relationships-by-example/?utm_source=chatgpt.com "Cypher: Variable Length Relationships by Example - GraphAware"
[5]: https://neo4j.com/docs/cypher-cheat-sheet/current/?utm_source=chatgpt.com "Cypher Cheat Sheet - Neo4j"
[6]: https://stackoverflow.com/questions/51593768/cypher-variable-length-pattern?utm_source=chatgpt.com "Cypher variable length pattern - neo4j - Stack Overflow"
