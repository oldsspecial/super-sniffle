import pytest
from super_sniffle.api import use, node, prop, var, param, call_subquery, unwind, literal, relationship, path
from super_sniffle.ast.expressions.function_expression import FunctionExpression
from super_sniffle.ast.expressions.variable import Variable

def test_basic_use_clause():
    """Test simple USE clause with database name."""
    query = use("neo4j").match(node("n")).return_("n")
    expected = "USE neo4j\nMATCH (n)\nRETURN n"
    assert query.to_cypher() == expected

def test_use_with_parameter():
    """Test USE clause with parameter binding."""
    query = use(param("database")).match(node("n")).return_("n")
    expected = "USE $database\nMATCH (n)\nRETURN n"
    assert query.to_cypher() == expected

def test_use_clause_ordering():
    """Test USE clause appears before MATCH."""
    query = use("movies").match(node("m:Movie")).where(prop("m", "year") > literal(2000)).return_("m.title")
    expected = "USE movies\nMATCH (m:Movie)\nWHERE m.year > 2000\nRETURN m.title"
    assert query.to_cypher() == expected

def test_use_with_complex_query():
    """Test USE clause with complex query patterns."""
    # Create path pattern using path function
    p_node = node("Person", variable="p")
    f_node = node("Person", variable="f")
    knows_rel = relationship("KNOWS", direction=">")
    pattern = path(p_node, knows_rel, f_node)
    query = (
        use("social_network")
        .match(pattern)
        .where(prop("p", "name") == literal("Alice"))
        .return_("f.name")
    )
    expected = "USE social_network\nMATCH (p:Person)-[:KNOWS]->(f:Person)\nWHERE p.name = 'Alice'\nRETURN f.name"
    assert query.to_cypher() == expected

def test_use_clause_empty_database_name():
    """Test validation for empty database name."""
    with pytest.raises(ValueError):
        use("")

def test_use_clause_special_characters():
    """Test USE clause with database names containing special characters."""
    query = use("my-database_123").match(node("n")).return_("n")
    expected = "USE my-database_123\nMATCH (n)\nRETURN n"
    assert query.to_cypher() == expected

def test_use_in_call_subquery():
    """Test USE clause within CALL subquery."""
    subquery = use("movies").match(node("m:Movie")).return_("m.title")
    query = call_subquery(subquery).return_("count(*) AS movie_count")
    expected = "CALL() {\n  USE movies\n  MATCH (m:Movie)\n  RETURN m.title\n}\nRETURN count(*) AS movie_count"
    assert query.to_cypher() == expected

def test_use_with_expression():
    """Test USE clause with variable expression."""
    query = use(var("graphName")).match(node("n")).return_("n")
    expected = "USE graphName\nMATCH (n)\nRETURN n"
    assert query.to_cypher() == expected

def test_use_with_parameter_in_call():
    """Test USE with parameter in CALL subquery."""
    subquery = use(param("db")).match(node("n")).return_("n")
    query = call_subquery(subquery).return_("count(n) AS node_count")
    expected = "CALL() {\n  USE $db\n  MATCH (n)\n  RETURN n\n}\nRETURN count(n) AS node_count"
    assert query.to_cypher() == expected

def test_unwind_call_with_use():
    """Test UNWIND with CALL containing USE clause."""
    # Create function expression manually since no public helper exists
    graph_expr = FunctionExpression("graph.byName", [Variable("graphName")])
    subquery = (
        use(graph_expr)
        .match(node("m:Movie"))
        .return_("m.title AS title")
    )
    query = (
        unwind(literal(["cineasts.latest", "cineasts.upcoming"]), "graphName")
        .call_subquery(subquery)
        .return_("graphName, title")
    )
    expected = (
        "UNWIND ['cineasts.latest', 'cineasts.upcoming'] AS graphName\n"
        "CALL() {\n"
        "  USE graph.byName(graphName)\n"
        "  MATCH (m:Movie)\n"
        "  RETURN m.title AS title\n"
        "}\n"
        "RETURN graphName, title"
    )
    assert query.to_cypher() == expected

def test_multiple_use_clauses():
    """Test that last USE clause takes precedence."""
    query = (
        use("old_db")
        .use("new_db")
        .match(node("n"))
        .return_("n")
    )
    expected = "USE new_db\nMATCH (n)\nRETURN n"
    assert query.to_cypher() == expected
