from typing import Any

"""
Utility functions for pattern classes
"""

def format_value(value: Any) -> str:
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
