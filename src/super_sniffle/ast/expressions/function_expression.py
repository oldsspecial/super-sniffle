from .expression import Expression

class FunctionExpression(Expression):
    def __init__(self, function_name: str, arguments: list, distinct: bool = False):
        self.function_name = function_name
        self.arguments = arguments
        self.distinct = distinct
    
    def to_cypher(self) -> str:
        if self.function_name.lower() == "count" and len(self.arguments) == 0:
            return "count(*)"
        args_str = ", ".join(arg.to_cypher() for arg in self.arguments)
        distinct_str = "DISTINCT " if self.distinct else ""
        return f"{self.function_name}({distinct_str}{args_str})"
        
    def as_(self, alias: str) -> str:
        return f"{self.to_cypher()} AS {alias}"
