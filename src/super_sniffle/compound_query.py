"""
Compound query for UNION and UNION ALL operations.
"""

from __future__ import annotations
from typing import List, TYPE_CHECKING
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from .api import QueryBuilder


@dataclass(frozen=True)
class CompoundQuery:
    """
    Represents a compound query using UNION or UNION ALL.
    """
    queries: List[QueryBuilder] = field(default_factory=list)
    union_operators: List[str] = field(default_factory=list)

    def union(self, other: QueryBuilder) -> "CompoundQuery":
        """
        Adds a query to be combined with UNION.
        """
        return CompoundQuery(
            queries=self.queries + [other],
            union_operators=self.union_operators + ["UNION"]
        )

    def union_all(self, other: QueryBuilder) -> "CompoundQuery":
        """
        Adds a query to be combined with UNION ALL.
        """
        return CompoundQuery(
            queries=self.queries + [other],
            union_operators=self.union_operators + ["UNION ALL"]
        )

    def to_cypher(self) -> str:
        """
        Converts the compound query to a Cypher string.
        """
        result = [self.queries[0].to_cypher()]
        for i, query in enumerate(self.queries[1:]):
            result.append(self.union_operators[i])
            result.append(query.to_cypher())
        return "\n".join(result)
