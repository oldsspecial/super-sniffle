# Public API for super-sniffle.

# This module contains the main functions that users will interact with to
# construct Cypher queries. It provides a functional interface for building
# query components and assembling them into complete queries.


from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, field

# Import expression and pattern classes
from .ast.expressions import Expression, OrderByExpression, Property, Variable, Parameter, Literal, FunctionExpression
from .ast.patterns import NodePattern, RelationshipPattern, PathPattern, QuantifiedPathPattern, BaseLabelExpr, L, LabelAtom
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
        
    def group_by(self, *expressions: str) -> 'QueryBuilder':
        """
        Add a GROUP BY clause to the query.
        
        Args:
            *expressions: Expressions to group by
            
        Returns:
            QueryBuilder object with the GROUP BY clause added
            
        Example:
            >>> query = match(node("p", "Person")).return_("p.department", count().as_("employees")).group_by("p.department")
        """
        from .clauses.group_by import GroupByClause
        return QueryBuilder(self.clauses + [GroupByClause(list(expressions))])

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


def node(*labels: Union[str, BaseLabelExpr], variable: Optional[str] = None, **properties: Any) -> NodePattern:
    """
    Create a node pattern with optional variable, labels or expressions, and properties.
    
    Args:
        *labels: Node labels (strings) or label expressions (using L() helper)
        variable: Optional variable name for the node
        **properties: Node properties
        
    Returns:
        A NodePattern object representing the node pattern
        
    Example:
        # Simple node with variable and label
        >>> person = node("Person", variable="p", age=30, name="Alice")
        
        # Node with complex label expression
        >>> admin = node(L("Person") & L("Admin"), variable="a")
        
        # Node without variable
        >>> anonymous = node("User")
        
        # With inline condition:
        >>> adult = node("Person", variable="p").where(prop("p", "age") > 18)
    """
    # Convert simple string labels to label atoms
    processed_labels = []
    for label in labels:
        if isinstance(label, str):
            processed_labels.append(LabelAtom(label))
        else:
            processed_labels.append(label)
    
    return NodePattern(variable=variable, labels=tuple(processed_labels), properties=properties)


def relationship(
    *types: str,
    direction: str = "-",
    variable: Optional[str] = None,
    **properties: Any,
) -> RelationshipPattern:
    """Create a relationship pattern with support for multiple types.

    Args:
        *types: One or more relationship types (will be OR'ed together with |)
        direction: The relationship direction ("-", "->", or "<-")
        variable: The variable name for the relationship (optional)
        properties: Key-value pairs for properties (optional)

    Returns:
        A RelationshipPattern instance

    Example:
        # Single type
        >>> knows = relationship("KNOWS", direction=">", variable="r", since=2020)
        # Multiple types (KNOWS|LIKES)
        >>> knows_or_likes = relationship("KNOWS", "LIKES", direction=">", variable="r")
    """
    # Map direction to RelationshipPattern's internal representation
    if direction in ("->", ">"):
        direction = ">"
    elif direction in ("<-", "<"):
        direction = "<"
    elif direction not in ("-", "--"):
        direction = "-"
    else:
        # Already in correct format
        pass

    # Join the types with | for Cypher OR syntax
    type_str = "|".join(types) if types else ""

    return RelationshipPattern(
        direction=direction,
        variable=variable,
        type=type_str,
        properties=properties,
    )


def path(*elements: Union[NodePattern, RelationshipPattern, PathPattern]) -> PathPattern:
    """
    Create a path pattern from nodes, relationships, or existing paths.
    
    Args:
        *elements: Alternating NodePattern, RelationshipPattern, or PathPattern objects.
                   PathPattern objects will be flattened into their elements.
        
    Returns:
        A PathPattern object representing the combined path pattern
        
    Example:
        >>> base_path = path(node("a"), relationship(">", "r"), node("b"))
        >>> extended_path = path(base_path, node("c"))
        >>> # Results in: (a)-[r]->(b)--(c)
    """
    flattened = []
    for elem in elements:
        if isinstance(elem, PathPattern):
            flattened.extend(elem.elements)
        else:
            flattened.append(elem)
    return PathPattern(flattened)


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


# Aggregation functions
def count(expression: Optional[Expression] = None, distinct: bool = False) -> FunctionExpression:
    """
    Create a count function expression.
    
    Args:
        expression: Optional expression to count (if None, counts all records)
        distinct: Whether to count distinct values
        
    Returns:
        A FunctionExpression representing the count function
        
    Example:
        >>> count()  # Returns: count(*)
        >>> count(prop("p", "name"), distinct=True)  # Returns: count(DISTINCT p.name)
    """
    args = [expression] if expression is not None else []
    return FunctionExpression("count", args, distinct)


def sum(expression: Expression, distinct: bool = False) -> FunctionExpression:
    """
    Create a sum function expression.
    
    Args:
        expression: Expression to sum
        distinct: Whether to sum distinct values
        
    Returns:
        A FunctionExpression representing the sum function
        
    Example:
        >>> sum(prop("p", "age"))  # Returns: sum(p.age)
    """
    return FunctionExpression("sum", [expression], distinct)


def avg(expression: Expression, distinct: bool = False) -> FunctionExpression:
    """
    Create an average function expression.
    
    Args:
        expression: Expression to average
        distinct: Whether to average distinct values
        
    Returns:
        A FunctionExpression representing the avg function
        
    Example:
        >>> avg(prop("p", "age"))  # Returns: avg(p.age)
    """
    return FunctionExpression("avg", [expression], distinct)


def min(expression: Expression) -> FunctionExpression:
    """
    Create a min function expression.
    
    Args:
        expression: Expression to find the minimum of
        
    Returns:
        A FunctionExpression representing the min function
        
    Example:
        >>> min(prop("p", "age"))  # Returns: min(p.age)
    """
    return FunctionExpression("min", [expression])


def max(expression: Expression) -> FunctionExpression:
    """
    Create a max function expression.
    
    Args:
        expression: Expression to find the maximum of
        
    Returns:
        A FunctionExpression representing the max function
        
    Example:
        >>> max(prop("p", "age"))  # Returns: max(p.age)
    """
    return FunctionExpression("max", [expression])
