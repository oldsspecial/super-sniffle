import pytest
from super_sniffle.api import call_procedure, optional_call_procedure, QueryBuilder, var, literal

def test_basic_call_procedure():
    query = call_procedure("db.labels")
    cypher = query.to_cypher()
    assert cypher == "CALL db.labels()"

def test_call_procedure_with_arguments():
    query = call_procedure("dbms.checkConfigValue", "server.bolt.enabled", "true")
    cypher = query.to_cypher()
    assert cypher == "CALL dbms.checkConfigValue('server.bolt.enabled', 'true')"

def test_call_procedure_with_expressions():
    query = call_procedure("apoc.neighbors.tohop", var("n"), "KNOWS>", literal(1))
    cypher = query.to_cypher()
    assert cypher == "CALL apoc.neighbors.tohop(n, 'KNOWS>', 1)"

def test_optional_call_procedure():
    query = optional_call_procedure("apoc.neighbors.tohop", var("n"), "KNOWS>", literal(1))
    cypher = query.to_cypher()
    assert cypher == "OPTIONAL CALL apoc.neighbors.tohop(n, 'KNOWS>', 1)"

def test_call_procedure_in_query_builder():
    query = QueryBuilder().call_procedure("db.labels")
    cypher = query.to_cypher()
    assert cypher == "CALL db.labels()"

def test_optional_call_procedure_in_query_builder():
    query = QueryBuilder().optional_call_procedure("apoc.neighbors.tohop", var("n"), "KNOWS>", literal(1))
    cypher = query.to_cypher()
    assert cypher == "OPTIONAL CALL apoc.neighbors.tohop(n, 'KNOWS>', 1)"
