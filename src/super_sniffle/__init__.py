"""
super-sniffle: A Functional Cypher Query Builder for Neo4j

A Python library for building Neo4j Cypher queries in a functional and composable way.
It provides an intuitive API for constructing complex graph queries with type safety
and proper escaping.

Example:
    >>> from super_sniffle import node, prop, param, match
    >>> 
    >>> # Build a query to find friends
    >>> query = match(
    ...     node("p", "Person").relates_to(">", "KNOWS", "r", node("f", "Person"))
    ... ).where(
    ...     (prop("p", "age") > param("min_age")) & 
    ...     (prop("f", "city") == param("city"))
    ... )
    >>> 
    >>> print(query.to_cypher())
    >>> # MATCH (p:Person)-[r:KNOWS]->(f:Person)
    >>> # WHERE p.age > $min_age AND f.city = $city
"""

__version__ = "0.1.0"
__author__ = "super-sniffle contributors"

# Main API exports
from .api import (
    prop,
    var,
    param, 
    literal,
    node,
    relationship,
    path,
    match,
    asc,
    desc,
)

# AST components (for advanced usage)
from .ast import (
    Property,
    Parameter, 
    Literal,
    NodePattern,
    RelationshipPattern,
    PathPattern,
)

# Clause components (for advanced usage) 
from .clauses import (
    MatchClause,
)

__all__ = [
    # Core functions
    "prop",
    "var",
    "param",
    "literal", 
    "node",
    "relationship",
    "path",
    "match",
    "asc",
    "desc",
    
    # AST classes
    "Property",
    "Parameter",
    "Literal",
    "NodePattern", 
    "RelationshipPattern",
    "PathPattern",
    
    # Clause classes
    "MatchClause",
]
