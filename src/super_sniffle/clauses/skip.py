from dataclasses import dataclass
from typing import Optional, Union

from super_sniffle.ast.expressions.expression import Expression
from .clause import Clause


@dataclass(frozen=True)
class SkipClause(Clause):
    """Represents a SKIP clause in a Cypher query."""
    count: Union[int, Expression]

    def to_cypher(self, indent: Optional[str] = None) -> str:
        """Convert the SKIP clause to a Cypher string."""
        prefix = indent if indent is not None else ""
        if isinstance(self.count, int):
            return f"{prefix}SKIP {self.count}"
        return f"{prefix}SKIP {self.count.to_cypher()}"
