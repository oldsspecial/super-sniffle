"""Label expression classes for advanced label matching in Cypher patterns."""
from __future__ import annotations

class BaseLabelExpr:
    """Base class for label expressions."""
    def __and__(self, other: 'BaseLabelExpr') -> 'LabelAnd':
        return LabelAnd(self, other)
    
    def __or__(self, other: 'BaseLabelExpr') -> 'LabelOr':
        return LabelOr(self, other)
    
    def __invert__(self) -> 'LabelNot':
        return LabelNot(self)

class LabelAtom(BaseLabelExpr):
    """Represents a single label atom."""
    def __init__(self, label: str):
        self.label = label
        
    def __str__(self) -> str:
        return self.label

class LabelAnd(BaseLabelExpr):
    """Represents a logical AND of label expressions."""
    def __init__(self, left: BaseLabelExpr, right: BaseLabelExpr):
        self.left = left
        self.right = right
        
    def __str__(self) -> str:
        return f"({self.left} & {self.right})"

class LabelOr(BaseLabelExpr):
    """Represents a logical OR of label expressions."""
    def __init__(self, left: BaseLabelExpr, right: BaseLabelExpr):
        self.left = left
        self.right = right
        
    def __str__(self) -> str:
        return f"({self.left} | {self.right})"

class LabelNot(BaseLabelExpr):
    """Represents a logical NOT for a label expression."""
    def __init__(self, expr: BaseLabelExpr):
        self.expr = expr
        
    def __str__(self) -> str:
        return f"!{self.expr}"

def L(label: str) -> LabelAtom:
    """Create a label atom from a string."""
    return LabelAtom(label)
