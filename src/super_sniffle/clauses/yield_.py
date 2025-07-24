from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from super_sniffle.clauses.clause import Clause


@dataclass(frozen=True)
class YieldClause(Clause):
    """
    AST representation of a YIELD clause for handling procedure output.
    
    Attributes:
        columns: List of tuples (column_name, alias) for the YIELD clause
        wildcard: Whether to use YIELD * (returns all columns)
    """
    columns: List[Tuple[str, Optional[str]]] = field(default_factory=list)
    wildcard: bool = False

    def __post_init__(self):
        """Validate the YIELD clause configuration."""
        if self.wildcard and self.columns:
            raise ValueError("Cannot specify both wildcard and columns in YIELD clause")
        
        if not self.wildcard and not self.columns:
            raise ValueError("YIELD clause requires either columns or wildcard")
            
        # Validate column names
        for col, alias in self.columns:
            if not col:
                raise ValueError("Column name cannot be empty")

    def to_cypher(self, indent: Optional[str] = None) -> str:
        """Generates Cypher representation of the YIELD clause."""
        prefix = indent if indent is not None else ""
        
        if self.wildcard:
            return f"{prefix}YIELD *"
            
        # Format columns with optional aliases
        column_strs = []
        for col, alias in self.columns:
            if alias:
                column_strs.append(f"{col} AS {alias}")
            else:
                column_strs.append(col)
                
        return f"{prefix}YIELD {', '.join(column_strs)}"
