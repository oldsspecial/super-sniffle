# super-sniffle

A Python library for generating Neo4j Cypher queries in a functional and flexible way using an AST-based approach.

## Overview

super-sniffle provides a clean, type-safe, and maintainable way to generate complex Neo4j Cypher READ queries programmatically, eliminating the need for error-prone string concatenation.

## Features

- **Functional API**: Build queries using composable functions and method chaining
- **Type Safety**: Comprehensive type hints for excellent IDE support
- **CYPHER25 Compliance**: Strict adherence to the CYPHER25 specification
- **Immutable Objects**: Safe composition without side effects
- **Well-Formatted Output**: Generates readable, properly indented Cypher queries
- **Zero Dependencies**: Minimal external dependencies for easy installation
- **Label Expressions**: Complex label matching using &, |, and ! operators
- **Quantified Path Patterns**: Variable-length paths with *, +, and {min,max} quantifiers

## Installation

```bash
pip install super-sniffle
```

For development:

```bash
git clone https://github.com/oldsspecial/super-sniffle.git
cd super-sniffle
poetry install
```

## Quick Start

> **Note**: super-sniffle is currently in active development. The API is stable for basic Cypher READ operations.

```python
from super_sniffle import match, node, relationship, prop, param

# Build a simple query
query = (
    match(node("p", "Person"))
    .where(prop("p", "age").gt(param("min_age")))
    .return_("p.name", "p.age")
    .order_by("p.age")
    .limit(10)
    .to_cypher()
)

print(query)
# Output:
# MATCH (p:Person)
# WHERE p.age > $min_age
# RETURN p.name, p.age
# ORDER BY p.age
# LIMIT 10
```

### Complex Patterns

```python
# Basic relationship pattern
query = (
    match(
        node("p", "Person")
        .relates_to(">", "KNOWS", node("f", "Person"))
    )
    .return_("p.name", "f.name")
    .to_cypher()
)

# Label expressions and quantified paths
query = (
    match(
        node("p", L("Person") & L("Employee"))
        .relates_to("r", "KNOWS*1..5", ">", node("f", "Person"))
    )
    .where(prop("p", "department").equals("Engineering"))
    .return_("p.name", "f.name")
    .to_cypher()
)
```

## Why super-sniffle?

### Before (String Concatenation)
```python
# Error-prone and hard to maintain
def build_person_query(min_age, city_name):
    return f"""
    MATCH (p:Person)-[:KNOWS]->(f:Person)-[:LIVES_IN]->(c:City)
    WHERE p.age > {min_age} AND c.name = '{city_name}'
    RETURN p.name, f.name, c.name
    """
```

### After (super-sniffle)
```python
# Type-safe and composable
def build_person_query():
    return (
        match(
            node("Person", variable="p")
            .relates_to("r1", "KNOWS", ">", node("Person", variable="f"))
            .relates_to("r2", "LIVES_IN", ">", node("City", variable="c"))
        )
        .where(
            prop("p", "age").gt(param("min_age"))
            .and_(prop("c", "name").equals(param("city_name")))
        )
        .return_("p.name", "f.name", "c.name")
    )
```

## Development Status

super-sniffle is currently in active development. We've implemented all basic Cypher READ clauses and have comprehensive test coverage.

### Current Progress
- ✅ Project structure and configuration
- ✅ Architecture design and documentation
- ✅ Core AST components
- ✅ Basic query clauses (MATCH, WHERE, RETURN, WITH, ORDER BY, LIMIT, SKIP, UNION)
- ✅ String generation
- ✅ Advanced Cypher features:
  - Quantified path patterns with *, +, and {min,max} quantifiers
  - Label expressions for complex node matching
  - Automatic implicit relationship insertion
- ✅ Documentation and examples
- ✅ Comprehensive test coverage (100% pass rate)

## Scope

### Supported Features (Planned)
- READ queries only (MATCH, WHERE, RETURN, etc.)
- All major Cypher READ operations and patterns
- Complex patterns including quantified path patterns
- CALL() clauses for procedures
- APOC function calls (read-only subset)
- Query composition and optimization

### Not Supported
- Query execution (use Neo4j drivers for that)
- Write operations (CREATE, MERGE, DELETE, etc.)
- Administrative commands
- Database management features
- Multiple relationship types per relationship (now enforces single type per Cypher specification)

## Contributing

We welcome contributions! Please see our development guidelines:

1. Install development dependencies: `poetry install`
2. Set up pre-commit hooks: `poetry run pre-commit install`
3. Run tests: `poetry run pytest`
4. Run type checking: `poetry run mypy src tests`
5. Format code: `poetry run black . && poetry run isort .`

## Requirements

- Python 3.8+
- No runtime dependencies (development dependencies listed in `pyproject.toml`)

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- **GitHub**: https://github.com/oldsspecial/super-sniffle
- **Documentation**: https://super-sniffle.readthedocs.io (coming soon)
- **PyPI**: https://pypi.org/project/super-sniffle/ (coming soon)
- **Issues**: https://github.com/oldsspecial/super-sniffle/issues

---

*super-sniffle is not affiliated with Neo4j, Inc. Neo4j is a trademark of Neo4j, Inc.*
