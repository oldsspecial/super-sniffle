"""
Pattern classes for representing Cypher query patterns.

This module contains classes for nodes, relationships, and paths that can
include inline WHERE conditions, supporting Cypher's native syntax for
pattern-based filtering.
"""

from dataclasses import dataclass, field
from dataclasses import replace
from typing import Dict, List, Optional, Tuple, Any, Union, Sequence
from .expressions import Expression


def _format_value(value: Any) -> str:
    """Format a value for Cypher output."""
    if isinstance(value, str):
        # Escape single quotes and wrap in quotes
        escaped = value.replace("'", "\\'")
        return f"'{escaped}'"
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif value is None:
        return "null"
    else:
        return str(value)


@dataclass(frozen=True)
class NodePattern:
    """
    Represents a node pattern in a Cypher query.
    
    Supports both basic node patterns and patterns with inline WHERE conditions.
    
    Attributes:
        variable: Variable name for the node (e.g., "p", "user")
        labels: Tuple of node labels (e.g., ("Person", "User"))
        properties: Dictionary of property constraints
        condition: Optional inline WHERE condition
    """
    variable: str
    labels: Union[str, Tuple[str, ...]] = ()
    properties: Dict[str, Any] = field(default_factory=dict)
    condition: Optional[Expression] = None

    def __post_init__(self):
        # Convert single string label to tuple
        if isinstance(self.labels, str):
            object.__setattr__(self, "labels", (self.labels,))
    
    def where(self, condition: Expression) -> 'NodePattern':
        """
        Add a WHERE condition to this node pattern.
        
        Args:
            condition: Expression representing the WHERE condition
            
        Returns:
            New NodePattern with the condition added
            
        Example:
            >>> person = node("p", "Person")
            >>> adult = person.where(prop("p", "age") > 18)
            >>> # Generates: (p:Person WHERE p.age > 18)
        """
        return replace(self, condition=condition)
    
    def relates_to(self, variable: Optional[str] = None, rel_type: str = "", 
                  direction: str = "-", 
                  target_node: Optional['NodePattern'] = None,
                  **properties: Any) -> Union['RelationshipPattern', 'PathPattern']:
        """
        Create a relationship from this node to another node.
        
        Args:
            variable: Optional variable name for the relationship
            rel_type: Relationship type (e.g., "KNOWS", "FOLLOWS")
            direction: Relationship direction ("<", ">", or "-" for undirected, default: "-")
            target_node: Optional target node (if None, only the relationship is returned)
            **properties: Relationship properties
            
        Returns:
            If target_node is provided, returns a PathPattern.
            Otherwise, returns the RelationshipPattern.
            
        Example:
            >>> person = node("p", "Person")
            >>> friend_path = person.relates_to("r", "KNOWS", ">", node("f", "Person"))
            >>> # Generates: (p:Person)-[r:KNOWS]->(f:Person)
            
            >>> # Using defaults for undirected relationship:
            >>> friend_path = person.relates_to("r", "KNOWS", target_node=node("f", "Person"))
            >>> # Generates: (p:Person)-[r:KNOWS]-(f:Person)
        """
        if not rel_type:
            raise ValueError("rel_type is required")
        
        # Create the relationship with a single type
        rel = RelationshipPattern(direction, variable, rel_type, properties)
        
        # If no target node, return just the relationship
        if target_node is None:
            return rel
            
        # Otherwise, create and return a path
        return PathPattern([self, rel, target_node])
    
    def to_cypher(self) -> str:
        """
        Convert node pattern to Cypher string.
        
        Returns:
            Cypher representation of the node pattern
            
        Example:
            >>> node("p", "Person").where(prop("p", "age") > 18).to_cypher()
            >>> # Returns: "(p:Person WHERE p.age > 18)"
        """
        result = f"({self.variable if self.variable else ''}"
        
        # Add labels
        if self.labels:
            result += ":" + ":".join(self.labels)
        
        # Add properties
        if self.properties:
            props_str = ", ".join(f"{k}: {_format_value(v)}" 
                                for k, v in self.properties.items())
            result += f" {{{props_str}}}"
        
        # Add inline WHERE condition
        if self.condition:
            result += f" WHERE {self.condition.to_cypher()}"
        
        result += ")"
        return result


@dataclass(frozen=True)
class RelationshipPattern:
    """
    Represents a relationship pattern in a Cypher query.
    
    Supports both basic relationship patterns and patterns with inline WHERE conditions.
    
    Attributes:
        direction: Relationship direction ("<", ">", or "-" for undirected)
        variable: Optional variable name for the relationship
        type: Relationship type (e.g., "KNOWS")
        properties: Dictionary of property constraints
        condition: Optional inline WHERE condition
    """
    direction: str  # "<", ">", or "-" for undirected
    variable: Optional[str] = None
    type: str = ""
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
            rel_content += ":" + self.type
        
        if self.properties:
            props_str = ", ".join(f"{k}: {_format_value(v)}" 
                                for k, v in self.properties.items())
            rel_content += f" {{{props_str}}}"
        
        # Add inline WHERE condition
        if self.condition:
            rel_content += f" WHERE {self.condition.to_cypher()}"
        
        # Build the full relationship pattern with direction
        if self.direction == "<":
            return f"<-[{rel_content}]-"
        elif self.direction == ">":
            return f"-[{rel_content}]->"
        else:  # undirected
            return f"-[{rel_content}]-"


@dataclass(frozen=True)
class PathPattern:
    """
    Represents a path pattern in a Cypher query.
    
    A path is a sequence of alternating nodes and relationships that form
    a traversal pattern in the graph.
    
    Attributes:
        elements: List of NodePattern and RelationshipPattern objects
        variable: Optional variable name for the path
    """
    elements: Sequence[Union[NodePattern, RelationshipPattern]]
    variable: Optional[str] = None
    
    def __post_init__(self):
        """Automatically insert implicit relationships between consecutive nodes."""
        new_elements = []
        for i, elem in enumerate(self.elements):
            new_elements.append(elem)
            
            # Check if next element exists and both are nodes
            if i < len(self.elements) - 1 and isinstance(elem, NodePattern) and isinstance(self.elements[i+1], NodePattern):
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
        path_str = "".join(elem.to_cypher() for elem in self.elements)
        if self.variable:
            return f"{self.variable} = {path_str}"
        return path_str
        
    def as_(self, variable: str) -> 'PathPattern':
        """Assign the path to a variable"""
        return replace(self, variable=variable)

    def quantify(self, min_hops: Optional[int] = None, max_hops: Optional[int] = None) -> "QuantifiedPathPattern":
        """
        Applies a quantifier to the path pattern.
        
        Args:
            min_hops: Minimum number of hops.
            max_hops: Maximum number of hops.
            
        Returns:
            A QuantifiedPathPattern object.
        """
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
        return QuantifiedPathPattern(self, "+")

    def zero_or_more(self) -> "QuantifiedPathPattern":
        """
        Applies a '*' quantifier to the path pattern (zero or more hops).
        """
        return QuantifiedPathPattern(self, "*")
    
    def where(self, condition: Expression) -> 'PathPattern':
        """
        Add a WHERE condition to the last element in the path.
        
        This is a convenience method for adding conditions to path patterns.
        
        Args:
            condition: Expression representing the WHERE condition
            
        Returns:
            New PathPattern with the condition added to the last element
        """
        if not self.elements:
            raise ValueError("Cannot add WHERE condition to empty path")
        
        # Apply condition to the last element
        last_element = self.elements[-1]
        new_last = last_element.where(condition)
        
        # Create new path with updated last element
        new_elements = list(self.elements[:-1]) + [new_last]
        return replace(self, elements=new_elements)

    def concat(self, other: 'PathPattern') -> 'PathPattern':
        """
        Concatenate this path with another path.
        
        The resulting path will have the elements of this path followed by the elements of the other path.
        If the last element of this path and the first element of the other path are both nodes, 
        an implicit relationship (--) will be inserted between them.
        
        The variable of the resulting path is set to the variable of the first path (if any).
        
        Args:
            other: The path to concatenate to this path.
            
        Returns:
            A new PathPattern representing the concatenated path.
        """
        if not self.elements:
            return other
        if not other.elements:
            return self
            
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
        
    def __add__(self, other: 'PathPattern') -> 'PathPattern':
        """
        Concatenate this path with another path using the '+' operator.
        
        This is equivalent to calling `self.concat(other)`.
        
        Args:
            other: The path to concatenate to this path.
            
        Returns:
            A new PathPattern representing the concatenated path.
        """
        return self.concat(other)


@dataclass(frozen=True)
class QuantifiedPathPattern:
    """
    Represents a quantified path pattern, e.g., `((p)-[:KNOWS]->(f))+`.
    
    Attributes:
        path: The PathPattern to quantify.
        quantifier: The quantifier string (e.g., "*", "+", "{1,5}").
        variable: Optional variable name for the quantified path
    """
    path: "PathPattern"
    quantifier: str
    variable: Optional[str] = None

    def to_cypher(self) -> str:
        """
        Converts the quantified path pattern to a Cypher string.
        """
        base = f"({self.path.to_cypher()}){self.quantifier}"
        if self.variable:
            return f"{self.variable} = {base}"
        return base
        
    def as_(self, variable: str) -> 'QuantifiedPathPattern':
        """Assign the quantified path to a variable"""
        return replace(self, variable=variable)


# Convenience functions for creating common patterns

def simple_node_pattern(variable: str, *labels: str, **properties: Any) -> NodePattern:
    """
    Create a simple node pattern.
    
    Args:
        variable: Variable name for the node
        *labels: Node labels
        **properties: Node properties
        
    Returns:
        NodePattern object
    """
    return NodePattern(variable, labels, properties)


def simple_relationship_pattern(direction: str = "-", variable: Optional[str] = None, 
                               type: str = "", **properties: Any) -> RelationshipPattern:
    """
    Create a simple relationship pattern.
    
    Args:
        direction: Relationship direction ("<", ">", or "-")
        variable: Optional variable name
        type: Relationship type
        **properties: Relationship properties
        
    Returns:
        RelationshipPattern object
    """
    return RelationshipPattern(direction, variable, type, properties)


def simple_path(*elements: Union[NodePattern, RelationshipPattern]) -> PathPattern:
    """
    Create a path pattern from nodes and relationships.
    
    Args:
        *elements: Alternating NodePattern and RelationshipPattern objects
        
    Returns:
        PathPattern object
    """
    return PathPattern(list(elements))
