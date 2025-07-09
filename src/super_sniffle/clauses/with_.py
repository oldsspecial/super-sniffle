"""
WITH clause implementation for Cypher queries.

This module contains the WithClause class that represents WITH clauses
in Cypher queries and supports method chaining with other clauses.
"""

from dataclasses import dataclass, replace
from typing import List, Optional, Union, TYPE_CHECKING, Tuple

from ..ast.expressions import Expression
from .match import Clause, MatchClause

if TYPE_CHECKING:
    from ..ast.expressions import OrderByExpression


@dataclass(frozen=True)
class MatchAfterWithClause(MatchClause):
    """
    A specialized MatchClause that follows a WITH clause.
    
    This class knows how to render itself with the preceding WITH context,
    ensuring proper clause ordering when MATCH follows WITH.
    """
    with_context: Optional['WithClause'] = None
    
    def to_cypher(self) -> str:
        """
        Convert the MATCH clause to Cypher, including the WITH context.
        
        Returns:
            Cypher representation including the preceding WITH clause
        """
        result = ""
        
        # First render the WITH context
        if self.with_context:
            # Create a clean version of the WITH clause without any next_clause
            clean_with = replace(self.with_context, next_clause=None)
            result += clean_with.to_cypher() + "\n"
        
        # Then render this MATCH clause
        patterns_str = ", ".join(p.to_cypher() for p in self.patterns)
        result += f"MATCH {patterns_str}"
        
        # Then render any next clauses
        if self.next_clause:
            result += f"\n{self.next_clause.to_cypher()}"
            
        return result


@dataclass(frozen=True)
class WithClause(Clause):
    """
    Represents a WITH clause in a Cypher query.
    
    The WITH clause allows query parts to be chained together, piping the results
    from one to be used as starting points or criteria in the next. It can be used
    to filter, transform, and reshape the results before they're passed to the
    next part of the query.
    
    Attributes:
        projections: List of strings or tuples representing what to pass forward
        distinct: Whether to return only distinct results
        preceding_clause: Optional clause that comes before this WITH clause
        next_clause: Optional next clause in the query chain
    """
    projections: List[Union[str, Tuple[str, str]]]
    distinct: bool = False
    preceding_clause: Optional[Clause] = None
    next_clause: Optional[Clause] = None
    
    def match(self, *patterns):
        """
        Add another MATCH clause after the WITH clause.
        
        This allows building queries with multiple query parts separated by WITH clauses,
        which is useful for complex graph patterns that need to be matched separately.
        
        Args:
            *patterns: Patterns to match in the new MATCH clause
            
        Returns:
            A new MatchAfterWithClause instance that preserves the WITH context
            
        Example:
            >>> query = (
            ...     match(node("p", "Person"))
            ...     .with_("p")
            ...     .match(node("p").relates_to("KNOWS", ">", node("friend", "Person")))
            ... )
            >>> # Generates: 
            >>> # MATCH (p:Person)
            >>> # WITH p
            >>> # MATCH (p)-[:KNOWS]->(friend:Person)
        """
        # Create a new MatchAfterWithClause with this WITH clause as its context
        return MatchAfterWithClause(list(patterns), with_context=self)
    
    def where(self, condition: Expression):
        """
        Add a WHERE clause to filter the results from the WITH clause.
        
        The WHERE clause applies conditions to filter the results after the
        WITH clause projections.
        
        Args:
            condition: Expression representing the WHERE condition
            
        Returns:
            A new WhereClause instance
            
        Example:
            >>> query = (
            ...     match(node("p", "Person"))
            ...     .with_("p.name AS name", "p.age AS age")
            ...     .where(prop("age") > literal(30))
            ... )
            >>> # Generates:
            >>> # MATCH (p:Person)
            >>> # WITH p.name AS name, p.age AS age
            >>> # WHERE age > 30
        """
        # Import WhereClause here to avoid circular imports
        from .where import WhereClause
        
        # Return the WhereClause with this WithClause as its preceding clause
        return WhereClause(condition, preceding_clause=self, next_clause=self.next_clause)
    
    def with_(self, *projections: Union[str, Tuple[str, str]], distinct: bool = False):
        """
        Add another WITH clause to further transform the results.
        
        This allows chaining multiple WITH clauses for complex data transformation
        and filtering operations.
        
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
            ...     .with_("p")
            ...     .match(node("p").relates_to("KNOWS", ">", node("friend", "Person")))
            ...     .with_(("collect(friend)", "friends"))
            ... )
            >>> # Generates:
            >>> # MATCH (p:Person)
            >>> # WITH p
            >>> # MATCH (p)-[:KNOWS]->(friend:Person)
            >>> # WITH collect(friend) AS friends
        """
        # Create a new WithClause for the additional projections
        new_with = WithClause(list(projections), distinct, next_clause=self.next_clause)
        
        # Chain this WITH clause to the new WITH clause
        return replace(self, next_clause=new_with)
    
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
            ...     .with_("p.name AS name", "p.age AS age")
            ...     .return_("name", "age")
            ... )
            >>> # Generates:
            >>> # MATCH (p:Person)
            >>> # WITH p.name AS name, p.age AS age
            >>> # RETURN name, age
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
            ...     .with_(("p.name", "name"), ("p.age", "age"))
            ...     .order_by("name", desc("age"))
            ... )
            >>> # Generates:
            >>> # MATCH (p:Person)
            >>> # WITH p.name AS name, p.age AS age
            >>> # ORDER BY name, age DESC
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
            A new LimitClause instance (when implemented)
            
        Example:
            >>> query = (
            ...     match(node("p", "Person"))
            ...     .with_("p.name AS name", "p.age AS age")
            ...     .limit(10)
            ... )
            >>> # Generates:
            >>> # MATCH (p:Person)
            >>> # WITH p.name AS name, p.age AS age
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
            ...     .with_("p.name AS name", "p.age AS age")
            ...     .skip(10)
            ...     .limit(5)
            ... )
            >>> # Generates:
            >>> # MATCH (p:Person)
            >>> # WITH p.name AS name, p.age AS age
            >>> # SKIP 10
            >>> # LIMIT 5
        """
        # TODO: Implement SkipClause when needed
        raise NotImplementedError("SKIP clause will be implemented in upcoming releases")
    
    def with_next(self, next_clause: Clause) -> 'WithClause':
        """
        Set the next clause in the query.
        
        This is an internal method used for chaining clauses together.
        
        Args:
            next_clause: The next clause to execute
            
        Returns:
            A new WithClause with the specified next clause
        """
        return replace(self, next_clause=next_clause)
    
    def to_cypher(self) -> str:
        """
        Convert the WITH clause to a Cypher string.
        
        Returns:
            Cypher representation of the WITH clause and any chained clauses
            
        Example:
            >>> with_clause = WithClause(["p.name AS name", "p.age AS age"])
            >>> with_clause.to_cypher()
            >>> # Returns: "WITH p.name AS name, p.age AS age"
            
            >>> with_clause = WithClause(["p"], distinct=True)
            >>> with_clause.to_cypher()
            >>> # Returns: "WITH DISTINCT p"
        """
        result = ""
        
        # Add all preceding clauses (including chained MATCH clauses)
        if self.preceding_clause:
            # We need to render the full chain of preceding clauses
            result += self._render_preceding_clauses() + "\n"
        
        # Add this WITH clause
        distinct_str = "DISTINCT " if self.distinct else ""
        
        # Process projections (handle both strings and tuples)
        projection_strings = []
        for proj in self.projections:
            if isinstance(proj, str):
                projection_strings.append(proj)
            else:  # It's a tuple (expression, alias)
                expression, alias = proj
                projection_strings.append(f"{expression} AS {alias}")
        
        projections_str = ", ".join(projection_strings)
        result += f"WITH {distinct_str}{projections_str}"
        
        # Add the next clause if there is one
        if self.next_clause:
            result += f"\n{self.next_clause.to_cypher()}"
            
        return result
    
    def _render_preceding_clauses(self) -> str:
        """
        Render all preceding clauses in the correct order.
        
        This handles the case where there are multiple clauses that should
        all come before the WITH clause.
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
            
            # If the next clause is the same type as current, include it in the preceding clauses
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
