from .expression import Expression, ComparisonExpression
from typing import Any

class Property(Expression):
    """
    Represents a property of a node or relationship.
    
    Attributes:
        variable: Variable name (e.g., "p", "user", "rel")
        name: Property name (e.g., "age", "name", "weight")
    """
    def __init__(self, variable: str, name: str):
        self.variable = variable
        self.name = name
    
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
