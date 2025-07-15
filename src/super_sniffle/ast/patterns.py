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

# Label expression classes for advanced label matching
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

# Helper function for cleaner syntax
def L(label: str) -> LabelAtom:
    """Create a label atom from a string."""
    return LabelAtom(label)


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
                object.__setattr__(self, "labels", tuple(item.label if isinstance(item, LabelAtom) else item for item in converted))
    
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
            >>> node("Person").where(prop("age") > 18).to_cypher()
            >>> # Returns: "(:Person WHERE age > 18)"
        """
        result = f"({self.variable if self.variable else ''}"
        
        # Add labels or expressions
        if self.labels:
            if isinstance(self.labels, BaseLabelExpr):
                result += ":" + str(self.labels)
            elif isinstance(self.labels, tuple):
                # Handle tuple of strings or BaseLabelExpr
                labels_str = ":".join(str(label) for label in self.labels)
                result += ":" + labels_str
            else:
                result += ":" + str(self.labels)
        
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

    def __add__(self, other: Union['NodePattern', 'RelationshipPattern', 'PathPattern']) -> 'PathPattern':
        """Enable operator overloading for path construction."""
        if isinstance(other, NodePattern):
            return PathPattern([self, other])  # Will automatically insert implicit relationship
        elif isinstance(other, RelationshipPattern):
            return PathPattern([self, other])
        elif isinstance(other, PathPattern):
            return PathPattern([self]).concat(other)
        else:
            raise TypeError(f"Cannot add NodePattern to {type(other)}")


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
            rel_content += ":" + self.type
        
        if self.properties:
            props_str = ", ".join(f"{k}: {_format_value(v)}" 
                                for k, v in self.properties.items())
            rel_content += f" {{{props_str}}}"
        
        # Add inline WHERE condition
        if self.condition:
            rel_content += f" WHERE {self.condition.to_cypher()}"
        
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
        else:  # undirected
            return f"-[{rel_content}]-"

    def __add__(self, other: Union['NodePattern', 'PathPattern']) -> 'PathPattern':
        """Enable operator overloading for path construction."""
        if isinstance(other, NodePattern):
            return PathPattern([self, other])
        elif isinstance(other, PathPattern):
            return PathPattern([self]).concat(other)
        else:
            raise TypeError(f"Cannot add RelationshipPattern to {type(other)}")


@dataclass(frozen=True)
class PathPattern:
    """
    Represents a path pattern in a Cypher query.
    
    A path is a sequence of alternating nodes and relationships that form
    a traversal pattern in the graph.
    
    Attributes:
        elements: List of NodePattern, RelationshipPattern, or PathPattern objects
        variable: Optional variable name for the path
        condition: Optional WHERE condition for the entire path
    """
    elements: Sequence[Union[NodePattern, RelationshipPattern, 'PathPattern']]
    variable: Optional[str] = None
    condition: Optional[Expression] = None
    
    def __post_init__(self):
        """Automatically insert implicit relationships between consecutive nodes."""
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
        path_str = "".join(elem.to_cypher() for elem in self.elements)
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
        Add a WHERE condition to the entire path pattern.
        
        Args:
            condition: Expression representing the WHERE condition
            
        Returns:
            New PathPattern with the condition added
            
        Raises:
            ValueError: If attempting to add condition to an incomplete path
        """
        # Cannot add condition to incomplete path (ending with relationship)
        if self.elements and isinstance(self.elements[-1], RelationshipPattern):
            raise ValueError("Cannot add condition to incomplete path")
        return replace(self, condition=condition)

    def concat(self, other: Union['PathPattern', NodePattern, RelationshipPattern]) -> 'PathPattern':
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
        
    def __add__(self, other: Union['PathPattern', NodePattern, RelationshipPattern]) -> 'PathPattern':
        """
        Concatenate this path with another path, node, or relationship using the '+' operator.
        
        This is equivalent to calling `self.concat(other)`.
        
        Args:
            other: The pattern to concatenate to this path.
            
        Returns:
            A new PathPattern representing the concatenated path.
        """
        return self.concat(other)


def node(*labels: str, variable: Optional[str] = None, **properties: Any) -> NodePattern:
    """
    Create a node pattern with the given labels and properties.
    
    Args:
        *labels: Labels for the node
        variable: Optional variable name
        **properties: Properties for the node
        
    Returns:
        NodePattern object
    """
    return NodePattern(variable, labels, properties)


def relationship(direction: str, type: Optional[str] = None, variable: Optional[str] = None, **properties: Any) -> RelationshipPattern:
    """
    Create a relationship pattern with the given type and properties.
    
    Args:
        direction: Relationship direction ("<", ">", or "-" for undirected)
        type: Relationship type (optional)
        variable: Optional variable name
        **properties: Properties for the relationship
        
    Returns:
        RelationshipPattern object
    """
    return RelationshipPattern(direction, variable, type, properties)


def path(*elements: Union[NodePattern, RelationshipPattern, PathPattern]) -> PathPattern:
    """
    Create a path pattern from nodes, relationships, and paths.
    
    Args:
        *elements: Alternating NodePattern, RelationshipPattern, and PathPattern objects
        
    Returns:
        PathPattern object
    """
    # Flatten any PathPattern elements
    flat_elements = []
    for elem in elements:
        if isinstance(elem, PathPattern):
            flat_elements.extend(elem.elements)
        else:
            flat_elements.append(elem)
    return PathPattern(flat_elements)


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
