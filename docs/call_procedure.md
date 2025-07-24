

# `CALL` Procedure

The `CALL` clause is used to invoke a procedure deployed in the database.

> **Note:** `CALL` also evaluates subqueries—see [CALL subqueries](#) for details. To list procedures, use [SHOW PROCEDURES](#).

Neo4j includes built-in procedures; see *Operations Manual → Procedures*. You can also create and deploy custom ones—see *Java Reference → User-defined procedures* ([Graph Database & Analytics][1]).

---

## Example Graph

Used in the examples below:

```cypher
CREATE
  (andy:Developer {name: 'Andy', born: 1991}),
  (beatrice:Developer {name: 'Beatrice', born: 1985}),
  (charlotte:Administrator {name: 'Charlotte', born: 1990}),
  (david:Administrator {name: 'David', born: 1994, nationality: 'Swedish'}),
  (andy)-[:KNOWS]->(beatrice),
  (beatrice)-[:KNOWS]->(charlotte),
  (andy)-[:KNOWS]->(david);
```

([Graph Database & Analytics][2])

---

## Basic `CALL` Examples

### Example 1: Call without arguments

```cypher
CALL db.labels();
```

Lists all labels:

| label           |
| --------------- |
| "Developer"     |
| "Administrator" |

Parentheses are optional for zero-arity procedures when the query consists solely of `CALL`. ([Graph Database & Analytics][1])

---

### Example 2: Call with literal arguments

```cypher
CALL dbms.checkConfigValue('server.bolt.enabled', 'true');
```

Returns:

| valid | message            |
| ----- | ------------------ |
| true  | "requires restart" |

([Graph Database & Analytics][2])

---

### Example 3: Call with parameter arguments

```cypher
:param setting => 'server.bolt.enabled';
:param value => 'true';

CALL dbms.checkConfigValue($setting, $value);
```

Equivalent result. ([Graph Database & Analytics][2])

---

### Example 4: Mixed literal & parameter

```cypher
:param setting => 'server.bolt.enabled';

CALL dbms.checkConfigValue($setting, 'true');
```

Also returns the same result. ([Graph Database & Analytics][2])

---

## Using `YIELD`

Select specific return columns from procedures:

### Example 5: `YIELD *`

```cypher
CALL db.labels() YIELD *
```

Returns all columns. Note that deprecated columns are included. Only valid in standalone calls without additional clauses. ([Graph Database & Analytics][1])

---

### Example 6: Specific `YIELD` with filter

First, retrieve signature to know columns:

```cypher
SHOW PROCEDURES
YIELD name, signature
WHERE name = 'db.propertyKeys'
RETURN signature;
```

Returns:

```
"db.propertyKeys() :: (propertyKey :: STRING)"
```

Then:

```cypher
CALL db.propertyKeys() YIELD propertyKey AS prop
MATCH (n)
WHERE n[prop] IS NOT NULL
RETURN prop, count(n) AS numNodes;
```

Results might be:

| prop          | numNodes |
| ------------- | -------- |
| "name"        | 4        |
| "born"        | 4        |
| "nationality" | 1        |

([Graph Database & Analytics][2])

---

### VOID Procedures

Procedures that produce side-effects without returning records are called VOID procedures. They don’t support `YIELD` and behave like `WITH *` in query streams. ([Graph Database & Analytics][1])

---

## Optional Procedure Calls

Use `OPTIONAL CALL` to ensure rows without output still appear (with `null` results).

### Example 7: `CALL` vs `OPTIONAL CALL`

Graph procedure:

```cypher
MATCH (n)
CALL apoc.neighbors.tohop(n, "KNOWS>", 1)
YIELD node
RETURN n.name AS name, collect(node.name) AS connections;
```

Returns rows only for nodes with outgoing `KNOWS>` relationships. ([Graph Database & Analytics][1])

With `OPTIONAL CALL`:

```cypher
MATCH (n)
OPTIONAL CALL apoc.neighbors.tohop(n, "KNOWS>", 1)
YIELD node
RETURN n.name AS name, collect(node.name) AS connections;
```

Now includes nodes with no such relationships, with `[]` as their `connections`. ([Graph Database & Analytics][1])

---

*Converted from Neo4j Cypher manual.*

[1]: https://neo4j.com/docs/cypher-manual/25/clauses/call/?utm_source=chatgpt.com "CALL procedure - Cypher Manual"
[2]: https://neo4j.com/docs/cypher-manual/25/clauses/call/ "CALL procedure - Cypher Manual"
