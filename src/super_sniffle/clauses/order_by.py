"""
ORDER BY clause implementation for Cypher queries.

This module contains the OrderByClause class that represents ORDER BY clauses
in Cypher queries and supports method chaining with other clauses.
"""

from dataclasses import dataclass, replace
from typing import List, Optional, Union

from ..ast.expressions import OrderByExpression
from .match import Clause


@dataclass(frozen=True)
class OrderByClause(Clause):
    """
    Represents an ORDER BY clause in a Cypher query.
    
    The ORDER BY clause sorts the query results based on one or more
    fields, with optional ASC/DESC modifiers.
    
    Attributes:
        expressions: List of OrderByExpression objects defining sort criteria
        preceding_clause: Optional clause that comes before this ORDER BY clause
        next_clause: Optional next clause in the query chain
    """
    expressions: List[Union[str, OrderByExpression]]
    preceding_clause: Optional[Clause] = None
    next_clause: Optional[Clause] = None
    
    def limit(self, count: Union[int, str]):
        """
        Add a LIMIT clause to limit the number of results.
        
        The LIMIT clause restricts the number of results returned by the query.
        
        Args:
            count: Maximum number of results to return
            
        Returns:
            A new LimitClause instance
            
        Example:
            >>> query = (
            ...     match(node("p", "Person"))
            ...     .return_("p.name", "p.age")
            ...     .order_by("p.age")
            ...     .limit(10)
            ... )
            >>> # Generates:
            >>> # MATCH (p:Person)
            >>> # RETURN p.name, p.age
            >>> # ORDER BY p.age
            >>> # LIMIT 10
        """
        from .limit import LimitClause
        return LimitClause(count, preceding_clause=self)
    
    def skip(self, count: Union[int, str]):
        """
        Add a SKIP clause to skip a number of results.
        
        The SKIP clause skips a specified number of results before returning
        the remaining ones. Often used with LIMIT for pagination.
        
        Args:
            count: Number of results to skip
            
        Returns:
            A new SkipClause instance
            
        Example:
            >>> query = (
            ...     match(node("p", "Person"))
            ...     .return_("p.name", "p.age")
            ...     .order_by("p.age")
            ...     .skip(10)
            ...     .limit(5)
            ... )
            >>> # Generates:
            >>> # MATCH (p:Person)
            >>> # RETURN p.name, p.age
            >>> # ORDER BY p.age
            >>> # SKIP 10
            >>> # LIMIT 5
        """
        from .skip import SkipClause
        return SkipClause(count, preceding_clause=self)
    
    def return_(self, *projections: str, distinct: bool = False):
        """
        Add a RETURN clause to specify what to return from the query.
        
        The RETURN clause defines what data should be returned from the query,
        such as node properties, relationships, or computed values.
        
        Args:
            *projections: Strings representing what to return.
                         Use "*" or no arguments to return everything.
            distinct: Whether to return only distinct results
            
        Returns:
            A new ReturnClause instance
            
        Example:
            >>> query = (
            ...     match(node("p", "Person"))
            ...     .order_by("p.age")
            ...     .return_("p.name", "p.age")
            ... )
            >>> # Generates:
            >>> # MATCH (p:Person)
            >>> # ORDER BY p.age
            >>> # RETURN p.name, p.age
        """
        from .return_ import ReturnClause
        
        # Handle the case of returning everything
        if not projections or (len(projections) == 1 and projections[0] == "*"):
            projections = ["*"]
        
        return_clause = ReturnClause(list(projections), distinct)
        
        # Chain the return clause
        return replace(self, next_clause=return_clause)
    
    def with_next(self, next_clause: Clause) -> 'OrderByClause':
        """
        Set the next clause in the query.
        
        This is an internal method used for chaining clauses together.
        
        Args:
            next_clause: The next clause to execute
            
        Returns:
            A new OrderByClause with the specified next clause
        """
        return replace(self, next_clause=next_clause)
    
    def to_cypher(self) -> str:
        """
        Convert the ORDER BY clause to a Cypher string.
        
        Returns:
            Cypher representation of the ORDER BY clause and any chained clauses
            
        Example:
            >>> from super_sniffle.ast.expressions import OrderByExpression
            >>> order_clause = OrderByClause([
            ...     OrderByExpression("p.age", False),
            ...     OrderByExpression("p.name", True)
            ... ])
            >>> order_clause.to_cypher()
            >>> # Returns: "ORDER BY p.age, p.name DESC"
        """
        result = ""
        
        # Add preceding clause if there is one
        if self.preceding_clause:
            # Create a clean version without next_clause to avoid duplication
            clean_preceding = replace(self.preceding_clause, next_clause=None)
            result += f"{clean_preceding.to_cypher()}\n"
        
        # Add ORDER BY clause
        expressions_str = ", ".join(
            expr.to_cypher() if hasattr(expr, 'to_cypher') else str(expr) 
            for expr in self.expressions
        )
        result += f"ORDER BY {expressions_str}"
        
        # Add next clause if there is one
        if self.next_clause:
            result += f"\n{self.next_clause.to_cypher()}"
            
        return result
