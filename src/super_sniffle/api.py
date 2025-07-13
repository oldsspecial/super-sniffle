# Public API for super-sniffle.

# This module contains the main functions that users will interact with to
# construct Cypher queries. It provides a functional interface for building
# query components and assembling them into complete queries.


from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, field

# Import expression and pattern classes
from .ast.expressions import Expression, OrderByExpression, Property, Variable, Parameter, Literal
from .ast.patterns import NodePattern, RelationshipPattern, PathPattern, QuantifiedPathPattern
from .clauses.clause import Clause
from .compound_query import CompoundQuery
from .clauses.match import MatchClause


@dataclass(frozen=True)
class QueryBuilder:
    """
    A builder for constructing Cypher queries in a fluent, chainable manner.
    """
    clauses: List[Clause] = field(default_factory=list)

    def match(self, *patterns: Union[NodePattern, RelationshipPattern, PathPattern, QuantifiedPathPattern]) -> 'QueryBuilder':
        from .clauses.match import MatchClause
        return QueryBuilder(self.clauses + [MatchClause(list(patterns))])

    def where(self, condition: Expression) -> 'QueryBuilder':
        from .clauses.where import WhereClause
        return QueryBuilder(self.clauses + [WhereClause(condition)])

    def with_(self, *projections: Union[str, Tuple[str, str]], distinct: bool = False) -> 'QueryBuilder':
        from .clauses.with_ import WithClause
        return QueryBuilder(self.clauses + [WithClause(list(projections), distinct)])

    def return_(self, *projections: str, distinct: bool = False) -> 'QueryBuilder':
        from .clauses.return_ import ReturnClause
        projections_list = list(projections)
        if not projections_list or (len(projections_list) == 1 and projections_list[0] == "*"):
            projections_list = ["*"]
        return QueryBuilder(self.clauses + [ReturnClause(projections_list, distinct)])

    def order_by(self, *fields: Union[str, OrderByExpression]) -> 'QueryBuilder':
        from .clauses.order_by import OrderByClause
        from .ast.expressions import OrderByExpression as OrderByExpr
        expressions: List[Union[str, OrderByExpression]] = [OrderByExpr(field) if isinstance(field, str) else field for field in fields]
        return QueryBuilder(self.clauses + [OrderByClause(expressions)])

    def skip(self, count: Union[int, str]) -> 'QueryBuilder':
        from .clauses.skip import SkipClause
        # Remove existing skip clauses to ensure the last one takes precedence
        new_clauses = [c for c in self.clauses if not isinstance(c, SkipClause)]
        return QueryBuilder(new_clauses + [SkipClause(count)])

    def limit(self, count: Union[int, str]) -> 'QueryBuilder':
        from .clauses.limit import LimitClause
        # Remove existing limit clauses to ensure the last one takes precedence
        new_clauses = [c for c in self.clauses if not isinstance(c, LimitClause)]
        return QueryBuilder(new_clauses + [LimitClause(count)])

    def union(self, other: "QueryBuilder") -> "CompoundQuery":
        """
        Combines this query with another using UNION.
        """
        return CompoundQuery(queries=[self, other], union_operators=["UNION"])

    def union_all(self, other: "QueryBuilder") -> "CompoundQuery":
        """
        Combines this query with another using UNION ALL.
        """
        return CompoundQuery(queries=[self, other], union_operators=["UNION ALL"])

    def to_cypher(self) -> str:
        """
        Converts the constructed query to a Cypher string.
        """
        from .clauses.return_ import ReturnClause
        from .clauses.with_ import WithClause
        from .clauses.limit import LimitClause
        from .clauses.skip import SkipClause
        from .clauses.order_by import OrderByClause

        # Separate pagination clauses from the rest
        pagination_clauses = []
        other_clauses = []
        for c in self.clauses:
            if isinstance(c, (OrderByClause, SkipClause, LimitClause)):
                pagination_clauses.append(c)
            else:
                other_clauses.append(c)

        # Define the correct order for pagination clauses
        pagination_order = {
            "OrderByClause": 0,
            "SkipClause": 1,
            "LimitClause": 2,
        }

        # Sort the pagination clauses
        sorted_pagination_clauses = sorted(
            pagination_clauses,
            key=lambda c: pagination_order.get(c.__class__.__name__, 99)
        )

        # A special case for queries that end with LIMIT/SKIP without a RETURN or WITH.
        # A RETURN * should be implicitly added.
        if sorted_pagination_clauses and not any(isinstance(c, (ReturnClause, WithClause)) for c in other_clauses):
            other_clauses.append(ReturnClause(["*"]))

        all_clauses = other_clauses + sorted_pagination_clauses
        return "\n".join(c.to_cypher() for c in all_clauses)


def match(*patterns: Union[NodePattern, RelationshipPattern, PathPattern, QuantifiedPathPattern]) -> QueryBuilder:
    """
    Create a MATCH clause with the given patterns.
    
    Args:
        *patterns: Pattern objects to match against
        
    Returns:
        A QueryBuilder object that can be chained with other clauses
        
    Example:
        >>> query = match(node("p", "Person")).where(prop("p", "age") > 30)
    """
    return QueryBuilder([MatchClause(list(patterns))])


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


def var(name: str) -> Variable:
    """
    Create a variable reference.
    
    Args:
        name: Variable name
        
    Returns:
        A Variable object representing the variable reference
        
    Example:
        >>> count_var = var("friendCount")
        >>> # Can now use operators: count_var > 5
        >>> # Use in WHERE clauses after WITH: .where(var("friendCount") > literal(3))
    """
    return Variable(name)


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


def asc(field: str) -> OrderByExpression:
    """
    Create an ascending sort expression for ORDER BY clauses.
    
    Args:
        field: Field name to sort by in ascending order
        
    Returns:
        An OrderByExpression object for ascending sort
        
    Example:
        >>> age_asc = asc("p.age")
        >>> # Use in ORDER BY: .order_by(asc("p.age"), desc("p.name"))
    """
    return OrderByExpression(field, False)


def desc(field: str) -> OrderByExpression:
    """
    Create a descending sort expression for ORDER BY clauses.
    
    Args:
        field: Field name to sort by in descending order
        
    Returns:
        An OrderByExpression object for descending sort
        
    Example:
        >>> age_desc = desc("p.age")
        >>> # Use in ORDER BY: .order_by(asc("p.name"), desc("p.age"))
    """
    return OrderByExpression(field, True)
