# Missing Features: super-sniffle

## ✅ **COMPLETED Features** (Updated Status)

### USE Clause
- **Status**: ✅ **COMPLETED** - Fully implemented and tested
- **Implementation**: `UseClause` AST class + API integration
- **Tests**: 11 comprehensive unit tests passing
- **Usage**: `use("database_name")` or `QueryBuilder().use("database")`

## 🔴 **ACTUALLY Missing - Immediate Priority**

### 1. CALL Procedure Support
- **Status**: ❌ **MISSING** - Not yet implemented
- **Purpose**: Support for calling database procedures (distinct from CALL subqueries)
- **Cypher Examples**:
  - `CALL db.labels()`
  - `CALL dbms.checkConfigValue('setting', 'value')`
  - `CALL apoc.neighbors.tohop(n, "KNOWS>", 1)`
- **Key Requirements**:
  - Procedure name (string)
  - Procedure arguments (literals, parameters, expressions)
  - Optional vs required calls
  - Integration with YIELD clause

### 2. YIELD Clause
- **Status**: ❌ **MISSING** - Not yet implemented
- **Purpose**: Handle output from procedure calls
- **Cypher Examples**:
  - `CALL db.labels() YIELD label`
  - `CALL db.labels() YIELD *`
  - `CALL apoc.neighbors.tohop(n, "KNOWS>", 1) YIELD node`
- **Key Requirements**:
  - Select specific return columns
  - Aliasing support (`YIELD column AS alias`)
  - Wildcard support (`YIELD *`)
  - Integration with CALL procedure

### 3. CALL IN TRANSACTIONS
- **Status**: ❌ **MISSING** - Not yet implemented
- **Purpose**: Batch processing with transaction management
- **Cypher Examples**:
  - `CALL { ... } IN TRANSACTIONS`
  - `CALL { ... } IN TRANSACTIONS OF 1000 ROWS`

## 🟡 **Future Enhancements**

### Dynamic Parameters
- **Status**: ❌ **MISSING** - Lower priority
- **Purpose**: Dynamic label/type/property access via parameters
- **Cypher Examples**:
  - `MATCH (n:$label)` - dynamic labels
  - `MATCH ()-[r:$type]->()` - dynamic relationship types
  - `n[$property]` - dynamic property access

## Implementation Priority (Updated)

1. **CALL Procedure + YIELD** (Critical - missing functionality)
2. **CALL IN TRANSACTIONS** (Advanced feature)
3. **Dynamic Parameters** (Convenience feature)

## Notes
- ✅ USE clause is fully implemented and tested
- ✅ CALL subquery is fully implemented and tested
- ✅ All basic Cypher READ operations are complete
- 🎯 Focus should be on CALL procedure implementation next
