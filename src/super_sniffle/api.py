"""
Public API for super-sniffle.

This module contains the main functions that users will interact with to
construct Cypher queries. It provides a functional interface for building
query components and assembling them into complete queries.
"""

from typing import Any, Dict, List, Optional, Union

# Import expression and pattern classes
from .ast import Property, Parameter, Literal, NodePattern, RelationshipPattern, PathPattern

# TODO: Import from clause modules when implemented
# from .clauses import MatchClause, WhereClause, ReturnClause


def match(*patterns: Union[NodePattern, RelationshipPattern, PathPattern]):
    """
    Create a MATCH clause with the given patterns.
    
    Args:
        *patterns: Pattern objects to match against
        
    Returns:
        A MatchClause object that can be chained with other clauses
        
    Example:
        >>> query = match(node("p", "Person")).where(prop("p", "age") > 30)
    """
    from .clauses.match import MatchClause
    return MatchClause(list(patterns))


def node(variable: str, *labels: str, **properties: Any) -> NodePattern:
    """
    Create a node pattern.
    
    Args:
        variable: Variable name for the node
        *labels: Node labels
        **properties: Node properties
        
    Returns:
        A NodePattern object representing the node pattern
        
    Example:
        >>> person = node("p", "Person", age=30, name="Alice")
        >>> # With inline condition:
        >>> adult = node("p", "Person").where(prop("p", "age") > 18)
    """
    return NodePattern(variable, labels, properties)


def relationship(direction: str = "-", variable: Optional[str] = None, 
                *types: str, **properties: Any) -> RelationshipPattern:
    """
    Create a relationship pattern.
    
    Args:
        direction: Relationship direction ("<", ">", or "-" for undirected)
        variable: Optional variable name for the relationship
        *types: Relationship types
        **properties: Relationship properties
        
    Returns:
        A RelationshipPattern object representing the relationship pattern
        
    Example:
        >>> knows = relationship(">", "r", "KNOWS", since=2020)
        >>> # With inline condition:
        >>> recent = relationship(">", "r", "KNOWS").where(prop("r", "since") > 2022)
    """
    return RelationshipPattern(direction, variable, types, properties)


def path(*elements: Union[NodePattern, RelationshipPattern]) -> PathPattern:
    """
    Create a path pattern from nodes and relationships.
    
    Args:
        *elements: Alternating NodePattern and RelationshipPattern objects
        
    Returns:
        A PathPattern object representing the path pattern
        
    Example:
        >>> friends = path(
        ...     node("p1", "Person"),
        ...     relationship(">", "r", "KNOWS"),
        ...     node("p2", "Person")
        ... )
        >>> # With inline conditions:
        >>> active_friends = path(
        ...     node("p1", "Person").where(prop("p1", "active") == True),
        ...     relationship(">", "r", "KNOWS").where(prop("r", "since") > 2020),
        ...     node("p2", "Person")
        ... )
    """
    return PathPattern(list(elements))


def prop(variable: str, property_name: str) -> Property:
    """
    Create a property reference.
    
    Args:
        variable: Variable name
        property_name: Property name
        
    Returns:
        A Property object representing the property reference
        
    Example:
        >>> age_prop = prop("p", "age")
        >>> # Can now use operators: age_prop > 30
    """
    return Property(variable, property_name)


def param(name: str) -> Parameter:
    """
    Create a parameter reference.
    
    Args:
        name: Parameter name
        
    Returns:
        A Parameter object representing the parameter reference
        
    Example:
        >>> age_param = param("min_age")
        >>> # Use in comparisons: prop("p", "age") > age_param
    """
    return Parameter(name)


def literal(value: Any) -> Literal:
    """
    Create a literal value.
    
    Args:
        value: The literal value (string, number, boolean, etc.)
        
    Returns:
        A Literal object representing the literal value
        
    Example:
        >>> name_literal = literal("Alice")
        >>> age_literal = literal(30)
        >>> # Use in comparisons: prop("p", "name") == name_literal
    """
    return Literal(value)
