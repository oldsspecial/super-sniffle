from dataclasses import dataclass
from typing import List, Optional, Union

from .clause import Clause
from ..ast.patterns import NodePattern, RelationshipPattern, PathPattern, QuantifiedPathPattern


@dataclass(frozen=True)
class MatchClause(Clause):
    """Represents a MATCH clause in a Cypher query."""
    patterns: List[Union[NodePattern, RelationshipPattern, PathPattern, QuantifiedPathPattern]]

    def to_cypher(self, indent: Optional[str] = None) -> str:
        """
        Convert the MATCH clause to a Cypher string.
        """
        prefix = indent if indent is not None else ""
        pattern_str = ", ".join(pattern.to_cypher() for pattern in self.patterns)
        return f"{prefix}MATCH {pattern_str}"
