from dataclasses import dataclass
from typing import Sequence, Union

from ..ast.patterns import NodePattern, RelationshipPattern, PathPattern, QuantifiedPathPattern
from .clause import Clause


@dataclass(frozen=True)
class OptionalMatchClause(Clause):
    patterns: Sequence[Union[NodePattern, RelationshipPattern, PathPattern, QuantifiedPathPattern]]

    def to_cypher(self) -> str:
        patterns = ", ".join(pattern.to_cypher() for pattern in self.patterns)
        return f"OPTIONAL MATCH {patterns}"
