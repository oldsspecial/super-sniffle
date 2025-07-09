"""
Expression classes for building Cypher query conditions.

This module provides expression classes that support operator overloading
for more intuitive query condition construction. It allows developers to
use Python operators like ==, >, <, &, |, ~ to build Cypher WHERE clauses.
"""

from dataclasses import dataclass
from typing import Any, Union


@dataclass(frozen=True)
class Expression:
    """
    Base class for all expressions.
    
    Provides operator overloading for logical operations and defines
    the interface for converting expressions to Cypher strings.
    """
    
    def to_cypher(self) -> str:
        """Convert expression to Cypher string."""
        raise NotImplementedError("Subclasses must implement to_cypher()")
    
    def __and__(self, other: "Expression") -> "LogicalExpression":
        """
        Logical AND operation using & operator.
        
        Args:
            other: Another expression to combine with AND
            
        Returns:
            LogicalExpression representing the AND operation
            
        Example:
            >>> expr1 & expr2  # Generates: (expr1) AND (expr2)
        """
        return LogicalExpression(self, "AND", other)
    
    def __or__(self, other: "Expression") -> "LogicalExpression":
        """
        Logical OR operation using | operator.
        
        Args:
            other: Another expression to combine with OR
            
        Returns:
            LogicalExpression representing the OR operation
            
        Example:
            >>> expr1 | expr2  # Generates: (expr1) OR (expr2)
        """
        return LogicalExpression(self, "OR", other)
    
    def __invert__(self) -> "NotExpression":
        """
        Logical NOT operation using ~ operator.
        
        Returns:
            NotExpression representing the NOT operation
            
        Example:
            >>> ~expr  # Generates: NOT (expr)
        """
        return NotExpression(self)


@dataclass(frozen=True)
class ComparisonExpression(Expression):
    """
    Represents a comparison between two values.
    
    Attributes:
        left: Left-hand side of the comparison (typically a Property)
        operator: Comparison operator (=, >, <, >=, <=, <>, etc.)
        right: Right-hand side of the comparison (value, parameter, etc.)
    """
    left: Any
    operator: str
    right: Any
    
    def to_cypher(self) -> str:
        """
        Convert comparison to Cypher string.
        
        Returns:
            Cypher string representation of the comparison
            
        Example:
            >>> ComparisonExpression(prop("p", "age"), ">", param("min_age"))
            >>> # Returns: "p.age > $min_age"
        """
        left_cypher = (
            self.left.to_cypher() 
            if hasattr(self.left, 'to_cypher') 
            else str(self.left)
        )
        right_cypher = (
            self.right.to_cypher() 
            if hasattr(self.right, 'to_cypher') 
            else str(self.right)
        )
        return f"{left_cypher} {self.operator} {right_cypher}"


@dataclass(frozen=True)
class LogicalExpression(Expression):
    """
    Represents a logical operation (AND, OR) between expressions.
    
    Attributes:
        left: Left-hand expression
        operator: Logical operator ("AND" or "OR")
        right: Right-hand expression
    """
    left: Expression
    operator: str
    right: Expression
    
    def to_cypher(self) -> str:
        """
        Convert logical expression to Cypher string.
        
        Returns:
            Cypher string with parentheses around sub-expressions
            
        Example:
            >>> LogicalExpression(expr1, "AND", expr2)
            >>> # Returns: "(expr1) AND (expr2)"
        """
        return f"({self.left.to_cypher()}) {self.operator} ({self.right.to_cypher()})"


@dataclass(frozen=True)
class NotExpression(Expression):
    """
    Represents a NOT operation on an expression.
    
    Attributes:
        expression: The expression to negate
    """
    expression: Expression
    
    def to_cypher(self) -> str:
        """
        Convert NOT expression to Cypher string.
        
        Returns:
            Cypher string with NOT operator
            
        Example:
            >>> NotExpression(expr)
            >>> # Returns: "NOT (expr)"
        """
        return f"NOT ({self.expression.to_cypher()})"


@dataclass(frozen=True)
class Property(Expression):
    """
    Represents a property of a node or relationship.
    
    Attributes:
        variable: Variable name (e.g., "p", "user", "rel")
        name: Property name (e.g., "age", "name", "weight")
    """
    variable: str
    name: str
    
    def to_cypher(self) -> str:
        """
        Convert property to Cypher string.
        
        Returns:
            Cypher property reference
            
        Example:
            >>> Property("p", "age")
            >>> # Returns: "p.age"
        """
        return f"{self.variable}.{self.name}"
    
    # Comparison operators
    def __eq__(self, other: Any) -> ComparisonExpression:
        """Equality comparison using == operator."""
        return ComparisonExpression(self, "=", other)
    
    def __ne__(self, other: Any) -> ComparisonExpression:
        """Inequality comparison using != operator."""
        return ComparisonExpression(self, "<>", other)
    
    def __gt__(self, other: Any) -> ComparisonExpression:
        """Greater than comparison using > operator."""
        return ComparisonExpression(self, ">", other)
    
    def __lt__(self, other: Any) -> ComparisonExpression:
        """Less than comparison using < operator."""
        return ComparisonExpression(self, "<", other)
    
    def __ge__(self, other: Any) -> ComparisonExpression:
        """Greater than or equal comparison using >= operator."""
        return ComparisonExpression(self, ">=", other)
    
    def __le__(self, other: Any) -> ComparisonExpression:
        """Less than or equal comparison using <= operator."""
        return ComparisonExpression(self, "<=", other)
    
    # Method-based API for special operations
    def contains(self, value: Any) -> ComparisonExpression:
        """
        String contains operation.
        
        Args:
            value: Value to check if contained in the property
            
        Returns:
            ComparisonExpression using CONTAINS operator
        """
        return ComparisonExpression(self, "CONTAINS", value)
    
    def starts_with(self, value: Any) -> ComparisonExpression:
        """
        String starts with operation.
        
        Args:
            value: Value to check if property starts with
            
        Returns:
            ComparisonExpression using STARTS WITH operator
        """
        return ComparisonExpression(self, "STARTS WITH", value)
    
    def ends_with(self, value: Any) -> ComparisonExpression:
        """
        String ends with operation.
        
        Args:
            value: Value to check if property ends with
            
        Returns:
            ComparisonExpression using ENDS WITH operator
        """
        return ComparisonExpression(self, "ENDS WITH", value)
    
    def in_list(self, values: Any) -> ComparisonExpression:
        """
        List membership operation.
        
        Args:
            values: List or parameter containing values to check
            
        Returns:
            ComparisonExpression using IN operator
        """
        return ComparisonExpression(self, "IN", values)
    
    def is_null(self) -> ComparisonExpression:
        """
        NULL check operation.
        
        Returns:
            ComparisonExpression checking if property IS NULL
        """
        return ComparisonExpression(self, "IS", "NULL")
    
    def is_not_null(self) -> ComparisonExpression:
        """
        NOT NULL check operation.
        
        Returns:
            ComparisonExpression checking if property IS NOT NULL
        """
        return ComparisonExpression(self, "IS NOT", "NULL")


@dataclass(frozen=True)
class Variable(Expression):
    """
    Represents a variable reference (not a property).
    
    Variables can be introduced by WITH clauses, UNWIND, function calls,
    or other query constructs that create named values.
    
    Attributes:
        name: Variable name
    """
    name: str
    
    def to_cypher(self) -> str:
        """
        Convert variable to Cypher string.
        
        Returns:
            Cypher variable reference
            
        Example:
            >>> Variable("friendCount")
            >>> # Returns: "friendCount"
        """
        return self.name
    
    # Comparison operators
    def __eq__(self, other: Any) -> ComparisonExpression:
        """Equality comparison using == operator."""
        return ComparisonExpression(self, "=", other)
    
    def __ne__(self, other: Any) -> ComparisonExpression:
        """Inequality comparison using != operator."""
        return ComparisonExpression(self, "<>", other)
    
    def __gt__(self, other: Any) -> ComparisonExpression:
        """Greater than comparison using > operator."""
        return ComparisonExpression(self, ">", other)
    
    def __lt__(self, other: Any) -> ComparisonExpression:
        """Less than comparison using < operator."""
        return ComparisonExpression(self, "<", other)
    
    def __ge__(self, other: Any) -> ComparisonExpression:
        """Greater than or equal comparison using >= operator."""
        return ComparisonExpression(self, ">=", other)
    
    def __le__(self, other: Any) -> ComparisonExpression:
        """Less than or equal comparison using <= operator."""
        return ComparisonExpression(self, "<=", other)
    
    # Method-based API for special operations
    def contains(self, value: Any) -> ComparisonExpression:
        """
        String contains operation.
        
        Args:
            value: Value to check if contained in the variable
            
        Returns:
            ComparisonExpression using CONTAINS operator
        """
        return ComparisonExpression(self, "CONTAINS", value)
    
    def starts_with(self, value: Any) -> ComparisonExpression:
        """
        String starts with operation.
        
        Args:
            value: Value to check if variable starts with
            
        Returns:
            ComparisonExpression using STARTS WITH operator
        """
        return ComparisonExpression(self, "STARTS WITH", value)
    
    def ends_with(self, value: Any) -> ComparisonExpression:
        """
        String ends with operation.
        
        Args:
            value: Value to check if variable ends with
            
        Returns:
            ComparisonExpression using ENDS WITH operator
        """
        return ComparisonExpression(self, "ENDS WITH", value)
    
    def in_list(self, values: Any) -> ComparisonExpression:
        """
        List membership operation.
        
        Args:
            values: List or parameter containing values to check
            
        Returns:
            ComparisonExpression using IN operator
        """
        return ComparisonExpression(self, "IN", values)
    
    def is_null(self) -> ComparisonExpression:
        """
        NULL check operation.
        
        Returns:
            ComparisonExpression checking if variable IS NULL
        """
        return ComparisonExpression(self, "IS", "NULL")
    
    def is_not_null(self) -> ComparisonExpression:
        """
        NOT NULL check operation.
        
        Returns:
            ComparisonExpression checking if variable IS NOT NULL
        """
        return ComparisonExpression(self, "IS NOT", "NULL")


@dataclass(frozen=True)
class Parameter(Expression):
    """
    Represents a query parameter.
    
    Attributes:
        name: Parameter name (without the $ prefix)
    """
    name: str
    
    def to_cypher(self) -> str:
        """
        Convert parameter to Cypher string.
        
        Returns:
            Cypher parameter reference with $ prefix
            
        Example:
            >>> Parameter("min_age")
            >>> # Returns: "$min_age"
        """
        return f"${self.name}"


@dataclass(frozen=True)
class Literal(Expression):
    """
    Represents a literal value in a query.
    
    Attributes:
        value: The literal value (string, number, boolean, etc.)
    """
    value: Any
    
    def to_cypher(self) -> str:
        """
        Convert literal to Cypher string.
        
        Returns:
            Cypher representation of the literal value
            
        Example:
            >>> Literal("Alice")  # Returns: "'Alice'"
            >>> Literal(42)       # Returns: "42"
            >>> Literal(True)     # Returns: "true"
        """
        if isinstance(self.value, str):
            # Escape single quotes and wrap in quotes
            escaped = self.value.replace("'", "\\'")
            return f"'{escaped}'"
        elif isinstance(self.value, bool):
            return "true" if self.value else "false"
        elif self.value is None:
            return "null"
        else:
            return str(self.value)


@dataclass(frozen=True)
class OrderByExpression:
    """
    Represents a field in an ORDER BY clause with direction.
    
    Attributes:
        field: The field to sort by
        descending: Whether to sort in descending order (defaults to False for ascending)
    """
    field: str
    descending: bool = False
    
    def to_cypher(self) -> str:
        """
        Convert to Cypher string.
        
        Returns:
            Cypher representation of the sort field with direction
            
        Example:
            >>> OrderByExpression("p.age")  # Returns: "p.age"
            >>> OrderByExpression("p.age", True)  # Returns: "p.age DESC"
        """
        direction = " DESC" if self.descending else ""
        return f"{self.field}{direction}"
