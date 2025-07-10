"""
MATCH clause implementation for Cypher queries.

This module contains the MatchClause class that represents MATCH clauses
in Cypher queries and supports method chaining with other clauses.
"""

from dataclasses import dataclass, field, replace
from typing import List, Optional, Union, Any, TYPE_CHECKING, Tuple

from super_sniffle.clauses.clause import Clause

from ..ast.patterns import NodePattern, RelationshipPattern, PathPattern
from ..ast.expressions import Expression

if TYPE_CHECKING:
    from ..ast.expressions import OrderByExpression


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
        new_match = MatchClause(list(patterns), next_clause=self.next_clause)
        
        # Chain this match clause to the new match clause
        return replace(self, next_clause=new_match)
    
    def where(self, condition: Expression):
        """
        Add a WHERE clause to filter the matched patterns.
        
        The WHERE clause applies conditions to filter the results of the
        MATCH clause based on property values or other criteria.
        
        Args:
            condition: Expression representing the WHERE condition
            
        Returns:
            A new WhereClause instance
            
        Example:
            >>> query = (
            ...     match(node("p", "Person"))
            ...     .where(prop("p", "age") > 30)
            ... )
            >>> # Generates:
            >>> # MATCH (p:Person)
            >>> # WHERE p.age > 30
        """
        # Import WhereClause here to avoid circular imports
        from .where import WhereClause
        
        # Collect all consecutive MATCH clauses as the preceding clause
        # This ensures that multiple MATCH clauses are grouped together before WHERE
        full_preceding_match = self._collect_all_match_clauses()
        
        # Find the non-MATCH next clause (if any) after all the MATCH clauses
        non_match_next_clause = self._find_non_match_next_clause()
        
        # Return the WhereClause with all MATCH clauses as its preceding clause
        return WhereClause(condition, preceding_clause=full_preceding_match, next_clause=non_match_next_clause)
    
    def _collect_all_match_clauses(self) -> 'MatchClause':
        """
        Collect all consecutive MATCH clauses into a single chain.
        
        This ensures that when WHERE is added, all MATCH clauses are properly
        grouped together before the WHERE clause.
        """
        # Simply return self - the _render_preceding_clauses method in WhereClause
        # will handle collecting all consecutive MATCH clauses properly
        return self
    
    def _find_non_match_next_clause(self) -> Optional[Clause]:
        """
        Find the first non-MATCH clause in the chain.
        
        This is used to determine what should come after the WHERE clause.
        """
        current = self
        while current and isinstance(current, MatchClause):
            current = current.next_clause
        return current
    
    def with_(self, *projections: Union[str, Tuple[str, str]], distinct: bool = False):
        """
        Add a WITH clause to pipe results to subsequent query parts.
        
        The WITH clause allows query parts to be chained together, piping the results
        from one to be used as starting points or criteria in the next.
        
        Args:
            *projections: Projections to include. Each projection can be:
                         - A string (raw projection, e.g., "p")
                         - A tuple of (expression, alias), e.g., ("count(n)", "cnt")
            distinct: Whether to return only distinct results
            
        Returns:
            A new WithClause instance
            
        Example:
            >>> query = (
            ...     match(node("p", "Person"))
            ...     .with_(("p.name", "name"), ("p.age", "age"))
            ... )
            >>> # Generates:
            >>> # MATCH (p:Person)
            >>> # WITH p.name AS name, p.age AS age
            
            >>> query = (
            ...     match(node("p", "Person"))
            ...     .with_("p")
            ... )
            >>> # Generates:
            >>> # MATCH (p:Person)
            >>> # WITH p
        """
        # Import WithClause here to avoid circular imports
        from .with_ import WithClause
        
        # Collect all consecutive MATCH clauses as the preceding clause
        # This ensures that multiple MATCH clauses are grouped together before WITH
        full_preceding_match = self._collect_all_match_clauses()
        
        # Find the non-MATCH next clause (if any) after all the MATCH clauses
        non_match_next_clause = self._find_non_match_next_clause()
        
        # Return the WithClause with all MATCH clauses as its preceding clause
        return WithClause(list(projections), distinct, preceding_clause=full_preceding_match, next_clause=non_match_next_clause)
    
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
            ...     .return_("p.name", "p.age")
            ... )
            >>> # Generates:
            >>> # MATCH (p:Person)
            >>> # RETURN p.name, p.age
            
            >>> query = match(node("p", "Person")).return_()
            >>> # Generates:
            >>> # MATCH (p:Person)
            >>> # RETURN *
            
            >>> query = match(node("p", "Person")).return_(distinct=True)
            >>> # Generates:
            >>> # MATCH (p:Person)
            >>> # RETURN DISTINCT *
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
    
    def order_by(self, *fields: Union[str, 'OrderByExpression']):
        """
        Add an ORDER BY clause to sort the results.
        
        The ORDER BY clause sorts the query results based on one or more
        fields, with optional ASC/DESC modifiers.
        
        Args:
            *fields: Fields to sort by. Each field can be:
                    - A string (field name, defaults to ascending)
                    - An OrderByExpression created with asc() or desc()
            
        Returns:
            A new OrderByClause instance
            
        Example:
            >>> from super_sniffle import asc, desc
            >>> query = (
            ...     match(node("p", "Person"))
            ...     .return_("p.name", "p.age")
            ...     .order_by("p.name", desc("p.age"))
            ... )
            >>> # Generates:
            >>> # MATCH (p:Person)
            >>> # RETURN p.name, p.age
            >>> # ORDER BY p.name, p.age DESC
        """
        from ..ast.expressions import OrderByExpression
        from .order_by import OrderByClause
        
        # Convert string fields to OrderByExpression objects
        expressions = []
        for field in fields:
            if isinstance(field, str):
                expressions.append(OrderByExpression(field))
            else:
                expressions.append(field)
        
        return OrderByClause(expressions, preceding_clause=self)
    
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
            ...     .return_("p.name")
            ...     .limit(10)
            ... )
            >>> # Generates:
            >>> # MATCH (p:Person)
            >>> # RETURN p.name
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
            ...     .return_("p.name")
            ...     .skip(10)
            ... )
            >>> # Generates:
            >>> # MATCH (p:Person)
            >>> # RETURN p.name
            >>> # SKIP 10
        """
        from .skip import SkipClause
        return SkipClause(count, preceding_clause=self)
    
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
