

## 📘 Read Query

### 🔹 Read Query Structure

```cypher
[USE]
[MATCH [WHERE]]
[OPTIONAL MATCH [WHERE]]
[WITH [ORDER BY] [SKIP] [LIMIT] [WHERE]]
RETURN [ORDER BY] [SKIP] [LIMIT]
```

* Baseline for pattern search operations.
* `USE`, `MATCH`, `OPTIONAL MATCH`, `WITH`, and `RETURN` are clauses.
* Cypher keywords are not case-sensitive.
* Cypher is case-sensitive for variables.

---

## 📘 Composed Queries

```cypher
USE neo4j
MATCH (m:Movie)
RETURN m.title
```

* Direct the query to run on a specific database.

```cypher
CALL {
  MATCH (a:Actor)-[:ACTED_IN]->(m:Movie)
  RETURN a, m
}
RETURN count(*)
```

* Subqueries isolate variable scope.

```cypher
CALL {
  MATCH (a:Actor)-[:ACTED_IN]->(m:Movie)
  RETURN a.name AS name
}
WITH name
RETURN count(name)
```

* Output from the subquery can be passed forward using `WITH`.

---

## 📘 Patterns

```cypher
MATCH (n)
RETURN n
```

* Match all nodes and return them.

```cypher
MATCH (movie:Movie)
RETURN movie.title
```

* Match all nodes with the `Movie` label.

```cypher
MATCH (:Person {name: 'Oliver Stone'})-[r]->()
RETURN type(r) AS relType
```

* Find relationship types from a node.

```cypher
MATCH (:Movie {title: 'Wall Street'})<-[:ACTED_IN]-(actor:Person)
RETURN actor.name AS actor
```

* Match nodes and relationships by type and direction.

```cypher
MATCH path = ()-[:ACTED_IN]->(movie:Movie)
RETURN path
```

* Assign path to a variable and return it.

```cypher
MATCH (movie:$label)
RETURN movie.title AS movieTitle
```

* Dynamically reference a node label using parameters.

```cypher
CALL db.relationshipTypes()
YIELD relationshipType
MATCH ()-[r:$(relationshipType)]->()
RETURN relationshipType, count(r) AS relationshipCount
```

* Use `CALL` and dynamic parameters to match on variable relationship types.

---

## 📘 Clauses

### 🔹 MATCH

```cypher
MATCH (n:Person)
RETURN n
```

* Find nodes by label.

### 🔹 OPTIONAL MATCH

```cypher
MATCH (p:Person {name: 'Martin Sheen'})
OPTIONAL MATCH (p)-[r:DIRECTED]->()
RETURN p.name, r
```

* Allows for missing patterns, returns `null` for unmatched parts.

### 🔹 WHERE

```cypher
MATCH (n)
WHERE n:Swedish
RETURN n.name AS name
```

* Filter based on labels.

```cypher
MATCH (n:Person)
WHERE n.age < 35
RETURN n.name AS name, n.age AS age
```

* Filter based on properties.

```cypher
MATCH (:Person {name: 'Andy'})-[k:KNOWS]->(f)
WHERE k.since < 2000
RETURN f.name AS oldFriend
```

* Filter on relationship properties.

```cypher
MATCH (n:Person)
WHERE n[$propname] > 40
RETURN n.name AS name, n.age AS age
```

* Use dynamic property access.

```cypher
WITH 35 AS minAge
MATCH (a:Person WHERE a.name = 'Andy')-[:KNOWS]->(b:Person WHERE b.age > minAge)
RETURN b.name AS name
```

* WHERE inside pattern.

### 🔹 RETURN

```cypher
MATCH (p:Person {name: 'Keanu Reeves'})
RETURN p
```

* Return entire node.

```cypher
MATCH (p:Person {name: 'Keanu Reeves'})-[r:ACTED_IN]->(m)
RETURN type(r)
```

* Return relationship type.

```cypher
MATCH (p:Person {name: 'Keanu Reeves'})
RETURN p.bornIn
```

* Return a property.

```cypher
MATCH p = (keanu:Person {name: 'Keanu Reeves'})-[r]->(m)
RETURN *
```

* Return all matched variables.

```cypher
MATCH (p:Person {name: 'Keanu Reeves'})-->(m)
RETURN DISTINCT m
```

* Use `DISTINCT` to avoid duplicates.


