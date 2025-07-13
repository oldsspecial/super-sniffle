"""
RETURN clause implementation for Cypher queries.
"""

from dataclasses import dataclass
from typing import List

from .clause import Clause


@dataclass(frozen=True)
class ReturnClause(Clause):
    """
    Represents a RETURN clause in a Cypher query.
    """
    projections: List[str]
    distinct: bool = False

    def to_cypher(self) -> str:
        """
        Convert the RETURN clause to a Cypher string.
        """
        distinct_str = "DISTINCT " if self.distinct else ""
        projections_str = ", ".join(self.projections)
        return f"RETURN {distinct_str}{projections_str}"

