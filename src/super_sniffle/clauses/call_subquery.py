"""
CALL subquery clause implementation for Cypher queries.

This module implements the CALL subquery functionality that allows running
subqueries with variable scoping in Neo4j Cypher.
"""

from dataclasses import dataclass
from typing import List, Optional, Union, Any

from .clause import Clause


@dataclass(frozen=True)
class CallSubqueryClause(Clause):
    """
    Represents a CALL subquery clause in a Cypher query.
    
    This implements the modern CALL subquery syntax with variable scoping:
    - CALL() { ... } - no variable scoping
    - CALL(var1, var2) { ... } - specific variable scoping
    - CALL(*) { ... } - all variables scoping
    - OPTIONAL CALL() { ... } - optional subquery
    
    Args:
        subquery: The inner query to execute as a subquery
        variables: Variable scoping specification:
            - None: CALL() - no variables
            - "*": CALL(*) - all variables
            - List[str]: CALL(var1, var2) - specific variables
        optional: Whether to make this an OPTIONAL CALL
    """
    subquery: Any  # QueryBuilder - avoiding circular import
    variables: Optional[Union[str, List[str]]] = None
    optional: bool = False

    def to_cypher(self, indent: Optional[str] = None) -> str:
        """
        Convert the CALL subquery clause to a Cypher string.
        
        Args:
            indent: Optional indentation prefix for each line
            
        Returns:
            Cypher string representation of the CALL subquery
        """
        prefix = indent if indent is not None else ""
        # Build the variable scoping part
        if self.variables is None or (isinstance(self.variables, list) and len(self.variables) == 0):
            var_scope = "()"
        elif self.variables == "*":
            var_scope = "(*)"
        elif isinstance(self.variables, str):
            var_scope = f"({self.variables})"
        elif isinstance(self.variables, list):
            var_scope = f"({', '.join(self.variables)})"
        else:
            var_scope = ""
        
        # Get the subquery Cypher with proper indentation
        body_indent = prefix + "  " if prefix else "  "
        body = self.subquery.to_cypher(indent=body_indent)
        
        # Format the CALL clause
        call_keyword = "OPTIONAL CALL" if self.optional else "CALL"
        return f"{prefix}{call_keyword}{var_scope} {{\n{body}\n{prefix}}}"
