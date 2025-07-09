"""
LIMIT clause implementation for Cypher queries.

This module contains the LimitClause class that represents LIMIT clauses
in Cypher queries and supports method chaining with other clauses.
"""

from dataclasses import dataclass, replace
from typing import Optional, Union

from .match import Clause


@dataclass(frozen=True)
class LimitClause(Clause):
    """
    Represents a LIMIT clause in a Cypher query.
    
    The LIMIT clause restricts the number of results returned by the query.
    
    Attributes:
        count: Maximum number of results to return
        preceding_clause: Optional clause that comes before this LIMIT clause
        next_clause: Optional next clause in the query chain
    """
    count: Union[int, str]
    preceding_clause: Optional[Clause] = None
    next_clause: Optional[Clause] = None
    
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
            ...     .limit(10)
            ...     .skip(5)
            ... )
            >>> # Generates:
            >>> # MATCH (p:Person)
            >>> # RETURN p.name, p.age
            >>> # LIMIT 10
            >>> # SKIP 5
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
            ...     .limit(10)
            ...     .return_("p.name", "p.age")
            ... )
            >>> # Generates:
            >>> # MATCH (p:Person)
            >>> # LIMIT 10
            >>> # RETURN p.name, p.age
        """
        from .return_ import ReturnClause
        
        # Handle the case of returning everything
        if not projections or (len(projections) == 1 and projections[0] == "*"):
            projections = ["*"]
        
        return_clause = ReturnClause(list(projections), distinct)
        
        # Chain the return clause
        return replace(self, next_clause=return_clause)
    
    def with_next(self, next_clause: Clause) -> 'LimitClause':
        """
        Set the next clause in the query.
        
        This is an internal method used for chaining clauses together.
        
        Args:
            next_clause: The next clause to execute
            
        Returns:
            A new LimitClause with the specified next clause
        """
        return replace(self, next_clause=next_clause)
    
    def to_cypher(self) -> str:
        """
        Convert the LIMIT clause to a Cypher string.
        
        Returns:
            Cypher representation of the LIMIT clause and any chained clauses
            
        Example:
            >>> limit_clause = LimitClause(10)
            >>> limit_clause.to_cypher()
            >>> # Returns: "LIMIT 10"
        """
        result = ""
        
        # Add preceding clause if there is one
        if self.preceding_clause:
            # Create a clean version without next_clause to avoid duplication
            clean_preceding = replace(self.preceding_clause, next_clause=None)
            result += f"{clean_preceding.to_cypher()}\n"
        
        # Add LIMIT clause
        result += f"LIMIT {self.count}"
        
        # Add next clause if there is one
        if self.next_clause:
            result += f"\n{self.next_clause.to_cypher()}"
            
        return result
