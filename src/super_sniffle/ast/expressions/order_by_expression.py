from .expression import Expression

class OrderByExpression:
    def __init__(self, field: str, descending: bool = False):
        self.field = field
        self.descending = descending
    
    def to_cypher(self) -> str:
        direction = " DESC" if self.descending else ""
        return f"{self.field}{direction}"
