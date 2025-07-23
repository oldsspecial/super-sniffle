from dataclasses import dataclass
from typing import Union, Optional

from super_sniffle.ast.expressions.expression import Expression
from super_sniffle.clauses.clause import Clause


@dataclass(frozen=True)
class UseClause(Clause):
    """AST representation of a USE clause for database selection.
    
    Attributes:
        database: Database name or expression resolving to a database name.
                  Can be a string, Parameter, FunctionExpression, etc.
    """
    database: Union[str, Expression]

    def __post_init__(self):
        """Validate the database name/expression."""
        if isinstance(self.database, str) and not self.database:
            raise ValueError("Database name cannot be empty")

    def to_cypher(self, indent: Optional[str] = None) -> str:
        """Generates Cypher representation of the USE clause."""
        prefix = indent if indent is not None else ""
        if isinstance(self.database, str):
            # Handle string literals
            return f"{prefix}USE {self.database}"
        else:
            # Handle expressions like parameters and function calls
            return f"{prefix}USE {self.database.to_cypher()}"
