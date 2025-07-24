from dataclasses import dataclass, field
from typing import List, Optional, Union, TYPE_CHECKING

from super_sniffle.ast.expressions.expression import Expression
from super_sniffle.clauses.clause import Clause

if TYPE_CHECKING:
    from .yield_ import YieldClause


@dataclass(frozen=True)
class CallProcedureClause(Clause):
    """
    AST representation of a CALL procedure clause for invoking database procedures.
    
    Attributes:
        procedure_name: Name of the procedure to call (e.g., 'db.labels')
        arguments: List of arguments to pass to the procedure
        optional: Whether this is an OPTIONAL CALL
        yield_clause: Optional YIELD clause for handling procedure output
    """
    procedure_name: str
    arguments: List[Union[str, Expression]] = field(default_factory=list)
    optional: bool = False
    yield_clause: Optional['YieldClause'] = None

    def __post_init__(self):
        """Validate procedure name and arguments."""
        if not self.procedure_name:
            raise ValueError("Procedure name cannot be empty")
        
        # Validate that all arguments are either strings or Expressions
        for arg in self.arguments:
            if not isinstance(arg, (str, Expression)):
                raise TypeError(f"Procedure arguments must be strings or Expressions, got {type(arg)}")

    def to_cypher(self, indent: Optional[str] = None) -> str:
        """Generates Cypher representation of the CALL procedure clause."""
        prefix = indent if indent is not None else ""
        
        # Build OPTIONAL CALL if specified
        call_keyword = "OPTIONAL CALL" if self.optional else "CALL"
        
        # Build arguments string
        def format_arg(arg):
            if isinstance(arg, str):
                return f"'{arg}'"  # Wrap strings in single quotes
            elif isinstance(arg, Expression):
                return arg.to_cypher()
            return str(arg)
        
        args_str = ", ".join(format_arg(arg) for arg in self.arguments)
        
        # Build the base CALL clause
        cypher = f"{prefix}{call_keyword} {self.procedure_name}({args_str})"
        
        # Append YIELD clause if present
        if self.yield_clause:
            cypher += "\n" + self.yield_clause.to_cypher(indent)
            
        return cypher
