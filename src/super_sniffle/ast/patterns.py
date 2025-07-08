"""
Pattern classes for representing Cypher query patterns.

This module contains classes for nodes, relationships, and paths that can
include inline WHERE conditions, supporting Cypher's native syntax for
pattern-based filtering.
"""

from dataclasses import dataclass, field, replace
from typing import Dict, List, Optional, Tuple, Any, Union
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
    labels: Tuple[str, ...] = ()
    properties: Dict[str, Any] = field(default_factory=dict)
    condition: Optional[Expression] = None
    
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
    
    def relates_to(self, direction: str, rel_type: str, 
                  variable: Optional[str] = None, 
                  target_node: Optional['NodePattern'] = None,
                  **properties: Any) -> Union['RelationshipPattern', 'PathPattern']:
        """
        Create a relationship from this node to another node.
        
        Args:
            direction: Relationship direction ("<", ">", or "-")
            rel_type: Relationship type (e.g., "KNOWS", "FOLLOWS")
            variable: Optional variable name for the relationship
            target_node: Optional target node (if None, only the relationship is returned)
            **properties: Relationship properties
            
        Returns:
            If target_node is provided, returns a PathPattern.
            Otherwise, returns the RelationshipPattern.
            
        Example:
            >>> person = node("p", "Person")
            >>> friend_path = person.relates_to(">", "KNOWS", "r", node("f", "Person"))
            >>> # Generates: (p:Person)-[r:KNOWS]->(f:Person)
            
            >>> # Alternative with keyword arguments:
            >>> friend_path = person.relates_to(">", "KNOWS", variable="r", target_node=node("f", "Person"))
        """
        # Handle the common case where variable and target_node are passed positionally
        # relates_to(direction, rel_type, variable, target_node)
        if variable is not None and isinstance(variable, str) and target_node is None:
            # Check if there are extra positional arguments
            # This handles: relates_to(">", "KNOWS", "r", node(...))
            pass  # variable is already set correctly
        
        # Create the relationship with a single type
        rel = RelationshipPattern(direction, variable, (rel_type,), properties)
        
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
        result = f"({self.variable}"
        
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
        types: Tuple of relationship types (e.g., ("KNOWS", "FRIENDS_WITH"))
        properties: Dictionary of property constraints
        condition: Optional inline WHERE condition
    """
    direction: str  # "<", ">", or "-" for undirected
    variable: Optional[str] = None
    types: Tuple[str, ...] = ()
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
        
        if self.types:
            rel_content += ":" + ":".join(self.types)
        
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
    """
    elements: List[Union[NodePattern, RelationshipPattern]]
    
    def to_cypher(self) -> str:
        """
        Convert path pattern to Cypher string.
        
        Returns:
            Cypher representation of the path pattern
            
        Example:
            >>> path = PathPattern([
            ...     NodePattern("p1", ("Person",)),
            ...     RelationshipPattern(">", "r", ("KNOWS",)),
            ...     NodePattern("p2", ("Person",))
            ... ])
            >>> path.to_cypher()
            >>> # Returns: "(p1:Person)-[r:KNOWS]->(p2:Person)"
        """
        return "".join(elem.to_cypher() for elem in self.elements)
    
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
        new_elements = self.elements[:-1] + [new_last]
        return replace(self, elements=new_elements)


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
                               *types: str, **properties: Any) -> RelationshipPattern:
    """
    Create a simple relationship pattern.
    
    Args:
        direction: Relationship direction ("<", ">", or "-")
        variable: Optional variable name
        *types: Relationship types
        **properties: Relationship properties
        
    Returns:
        RelationshipPattern object
    """
    return RelationshipPattern(direction, variable, types, properties)


def simple_path(*elements: Union[NodePattern, RelationshipPattern]) -> PathPattern:
    """
    Create a path pattern from nodes and relationships.
    
    Args:
        *elements: Alternating NodePattern and RelationshipPattern objects
        
    Returns:
        PathPattern object
    """
    return PathPattern(list(elements))
