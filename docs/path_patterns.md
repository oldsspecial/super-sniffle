Here's a concise, AI‑developer‑agent‑friendly summary of the **entire "Different Paths" section** in the Neo4j Cypher Patterns manual, covering fixed‑length patterns, variable‑length patterns, shortest paths, and non‑linear graph patterns:

---

## 1. Fixed‑length Path Patterns 🔁

* **Definition**: A path must begin and end with a node, alternating consistently between node and relationship patterns. Fixed‑length indicates every segment is explicit. ([Graph Database & Analytics][1])
* **Rules**:

  * Must include at least one node.
  * No adjacent node patterns without a relationship.
  * Cannot end or start with just a relationship. ([Graph Database & Analytics][2])
* **Use Cases**: Traversing a predetermined structure or hierarchy of known depth. ([Graph Database & Analytics][3])

---

## 2. Variable‑Length Patterns (Quantified Path Patterns + Quantified Relationships)

### Quantified Path Patterns

* **Syntax**: `(<sub-path>){min,max}` where the sub-path includes at least one relationship. ([Graph Database & Analytics][2])
* **Semantics**: Repeats the sub-path between `min` and `max` times, chaining them into a longer path while merging boundary nodes.&#x20;
* **Group Variables**: Variables inside the quantified part become lists outside; inside they behave as scalars. Filters on variable internals must reside inside the quantified pattern.&#x20;
* **Constraints**:

  * At least one relationship in the sub-pattern.
  * No nesting of quantified path patterns.
  * Relationships cannot repeat in a match; nodes can. ([Graph Database & Analytics][2])

### Quantified Relationships

* **Syntax**: `-[:TYPE*min..max]->` between node patterns. Can be seen as shorthand for a path pattern with a single relationship type. ([Graph Database & Analytics][2])
* **Use Cases**: Cleaner syntax when only one relationship type is repeated. Filters inside are more limited than full quantified path patterns.&#x20;

### Example

Matching varying-length sequences of stops in a train route:

````cypher
MATCH (:Station {name: 'Denmark Hill'})<-[:CALLS_AT]-(d:Stop)
      ((:Stop)-[:NEXT]->(:Stop)){1,3}
      (a:Stop)-[:CALLS_AT]->(:Station {name: 'Clapham Junction'})
RETURN d.departs, a.arrives
``` :contentReference[oaicite:24]{index=24}

---

## 3. Shortest Paths  
- **Keyword**: `SHORTEST k` identifies the top‑k shortest paths by hop count between two nodes. :contentReference[oaicite:25]{index=25}  
- **Behaviors**:
  - `SHORTEST 1`: returns one of possibly many equally-short paths (non-deterministic).
  - `SHORTEST 2+`: returns all shortest paths grouped by increasing length tiers. :contentReference[oaicite:26]{index=26}  
- **Usage**: Path variable `p = SHORTEST k (start)-[relationship*]->+(end)` used to capture the path. :contentReference[oaicite:27]{index=27}  
- **Filtering**:
  - **Pre-filter**: Place filters inside path pattern to narrow candidate paths before the shortest‑path selection. :contentReference[oaicite:28]{index=28}  
  - **Post-filter**: Placing filters at `MATCH … WHERE` applies after selection, potentially eliminating results. :contentReference[oaicite:29]{index=29}  

---

## 4. Non‑Linear (Graph) Patterns & Equijoins  
- **Concept**: You can combine multiple path patterns in one `MATCH`, forming structures beyond simple chains—e.g. “T” shapes, cycles. :contentReference[oaicite:30]{index=30}  
- **Equijoins**:
  - Declaring the same variable in different segments causes those elements to bind to the *same* node/relationship.
  - Valid only for variables declared outside quantified path patterns. :contentReference[oaicite:31]{index=31}  
- **Cartesian joins**: Patterns without shared variables produce Cartesian products of matches. :contentReference[oaicite:32]{index=32}  
- **Examples**:
  - `(:A)-->(x)-->(:B), (x)-[:R]->+(y), (:C)-->(y)-->(:D)` creates a “H” shaped overall graph structure. :contentReference[oaicite:33]{index=33}  
  - Variables carried from previous `MATCH` can be referenced inside quantified patterns if defined outside them. :contentReference[oaicite:34]{index=34}  

---

## 🧠 AI‑Agent Quick Reference Table

| Pattern Type                  | Syntax Example                               | Behavior / Use Case                                  |
|------------------------------|-----------------------------------------------|------------------------------------------------------|
| Fixed‑length path            | `(a)-[:R]->(b)-[:S]->(c)`                    | Deterministic structure of known depth               |
| Quantified path pattern      | `(( )‑[:R]->( )){min,max}`                   | Multi-hop, defined subpath repeated flexibly         |
| Quantified relationship      | `()-[:R*min..max]->()`                       | Simplified when repeating a single relationship type  |
| Shortest paths               | `p = SHORTEST k (start)-[*]->+(end)`         | Find top‑k shortest by hops with optional pre-filtration |
| Non‑linear graph pattern     | `(a)-->(x)-->(b), (x)-[:R]->+(y), ...`        | Shapes like T or H using shared variables (equijoins)|

---

## ✅ Advice for AI Coding Tasks  
- For tasks requiring dynamic-depth traversal, use **quantified path patterns**, enabling full filtering inside pattern and group variables for result lists.  
- Where only a single relationship type repeats, prefer **quantified relationships** for concise syntax.  
- Use **SHORTEST k** when minimal-hops routes are needed; apply filters properly depending on pre‑ or post‑selection.  
- To model branching or reuse nodes, combine path patterns and use **equijoins** via shared variable names.

---

Let me know if you'd like example templates or scaffolding code for generating queries or analyzing these patterns!
::contentReference[oaicite:35]{index=35}
````

[1]: https://neo4j.com/docs/cypher-manual/current/patterns/fixed-length-patterns/?utm_source=chatgpt.com "Fixed-length patterns - Cypher Manual - Neo4j"
[2]: https://neo4j.com/docs/cypher-manual/current/patterns/reference/?utm_source=chatgpt.com "Syntax and semantics - Cypher Manual - Neo4j"
[3]: https://neo4j.com/docs/cypher-manual/current/patterns/variable-length-patterns/?utm_source=chatgpt.com "Variable-length patterns - Cypher Manual - Neo4j"
