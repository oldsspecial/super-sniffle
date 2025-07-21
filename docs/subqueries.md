Here’s a full conversion of the **Neo4j Cypher manual** page on `CALL … subqueries` into Markdown:

---

# CALL subqueries

The `CALL` clause can be used to invoke subqueries that execute operations within a defined scope, thereby optimizing data handling and query efficiency. Unlike other subqueries in Cypher®, `CALL` subqueries can perform database changes (e.g. `CREATE` new nodes).
This is distinct from calling stored procedures; for that, refer to **CALL procedure** ([Graph Database & Analytics][1]).

---

## Example graph

```cypher
CREATE (teamA:Team {name: 'Team A'}),
       (teamB:Team {name: 'Team B'}),
       (teamC:Team {name: 'Team C'}),
       (playerA:Player {name: 'Player A', age: 21}),
       (playerB:Player {name: 'Player B', age: 23}),
       (playerC:Player {name: 'Player C', age: 19}),
       (playerD:Player {name: 'Player D', age: 30}),
       (playerE:Player {name: 'Player E', age: 25}),
       (playerF:Player {name: 'Player F', age: 35}),
       (playerA)-[:PLAYS_FOR]->(teamA),
       (playerB)-[:PLAYS_FOR]->(teamA),
       (playerD)-[:PLAYS_FOR]->(teamB),
       (playerE)-[:PLAYS_FOR]->(teamC),
       (playerF)-[:PLAYS_FOR]->(teamC),
       (teamA)-[:OWES {dollars: 1500}]->(teamB),
       (teamA)-[:OWES {dollars: 3000}]->(teamB),
       (teamB)-[:OWES {dollars: 1700}]->(teamC),
       (teamC)-[:OWES {dollars: 5000}]->(teamB);
```

---

## Semantics & Performance

* `CALL` subqueries are executed **once per incoming row**.
* Variables returned by the subquery become available in the outer scope.
* Changes in one execution may be observed by subsequent ones.
* Temporary state inside the subquery is cleaned up each time, aiding memory management ([Graph Database & Analytics][1]).

### Example 1: Basic usage

```cypher
UNWIND [0, 1, 2] AS x
CALL () {
  RETURN 'hello' AS innerReturn
}
RETURN innerReturn;
```

**Result**: `'hello'` repeated 3 times ([Graph Database & Analytics][1]).

---

### Example 2: Incremental updates

```cypher
UNWIND [1, 2, 3] AS x
CALL () {
    MATCH (p:Player {name: 'Player A'})
    SET p.age = p.age + 1
    RETURN p.age AS newAge
}
MATCH (p:Player {name: 'Player A'})
RETURN x AS iteration, newAge, p.age AS totalAge;
```

Demonstrates that updates in earlier iterations are visible in later ones ([Graph Database & Analytics][1]).

---

### Example 3: Reduced memory footprint

```cypher
MATCH (t:Team)
CALL (t) {
  MATCH (p:Player)-[:PLAYS_FOR]->(t)
  RETURN collect(p) AS players
}
RETURN t AS team, players;
```

Each team is processed separately, reducing memory usage ([Graph Database & Analytics][1]).

---

## Importing variables

Variables from the outer scope **must be explicitly imported**, using either a **scope clause** (`CALL (vars...)`) or the deprecated `WITH` syntax.

### Scope clause

#### Specific variables

```cypher
MATCH (p:Player), (t:Team)
CALL (p) {
  WITH rand() AS random
  SET p.rating = random
  RETURN p.name AS playerName, p.rating AS rating
}
RETURN playerName, rating, t AS team
ORDER BY rating
LIMIT 1;
```

#### All variables

```cypher
CALL (*) { … }
```

#### No variables

```cypher
CALL () { … }
```

As of Neo4j 5.23, omitting the scope clause is deprecated ([Graph Database & Analytics][1]).

---

### Deprecated WITH clause

```cypher
CALL {
  WITH t
  MATCH (p:Player)-[:PLAYS_FOR]->(t)
  RETURN collect(p) AS players
}
```

**Restrictions**:

* `WITH` must be first (or second after `USE`).
* Cannot follow with `DISTINCT`, `ORDER BY`, `WHERE`, `SKIP`, or `LIMIT`.
* To filter, use a second `WITH` inside the block ([Graph Database & Analytics][1]).

---

## OPTIONAL CALL

Behaves like `OPTIONAL MATCH`: returns rows with null if no results:

```cypher
MATCH (p:Player)
OPTIONAL CALL (p) {
    MATCH (p)-[:PLAYS_FOR]->(team:Team)
    RETURN team
}
RETURN p.name AS playerName, team.name AS team;
```

Players without teams still appear, with `null` ([Graph Database & Analytics][1]).

---

## Execution order

The order of rows entering a `CALL` subquery is **undefined** unless you use `ORDER BY` before the call ([Graph Database & Analytics][1]).

---

## Using CALL with UNION

You can use `UNION` or `UNION ALL` inside a `CALL` subquery:

```cypher
CALL () {
  MATCH (p:Player)
  RETURN p
  ORDER BY p.age ASC
  LIMIT 1
UNION
  MATCH (p:Player)
  RETURN p
  ORDER BY p.age DESC
  LIMIT 1
}
RETURN p.name AS playerName, p.age AS age;
```

---

### Combining UNION ALL with aggregation

```cypher
MATCH (t:Team)
CALL (t) {
  OPTIONAL MATCH (t)-[o:OWES]->(other:Team)
  RETURN o.dollars * -1 AS moneyOwed
  UNION ALL
  OPTIONAL MATCH (other)-[o:OWES]->(t)
  RETURN o.dollars AS moneyOwed
}
RETURN t.name AS team, sum(moneyOwed) AS amountOwed
ORDER BY amountOwed DESC;
```

---

## Aggregations & row count

Returning subqueries **affect** the number of output rows.

Unit subqueries (no `RETURN`) maintain the same number of rows and are used for side-effects like `CREATE`, `SET`, `DELETE` ([Graph Database & Analytics][1]).

### Example: Unit subquery

```cypher
MATCH (p:Player)
CALL (p) {
  UNWIND range(1, 3) AS i
  CREATE (:Person {name: p.name})
}
RETURN count(*);
```

---

## Summary

* `CALL` subqueries run per input row, can change graph, and return variables to outer scope.
* Variables must be imported explicitly.
* Returning subqueries affect row counts; unit subqueries do not.
* Use `ORDER BY` before `CALL` to control execution order.
* Can be combined with `UNION`/`UNION ALL` for complex processing ([Graph Database & Analytics][1]).

---

Let me know if you'd like examples for using call-subqueries in transactions or advanced use cases!

[1]: https://neo4j.com/docs/cypher-manual/current/subqueries/call-subquery/?utm_source=chatgpt.com "CALL subqueries - Cypher Manual - Neo4j"
