from dataclasses import dataclass
from typing import List, Optional

from .clause import Clause


@dataclass(frozen=True)
class WithClause(Clause):
    """Represents a WITH clause in a Cypher query."""
    projections: List[str]
    distinct: bool = False

    def to_cypher(self, indent: Optional[str] = None) -> str:
        """
        Convert the WITH clause to a Cypher string.
        """
        prefix = indent if indent is not None else ""
        distinct_str = " DISTINCT" if self.distinct else ""
        
        # Process projections that could be strings or tuples (expression, alias)
        processed_projections = []
        for proj in self.projections:
            if isinstance(proj, tuple):
                # Tuple format: (expression, alias)
                processed_projections.append(f"{proj[0]} AS {proj[1]}")
            else:
                processed_projections.append(proj)
                
        projections_str = ", ".join(processed_projections)
        return f"{prefix}WITH{distinct_str} {projections_str}"
