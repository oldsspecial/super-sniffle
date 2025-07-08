"""
WHERE clause implementation for Cypher queries.

This module contains the WhereClause class that represents WHERE clauses
in Cypher queries and supports method chaining with other clauses.
"""

from dataclasses import dataclass, replace
from typing import Optional, Union

from ..ast.expressions import Expression
from .match import Clause


@dataclass(frozen=True)
class WhereClause(Clause):
    """
    Represents a WHERE clause in a Cypher query.
    
    The WHERE clause filters the results of previous clauses based on conditions.
    It can be chained with other clauses to form complete queries.
    
    Attributes:
        condition: Expression representing the WHERE condition
        next_clause: Optional next clause in the query chain
    """
    condition: Expression
    next_clause: Optional[Clause] = None
    
    def return_(self, *projections: str):
        """
        Add a RETURN clause to specify what to return from the query.
        
        The RETURN clause defines what data should be returned from the query,
        such as node properties, relationships, or computed values.
        
        Args:
            *projections: Strings representing what to return
            
        Returns:
            A new ReturnClause instance (when implemented)
            
        Example:
            >>> query = (
            ...     match(node("p", "Person"))
            ...     .where(prop("p", "age") > 30)
            ...     .return_("p.name", "p.age")
            ... )
            >>> # Generates:
            >>> # MATCH (p:Person)
            >>> # WHERE p.age > 30
            >>> # RETURN p.name, p.age
        """
        # TODO: Implement ReturnClause when needed
        raise NotImplementedError("RETURN clause will be implemented in upcoming releases")
    
    def order_by(self, *fields: str):
        """
        Add an ORDER BY clause to sort the results.
        
        The ORDER BY clause sorts the query results based on one or more
        fields, with optional ASC/DESC modifiers.
        
        Args:
            *fields: Fields to sort by, with optional ASC/DESC
            
        Returns:
            A new OrderByClause instance (when implemented)
            
        Example:
            >>> query = (
            ...     match(node("p", "Person"))
            ...     .where(prop("p", "age") > 30)
            ...     .return_("p.name", "p.age")
            ...     .order_by("p.age DESC", "p.name")
            ... )
            >>> # Generates:
            >>> # MATCH (p:Person)
            >>> # WHERE p.age > 30
            >>> # RETURN p.name, p.age
            >>> # ORDER BY p.age DESC, p.name
        """
        # TODO: Implement OrderByClause when needed
        raise NotImplementedError("ORDER BY clause will be implemented in upcoming releases")
    
    def limit(self, count: Union[int, str]):
        """
        Add a LIMIT clause to limit the number of results.
        
        The LIMIT clause restricts the number of results returned by the query.
        
        Args:
            count: Maximum number of results to return
            
        Returns:
            A new LimitClause instance (when implemented)
            
        Example:
            >>> query = (
            ...     match(node("p", "Person"))
            ...     .where(prop("p", "age") > 30)
            ...     .return_("p.name")
            ...     .limit(10)
            ... )
            >>> # Generates:
            >>> # MATCH (p:Person)
            >>> # WHERE p.age > 30
            >>> # RETURN p.name
            >>> # LIMIT 10
        """
        # TODO: Implement LimitClause when needed
        raise NotImplementedError("LIMIT clause will be implemented in upcoming releases")
    
    def with_next(self, next_clause: Clause) -> 'WhereClause':
        """
        Set the next clause in the query.
        
        This is an internal method used for chaining clauses together.
        
        Args:
            next_clause: The next clause to execute
            
        Returns:
            A new WhereClause with the specified next clause
        """
        return replace(self, next_clause=next_clause)
    
    def to_cypher(self) -> str:
        """
        Convert the WHERE clause to a Cypher string.
        
        Returns:
            Cypher representation of the WHERE clause and any chained clauses
            
        Example:
            >>> where(prop("p", "age") > 30).to_cypher()
            >>> # Returns: "WHERE p.age > 30"
        """
        result = f"WHERE {self.condition.to_cypher()}"
        
        # Add the next clause if there is one
        if self.next_clause:
            result += f"\n{self.next_clause.to_cypher()}"
            
        return result
