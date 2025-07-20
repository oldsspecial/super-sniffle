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
        variable: Optional variable name for the relationship
        type: Optional relationship type (e.g., "KNOWS")
        properties: Dictionary of property constraints
        condition: Optional inline WHERE condition
        start_node: Optional reference to start node (for API chaining)
    """
    direction: str  # "<", ">", or "-" for undirected
    variable: Optional[str] = None
    type: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    condition: Optional[Expression] = None
    start_node: Optional['NodePattern'] = field(default=None, compare=False)  # Not part of pattern identity
    
    def node(self, *labels: str, variable: Optional[str] = None, **properties: Any) -> 'PathPattern':
        """
        Create an end node and return a complete path pattern.
        
        Args:
            *labels: Node labels
            variable: Optional node variable name
            **properties: Node properties
            
        Returns:
            PathPattern containing start node, relationship, and end node
            
        Example:
            >>> person = node("p", "Person")
            >>> path = person.relationship("KNOWS", ">").node("f", "Person")
            >>> # Generates: (p:Person)-[:KNOWS]->(f:Person)
        """
        from .node_pattern import NodePattern
        from .path_pattern import PathPattern
        
        if not self.start_node:
            raise ValueError("RelationshipPattern missing start_node reference")
            
        end_node = NodePattern(variable, labels, properties)
        return PathPattern([self.start_node, self, end_node])
    
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
        
        # Build the relationship string
        if not rel_content:
            if self.direction == "<":
                rel_str = "<--"
            elif self.direction == ">":
                rel_str = "-->"
            else:
                rel_str = "--"
        else:
            if self.direction == "<":
                rel_str = f"<-[{rel_content}]-"
            elif self.direction == ">":
                rel_str = f"-[{rel_content}]->"
            else:
                rel_str = f"-[{rel_content}]-"

        # Prepend start node if present
        if self.start_node:
            return self.start_node.to_cypher() + rel_str
        return rel_str

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
