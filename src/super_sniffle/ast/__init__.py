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
    Variable,
    Parameter,
    Literal,
    FunctionExpression,
    OrderByExpression,
)

# Import pattern classes
from .patterns import (
    NodePattern,
    RelationshipPattern,
    PathPattern,
    QuantifiedPathPattern,
    L,
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
    "Variable",
    "Parameter",
    "Literal",
    "FunctionExpression",
    "OrderByExpression",
    # Pattern classes
    "NodePattern",
    "RelationshipPattern",
    "PathPattern",
    "QuantifiedPathPattern",
    "L",
    # TODO: Add other classes when implemented
    # "Clause",
    # "MatchClause",
    # "WhereClause", 
    # "ReturnClause",
]
