"""
WHERE clause implementation for Cypher queries.
"""

from dataclasses import dataclass
from typing import Optional

from ..ast.expressions import Expression
from .clause import Clause


@dataclass(frozen=True)
class WhereClause(Clause):
    """
    Represents a WHERE clause in a Cypher query.
    """
    condition: Expression

    def to_cypher(self, indent: Optional[str] = None) -> str:
        """
        Convert the WHERE clause to a Cypher string.
        """
        prefix = indent if indent is not None else ""
        return f"{prefix}WHERE {self.condition.to_cypher()}"
