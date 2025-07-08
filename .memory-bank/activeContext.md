# Active Context: super-sniffle

## Current Focus
**Completing Basic Query Construction** - We just achieved a major milestone with the RETURN clause implementation! The core query building blocks (MATCH, WHERE, RETURN) are now fully functional with proper clause chaining. Next priority is completing the basic query functionality with ORDER BY, LIMIT, and SKIP clauses.

## Recent Changes
- ✅ Implemented complete operator-based expression system
- ✅ Built inline pattern conditions with native Cypher syntax support
- ✅ Created NodePattern, RelationshipPattern, and PathPattern classes
- ✅ **COMPLETED: Full MATCH clause implementation with chaining**
- ✅ **COMPLETED: Enhanced WHERE clause with complex chaining support**
- ✅ **COMPLETED: Full RETURN clause with projections, DISTINCT, and "return everything" (*) support**
- ✅ Fixed complex clause ordering issues (MATCH → WHERE → RETURN)
- ✅ Added comprehensive unit tests and real-world examples (test_return_demo.py)
- 📋 **NEXT PRIORITY**: ORDER BY, LIMIT, SKIP clauses to complete basic functionality

## Active Decisions

### API Design
- Functional approach with immutable objects
- Method chaining for query construction
- **Operator-based syntax for WHERE clauses** - Using Python operator overloading for intuitive condition building
- **Inline pattern conditions** - Support for Cypher's native inline WHERE syntax: `(p:Person WHERE p.age > 20)`
- Dual API support - both method-based and operator-based approaches
- Clear separation between components and string generation
- Type hints throughout for IDE support

### Implementation Strategy
- Start with core AST components
- Implement basic query clauses (MATCH, WHERE, RETURN)
- Add string generation capabilities
- Expand to more complex Cypher features

### Development Workflow
- Test-driven development approach
- Documentation-first for public APIs
- Regular refactoring to maintain clean architecture

## Current Patterns and Preferences

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
- High test coverage target (>90%)

## Project Insights

### Key Challenges
1. **Balancing flexibility and simplicity** - Making the API powerful enough for complex queries while keeping it intuitive
2. **Cypher syntax complexity** - Handling all the edge cases and variations in Cypher syntax
3. **String formatting** - Generating well-formatted, readable Cypher strings
4. **Performance** - Ensuring efficient query generation for large, complex queries

### Learning Resources
- [Neo4j Cypher Manual](https://neo4j.com/docs/cypher-manual/current/)
- [CYPHER25 Specification](https://s3.amazonaws.com/artifacts.opencypher.org/openCypher9.pdf)
- [Python Dataclasses Documentation](https://docs.python.org/3/library/dataclasses.html)
- [Visitor Pattern in Python](https://refactoring.guru/design-patterns/visitor/python/example)

## Priority Feature: Global Conditions System

### Requirements
- **Problem**: Need to automatically apply conditions like `apoc.node.degree(n) < 1000` to prevent performance issues
- **Solution**: Registry of global conditions that are automatically ANDed with explicit conditions
- **Key Requirement**: Conditions must be applied **inline** for better readability when debugging

### Implementation Approach
```python
# Example Usage:
context = QueryContext()
context.add_node_condition(
    func("apoc.node.degree", "n") < 1000, 
    label="Person"
)

# Query with explicit condition
query = match(node("p", "Person").where(prop("p", "age") > 30))

# Generated Cypher (with global conditions applied inline):
# MATCH (p:Person WHERE p.age > 30 AND apoc.node.degree(p) < 1000)
```

### Core Components Needed
1. **QueryContext class** - Registry for global conditions by label/type
2. **Function expression support** - For APOC functions like `apoc.node.degree()`
3. **Pattern integration** - Modify `to_cypher()` methods to accept context
4. **Condition merging logic** - AND global conditions with explicit ones
5. **API functions** - Clean interface for registering global conditions

### Benefits
- Prevent accidental performance issues
- Centralized performance/business logic
- Cleaner, more readable queries
- Consistent condition application across codebase

## Next Steps

### Immediate Tasks (UPDATED PRIORITY)
1. **Implement global conditions system** - QueryContext and function expressions
2. **Add function call expressions** - Support for `func("apoc.node.degree", var)`
3. **Integrate with pattern classes** - Update `to_cypher()` methods
4. **Write comprehensive tests** - Cover all condition combinations
5. **Create usage examples** - Real-world scenarios with global conditions
6. Add simple MATCH clause implementation

### Short-term Goals
1. Implement all basic Cypher READ clauses
2. Add support for complex path patterns
3. Develop parameter handling
4. Create comprehensive examples
5. Set up CI/CD pipeline

### Medium-term Goals
1. Add support for all CYPHER25 READ features
2. Implement query optimization
3. Develop comprehensive documentation
4. Create migration guides from string-based queries
5. Publish initial package to PyPI

## Open Questions
1. How to handle custom functions and procedures in a type-safe way?
2. What's the best approach for formatting complex nested queries?
3. How to provide helpful error messages for invalid query constructions?
4. What level of validation should happen at query construction vs. string generation time?
