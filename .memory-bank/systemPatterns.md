# System Patterns: super-sniffle

## Architecture Overview

super-sniffle follows a layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────┐
│            Public API               │
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│         Query Components            │
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│        AST Construction             │
└───────────────┬─────────────────────┘
                │
┌───────────────▼─────────────────────┐
│       String Generation             │
└─────────────────────────────────────┘
```

### 1. Public API Layer
The top-level interface that developers interact with directly. Provides intuitive functions and classes for query construction.

### 2. Query Components Layer
Implements the building blocks of Cypher queries (nodes, relationships, patterns, clauses) as composable objects.

### 3. AST Construction Layer
Transforms the query components into an Abstract Syntax Tree (AST) that represents the structure of the Cypher query.

### 4. String Generation Layer
Traverses the AST to produce properly formatted Cypher query strings.

## Core Design Patterns

### Immutable Builder Pattern
Each query operation returns a new query object rather than modifying the existing one. This enables:
- Method chaining for fluent interfaces
- Safe composition without side effects
- Thread safety
- Easier testing

```python
# Example of immutable builder pattern
query1 = match(node("n", "Person"))
query2 = query1.where(prop("n", "age").gt(30))  # query1 remains unchanged
```

### Composable Functions
Pure functions that can be combined to create complex query patterns:

```python
def person_node(var_name):
    return node(var_name, "Person")

def knows_relationship(from_var, to_var):
    return relationship(from_var, "KNOWS", to_var)

# Composition
pattern = person_node("p").relates_to(knows_relationship, person_node("f"))
```

### Abstract Syntax Tree (AST)
Using dataclasses to represent the query structure:

```python
@dataclass(frozen=True)
class Node:
    variable: str
    labels: List[str]
    properties: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class Relationship:
    variable: Optional[str]
    types: List[str]
    properties: Dict[str, Any] = field(default_factory=dict)
    direction: Direction = Direction.OUTGOING
```

### Visitor Pattern
For traversing the AST and generating Cypher strings:

```python
class CypherGenerator(Visitor):
    def visit_node(self, node: Node) -> str:
        # Generate Cypher for a node
        
    def visit_relationship(self, rel: Relationship) -> str:
        # Generate Cypher for a relationship
        
    # Other visit methods...
```

## Key Technical Decisions

### 1. Dataclasses for AST
Using Python's dataclasses for AST nodes provides:
- Immutability (with frozen=True)
- Automatic equality and hash methods
- Clear structure and type hints
- Serialization capabilities

### 2. Type Hints Throughout
Comprehensive type annotations for:
- Better IDE support
- Static analysis
- Self-documenting code
- Catching errors early

### 3. Functional Approach
Preference for pure functions and immutable data structures to:
- Simplify testing
- Enable composition
- Reduce side effects
- Improve code reasoning

### 4. String Generation Strategy
Two-phase approach:
1. Build complete AST first
2. Generate formatted string in a single pass

This allows for:
- Optimization before string generation
- Consistent formatting
- Proper indentation and line breaks for readability

## Component Relationships

### Query Building Flow
1. User creates query components (nodes, relationships, patterns)
2. Components are assembled into clauses (MATCH, WHERE, etc.)
3. Clauses are combined into a complete query
4. Query is converted to an AST
5. AST is rendered as a Cypher string

### Error Handling Strategy
- Early validation at the component level
- Type checking through static analysis
- Runtime validation before string generation
- Clear error messages with context

## Critical Implementation Paths

### Pattern Construction
The most complex part of the system, handling:
- Variable-length paths
- Quantified path patterns
- Named paths
- Pattern comprehensions

### Parameter Handling
Safe parameterization of values to prevent injection:
```python
# Instead of directly embedding values
.where(prop("n", "name").equals(param("name")))
# Generates: WHERE n.name = $name
```

### Formatting and Indentation
Ensuring generated queries are readable and maintainable:
```cypher
MATCH (p:Person)
WHERE p.age > 30
RETURN p.name, p.age
ORDER BY p.age DESC
LIMIT 10
```
