from dataclasses import dataclass
from typing import List, Optional

from .clause import Clause


@dataclass(frozen=True)
class GroupByClause(Clause):
    """
    Represents a GROUP BY clause in a Cypher query.
    """
    expressions: List[str]

    def to_cypher(self, indent: Optional[str] = None) -> str:
        """
        Convert the GROUP BY clause to a Cypher string.
        """
        prefix = indent if indent is not None else ""
        return f"{prefix}GROUP BY {', '.join(self.expressions)}"
