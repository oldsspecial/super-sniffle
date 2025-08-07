from .expression import Expression, ComparisonExpression
from typing import Any

class Variable(Expression):
    def __init__(self, name: str):
        self.name = name
    
    def to_cypher(self) -> str:
        return self.name
    
    def __str__(self) -> str:
        """String representation returns the variable name."""
        return self.name
    
    def __eq__(self, other: Any) -> ComparisonExpression:
        return ComparisonExpression(self, "=", other)
    
    def __ne__(self, other: Any) -> ComparisonExpression:
        return ComparisonExpression(self, "<>", other)
    
    def __gt__(self, other: Any) -> ComparisonExpression:
        return ComparisonExpression(self, ">", other)
    
    def __lt__(self, other: Any) -> ComparisonExpression:
        return ComparisonExpression(self, "<", other)
    
    def __ge__(self, other: Any) -> ComparisonExpression:
        return ComparisonExpression(self, ">=", other)
    
    def __le__(self, other: Any) -> ComparisonExpression:
        return ComparisonExpression(self, "<=", other)
    
    def contains(self, value: Any) -> ComparisonExpression:
        return ComparisonExpression(self, "CONTAINS", value)
    
    def starts_with(self, value: Any) -> ComparisonExpression:
        return ComparisonExpression(self, "STARTS WITH", value)
    
    def ends_with(self, value: Any) -> ComparisonExpression:
        return ComparisonExpression(self, "ENDS WITH", value)
    
    def in_list(self, values: Any) -> ComparisonExpression:
        return ComparisonExpression(self, "IN", values)
    
    def is_null(self) -> ComparisonExpression:
        return ComparisonExpression(self, "IS", "NULL")
    
    def is_not_null(self) -> ComparisonExpression:
        return ComparisonExpression(self, "IS NOT", "NULL")
