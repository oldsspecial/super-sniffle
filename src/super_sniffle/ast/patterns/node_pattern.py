from __future__ import annotations
from dataclasses import dataclass, field, replace
from typing import Optional, Tuple, Dict, Any, Union
from .base_label_expr import BaseLabelExpr, L
from ..expressions import Expression
from super_sniffle.ast.formatting_utils import format_value
from .relationship_pattern import RelationshipPattern  # Add import
from .path_pattern import PathPattern  # Add import

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
        max_degree: Optional maximum degree constraint
        degree_direction: Optional relationship direction for degree constraint ("in", "out")
        degree_rel_type: Optional relationship type for degree constraint
    """
    variable: Optional[str] = None
    labels: Union[Tuple[Union[str, BaseLabelExpr], ...], BaseLabelExpr, str] = ()
    properties: Dict[str, Any] = field(default_factory=dict)
    condition: Optional[Expression] = None
    max_degree: Optional[int] = None
    degree_direction: Optional[str] = None
    degree_rel_type: Optional[str] = None

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
        
        # Validate degree constraints at creation time
        self._validate_degree_params()
        
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
    
    def _validate_degree_params(self):
        """Validate degree constraint parameters."""
        if (self.max_degree is not None or 
            self.degree_direction is not None or 
            self.degree_rel_type is not None):
            if self.variable is None:
                raise ValueError(
                    "Variable name is required when using degree constraints "
                    "(max_degree, degree_direction, or degree_rel_type)"
                )
            if self.max_degree is None:
                raise ValueError(
                    "max_degree must be provided when using degree constraints"
                )
    
    
    def to_cypher(self) -> str:
        """
        Convert node pattern to Cypher string.
        
        Returns:
            Cypher representation of the node pattern
            
        Example:
            >>> node("Person").where(prop("age") > 18).to_cypher()
            >>> # Returns: "(:Person WHERE age > 18)"
        """
        parts = []
        
        # Handle variable and labels separately
        cypher_parts = []
        if self.variable:
            cypher_parts.append(self.variable)
        
        # Add labels or expressions
        if self.labels:
            # Handle label expressions
            if isinstance(self.labels, BaseLabelExpr):
                labels_str = str(self.labels)
                # Wrap complex expressions in backticks if they contain operators
                if any(op in labels_str for op in ["&", "|", "!"]):
                    labels_str = f"`{labels_str}`"
            elif isinstance(self.labels, tuple):
                # Handle tuple of strings - join with colons for multiple labels
                labels_str = ":".join(str(label) for label in self.labels)
            else:
                # Handle single string label
                labels_str = str(self.labels)
            
            cypher_parts.append(labels_str)
        
        # Combine variable and labels
        label_str = ""
        if cypher_parts:
            label_str = ":".join(cypher_parts)
        
        # Add properties
        properties_str = ""
        if self.properties:
            props = ", ".join(f"{k}: {format_value(v)}" for k, v in self.properties.items())
            properties_str = f" {{{props}}}"
        
        # Add inline WHERE condition
        # Validation already happened in __post_init__
        
        condition_str = ""
        conditions: list[str] = []  # Explicit type declaration
        
        # Add existing condition if present
        if self.condition:
            cypher_str = self.condition.to_cypher()
            if cypher_str:
                conditions.append(cypher_str)
            
        # Add APOC degree condition if needed
        if self.max_degree is not None:
            # Determine APOC function based on direction
            if self.degree_direction == "in":
                func_name = "apoc.node.degree.in"
            elif self.degree_direction == "out":
                func_name = "apoc.node.degree.out"
            else:
                func_name = "apoc.node.degree"
            
            # Build function arguments
            args = [self.variable]
            if self.degree_rel_type:
                args.append(f"'{self.degree_rel_type}'")
                
            apoc_call = f"{func_name}({', '.join(args)}) < {self.max_degree}"
            conditions.append(apoc_call)
        
        # Combine all conditions, filtering out any None values
        if conditions:
            valid_conditions = [c for c in conditions if c is not None]
            condition_str = " WHERE " + " AND ".join(valid_conditions)
        
        return f"({label_str}{properties_str}{condition_str})"
    
    def relationship(self, rel_type: str = "", direction: str = "-", variable: Optional[str] = None, **properties: Any) -> "PathPattern":
        """
        Create a relationship pattern starting from this node and return a PathPattern.
        
        Args:
            rel_type: Relationship type (e.g., "KNOWS", "FOLLOWS")
            direction: Relationship direction ("<", ">", or "-" for undirected, default: "-")
            variable: Optional variable name for the relationship
            **properties: Relationship properties
            
        Returns:
            A PathPattern object containing the node and relationship
            
        Example:
            >>> person = node("p", "Person")
            >>> path = person.relationship("KNOWS", direction=">")
            >>> # The path can be extended: path.node("f", "Person") 
            >>> # Generates: (p:Person)-[:KNOWS]->(f:Person)
        """
        # Import locally to avoid circular dependency
        from .relationship_pattern import RelationshipPattern
        from .path_pattern import PathPattern
        
        # Map direction to RelationshipPattern's internal representation
        if direction in ("->", ">"):
            direction = ">"
        elif direction in ("<-", "<"):
            direction = "<"
        elif direction not in ("-", "--"):
            direction = "-"
        
        # Create the relationship pattern
        rel = RelationshipPattern(
            direction=direction,
            variable=variable,
            type=rel_type,
            properties=properties
        )
        
        # Return a PathPattern containing both the node and the relationship
        return PathPattern([self, rel])
        
    def __add__(self, other: Union[NodePattern, RelationshipPattern, PathPattern]) -> PathPattern:  # Remove quotes around types
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
