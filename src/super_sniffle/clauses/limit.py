from dataclasses import dataclass
from typing import Optional

from .clause import Clause


@dataclass(frozen=True)
class LimitClause(Clause):
    """Represents a LIMIT clause in a Cypher query."""
    count: int

    def to_cypher(self, indent: Optional[str] = None) -> str:
        """Convert the LIMIT clause to a Cypher string."""
        prefix = indent if indent is not None else ""
        return f"{prefix}LIMIT {self.count}"
