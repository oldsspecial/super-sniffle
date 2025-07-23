from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Clause:
    """Base class for all Cypher clauses."""

    def to_cypher(self, indent: Optional[str] = None) -> str:
        """
        Convert clause to Cypher string.
        
        Args:
            indent: Optional indentation prefix for each line. 
                    Defaults to None (no indentation).
                    
        Returns:
            Cypher string representation of the clause
        """
        raise NotImplementedError("Subclasses must implement to_cypher()")
