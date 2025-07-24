import pytest
from super_sniffle.api import call_procedure, QueryBuilder, var, literal

def test_basic_yield_clause():
    query = call_procedure("db.labels").yield_("label")
    cypher = query.to_cypher()
    assert cypher == "CALL db.labels()\nYIELD label"

def test_yield_with_alias():
    query = call_procedure("db.propertyKeys").yield_(("propertyKey", "prop"))
    cypher = query.to_cypher()
    assert cypher == "CALL db.propertyKeys()\nYIELD propertyKey AS prop"

def test_yield_wildcard():
    query = call_procedure("db.labels").yield_(wildcard=True)
    cypher = query.to_cypher()
    assert cypher == "CALL db.labels()\nYIELD *"

def test_yield_multiple_columns():
    query = call_procedure("apoc.meta.stats").yield_("label", ("propertyCount", "count"), "nodeCount")
    cypher = query.to_cypher()
    assert cypher == "CALL apoc.meta.stats()\nYIELD label, propertyCount AS count, nodeCount"

def test_yield_in_query_builder():
    query = QueryBuilder().call_procedure("db.labels").yield_("label")
    cypher = query.to_cypher()
    assert cypher == "CALL db.labels()\nYIELD label"

def test_yield_with_other_clauses():
        query = (
            QueryBuilder()
            .call_procedure("db.labels")
            .yield_("label")
            .where(var("label").contains(literal("User")))
            .return_("label")
        )
        cypher = query.to_cypher()
        assert cypher == "CALL db.labels()\nYIELD label\nWHERE label CONTAINS 'User'\nRETURN label"
