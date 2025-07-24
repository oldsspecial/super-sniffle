from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Union

from .clause import Clause


@dataclass(frozen=True)
class ReturnClause(Clause):
    """Represents a RETURN clause in a Cypher query."""
    projections: List[Tuple[str, Optional[str]]] = field(default_factory=list)
    distinct: bool = False

    def __post_init__(self):
        """Validate the RETURN clause configuration."""
        if not self.projections:
            raise ValueError("RETURN clause requires at least one projection")
            
        # Validate projection items
        for expr, alias in self.projections:
            if not expr:
                raise ValueError("Projection expression cannot be empty")

    def to_cypher(self, indent: Optional[str] = None) -> str:
        """
        Convert the RETURN clause to a Cypher string.
        """
        prefix = indent if indent is not None else ""
        distinct_str = " DISTINCT" if self.distinct else ""
        
        # Format projections with optional aliases
        projection_strs = []
        for expr, alias in self.projections:
            if alias:
                projection_strs.append(f"{expr} AS {alias}")
            else:
                projection_strs.append(expr)
                
        return f"{prefix}RETURN{distinct_str} {', '.join(projection_strs)}"
