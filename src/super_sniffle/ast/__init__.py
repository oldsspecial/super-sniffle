"""
AST (Abstract Syntax Tree) dataclasses for representing Cypher query structure.

This module contains the dataclass definitions that form the abstract syntax
tree representation of Cypher queries. These classes provide the structural
foundation for query construction and manipulation.
"""

# Import expression classes
from .expressions import (
    Expression,
    ComparisonExpression,
    LogicalExpression,
    NotExpression,
    Property,
    Parameter,
    Literal,
)

# Import pattern classes
from .patterns import (
    NodePattern,
    RelationshipPattern,
    PathPattern,
    simple_node_pattern,
    simple_relationship_pattern,
    simple_path,
)

# TODO: Import other AST classes when implemented
# from .clauses import Clause, MatchClause, WhereClause, ReturnClause

__all__ = [
    # Expression classes
    "Expression",
    "ComparisonExpression",
    "LogicalExpression",
    "NotExpression",
    "Property",
    "Parameter",
    "Literal",
    # Pattern classes
    "NodePattern",
    "RelationshipPattern",
    "PathPattern",
    "simple_node_pattern",
    "simple_relationship_pattern",
    "simple_path",
    # TODO: Add other classes when implemented
    # "Clause",
    # "MatchClause",
    # "WhereClause", 
    # "ReturnClause",
]
