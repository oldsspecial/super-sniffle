from typing import Any

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
