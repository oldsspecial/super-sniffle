from .expression import Expression
from typing import Any

class Literal(Expression):
    def __init__(self, value: Any):
        self.value = value
    
    def to_cypher(self) -> str:
        if isinstance(self.value, str):
            escaped = self.value.replace('"', '\\"')
            return f'"{escaped}"'
        elif isinstance(self.value, bool):
            return "true" if self.value else "false"
        elif self.value is None:
            return "null"
        else:
            return str(self.value)
