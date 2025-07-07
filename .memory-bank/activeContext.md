# Active Context: super-sniffle

## Current Focus
The project is in the initial planning and setup phase. We are establishing the core architecture, design patterns, and project structure for the super-sniffle library.

## Recent Changes
- Created the memory bank structure
- Defined the project brief and scope
- Established the product context and user workflows
- Outlined the system architecture and design patterns
- Documented the technical context and development environment

## Active Decisions

### API Design
- Functional approach with immutable objects
- Method chaining for query construction
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

## Next Steps

### Immediate Tasks
1. Set up the basic project structure
2. Create the core AST dataclasses
3. Implement basic node and relationship patterns
4. Add simple MATCH clause support
5. Develop string generation for basic patterns
6. Write initial tests for core components

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
