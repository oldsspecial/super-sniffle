"""
MATCH clause implementation for Cypher queries.
"""

from dataclasses import dataclass
from typing import List, Union

from .clause import Clause
from ..ast import NodePattern, RelationshipPattern, PathPattern, QuantifiedPathPattern


@dataclass(frozen=True)
class MatchClause(Clause):
    """
    Represents a MATCH clause in a Cypher query.
    """
    patterns: List[Union[NodePattern, RelationshipPattern, PathPattern, QuantifiedPathPattern]]

    def to_cypher(self) -> str:
        """
        Convert the MATCH clause to a Cypher string.
        """
        patterns_str = ", ".join(p.to_cypher() for p in self.patterns)
        return f"MATCH {patterns_str}"

@dataclass(frozen=True)
class OptionalMatchClause(Clause):
    """
    Represents an OPTIONAL MATCH clause in a Cypher query.
    """
    patterns: List[Union[NodePattern, RelationshipPattern, PathPattern, QuantifiedPathPattern]]

    def to_cypher(self) -> str:
        """
        Convert the OPTIONAL MATCH clause to a Cypher string.
        """
        patterns_str = ", ".join(p.to_cypher() for p in self.patterns)
        return f"OPTIONAL MATCH {patterns_str}"
