# Project Brief: super-sniffle

## Project Overview
super-sniffle is a Python library for generating Neo4j Cypher queries in a functional and flexible way. The library focuses on creating well-formatted, maintainable Cypher READ queries through an AST-based approach.

## Core Mission
To provide developers with a clean, type-safe, and maintainable way to generate complex Neo4j Cypher queries programmatically, eliminating the need for error-prone string concatenation.

## Key Objectives
1. Generate syntactically correct CYPHER25 READ queries
2. Provide a functional, composable API for query construction
3. Support all major Cypher READ operations and patterns
4. Ensure excellent IDE integration with tab-completion
5. Deliver comprehensive documentation and testing

## Scope
### In Scope
- READ queries only (MATCH, WHERE, RETURN, etc.)
- CYPHER25 specification compliance
- Support for complex patterns including quantified path patterns
- CALL() clauses for procedures
- APOC function calls (read-only subset)
- Query composition and optimization
- Well-formatted string output

### Out of Scope
- Query execution (no Neo4j driver integration)
- Write operations (CREATE, MERGE, DELETE, etc.)
- Administrative commands and queries
- Database management features
- Authentication/authorization

## Success Criteria
1. Developers can construct complex queries with less code than string concatenation
2. Generated queries are always syntactically valid CYPHER25
3. The API is intuitive and discoverable through IDE features
4. Documentation covers all use cases with clear examples
5. Test coverage ensures reliability and correctness

## Target Users
Developers who:
- Are familiar with Neo4j and Cypher
- Need to create complex read queries
- Value code maintainability and readability
- Want IDE support for query construction

## Timeline
Initial development will focus on core query components, followed by more advanced Cypher features and optimizations.
