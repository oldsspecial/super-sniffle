"""
ORDER BY clause implementation for Cypher queries.
"""

from dataclasses import dataclass
from typing import List, Union

from ..ast.expressions import OrderByExpression
from .clause import Clause


@dataclass(frozen=True)
class OrderByClause(Clause):
    """
    Represents an ORDER BY clause in a Cypher query.
    """
    expressions: List[Union[str, OrderByExpression]]

    def to_cypher(self) -> str:
        """
        Convert the ORDER BY clause to a Cypher string.
        """
        expressions_str = ", ".join(
            expr.to_cypher() if hasattr(expr, 'to_cypher') else str(expr) 
            for expr in self.expressions
        )
        return f"ORDER BY {expressions_str}"

