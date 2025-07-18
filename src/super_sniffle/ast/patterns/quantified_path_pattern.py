from dataclasses import dataclass, replace
from typing import Optional
from .path_pattern import PathPattern

@dataclass(frozen=True)
class QuantifiedPathPattern:
    """
    Represents a quantified path pattern, e.g., `((p)-[:KNOWS]->(f))+`.
    
    Attributes:
        path: The PathPattern to quantify.
        quantifier: The quantifier string (e.g., "*", "+", "{1,5}").
        variable: Optional variable name for the quantified path
    """
    path: PathPattern
    quantifier: str
    variable: Optional[str] = None

    def to_cypher(self) -> str:
        """
        Converts the quantified path pattern to a Cypher string.
        """
        # For single relationship patterns, don't wrap in parentheses
        # Use string type check to avoid circular imports
        if len(self.path.elements) == 1 and self.path.elements[0].__class__.__name__ == 'RelationshipPattern':
            base = self.path.to_cypher()
        else:
            base = f"({self.path.to_cypher()})"
        
        base += self.quantifier
        
        if self.variable:
            return f"{self.variable} = {base}"
        return base
        
    def as_(self, variable: str) -> 'QuantifiedPathPattern':
        """Assign the quantified path to a variable"""
        return replace(self, variable=variable)
