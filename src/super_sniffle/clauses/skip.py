"""
SKIP clause implementation for Cypher queries.

This module contains the SkipClause class that represents SKIP clauses
in Cypher queries and supports method chaining with other clauses.
"""

from dataclasses import dataclass, replace
from typing import Optional, Union

from .clause import Clause


@dataclass(frozen=True)
class SkipClause(Clause):
    """
    Represents a SKIP clause in a Cypher query.
    
    The SKIP clause skips a specified number of results before returning
    the remaining ones. Often used with LIMIT for pagination.
    
    Attributes:
        count: Number of results to skip
        preceding_clause: Optional clause that comes before this SKIP clause
        next_clause: Optional next clause in the query chain
    """
    count: Union[int, str]
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
            ...     .skip(5)
            ...     .limit(10)
            ... )
            >>> # Generates:
            >>> # MATCH (p:Person)
            >>> # RETURN p.name, p.age
            >>> # SKIP 5
            >>> # LIMIT 10
        """
        from .limit import LimitClause
        return LimitClause(count, preceding_clause=self)
    
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
            ...     .skip(10)
            ...     .return_("p.name", "p.age")
            ... )
            >>> # Generates:
            >>> # MATCH (p:Person)
            >>> # SKIP 10
            >>> # RETURN p.name, p.age
        """
        from .return_ import ReturnClause
        
        # Handle the case of returning everything
        if not projections or (len(projections) == 1 and projections[0] == "*"):
            projections = ["*"]
        
        return_clause = ReturnClause(list(projections), distinct)
        
        # Chain the return clause
        return replace(self, next_clause=return_clause)
    
    def with_next(self, next_clause: Clause) -> 'SkipClause':
        """
        Set the next clause in the query.
        
        This is an internal method used for chaining clauses together.
        
        Args:
            next_clause: The next clause to execute
            
        Returns:
            A new SkipClause with the specified next clause
        """
        return replace(self, next_clause=next_clause)
    
    def to_cypher(self) -> str:
        """
        Convert the SKIP clause to a Cypher string.
        
        Returns:
            Cypher representation of the SKIP clause and any chained clauses
            
        Example:
            >>> skip_clause = SkipClause(5)
            >>> skip_clause.to_cypher()
            >>> # Returns: "SKIP 5"
        """
        result = ""
        
        # Add preceding clause if there is one
        if self.preceding_clause:
            # Create a clean version without next_clause to avoid duplication
            clean_preceding = replace(self.preceding_clause, next_clause=None)
            result += f"{clean_preceding.to_cypher()}\n"
        
        # Add SKIP clause
        count_str = (
            self.count.to_cypher() if hasattr(self.count, 'to_cypher')
            else str(self.count)
        )
        result += f"SKIP {count_str}"
        
        # Add next clause if there is one
        if self.next_clause:
            result += f"\n{self.next_clause.to_cypher()}"
            
        return result
