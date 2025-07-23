from dataclasses import dataclass
from typing import Optional

from .clause import Clause


@dataclass(frozen=True)
class SkipClause(Clause):
    """Represents a SKIP clause in a Cypher query."""
    count: int

    def to_cypher(self, indent: Optional[str] = None) -> str:
        """Convert the SKIP clause to a Cypher string."""
        prefix = indent if indent is not None else ""
        return f"{prefix}SKIP {self.count}"
