from __future__ import annotations
from dataclasses import dataclass, field, replace
from typing import Optional, Tuple, Dict, Any, Union
from .base_label_expr import BaseLabelExpr, L
from ..expressions import Expression
from .utils import format_value

@dataclass(frozen=True)
class NodePattern:
    """
    Represents a node pattern in a Cypher query.
    
    Supports both basic node patterns and patterns with inline WHERE conditions.
    
    Attributes:
        variable: Optional variable name for the node (e.g., "p", "user")
        labels: Union[Tuple[Union[str, BaseLabelExpr], ...], BaseLabelExpr, str] = Labels or expressions
        properties: Dictionary of property constraints
        condition: Optional inline WHERE condition
    """
    variable: Optional[str] = None
    labels: Union[Tuple[Union[str, BaseLabelExpr], ...], BaseLabelExpr, str] = ()
    properties: Dict[str, Any] = field(default_factory=dict)
    condition: Optional[Expression] = None

    def __post_init__(self):
        # Convert single string label to tuple
        if isinstance(self.labels, str):
            object.__setattr__(self, "labels", (self.labels,))
        # If we have a tuple of labels, check if we need to convert to expression
        elif isinstance(self.labels, tuple):
            # Convert all strings in tuple to LabelAtom
            converted = []
            for item in self.labels:
                if isinstance(item, str):
                    converted.append(L(item))
                else:
                    converted.append(item)
            
            # If we have any expressions, combine them with AND
            if any(isinstance(item, BaseLabelExpr) for item in converted):
                expr = converted[0]
                for label in converted[1:]:
                    expr = expr & label
                object.__setattr__(self, "labels", expr)
            else:
                # Otherwise keep as tuple of strings
                object.__setattr__(self, "labels", tuple(str(item) for item in converted))
        
        # If variable is provided, ensure it's not treated as part of the label expression
        # This was causing issues like (:`(p & Person)`) instead of (p:Person)
        # We'll remove this conversion and handle variables separately in to_cypher
    
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
                  **properties: Any) -> Union['RelationshipPattern', 'PathPattern']:  # noqa: F821
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
        
        # Import locally to avoid circular dependency
        from .relationship_pattern import RelationshipPattern
        
        # Create the relationship with a single type
        rel = RelationshipPattern(direction, variable, rel_type, properties)
        
        # If no target node, return just the relationship
        if target_node is None:
            return rel
            
        # Otherwise, create and return a path
        from .path_pattern import PathPattern  # Local import to break circular dependency
        return PathPattern([self, rel, target_node])
    
    def to_cypher(self) -> str:
        """
        Convert node pattern to Cypher string.
        
        Returns:
            Cypher representation of the node pattern
            
        Example:
            >>> node("Person").where(prop("age") > 18).to_cypher()
            >>> # Returns: "(:Person WHERE age > 18)"
        """
        result = f"({self.variable if self.variable else ''}"
        
        # Add labels or expressions after variable
        if self.labels:
            # Handle label expressions
            if isinstance(self.labels, BaseLabelExpr):
                labels_str = str(self.labels)
                # Wrap complex expressions in backticks if they contain operators
                if any(op in labels_str for op in ["&", "|", "!"]):
                    result += f":`{labels_str}`"
                else:
                    result += f":{labels_str}"
            elif isinstance(self.labels, tuple):
                # Handle tuple of strings - join with colons for multiple labels
                labels_str = ":".join(
                    str(label) for label in self.labels
                )
                result += f":{labels_str}"
            else:
                # Handle single string label
                result += f":{self.labels}"
        
        # Add properties
        if self.properties:
            props_str = ", ".join(f"{k}: {format_value(v)}" 
                                for k, v in self.properties.items())
            result += f" {{{props_str}}}"
        
        # Add inline WHERE condition
        if self.condition:
            result += f" WHERE {self.condition.to_cypher()}"
        
        result += ")"
        return result
    
    def __add__(self, other: Union['NodePattern', 'RelationshipPattern', 'PathPattern']) -> 'PathPattern':  # noqa: F821
        """Enable operator overloading for path construction."""
        # Import locally to avoid circular dependencies
        from .relationship_pattern import RelationshipPattern
        from .path_pattern import PathPattern
        
        if isinstance(other, NodePattern):
            return PathPattern([self, other])  # Will automatically insert implicit relationship
        elif isinstance(other, RelationshipPattern):
            return PathPattern([self, other])
        elif isinstance(other, PathPattern):
            return PathPattern([self]).concat(other)
        else:
            raise TypeError(f"Cannot add NodePattern to {type(other)}")
