from .expression import Expression

class Parameter(Expression):
    def __init__(self, name: str):
        self.name = name
    
    def to_cypher(self) -> str:
        return f"${self.name}"
