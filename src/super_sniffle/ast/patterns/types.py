"""
Common types to break circular dependencies in pattern classes.
"""

from typing import TYPE_CHECKING, Union, TypeAlias
from ..expressions import Expression

if TYPE_CHECKING:
    from .node_pattern import NodePattern
    from .relationship_pattern import RelationshipPattern
    from .path_pattern import PathPattern
    from .quantified_path_pattern import QuantifiedPathPattern

# Define type aliases to avoid circular imports
NodeType: TypeAlias = "NodePattern"
RelType: TypeAlias = "RelationshipPattern"
PathType: TypeAlias = "PathPattern"
QuantifiedPathType: TypeAlias = "QuantifiedPathPattern"

PatternElement: TypeAlias = Union[NodeType, RelType, PathType]
