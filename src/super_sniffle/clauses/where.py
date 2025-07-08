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
        preceding_clause: Optional clause that comes before this WHERE clause
        next_clause: Optional next clause in the query chain
    """
    condition: Expression
    preceding_clause: Optional[Clause] = None
    next_clause: Optional[Clause] = None
    
    def with_(self, *projections: str, distinct: bool = False):
        """
        Add a WITH clause to pipe results to subsequent query parts.
        
        The WITH clause allows query parts to be chained together, piping the results
        from one to be used as starting points or criteria in the next.
        
        Args:
            *projections: Strings representing what to pass forward
            distinct: Whether to return only distinct results
            
        Returns:
            A new WithClause instance
            
        Example:
            >>> query = (
            ...     match(node("p", "Person"))
            ...     .where(prop("p", "age") > 30)
            ...     .with_("p.name AS name", "p.age AS age")
            ... )
            >>> # Generates:
            >>> # MATCH (p:Person)
            >>> # WHERE p.age > 30
            >>> # WITH p.name AS name, p.age AS age
        """
        # Import WithClause here to avoid circular imports
        from .with_ import WithClause
        
        # Return the WithClause with this WhereClause as its preceding clause
        return WithClause(list(projections), distinct, preceding_clause=self, next_clause=self.next_clause)
    
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
            ...     .where(prop("p", "age") > 30)
            ...     .return_("p.name", "p.age")
            ... )
            >>> # Generates:
            >>> # MATCH (p:Person)
            >>> # WHERE p.age > 30
            >>> # RETURN p.name, p.age
            
            >>> query = (
            ...     match(node("p", "Person"))
            ...     .where(prop("p", "age") > 30)
            ...     .return_()
            ... )
            >>> # Generates:
            >>> # MATCH (p:Person)
            >>> # WHERE p.age > 30
            >>> # RETURN *
        """
        # Import ReturnClause here to avoid circular imports
        from .return_ import ReturnClause
        
        # Handle the case of returning everything
        if not projections or (len(projections) == 1 and projections[0] == "*"):
            projections = ["*"]
        
        return_clause = ReturnClause(list(projections), distinct)
        
        # If this clause has a next clause, chain the return before it
        if self.next_clause:
            return replace(self, next_clause=return_clause.with_next(self.next_clause))
        
        # Otherwise, chain the return directly
        return replace(self, next_clause=return_clause)
    
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
        result = ""
        
        # Add all preceding clauses (including chained MATCH clauses)
        if self.preceding_clause:
            # We need to render the full chain of preceding clauses
            result += self._render_preceding_clauses() + "\n"
        
        # Add this WHERE clause
        result += f"WHERE {self.condition.to_cypher()}"
        
        # Add the next clause if there is one
        if self.next_clause:
            result += f"\n{self.next_clause.to_cypher()}"
            
        return result
    
    def _render_preceding_clauses(self) -> str:
        """
        Render all preceding clauses in the correct order.
        
        This handles the case where there are multiple MATCH clauses
        that should all come before the WHERE clause.
        """
        if not self.preceding_clause:
            return ""
        
        # Start with the preceding clause
        current = self.preceding_clause
        clauses = []
        
        # Collect all clauses in the chain
        while current:
            clauses.append(current)
            next_clause = getattr(current, 'next_clause', None) if hasattr(current, 'next_clause') else None
            
            # If the next clause is the same type as current (e.g., another MatchClause), 
            # include it in the preceding clauses
            if next_clause and type(next_clause) == type(current):
                current = next_clause
            else:
                break
        
        # Render each clause without its next_clause to avoid duplication
        result_parts = []
        for clause in clauses:
            if hasattr(clause, 'next_clause'):
                from dataclasses import replace
                clean_clause = replace(clause, next_clause=None)
                result_parts.append(clean_clause.to_cypher())
            else:
                result_parts.append(clause.to_cypher())
        
        return "\n".join(result_parts)
