# Missing Features: super-sniffle

## Priority List (Higher than CALL IN TRANSACTIONS, COLLECT, EXISTS subqueries)

### 🔴 CRITICAL - Immediate Priority

#### 1. USE Clause
- **Status**: Missing
- **Purpose**: Direct queries to run on specific databases
- **Cypher Example**: `USE neo4j MATCH (m:Movie) RETURN m.title`
- **Implementation Notes**: 
  - Add USE clause AST class
  - Support database name as string parameter
  - Integrate with query builder chain

#### 2. CALL Procedure Support
- **Status**: Missing  
- **Purpose**: Support for calling database procedures
- **Cypher Example**: `CALL db.relationshipTypes()`
- **Implementation Notes**:
  - Distinguish from CALL subqueries
  - Support procedure names and arguments
  - Handle procedure return values

#### 3. YIELD Clause
- **Status**: Missing
- **Purpose**: Handle output from procedure calls
- **Cypher Example**: `CALL db.relationshipTypes() YIELD relationshipType`
- **Implementation Notes**:
  - Integrate with CALL procedure support
  - Handle yielded variables and aliases

### 🟡 MEDIUM - Next Phase

#### 4. Dynamic Label Parameters
- **Status**: Missing
- **Purpose**: Dynamic label references using parameters
- **Cypher Example**: `MATCH (movie:$label) RETURN movie.title`
- **Implementation Notes**:
  - Support parameter placeholders in labels
  - Ensure proper parameter binding

#### 5. Dynamic Relationship Type Parameters
- **Status**: Missing
- **Purpose**: Dynamic relationship types using parameters
- **Cypher Example**: `MATCH ()-[r:$(relationshipType)]->()`
- **Implementation Notes**:
  - Support parameter placeholders in relationship types
  - Handle type validation

#### 6. Dynamic Property Access
- **Status**: Missing
- **Purpose**: Dynamic property access using parameters
- **Cypher Example**: `MATCH (n:Person) WHERE n[$propname] > 40`
- **Implementation Notes**:
  - Support bracket notation for dynamic properties
  - Ensure parameter safety

## Implementation Order

1. **USE Clause** - Foundation for multi-database support
2. **CALL Procedure + YIELD** - Core database interaction
3. **Dynamic Parameters** - Flexibility for parameterized queries

## Notes
- Pattern variable assignment is already supported via `match().as('variable')`
- These features take priority over CALL IN TRANSACTIONS, COLLECT, EXISTS subqueries
- Focus on READ operations as per project scope
