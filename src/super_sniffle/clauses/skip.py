"""
SKIP clause implementation for Cypher queries.
"""

from dataclasses import dataclass
from typing import Union

from .clause import Clause


@dataclass(frozen=True)
class SkipClause(Clause):
    """
    Represents a SKIP clause in a Cypher query.
    """
    count: Union[int, str]

    def to_cypher(self) -> str:
        """
        Convert the SKIP clause to a Cypher string.
        """
        count_str = (
            self.count.to_cypher() if hasattr(self.count, 'to_cypher')
            else str(self.count)
        )
        return f"SKIP {count_str}"

