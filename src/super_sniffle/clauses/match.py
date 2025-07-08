"""
MATCH clause implementation for Cypher queries.

This module contains the MatchClause class that represents MATCH clauses
in Cypher queries and supports method chaining with other clauses.
"""

from dataclasses import dataclass, field, replace
from typing import List, Optional, Union, Any

from ..ast.patterns import NodePattern, RelationshipPattern, PathPattern
from ..ast.expressions import Expression


@dataclass(frozen=True)
class Clause:
    """Base class for all Cypher clauses."""
    
    def to_cypher(self) -> str:
        """Convert clause to Cypher string."""
        raise NotImplementedError("Subclasses must implement to_cypher()")


@dataclass(frozen=True)
class MatchClause(Clause):
    """
    Represents a MATCH clause in a Cypher query.
    
    The MATCH clause is used to specify the patterns to search for in the
    graph database. It can be chained with other clauses to form complete
    queries.
    
    Attributes:
        patterns: List of patterns to match (nodes, relationships, or paths)
        next_clause: Optional next clause in the query chain
    """
    patterns: List[Union[NodePattern, RelationshipPattern, PathPattern]]
    next_clause: Optional[Clause] = None
    
    def match(self, *patterns: Union[NodePattern, RelationshipPattern, PathPattern]) -> 'MatchClause':
        """
        Add another MATCH clause to the query.
        
        This allows building queries with multiple MATCH clauses, which is
        useful for complex graph patterns that need to be matched separately.
        
        Args:
            *patterns: Patterns to match in the new MATCH clause
            
        Returns:
            A new MatchClause instance with the additional MATCH clause
            
        Example:
            >>> query = (
            ...     match(node("p", "Person"))
            ...     .match(node("c", "Company"))
            ... )
            >>> # Generates: 
            >>> # MATCH (p:Person)
            >>> # MATCH (c:Company)
        """
        # Create a new MatchClause for the additional patterns
        new_match = MatchClause(list(patterns))
        
        # If this clause has a next clause, chain the new match before it
        if self.next_clause:
            return replace(self, next_clause=new_match.with_next(self.next_clause))
        
        # Otherwise, chain the new match directly
        return replace(self, next_clause=new_match)
    
    def where(self, condition: Expression):
        """
        Add a WHERE clause to filter the matched patterns.
        
        The WHERE clause applies conditions to filter the results of the
        MATCH clause based on property values or other criteria.
        
        Args:
            condition: Expression representing the WHERE condition
            
        Returns:
            A new WhereClause instance (when implemented)
            
        Example:
            >>> query = (
            ...     match(node("p", "Person"))
            ...     .where(prop("p", "age") > 30)
            ... )
            >>> # Generates:
            >>> # MATCH (p:Person)
            >>> # WHERE p.age > 30
        """
        # TODO: Implement WhereClause when needed
        raise NotImplementedError("WHERE clause will be implemented in upcoming releases")
    
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
            ...     .return_("p.name", "p.age")
            ... )
            >>> # Generates:
            >>> # MATCH (p:Person)
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
    
    def with_next(self, next_clause: Clause) -> 'MatchClause':
        """
        Set the next clause in the query.
        
        This is an internal method used for chaining clauses together.
        
        Args:
            next_clause: The next clause to execute
            
        Returns:
            A new MatchClause with the specified next clause
        """
        return replace(self, next_clause=next_clause)
    
    def to_cypher(self) -> str:
        """
        Convert the MATCH clause to a Cypher string.
        
        Returns:
            Cypher representation of the MATCH clause and any chained clauses
            
        Example:
            >>> match(node("p", "Person")).to_cypher()
            >>> # Returns: "MATCH (p:Person)"
        """
        # Join patterns with commas
        patterns_str = ", ".join(p.to_cypher() for p in self.patterns)
        result = f"MATCH {patterns_str}"
        
        # Add the next clause if there is one
        if self.next_clause:
            result += f"\n{self.next_clause.to_cypher()}"
            
        return result
