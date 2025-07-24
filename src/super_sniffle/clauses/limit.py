from dataclasses import dataclass
from typing import Optional, Union

from super_sniffle.ast.expressions.expression import Expression
from .clause import Clause


@dataclass(frozen=True)
class LimitClause(Clause):
    """Represents a LIMIT clause in a Cypher query."""
    count: Union[int, Expression]

    def to_cypher(self, indent: Optional[str] = None) -> str:
        """Convert the LIMIT clause to a Cypher string."""
        prefix = indent if indent is not None else ""
        if isinstance(self.count, int):
            return f"{prefix}LIMIT {self.count}"
        return f"{prefix}LIMIT {self.count.to_cypher()}"
