# Technical Context: super-sniffle

## Technology Stack

### Core Technologies
- **Python 3.8+**: Base language, leveraging modern features like dataclasses and type hints
- **Neo4j Cypher 2.5**: Target query language specification
- **Type Annotations**: Comprehensive typing for IDE support and static analysis

### Development Tools
- **Poetry**: Dependency management and packaging
- **pytest**: Testing framework
- **mypy**: Static type checking
- **black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **pre-commit**: Git hooks for quality checks
- **Sphinx**: Documentation generation

### CI/CD
- **GitHub Actions**: Automated testing, linting, and publishing
- **PyPI**: Package distribution
- **Read the Docs**: Documentation hosting

## Development Environment

### Setup Requirements
```bash
# Clone repository
git clone git@github.com:oldsspecial/super-sniffle.git
cd super-sniffle

# Install dependencies with Poetry
poetry install

# Install pre-commit hooks
poetry run pre-commit install
```

### Project Structure
```
super-sniffle/
├── src/
│   └── super_sniffle/
│       ├── __init__.py
│       ├── api.py            # Public API functions
│       ├── ast/              # AST dataclasses
│       ├── components/       # Query components
│       ├── clauses/          # Cypher clause implementations
│       ├── formatters/       # String generation
│       └── utils/            # Helper utilities
├── tests/
│   ├── unit/                 # Unit tests
│   └── integration/          # Integration tests
├── docs/
│   ├── conf.py               # Sphinx configuration
│   └── index.rst             # Documentation root
├── examples/                 # Example usage
├── pyproject.toml            # Project metadata and dependencies
├── README.md                 # Project overview
└── LICENSE                   # License information
```

## Technical Constraints

### Python Version Support
- Minimum supported Python version: 3.8
- Target Python versions: 3.8, 3.9, 3.10, 3.11, 3.12

### Cypher Version Compliance
- Strict adherence to CYPHER25 specification
- No support for Neo4j-specific extensions outside CYPHER25

### Dependencies
- Minimal external dependencies to reduce installation complexity
- Core library should have zero runtime dependencies
- Optional integrations may have specific dependencies

### Performance Considerations
- Efficient AST construction for large queries
- Memory usage optimization for complex query patterns
- String generation performance for large result sets

## Packaging and Distribution

### Package Name
- PyPI package name: `super-sniffle`
- Import name: `super_sniffle`

### Versioning
- Semantic Versioning (SemVer)
- `major.minor.patch` format
- Initial development under 0.x versions

### Installation
```bash
# From PyPI
pip install super-sniffle

# Development installation
pip install -e .
```

## Testing Strategy

### Unit Testing
- Test each component in isolation
- Mock dependencies where appropriate
- High coverage target (>90%)

### Integration Testing
- Test complete query generation
- Verify output against expected Cypher strings
- Test with complex, real-world query patterns

### Property-Based Testing
- Generate random query components
- Verify structural properties of generated queries
- Ensure robustness against edge cases

## Documentation

### API Documentation
- Complete docstrings for all public APIs
- Type annotations for better IDE integration
- Examples in docstrings

### User Guide
- Getting started tutorial
- Common patterns and idioms
- Best practices
- Migration guide from string-based queries

### Examples
- Simple queries
- Complex patterns
- Real-world use cases
- Performance optimization

## Tool Usage Patterns

### Type Checking
```bash
# Run mypy
poetry run mypy src tests
```

### Testing
```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=super_sniffle
```

### Linting and Formatting
```bash
# Format code
poetry run black .
poetry run isort .

# Lint code
poetry run flake8
```

### Documentation Building
```bash
# Generate documentation
cd docs
poetry run make html
```

## IDE Integration

### VSCode
- Recommended extensions:
  - Python
  - Pylance
  - Python Test Explorer
  - Python Docstring Generator
  - autoDocstring

### PyCharm
- Enable type checking mode
- Configure pytest as test runner
- Set up black as formatter
