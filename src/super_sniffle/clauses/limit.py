"""
LIMIT clause implementation for Cypher queries.
"""

from dataclasses import dataclass
from typing import Union

from .clause import Clause


@dataclass(frozen=True)
class LimitClause(Clause):
    """
    Represents a LIMIT clause in a Cypher query.
    """
    count: Union[int, str]

    def to_cypher(self) -> str:
        """
        Convert the LIMIT clause to a Cypher string.
        """
        count_str = (
            self.count.to_cypher() if hasattr(self.count, 'to_cypher')
            else str(self.count)
        )
        return f"LIMIT {count_str}"

