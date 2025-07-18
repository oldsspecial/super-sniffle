from dataclasses import dataclass, field, replace
from typing import Optional, Sequence, Union, TYPE_CHECKING
from ..expressions import Expression
from .base_patterns import BasePathPattern
from .types import PatternElement, NodeType, RelType

if TYPE_CHECKING:
    from .node_pattern import NodePattern
    from .relationship_pattern import RelationshipPattern
    from .quantified_path_pattern import QuantifiedPathPattern

@dataclass(frozen=True)
class PathPattern(BasePathPattern):
    """
    Represents a path pattern in a Cypher query.
    
    A path is a sequence of alternating nodes and relationships that form
    a traversal pattern in the graph.
    
    Attributes:
        elements: List of pattern elements (nodes, relationships, or paths)
        variable: Optional variable name for the path
        condition: Optional WHERE condition for the entire path
    """
    elements: Sequence[PatternElement]
    variable: Optional[str] = None
    condition: Optional[Expression] = None
    
    def __post_init__(self):
        """Automatically insert implicit relationships between consecutive nodes."""
        # Import locally to avoid circular dependency
        from .relationship_pattern import RelationshipPattern
        from .node_pattern import NodePattern
        
        # First, flatten any PathPattern elements
        flattened_elements = []
        for elem in self.elements:
            if isinstance(elem, PathPattern):
                flattened_elements.extend(elem.elements)
            else:
                flattened_elements.append(elem)
        
        new_elements = []
        for i, elem in enumerate(flattened_elements):
            new_elements.append(elem)
            
            # Check if next element exists and both are nodes
            if i < len(flattened_elements) - 1 and isinstance(elem, NodePattern) and isinstance(flattened_elements[i+1], NodePattern):
                # Insert implicit relationship: no variable, no type, undirected
                new_elements.append(RelationshipPattern(direction="-"))
        
        # Update elements with implicit relationships
        object.__setattr__(self, "elements", new_elements)
    
    def to_cypher(self) -> str:
        """
        Convert path pattern to Cypher string.
        
        Returns:
            Cypher representation of the path pattern
            
        Example:
            >>> path = PathPattern([
            ...     NodePattern("p1", ("Person",)),
            ...     NodePattern("p2", ("Person",))
            ... ]).as_("p")
            >>> path.to_cypher()
            >>> # Returns: "p = (p1:Person)--(p2:Person)"
        """
        # Import locally to avoid circular dependencies
        from .node_pattern import NodePattern
        from .relationship_pattern import RelationshipPattern
        
        parts = []
        for elem in self.elements:
            # Handle anonymous elements efficiently
            if isinstance(elem, NodePattern) and elem.variable is None and not elem.labels and not elem.properties and elem.condition is None:
                parts.append("()")
            elif isinstance(elem, RelationshipPattern) and elem.variable is None and elem.type is None and not elem.properties and elem.condition is None:
                # Handle anonymous relationships
                if elem.direction == "<":
                    parts.append("<--")
                elif elem.direction == ">":
                    parts.append("-->")
                else:
                    parts.append("--")
            else:
                parts.append(elem.to_cypher())
                
        path_str = "".join(parts)
        if self.variable:
            base = f"{self.variable} = {path_str}"
        else:
            base = path_str
        
        # Add WHERE condition if present
        if self.condition:
            return f"{base} WHERE {self.condition.to_cypher()}"
        return base
        
    def as_(self, variable: str) -> 'PathPattern':
        """Assign the path to a variable"""
        return replace(self, variable=variable)

    def where(self, condition: Expression) -> 'PathPattern':
        """
        Add a WHERE condition to the entire path pattern.
        
        Args:
            condition: Expression representing the WHERE condition
            
        Returns:
            New PathPattern with the condition added
            
        Raises:
            ValueError: If attempting to add condition to an incomplete path
        """
        from .relationship_pattern import RelationshipPattern  # Import to avoid circular dependency
        # Cannot add condition to incomplete path (ending with relationship)
        if self.elements and isinstance(self.elements[-1], RelationshipPattern):
            raise ValueError("Cannot add condition to incomplete path")
        return replace(self, condition=condition)

    def quantify(self, min_hops: Optional[int] = None, max_hops: Optional[int] = None) -> "QuantifiedPathPattern":
        """
        Applies a quantifier to the path pattern.
        
        Args:
            min_hops: Minimum number of hops.
            max_hops: Maximum number of hops.
            
        Returns:
            A QuantifiedPathPattern object.
        """
        from .quantified_path_pattern import QuantifiedPathPattern  # Import to avoid circular dependency
        if min_hops is None and max_hops is None:
            raise ValueError("At least one of min_hops or max_hops must be specified.")
        
        if min_hops is not None and max_hops is not None and min_hops > max_hops:
            raise ValueError("min_hops cannot be greater than max_hops.")

        quantifier = f"{{{min_hops or ''}, {max_hops or ''}}}"
        return QuantifiedPathPattern(self, quantifier)

    def one_or_more(self) -> "QuantifiedPathPattern":
        """
        Applies a '+' quantifier to the path pattern (one or more hops).
        """
        from .quantified_path_pattern import QuantifiedPathPattern  # Import to avoid circular dependency
        return QuantifiedPathPattern(self, "+")

    def zero_or_more(self) -> "QuantifiedPathPattern":
        """
        Applies a '*' quantifier to the path pattern (zero or more hops).
        """
        from .quantified_path_pattern import QuantifiedPathPattern  # Import to avoid circular dependency
        return QuantifiedPathPattern(self, "*")
    
    def concat(self, other: Union['PathPattern', 'NodePattern', 'RelationshipPattern']) -> 'PathPattern':
        """
        Concatenate this path with another path, node, or relationship.
        
        The resulting path will have the elements of this path followed by the elements of the other pattern.
        If the last element of this path and the first element of the other pattern are both nodes, 
        an implicit relationship (--) will be inserted between them.
        
        The variable of the resulting path is set to the variable of the first path (if any).
        
        Args:
            other: The pattern to concatenate to this path.
            
        Returns:
            A new PathPattern representing the concatenated path.
            
        Raises:
            ValueError: If trying to append a relationship to a path ending with a relationship
        """
        # Local imports to avoid circular dependencies
        from .node_pattern import NodePattern
        from .relationship_pattern import RelationshipPattern
        
        if not self.elements:
            if isinstance(other, PathPattern):
                return other
            return PathPattern([other])
        if not other:
            return self
            
        # Convert other to a PathPattern if it's a single pattern
        if not isinstance(other, PathPattern):
            other = PathPattern([other])
            
        # Check for invalid concatenation: path ending with relationship + relationship
        if isinstance(self.elements[-1], RelationshipPattern) and other.elements:
            if isinstance(other.elements[0], RelationshipPattern):
                raise ValueError("Cannot append a relationship to a path ending with a relationship")
            
        # Skip duplicate node if last of first path and first of second path are the same node
        last_elem = self.elements[-1]
        first_elem = other.elements[0]
        if (isinstance(last_elem, NodePattern) and 
            isinstance(first_elem, NodePattern) and 
            last_elem.variable == first_elem.variable):
            new_elements = list(self.elements) + list(other.elements[1:])
        else:
            new_elements = list(self.elements) + list(other.elements)
            
        return PathPattern(new_elements, variable=self.variable)
        
    def __add__(self, other: Union['PathPattern', 'NodePattern', 'RelationshipPattern']) -> 'PathPattern':
        """
        Concatenate this path with another path, node, or relationship using the '+' operator.
        
        This is equivalent to calling `self.concat(other)`.
        
        Args:
            other: The pattern to concatenate to this path.
            
        Returns:
            A new PathPattern representing the concatenated path.
        """
        return self.concat(other)
