# Product Context: super-sniffle

## Problem Statement
Developers working with Neo4j databases often need to construct complex Cypher queries programmatically. The common approach of string concatenation becomes unwieldy and error-prone as queries grow in complexity. This leads to:

1. **Maintenance challenges** - Large string-based queries are difficult to read, update, and debug
2. **Syntax errors** - String concatenation easily introduces syntax errors that are only caught at runtime
3. **Poor IDE support** - String-based queries lack code completion, syntax highlighting, and other IDE features
4. **Reduced reusability** - Query fragments are difficult to compose and reuse effectively
5. **Testing difficulties** - String-based queries are challenging to test in isolation

## User Experience Goals
Developers using super-sniffle should experience:

1. **Intuitive construction** - Building queries should feel natural and follow Cypher's logical structure
2. **Discoverability** - IDE features should reveal available options and guide correct usage
3. **Confidence** - Generated queries should be syntactically valid by construction
4. **Readability** - Query construction code should be as clear and maintainable as the queries themselves
5. **Flexibility** - The library should accommodate complex query patterns without forcing workarounds

## User Workflows

### Basic Query Construction
```python
# Instead of:
query = f"MATCH (p:Person)-[:KNOWS]->(f:Person) WHERE p.name = '{name}' RETURN f.name"

# With super-sniffle:
query = (
    match(node("p", "Person").relates_to(">", "KNOWS", node("f", "Person")))
    .where(prop("p", "name").equals(param("name")))
    .return_("f.name")
    .to_cypher()
)
```

### Complex Pattern Composition
Developers should be able to build complex patterns incrementally, combining smaller patterns into larger ones with clear, functional composition.

### Query Reuse and Parameterization
Common query fragments should be easily extractable and reusable across different queries, with proper parameterization.

## Value Proposition
super-sniffle delivers value by:

1. **Reducing errors** - Eliminating an entire class of syntax errors through structured query building
2. **Improving productivity** - Enabling faster development through IDE assistance and reusable components
3. **Enhancing maintainability** - Making complex queries more readable and easier to modify
4. **Facilitating testing** - Allowing query components to be tested in isolation
5. **Enabling refactoring** - Making it safer to refactor and evolve query logic

## Market Positioning
While there are libraries for executing Cypher queries (like the official Neo4j drivers), super-sniffle focuses exclusively on query generation with a functional approach. It complements existing Neo4j tools rather than competing with them.

## Success Metrics
The success of super-sniffle will be measured by:

1. **Adoption** - Usage in real-world projects
2. **Query complexity** - Ability to handle increasingly complex query patterns
3. **Developer feedback** - Positive responses regarding usability and productivity
4. **Code quality** - Reduction in query-related bugs in projects using the library
5. **Community engagement** - Contributions, feature requests, and discussions
