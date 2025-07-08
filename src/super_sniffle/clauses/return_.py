"""
RETURN clause implementation for Cypher queries.

This module contains the ReturnClause class that represents RETURN clauses
in Cypher queries and supports method chaining with other clauses.
"""

from dataclasses import dataclass, replace
from typing import List, Optional, Union

from .match import Clause


@dataclass(frozen=True)
class ReturnClause(Clause):
    """
    Represents a RETURN clause in a Cypher query.
    
    The RETURN clause specifies what data should be returned from the query,
    such as node properties, relationships, or computed values.
    
    Attributes:
        projections: List of strings representing what to return
        distinct: Whether to return only distinct results
        next_clause: Optional next clause in the query chain
    """
    projections: List[str]
    distinct: bool = False
    next_clause: Optional[Clause] = None
    
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
            ...     .return_("p.name", "p.age")
            ...     .order_by("p.age DESC", "p.name")
            ... )
            >>> # Generates:
            >>> # MATCH (p:Person)
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
            ...     .return_("p.name")
            ...     .limit(10)
            ... )
            >>> # Generates:
            >>> # MATCH (p:Person)
            >>> # RETURN p.name
            >>> # LIMIT 10
        """
        # TODO: Implement LimitClause when needed
        raise NotImplementedError("LIMIT clause will be implemented in upcoming releases")
    
    def skip(self, count: Union[int, str]):
        """
        Add a SKIP clause to skip a number of results.
        
        The SKIP clause skips a specified number of results before returning
        the remaining ones. Often used with LIMIT for pagination.
        
        Args:
            count: Number of results to skip
            
        Returns:
            A new SkipClause instance (when implemented)
            
        Example:
            >>> query = (
            ...     match(node("p", "Person"))
            ...     .return_("p.name")
            ...     .skip(10)
            ...     .limit(5)
            ... )
            >>> # Generates:
            >>> # MATCH (p:Person)
            >>> # RETURN p.name
            >>> # SKIP 10
            >>> # LIMIT 5
        """
        # TODO: Implement SkipClause when needed
        raise NotImplementedError("SKIP clause will be implemented in upcoming releases")
    
    def with_next(self, next_clause: Clause) -> 'ReturnClause':
        """
        Set the next clause in the query.
        
        This is an internal method used for chaining clauses together.
        
        Args:
            next_clause: The next clause to execute
            
        Returns:
            A new ReturnClause with the specified next clause
        """
        return replace(self, next_clause=next_clause)
    
    def to_cypher(self) -> str:
        """
        Convert the RETURN clause to a Cypher string.
        
        Returns:
            Cypher representation of the RETURN clause and any chained clauses
            
        Example:
            >>> return_clause = ReturnClause(["p.name", "p.age"])
            >>> return_clause.to_cypher()
            >>> # Returns: "RETURN p.name, p.age"
            
            >>> return_clause = ReturnClause(["*"], distinct=True)
            >>> return_clause.to_cypher()
            >>> # Returns: "RETURN DISTINCT *"
        """
        distinct_str = "DISTINCT " if self.distinct else ""
        projections_str = ", ".join(self.projections)
        result = f"RETURN {distinct_str}{projections_str}"
        
        # Add the next clause if there is one
        if self.next_clause:
            result += f"\n{self.next_clause.to_cypher()}"
            
        return result
