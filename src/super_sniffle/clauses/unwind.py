"""
UNWIND clause implementation for Cypher queries.
"""

from dataclasses import dataclass
from typing import Union

from .clause import Clause
from ..ast.expressions import Expression


@dataclass(frozen=True)
class UnwindClause(Clause):
    """
    Represents an UNWIND clause in a Cypher query.
    """
    expression: Expression
    variable: str

    def to_cypher(self) -> str:
        """
        Convert the UNWIND clause to a Cypher string.
        """
        return f"UNWIND {self.expression.to_cypher()} AS {self.variable}"
