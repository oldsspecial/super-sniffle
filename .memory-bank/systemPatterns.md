# System Patterns: super-sniffle

## Architecture Overview

### Core Design Philosophy
The super-sniffle library follows a **functional, immutable, and composable** architecture where each component is:
- **Immutable**: Once created, objects cannot be modified
- **Composable**: Components can be combined to build complex queries
- **Type-safe**: Full type hints throughout for IDE support
- **Testable**: Each component has clear boundaries and behavior

### Key Architectural Patterns

#### 1. AST-Based Design
The library uses an Abstract Syntax Tree (AST) approach where:
- **Expressions** represent values and conditions
- **Patterns** represent graph structures
- **Clauses** represent query operations
- **Queries** are composed of ordered clauses

#### 2. Immutable Builder Pattern
- **QueryBuilder** provides fluent interface for query construction
- Each method returns a new instance (immutable)
- Method chaining enables readable query construction
- Clear separation between construction and string generation

#### 3. Expression System
**Base Classes:**
- `Expression`: Base class for all expressions
- `Property`: Represents property access (node.prop)
- `Variable`: Represents variable references
- `Parameter`: Represents query parameters
- `Literal`: Represents literal values
- `FunctionExpression`: Represents function calls (count, sum, etc.)

**Operator Overloading:**
- Comparison operators: `==`, `!=`, `>`, `<`, `>=`, `<=`
- Logical operators: `&` (AND), `|` (OR), `~` (NOT)
- Method-based operations: `.contains()`, `.starts_with()`, etc.

#### 4. Pattern System
**Node Patterns:**
- `NodePattern`: Represents nodes with labels and properties
- Label expressions: `&` (AND), `|` (OR), `!` (NOT)
- Inline WHERE conditions: `(n:Person WHERE n.age > 30)`

**Relationship Patterns:**
- `RelationshipPattern`: Represents relationships with types and properties
- Direction support: `--`, `->`, `<-`
- Single type constraint per Cypher specification

**Path Patterns:**
- `PathPattern`: Represents complex traversals
- `QuantifiedPathPattern`: Variable-length paths with quantifiers
- Automatic relationship insertion between consecutive nodes

#### 5. Clause System
**Core Clauses:**
- `MatchClause`: Basic pattern matching
- `OptionalMatchClause`: Left join equivalent
- `WhereClause`: Filtering conditions
- `WithClause`: Projection and variable binding
- `ReturnClause`: Final result specification
- `OrderByClause`: Sorting results
- `LimitClause`/`SkipClause`: Pagination
- `UnwindClause`: List unwinding
- `CallSubqueryClause`: Subquery execution
- `UseClause`: Database selection

**Clause Ordering:**
```
MATCH → WHERE → WITH → CALL → UNWIND → RETURN → ORDER BY → SKIP → LIMIT
```

### 6. Subquery Architecture
**CALL Subquery:**
- Variable scoping: CALL { ... }, CALL(var) { ... }, CALL(*) { ... }
- Integration with USE clause for database selection
- Proper clause ordering within subqueries

### 7. String Generation Patterns
**Consistent Formatting:**
- Single quotes for string literals
- Proper indentation for nested structures
- Clear separation between clauses
- Readable multi-line output

### 8. Testing Architecture
**Test Categories:**
- Unit tests for individual components
- Integration tests for clause combinations
- Real-world scenario tests
- Edge case coverage

**Test Patterns:**
- Descriptive test names
- AAA pattern (Arrange, Act, Assert)
- Comprehensive coverage for all public APIs

## Design Decisions

### 1. Immutable Objects
**Rationale:** Prevents accidental mutation and makes reasoning about queries easier
**Trade-offs:** Slightly more memory usage, but improved safety and predictability

### 2. Single Relationship Type Constraint
**Rationale:** Aligns with Cypher specification and prevents invalid queries
**Implementation:** Enforced at API level with clear error messages

### 3. String-based Projections in WITH Clause
**Rationale:** Provides maximum Cypher compatibility and flexibility
**Trade-offs:** Less type safety, but more expressive power

### 4. Operator Overloading for Expressions
**Rationale:** Provides intuitive, Pythonic syntax for building conditions
**Examples:** `prop('age') > 30`, `prop('name').contains('John')`

### 5. Automatic Relationship Insertion
**Rationale:** Improves API usability by reducing boilerplate
**Implementation:** Detects consecutive nodes and inserts implicit relationships

## Code Organization

### Directory Structure
```
src/super_sniffle/
├── api.py              # Public API functions
├── compound_query.py   # UNION support
├── ast/                # AST components
│   ├── expressions/    # Expression classes
│   └── patterns/       # Pattern classes
├── clauses/            # Clause implementations
└── utils/              # Utility functions
```

### Module Responsibilities
- **api.py**: Public interface and convenience functions
- **ast/**: Core AST components (expressions and patterns)
- **clauses/**: Individual clause implementations
- **compound_query.py**: Query composition and UNION support

## Integration Patterns

### 1. Query Construction Flow
```python
# Start with patterns
node = node('Person', 'p')
rel = relationship('KNOWS', 'r')

# Build query
query = (match(node)
         .where(prop('p.name') == 'Alice')
         .return_(var('p')))
```

### 2. Subquery Integration
```python
# CALL subquery with variable scoping
subquery = match(node('Person', 'p')).return_(var('p'))
query = match(node('Company', 'c')).call_subquery(subquery, ['c'])
```

### 3. UNWIND Integration
```python
# UNWIND with list processing
query = (unwind(param('names'), 'name')
         .match(node('Person', 'p'))
         .where(prop('p.name') == var('name'))
         .return_(var('p')))
```

## Error Handling Patterns

### 1. Validation at Construction Time
- Type checking for parameters
- Relationship type constraints
- Variable name validation

### 2. Clear Error Messages
- Descriptive error messages for invalid operations
- Helpful suggestions for fixing common mistakes

### 3. Type Safety
- Full type hints throughout
- MyPy-compatible type annotations
- IDE-friendly API design

## Performance Considerations

### 1. String Generation
- Lazy evaluation of string representations
- Efficient concatenation using join operations
- Minimal memory overhead for complex queries

### 2. Object Creation
- Lightweight objects for common patterns
- Efficient reuse of immutable components
- Optimized for query construction speed

## Future Extensibility

### 1. Plugin Architecture
- Clear interfaces for adding new clause types
- Extensible expression system
- Pattern system supports custom implementations

### 2. WRITE Operations
- Architecture supports extension to CREATE, MERGE, DELETE
- Clear separation between READ and WRITE operations
- Consistent API patterns for write operations

### 3. Query Optimization
- AST structure enables query analysis
- Potential for query optimization passes
- Extensible for custom optimization rules
