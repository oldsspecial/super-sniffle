from typing import Optional
from .clause import Clause


class NextClause(Clause):
    """
    Represents a NEXT clause in Cypher, used for sequential composition of queries.
    """
    def __init__(self):
        super().__init__()

    def to_cypher(self, indent: Optional[str] = None, **kwargs) -> str:
        """
        Convert the NEXT clause to a Cypher string.
        """
        prefix = indent if indent is not None else ""
        return f"{prefix}NEXT"
