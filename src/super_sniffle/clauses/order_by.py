from dataclasses import dataclass
from typing import List, Optional

from .clause import Clause
from ..ast.expressions.order_by_expression import OrderByExpression


@dataclass(frozen=True)
class OrderByClause(Clause):
    """Represents an ORDER BY clause in a Cypher query."""
    expressions: List[OrderByExpression]

    def to_cypher(self, indent: Optional[str] = None) -> str:
        """
        Convert the ORDER BY clause to a Cypher string.
        """
        prefix = indent if indent is not None else ""
        order_str = ", ".join(expr.to_cypher() for expr in self.expressions)
        return f"{prefix}ORDER BY {order_str}"
