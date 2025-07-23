# Active Context: super-sniffle

## Current Focus
**COMPLETED: CALL Subquery & UNWIND Implementation** - Ready for CALL IN TRANSACTIONS

## Recent Changes
- ✅ **COMPLETED: CALL subquery clause** - Added AST class, API method, string generation, and 18 comprehensive tests
- ✅ **COMPLETED: UNWIND clause** - Added AST class, API method, string generation, and comprehensive tests
- ✅ **COMPLETED: Codebase Refactoring** - Split patterns.py and expressions.py into one class per file for better maintainability
- ✅ **COMPLETED: Operator Overloading for Path Construction**:
  - Added `__add__` operator to NodePattern, RelationshipPattern, and PathPattern
  - Enhanced path() function to accept mixed pattern types
  - Implemented WHERE condition chaining for paths
  - Added comprehensive test coverage
- ✅ **COMPLETED: RelationshipPattern Type Constraint** - Enforced single relationship type per Cypher specification
- ✅ **COMPLETED: Path API improvements**:
  - Automatic insertion of implicit relationships ("--") between consecutive nodes
  - Fixed path concatenation to handle duplicate nodes at connection points
  - Maintained immutable pattern throughout
- ✅ **COMPLETED: Quantified Path Patterns** - Implemented variable-length path matching with quantifiers
- ✅ **COMPLETED: Label Expression System** - Added support for complex label expressions (&, |, !)
- ✅ Implemented complete operator-based expression system
- ✅ Built inline pattern conditions with native Cypher syntax support
- ✅ Created NodePattern, RelationshipPattern, PathPattern, and QuantifiedPathPattern classes
- ✅ **COMPLETED: Full MATCH clause implementation with chaining**
- ✅ **COMPLETED: Enhanced WHERE clause with complex chaining support**
- ✅ **COMPLETED: Full RETURN clause with projections, DISTINCT, and "return everything" (*) support**
- ✅ **COMPLETED: Full WITH clause implementation with tuple projections**
- ✅ **COMPLETED: Variable expression class and var() function implementation**
- ✅ **COMPLETED: ORDER BY clause with asc/desc functions**
- ✅ **COMPLETED: LIMIT and SKIP clauses for pagination**
- ✅ **COMPLETED: UNION and UNION ALL support**
- ✅ Fixed complex clause ordering issues (MATCH → WHERE → WITH → RETURN → ORDER BY → SKIP → LIMIT)
- ✅ Added comprehensive unit tests and real-world examples
- ✅ Updated all test cases to use proper var() function instead of workarounds
- ✅ **COMPLETED: Aggregation functions** - Implemented count(), sum(), avg(), min(), max() with GROUP BY support

## Active Decisions

### API Design
- **RelationshipPattern Type Constraint**:
  - Enforce single relationship type instead of multiple types
  - Update API functions to match new interface
  - Ensure Cypher compliance
- **Path API Improvements**:
  - Automatically insert implicit relationships between consecutive nodes
  - Skip duplicate nodes during path concatenation
  - Maintain immutable pattern throughout
- **Label Expression System**:
  - Implemented complex label expressions using &, |, and ! operators
  - Added L() helper function for cleaner syntax
- **Quantified Path Patterns**:
  - Added quantifiers like *, +, and {min,max} for variable-length paths
  - Implemented one_or_more() and zero_or_more() convenience methods
- **Variable Naming**:
  - Consistent use of variable names for nodes (p, n) and relationships (r)
  - Clear distinction between variables and properties
- Functional approach with immutable objects
- Method chaining for query construction
- **Operator-based syntax for WHERE clauses** - Using Python operator overloading for intuitive condition building
- **Inline pattern conditions** - Support for Cypher's native inline WHERE syntax: `(p:Person WHERE p.age > 20)`
- **Clear semantic distinction**: `prop()` for properties vs `var()` for variables
- Dual API support - both method-based and operator-based approaches
- Clear separation between components and string generation
- Type hints throughout for IDE support

### Implementation Strategy
- Start with core AST components
- Implement basic query clauses (MATCH, WHERE, RETURN, WITH)
- Add string generation capabilities
- Expand to more complex Cypher features
- Test-driven development with comprehensive coverage

### Development Workflow
- Test-driven development approach
- Documentation-first for public APIs
- Regular refactoring to maintain clean architecture
- Update memory bank after significant changes

## Project Insights

### Key Challenges Solved
1. **Codebase Refactoring** - Successfully split large files into maintainable modules without breaking functionality
2. **Path Construction** - Automated implicit relationship insertion between consecutive nodes
3. **Path Concatenation** - Fixed duplicate node issue during path combination
4. **Variable vs Property distinction** - Implemented semantic separation between variables and properties
5. **WITH clause flexibility** - String-based projections provide maximum Cypher compatibility
6. **Operator overloading** - Full expression system with Python operator support
7. **Clause chaining** - Complex query construction with proper ordering
8. **CALL Subquery Implementation** - Careful handling of variable scoping patterns
9. **UNWIND Clause** - Clean integration with existing clause system

### Recent Technical Insights
- Paths with consecutive nodes require implicit relationships for valid Cypher syntax
- Path concatenation must detect and handle duplicate nodes at connection points
- Clear semantic APIs prevent common mistakes (prop vs var usage)
- Comprehensive unit tests are crucial for maintaining complex pattern logic
- Immutable patterns simplify reasoning about query composition
- **CALL subquery** requires careful variable scoping to match Cypher specification
- **UNWIND clause** integrates seamlessly with existing clause ordering

## Current Implementation Status

### Completed Components
- ✅ **CALL Subquery**: Implemented with variable scoping support (CALL { ... }, CALL(var) { ... }, CALL(*) { ... })
- ✅ **UNWIND Clause**: Full implementation with expression and variable binding
- ✅ **Aggregation Functions**: Implemented count(), sum(), avg(), min(), max() with DISTINCT support
- ✅ **Path API**: Automatic implicit relationships, fixed concatenation logic
- ✅ **Expression System**: Property, Variable, Parameter, Literal classes with full operator support
- ✅ **Pattern System**: 
  - NodePattern with label expressions and inline conditions
  - RelationshipPattern with direction and type constraints
  - PathPattern with automatic relationship insertion
  - QuantifiedPathPattern for variable-length paths
- ✅ **MATCH Clause**: Full implementation with pattern support and chaining
- ✅ **WHERE Clause**: Complex condition building with operator overloading
- ✅ **RETURN Clause**: Projections, DISTINCT, and return-all (*) support
- ✅ **WITH Clause**: String-based projections, DISTINCT, and chaining support
- ✅ **USE Clause**: Database selection for top-level and subqueries
- ✅ **API Functions**: 
  - match(), node(), relationship(), path(), prop(), var(), param(), literal()
  - L() helper for label expressions
  - Quantifier methods: one_or_more(), zero_or_more()
  - Aggregation functions: count(), sum(), avg(), min(), max()
  - use() for database selection
  - call_subquery() for subqueries
  - unwind() for list unwinding

### Test Coverage
- ✅ **192/192 unit tests passing** (100% pass rate)
- ✅ **92% overall coverage**
- ✅ Comprehensive coverage for path operations
- ✅ Integration tests for clause combinations
- ✅ Real-world example demonstrations
- ✅ Edge case coverage for all operators
- ✅ **CALL subquery**: 18 comprehensive tests
- ✅ **UNWIND clause**: Full test suite

## Next Steps

### Immediate Tasks
1. ✅ **COMPLETED: CALL subquery**
2. ✅ **COMPLETED: UNWIND clause**
3. **Implement CALL IN TRANSACTIONS** - Add support for CALL subqueries with IN TRANSACTIONS clause
4. **Implement additional subquery types**:
   - COLLECT subqueries
   - COUNT subqueries  
   - EXISTS subqueries

### Short-term Goals
1. Complete all advanced Cypher READ features
2. Add comprehensive parameter handling
3. Create migration guides from string-based queries
4. Set up proper package distribution

### Medium-term Goals
1. Add support for WRITE operations (CREATE, UPDATE, DELETE)
2. Implement query optimization hints
3. Develop comprehensive documentation site
4. Create VS Code extension for syntax highlighting
5. Publish stable package to PyPI

## Architecture Decisions
- **CALL Subquery Design**: Clean separation between subquery and variable scoping
- **UNWIND Integration**: Seamless integration with existing clause ordering
- **String Formatting**: Consistent use of single quotes for string literals
- **Variable Scoping**: Clear patterns for CALL subquery variable handling
