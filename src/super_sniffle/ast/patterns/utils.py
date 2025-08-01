from typing import Union, Any
from .node_pattern import NodePattern
from .relationship_pattern import RelationshipPattern
from .path_pattern import PathPattern

def create_path(*elements: Union[NodePattern, RelationshipPattern, PathPattern]) -> PathPattern:
    """
    Create a path pattern from nodes and relationships, ensuring proper rendering.
    
    Args:
        *elements: Alternating NodePattern and RelationshipPattern objects.
        
    Returns:
        A PathPattern object representing the combined path pattern
        
    Example:
        >>> p = node("Person", variable="p")
        >>> r = relationship("KNOWS", direction=">", variable="r")
        >>> f = node("Person", variable="f")
        >>> path = create_path(p, r, f)
    """
    flattened = []
    for elem in elements:
        if isinstance(elem, PathPattern):
            flattened.extend(elem.elements)
        else:
            flattened.append(elem)
    return PathPattern(flattened)

def format_value(value: Any) -> str:
    """
    Format a value for use in property constraints.
    
    Args:
        value: The value to format
        
    Returns:
        String representation of the value in Cypher format
        
    Example:
        >>> format_value(42) -> '42'
        >>> format_value("text") -> '"text"'
        >>> format_value(True) -> 'true'
    """
    if isinstance(value, str):
        # Escape quotes in the string
        escaped = value.replace('"', '\\"')
        return f'"{escaped}"'
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif value is None:
        return "null"
    else:
        return str(value)
