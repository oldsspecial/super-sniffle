"""
Base classes for pattern implementations to avoid circular imports.
"""

from dataclasses import dataclass
from typing import Optional, Sequence, TYPE_CHECKING
from ..expressions import Expression
from .types import PatternElement

if TYPE_CHECKING:
    from .node_pattern import NodePattern
    from .relationship_pattern import RelationshipPattern

@dataclass(frozen=True)
class BasePathPattern:
    """
    Base class for path patterns to avoid circular imports.
    """
    elements: Sequence[PatternElement]
    variable: Optional[str] = None
    condition: Optional[Expression] = None

    # Common methods that don't depend on concrete implementations
    def to_cypher(self) -> str:
        """
        Convert path pattern to Cypher string.
        """
        # Implementation must be provided in concrete classes
        raise NotImplementedError("to_cypher must be implemented in concrete classes")
