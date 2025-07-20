import pytest
from src.super_sniffle.api import unwind, literal, var, QueryBuilder, node
from src.super_sniffle.clauses.unwind import UnwindClause
from src.super_sniffle.ast.expressions.function_expression import FunctionExpression

def test_unwind_clause_creation():
    """Test basic UNWIND clause creation"""
    expr = literal([1,2,3])
    clause = UnwindClause(expr, "x")
    assert clause.expression == expr
    assert clause.variable == "x"

def test_unwind_to_cypher():
    """Test UNWIND clause to_cypher conversion"""
    expr = literal([1,2,3])
    clause = UnwindClause(expr, "x")
    assert clause.to_cypher() == "UNWIND [1, 2, 3] AS x"

def test_unwind_with_variable():
    """Test UNWIND with variable expression"""
    clause = UnwindClause(var("myList"), "item")
    assert clause.to_cypher() == "UNWIND myList AS item"

def test_api_unwind_function():
    """Test top-level unwind API function"""
    q = unwind(literal([1,2,3]), "num")
    assert isinstance(q, QueryBuilder)
    assert len(q.clauses) == 1
    assert isinstance(q.clauses[0], UnwindClause)
    assert q.to_cypher() == "UNWIND [1, 2, 3] AS num"

def test_query_builder_unwind():
    """Test unwind method in QueryBuilder"""
    q = QueryBuilder().unwind(literal(["a","b","c"]), "letter")
    assert len(q.clauses) == 1
    assert q.to_cypher() == "UNWIND ['a', 'b', 'c'] AS letter"

def test_unwind_with_other_clauses():
    """Test UNWIND combined with other clauses"""
    q = (
        unwind(literal([1,2,3]), "x")
        .match(node("n"))
        .return_("n")
    )
    cypher = q.to_cypher()
    assert "UNWIND [1, 2, 3] AS x" in cypher
    assert "MATCH (n)" in cypher
    assert "RETURN n" in cypher
    assert cypher.split('\n')[0] == "UNWIND [1, 2, 3] AS x"
    assert cypher.split('\n')[1] == "MATCH (n)"
    assert cypher.split('\n')[2] == "RETURN n"

def test_unwind_complex_expression():
    """Test UNWIND with a complex expression"""
    expr = FunctionExpression("keys", [var("map")])
    clause = UnwindClause(expr, "key")
    assert clause.to_cypher() == "UNWIND keys(map) AS key"
