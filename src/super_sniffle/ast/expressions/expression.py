from dataclasses import dataclass
from typing import Any

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
    
    def __eq__(self, other: Any) -> Any:
        """
        Equality comparison using == operator.
        
        Returns:
            ComparisonExpression for query building or bool for actual comparisons
        """
        if isinstance(other, Expression):
            return ComparisonExpression(self, "=", other)
        return NotImplemented
    
    def __ne__(self, other: Any) -> Any:
        """
        Inequality comparison using != operator.
        
        Returns:
            ComparisonExpression for query building or bool for actual comparisons
        """
        if isinstance(other, Expression):
            return ComparisonExpression(self, "<>", other)
        return NotImplemented

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
