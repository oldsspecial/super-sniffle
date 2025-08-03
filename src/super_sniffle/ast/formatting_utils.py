from typing import Any

def format_value(value: Any) -> str:
    """
    Format a value for use in Cypher expressions and property constraints.
    
    Args:
        value: The value to format
        
    Returns:
        String representation of the value in Cypher format
        
    Example:
        >>> format_value(42) -> '42'
        >>> format_value("text") -> '"text"'
        >>> format_value(True) -> 'true'
        >>> format_value([1,2]) -> '[1,2]'
    """
    if isinstance(value, str):
        # Escape double quotes in the string
        escaped = value.replace('"', '\\"')
        return f'"{escaped}"'
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif value is None:
        return "null"
    elif isinstance(value, (list, tuple)):
        # Format each element recursively
        formatted_elements = [format_value(item) for item in value]
        return f'[{", ".join(formatted_elements)}]'
    elif isinstance(value, dict):
        # Format each key-value pair
        formatted_pairs = [f'{key}: {format_value(val)}' for key, val in value.items()]
        return f'{{{", ".join(formatted_pairs)}}}'
    else:
        return str(value)
