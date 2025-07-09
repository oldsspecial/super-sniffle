# Active Context: super-sniffle

## Current Focus
**Successfully Completed LIMIT and SKIP Clauses** - Just completed implementing the LIMIT and SKIP clauses for pagination and result limiting. These clauses complete the basic Cypher READ functionality, providing full support for result pagination, limiting, and offsetting. The implementation includes proper method chaining, parameter support, and integration with all existing clauses.

## Recent Changes
- ✅ Implemented complete operator-based expression system
- ✅ Built inline pattern conditions with native Cypher syntax support
- ✅ Created NodePattern, RelationshipPattern, and PathPattern classes
- ✅ **COMPLETED: Full MATCH clause implementation with chaining**
- ✅ **COMPLETED: Enhanced WHERE clause with complex chaining support**
- ✅ **COMPLETED: Full RETURN clause with projections, DISTINCT, and "return everything" (*) support**
- ✅ **COMPLETED: Full WITH clause implementation with tuple projections**
- ✅ **COMPLETED: Variable expression class and var() function implementation**
- ✅ **COMPLETED: ORDER BY clause with asc/desc functions**
- ✅ **COMPLETED: LIMIT and SKIP clauses for pagination**
- ✅ Fixed complex clause ordering issues (MATCH → WHERE → WITH → ORDER BY → LIMIT/SKIP → RETURN)
- ✅ Added comprehensive unit tests and real-world examples
- ✅ Updated all test cases to use proper var() function instead of workarounds
- 📋 **NEXT PRIORITY**: UNION support, aggregation functions, OPTIONAL MATCH

## Active Decisions

### API Design
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

### Development Workflow
- Test-driven development approach
- Documentation-first for public APIs
- Regular refactoring to maintain clean architecture

## Current Patterns and Preferences

### Expression System Design
- **Property references**: Use `prop("variable", "property_name")` for node/relationship properties
- **Variable references**: Use `var("variable_name")` for variables created by WITH, UNWIND, etc.
- **Parameter references**: Use `param("parameter_name")` for query parameters
- **Literal values**: Use `literal(value)` for inline values
- All expression types support full operator overloading (==, !=, >, <, >=, <=)
- All expression types support logical operations (&, |, ~)
- String-specific operations (contains, starts_with, ends_with) available as methods

### WITH Clause Design
- String-based projections for maximum flexibility
- Support for single and multiple projections
- DISTINCT support via optional parameter
- Full chaining support with WHERE and other clauses
- Clean integration with variable references via var() function

### Naming Conventions
- snake_case for functions and variables
- PascalCase for classes
- UPPER_CASE for constants
- Descriptive names that reflect Cypher terminology

### Code Organization
- Modular structure with clear separation of concerns
- Small, focused files with single responsibilities
- Comprehensive docstrings for all public APIs
- Examples in docstrings for complex functionality

### Testing Approach
- Unit tests for individual components
- Integration tests for complete queries
- Property-based tests for edge cases
- Demo scripts for real-world examples
- High test coverage target (>90%)

## Project Insights

### Key Challenges Solved
1. **Variable vs Property distinction** - Implemented semantic separation between variables and properties
2. **WITH clause flexibility** - String-based projections provide maximum Cypher compatibility
3. **Operator overloading** - Full expression system with Python operator support
4. **Clause chaining** - Complex query construction with proper ordering

### Recent Technical Insights
- Variables created by WITH clauses are fundamentally different from properties
- String-based projections offer more flexibility than structured objects for WITH clauses
- Operator overloading provides intuitive expression building
- Clear semantic APIs prevent common mistakes (prop vs var usage)

### Learning Resources
- [Neo4j Cypher Manual](https://neo4j.com/docs/cypher-manual/current/)
- [CYPHER25 Specification](https://s3.amazonaws.com/artifacts.opencypher.org/openCypher9.pdf)
- [Python Dataclasses Documentation](https://docs.python.org/3/library/dataclasses.html)
- [Visitor Pattern in Python](https://refactoring.guru/design-patterns/visitor/python/example)

## Current Implementation Status

### Completed Components
- ✅ **Expression System**: Property, Variable, Parameter, Literal classes with full operator support
- ✅ **Pattern System**: NodePattern, RelationshipPattern, PathPattern with inline conditions
- ✅ **MATCH Clause**: Full implementation with pattern support and chaining
- ✅ **WHERE Clause**: Complex condition building with operator overloading
- ✅ **RETURN Clause**: Projections, DISTINCT, and return-all (*) support
- ✅ **WITH Clause**: String-based projections, DISTINCT, and chaining support
- ✅ **API Functions**: match(), node(), relationship(), path(), prop(), var(), param(), literal()

### Test Coverage
- ✅ Unit tests for all expression types
- ✅ Integration tests for clause combinations
- ✅ Real-world example demonstrations
- ✅ Edge case coverage for all operators
- ✅ Variable vs property distinction validation

## Next Steps

### Immediate Tasks
1. **Implement ORDER BY clause** - Sorting support for query results
2. **Add LIMIT and SKIP clauses** - Pagination and result limiting
3. **Create UNION support** - Combining multiple query results
4. **Add aggregation functions** - Built-in functions like count(), sum(), avg()
5. **Implement OPTIONAL MATCH** - Left join equivalent for graph queries

### Short-term Goals
1. Complete all basic Cypher READ clauses
2. Add support for complex path patterns and variable-length relationships
3. Develop comprehensive parameter handling
4. Create migration guides from string-based queries
5. Set up proper package distribution

### Medium-term Goals
1. Add support for WRITE operations (CREATE, UPDATE, DELETE)
2. Implement query optimization hints
3. Develop comprehensive documentation site
4. Create VS Code extension for syntax highlighting
5. Publish stable package to PyPI

## Priority Feature: Function Support

### Requirements
- **Problem**: Need support for built-in Cypher functions (count(), sum(), avg()) and APOC functions
- **Solution**: Function expression class with proper argument handling
- **Key Features**: Type-safe function calls, aggregation support, custom function registration

### Implementation Approach
```python
# Example Usage:
from super_sniffle import func, match, node, var

# Built-in functions
query = (
    match(node("p", "Person"))
    .with_(func("count", "p").as_("personCount"))
    .where(var("personCount") > literal(100))
)

# APOC functions  
query = (
    match(node("n", "Node"))
    .where(func("apoc.node.degree", "n") < literal(1000))
)
```

### Core Components Needed
1. **Function expression class** - Handle function calls with arguments
2. **Built-in function registry** - Common Cypher functions
3. **Aggregation support** - Special handling for GROUP BY semantics
4. **Custom function support** - User-defined and APOC functions

## Open Questions
1. How to handle function argument type validation?
2. What's the best approach for aggregation function semantics?
3. How to provide helpful error messages for invalid function usage?
4. Should we support function composition and nesting?
