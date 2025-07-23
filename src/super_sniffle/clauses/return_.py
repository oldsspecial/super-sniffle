from dataclasses import dataclass
from typing import List, Optional

from .clause import Clause


@dataclass(frozen=True)
class ReturnClause(Clause):
    """Represents a RETURN clause in a Cypher query."""
    projections: List[str]
    distinct: bool = False

    def to_cypher(self, indent: Optional[str] = None) -> str:
        """
        Convert the RETURN clause to a Cypher string.
        """
        prefix = indent if indent is not None else ""
        distinct_str = " DISTINCT" if self.distinct else ""
        projections_str = ", ".join(self.projections)
        return f"{prefix}RETURN{distinct_str} {projections_str}"
