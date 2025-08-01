# Missing Features: super-sniffle

## ✅ **COMPLETED Features** 

### USE Clause
- **Status**: ✅ **COMPLETED** - Fully implemented and tested
- **Implementation**: `UseClause` AST class + API integration
- **Tests**: 11 comprehensive unit tests passing
- **Usage**: `use("database_name")` or `QueryBuilder().use("database")`

### CALL Procedure Support
- **Status**: ✅ **COMPLETED** - Fully implemented and tested
- **Implementation**: `CallProcedureClause` AST class + API integration
- **Tests**: Comprehensive unit tests passing
- **Usage**: `call_procedure("db.labels")` or `QueryBuilder().call_procedure("db.labels")`

### YIELD Clause
- **Status**: ✅ **COMPLETED** - Fully implemented and tested
- **Implementation**: `YieldClause` AST class + API integration
- **Tests**: Comprehensive unit tests passing
- **Usage**: `.yield_("label")` after CALL procedure

## 🔴 **ACTUALLY Missing - Immediate Priority**

### 1. CALL IN TRANSACTIONS
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

1. **CALL IN TRANSACTIONS** (Advanced feature)
2. **Dynamic Parameters** (Convenience feature)

## Notes
- ✅ USE clause is fully implemented and tested
- ✅ CALL subquery is fully implemented and tested
- ✅ CALL procedure is fully implemented and tested
- ✅ YIELD clause is fully implemented and tested
- ✅ All basic Cypher READ operations are complete
- 🎯 Focus should be on dynamic transactions next
