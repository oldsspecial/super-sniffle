from .clause import Clause
from typing import List

class GroupByClause(Clause):
    """
    Represents a GROUP BY clause in a Cypher query.
    
    Attributes:
        expressions: List of expressions to group by
    """
    def __init__(self, expressions: List[str]):
        self.expressions = expressions
        
    def to_cypher(self) -> str:
        """
        Convert the GROUP BY clause to a Cypher string.
        
        Returns:
            Cypher representation of the GROUP BY clause
        """
        return f"GROUP BY {', '.join(self.expressions)}"
