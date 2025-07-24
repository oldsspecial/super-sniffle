Here’s the Markdown conversion of the “Sequential queries (NEXT)” section from the Neo4j Cypher 25 Manual:

---

## Sequential queries (`NEXT`)

`NEXT` allows linear composition of queries into a sequence of smaller, self-contained segments, passing return values from one segment to the next. It improves modularity, readability, and can replace `CALL` subqueries or `WITH` clauses. It also enhances the usability of conditional `WHEN` and combined `UNION` queries ([Graph Database & Analytics][1]).

### 🧠 Benefits

* Clearer, more modular query structure
* Alternative to `CALL` subqueries and `WITH`
* Works well with `WHEN` and `UNION` constructs ([Graph Database & Analytics][2], [Graph Database & Analytics][1])

### Graph Setup for Examples

```cypher
CREATE
  (techCorp:Supplier {name: 'TechCorp', email: 'contact@techcorp.com'}),
  (foodies:Supplier {name: 'Foodies Inc.', email: 'info@foodies.com'}),

  (laptop:Product {name: 'Laptop', price: 1000}),
  (phone:Product {name: 'Phone', price: 500}),
  (headphones:Product {name: 'Headphones', price: 250}),
  (chocolate:Product {name: 'Chocolate', price: 5}),
  (coffee:Product {name: 'Coffee', price: 10}),

  (amir:Customer {firstName: 'Amir', lastName: 'Rahman', email: 'amir.rahman@example.com', discount: 0.1}),
  (keisha:Customer {firstName: 'Keisha', lastName: 'Nguyen', email: 'keisha.nguyen@example.com', discount: 0.2}),
  (mateo:Customer {firstName: 'Mateo', lastName: 'Ortega', email: 'mateo.ortega@example.com', discount: 0.05}),
  (hannah:Customer {firstName: 'Hannah', lastName: 'Connor', email: 'hannah.connor@example.com', discount: 0.15}),
  (leila:Customer {firstName: 'Leila', lastName: 'Haddad', email: 'leila.haddad@example.com', discount: 0.1}),
  (niko:Customer {firstName: 'Niko', lastName: 'Petrov', email: 'niko.petrov@example.com', discount: 0.25}),
  (yusuf:Customer {firstName: 'Yusuf', lastName: 'Abdi', email: 'yusuf.abdi@example.com', discount: 0.1}),

  // purchase relationships...
  (amir)-[:BUYS {date: date('2024-10-09')}]->(laptop),
  (amir)-[:BUYS {date: date('2025-01-10')}]->(chocolate),
  // ... (other BUYS and SUPPLIES goes here)
;
```

---

### ✅ Syntax

```cypher
<Query1>
NEXT
<Query2>
NEXT
<Query3>
```

---

### Passing variables

#### Single variable

```cypher
MATCH (c:Customer)
RETURN c AS customer
NEXT
MATCH (customer)-[:BUYS]->(:Product {name: 'Chocolate'})
RETURN customer.firstName AS chocolateCustomer;
```

**Result:**

```
chocolateCustomer
"Amir"
"Mateo"
"Yusuf"
```

#### Multiple variables

```cypher
MATCH (c:Customer)-[:BUYS]->(p:Product {name: 'Chocolate'})
RETURN c AS customer, p AS product
NEXT
RETURN
  customer.firstName AS chocolateCustomer,
  product.price * (1 - customer.discount) AS chocolatePrice;
```

**Result example:**

```
chocolateCustomer | chocolatePrice
"Amir"            | 4.5
```

> Note: A `RETURN` before `NEXT` may only include variables or aliased expressions—no raw literals.

Additionally, only variables explicitly returned are available in later segments ([Graph Database & Analytics][1]).

---

### ❓ Alternative to `CALL` subqueries

**Classic `CALL`:**

```cypher
MATCH (p:Product)
CALL {
  MATCH (c:Customer)-[:BUYS]->(p)
  RETURN collect(c.firstName) AS customers
}
RETURN p.name AS product, customers;
```

**With `NEXT`:**

```cypher
MATCH (p:Product)
RETURN p
NEXT
MATCH (c:Customer)-[:BUYS]->(p)
RETURN collect(c.firstName) AS customers, p
NEXT
RETURN p.name AS product, customers;
```

Cleaner, avoids nested parentheses, easier to read ([Graph Database & Analytics][1]).

---

### ✅ Conditional queries inside `NEXT`

```cypher
MATCH (c:Customer)-[:BUYS]->(:Product)<-[:SUPPLIES]-(s:Supplier)
RETURN c.firstName AS customer, s.name AS supplier
NEXT
WHEN supplier = "TechCorp" THEN
  RETURN customer, "Tech enjoyer" AS personality
WHEN supplier = "Foodies Inc." THEN
  RETURN customer, "Tropical plant enjoyer" AS personality
NEXT
RETURN customer, collect(DISTINCT personality) AS personalities
NEXT
WHEN size(personalities) > 1 THEN
  RETURN customer, "Enjoyer of tech and plants" AS personality
ELSE
  RETURN customer, personalities[0] AS personality;
```

Aggregates customers based on their bought products ([Graph Database & Analytics][1]).

---

### ⚠️ `NEXT` in `UNION`

If a `UNION` block contains `NEXT`, wrap it in `{}`:

```cypher
{
  <query using NEXT>
}
UNION
<other query>
```

---

Let me know if you'd like this in a GitHub-friendly outline, with more optimized formatting or examples!

[1]: https://neo4j.com/docs/cypher-manual/25/queries/composed-queries/sequential-queries/?utm_source=chatgpt.com "Sequential queries (NEXT) - Cypher Manual - Neo4j Graph Data Platform"
[2]: https://neo4j.com/docs/cypher-manual/current/introduction/cypher-neo4j/?utm_source=chatgpt.com "Cypher and Neo4j - Cypher Manual"
