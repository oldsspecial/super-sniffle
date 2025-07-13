"""
WHERE clause implementation for Cypher queries.
"""

from dataclasses import dataclass

from ..ast.expressions import Expression
from .clause import Clause


@dataclass(frozen=True)
class WhereClause(Clause):
    """
    Represents a WHERE clause in a Cypher query.
    """
    condition: Expression

    def to_cypher(self) -> str:
        """
        Convert the WHERE clause to a Cypher string.
        """
        return f"WHERE {self.condition.to_cypher()}"

