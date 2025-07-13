"""
WITH clause implementation for Cypher queries.
"""

from dataclasses import dataclass
from typing import List, Union, Tuple

from .clause import Clause


@dataclass(frozen=True)
class WithClause(Clause):
    """
    Represents a WITH clause in a Cypher query.
    """
    projections: List[Union[str, Tuple[str, str]]]
    distinct: bool = False

    def to_cypher(self) -> str:
        """
        Convert the WITH clause to a Cypher string.
        """
        distinct_str = "DISTINCT " if self.distinct else ""
        
        projection_strings = []
        for proj in self.projections:
            if isinstance(proj, str):
                projection_strings.append(proj)
            else:  # It's a tuple (expression, alias)
                expression, alias = proj
                projection_strings.append(f"{expression} AS {alias}")
        
        projections_str = ", ".join(projection_strings)
        return f"WITH {distinct_str}{projections_str}"

