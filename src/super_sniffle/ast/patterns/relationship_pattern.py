from dataclasses import dataclass, field, replace
from typing import Optional, Union, Dict, Any, TYPE_CHECKING
from ..expressions import Expression
from .quantified_path_pattern import QuantifiedPathPattern
from .utils import format_value
from .types import NodeType, PathType

if TYPE_CHECKING:
    from .base_patterns import BasePathPattern
    from .node_pattern import NodePattern
    from .path_pattern import PathPattern

@dataclass(frozen=True)
class RelationshipPattern:
    """
    Represents a relationship pattern in a Cypher query.
    
    Supports both basic relationship patterns and patterns with inline WHERE conditions.
    
    Attributes:
        direction: Relationship direction ("<", ">", or "-" for undirected)
        variable: Optional variable name for极 the relationship
        type: Optional relationship type (e.g., "KNOWS")
        properties: Dictionary of property constraints
        condition: Optional inline WHERE condition
    """
    direction: str  # "<", ">", or "-" for undirected
    variable: Optional[str] = None
    type: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    condition: Optional[Expression] = None
    
    def where(self, condition: Expression) -> 'RelationshipPattern':
        """
        Add a WHERE condition to this relationship pattern.
        
        Args:
            condition: Expression representing the WHERE condition
            
        Returns:
            New RelationshipPattern with the condition added
            
        Example:
            >>> knows = relationship(">", "r", "KNOWS")
            >>> recent = knows.where(prop("r", "since") > 2020)
            >>> # Generates: -[r:KNOWS WHERE r.since > 2020]->
        """
        return replace(self, condition=condition)
    
    def to_cypher(self) -> str:
        """
        Convert relationship pattern to Cypher string.
        
        Returns:
            Cypher representation of the relationship pattern
            
        Example:
            >>> relationship(">", "r", "KNOWS").where(prop("r", "since") > 2020).to_cypher()
            >>> # Returns: "-[r:KNOWS WHERE r.since > 2020]->"
        """
        # Build relationship content
        rel_content = ""
        
        if self.variable:
            rel_content += self.variable
        
        if self.type:
            # Always include colon before relationship type
            rel_content += ":" + self.type
        
        if self.properties:
            props_str = ", ".join(f"{k}: {format_value(v)}" 
                                for k, v in self.properties.items())
            # Add space if there's existing content
            if rel_content:
                rel_content += " "
            rel_content += f"{{{props_str}}}"
        
        # Add inline WHERE condition
        if self.condition:
            # Add space if there's existing content
            if rel_content:
                rel_content += " "
            rel_content += f"WHERE {self.condition.to_cypher()}"
        
        # If there's no content (anonymous relationship), use shorthand
        if not rel_content:
            if self.direction == "<":
                return "<--"
            elif self.direction == ">":
                return "-->"
            else:
                return "--"
        
        # Build the full relationship pattern with direction
        if self.direction == "<":
            return f"<-[{rel_content}]-"
        elif self.direction == ">":
            return f"-[{rel_content}]->"
        else:
            return f"-[{rel_content}]-"

    def __add__(self, other: Union['NodePattern', 'PathPattern']) -> 'PathPattern':
        """Enable operator overloading for path construction."""
        from .path_pattern import PathPattern  # Local import to avoid circular dependency
        if other.__class__.__name__ == 'NodePattern':
            return PathPattern([self, other])
        elif other.__class__.__name__ == 'PathPattern':
            # Create a temporary PathPattern containing just this relationship
            temp_path = PathPattern([self])
            # Concatenate with the other path
            return temp_path.concat(other)
        else:
            raise TypeError(f"Cannot add RelationshipPattern to {type(other)}")
            
    def quantify(self, min_hops: Optional[int] = None, max_hops: Optional[int] = None) -> "QuantifiedPathPattern":
        """
        Create a quantified relationship pattern (shorthand syntax).
        
        Generates: -[:REL_TYPE]->{min,max}
        
        Args:
            min_hops: Minimum number of hops
            max_hops: Maximum number of hops
            
        Returns:
            QuantifiedPathPattern object
            
        Example:
            >>> relationship(">", "KNOWS").quantify(1, 5)
            -[:KNOWS]->{1,5}
        """
        from .path_pattern import PathPattern  # Import to avoid circular dependency
        # Create quantifier string with proper 0 handling
        if min_hops is None and max_hops is None:
            raise ValueError("At least one of min_hops or max_hops must be specified")
        
        min_str = str(min_hops) if min_hops is not None else ''
        max_str = str(max_hops) if max_hops is not None else ''
        quantifier = f"{{{min_str},{max_str}}}"
        
        # Create a path pattern containing just this relationship
        path_pattern = PathPattern([self])
        return QuantifiedPathPattern(path_pattern, quantifier)
