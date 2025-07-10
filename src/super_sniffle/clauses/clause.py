from dataclasses import dataclass


@dataclass(frozen=True)
class Clause:
    """Base class for all Cypher clauses."""

    def to_cypher(self) -> str:
        """Convert clause to Cypher string."""
        raise NotImplementedError("Subclasses must implement to_cypher()")