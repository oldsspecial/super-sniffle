import pytest
from super_sniffle import match, node, prop, count, sum, avg, min, max

def test_count_function():
    """Test count function in RETURN clause."""
    query = match(node("Person", variable="p")).return_(count().as_("total"))
    assert query.to_cypher() == "MATCH (p:Person)\nRETURN count(*) AS total"

def test_count_distinct():
    """Test count distinct function."""
    query = match(node("Person", variable="p")).return_(count(prop("p", "name"), distinct=True).as_("unique_names"))
    assert query.to_cypher() == "MATCH (p:Person)\nRETURN count(DISTINCT p.name) AS unique_names"

def test_sum_function():
    """Test sum function."""
    query = match(node("Person", variable="p")).return_(sum(prop("p", "age")).as_("total_age"))
    assert query.to_cypher() == "MATCH (p:Person)\nRETURN sum(p.age) AS total_age"

def test_avg_function():
    """Test average function."""
    query = match(node("Person", variable="p")).return_(avg(prop("p", "age")).as_("avg_age"))
    assert query.to_cypher() == "MATCH (p:Person)\nRETURN avg(p.age) AS avg_age"

def test_min_function():
    """Test min function."""
    query = match(node("Person", variable="p")).return_(min(prop("p", "age")).as_("min_age"))
    assert query.to_cypher() == "MATCH (p:Person)\nRETURN min(p.age) AS min_age"

def test_max_function():
    """Test max function."""
    query = match(node("Person", variable="p")).return_(max(prop("p", "age")).as_("max_age"))
    assert query.to_cypher() == "MATCH (p:Person)\nRETURN max(p.age) AS max_age"

def test_group_by_with_aggregation():
    """Test aggregation with GROUP BY."""
    query = match(node("Person", variable="p")) \
        .return_("p.department", count().as_("employees")) \
        .group_by("p.department")
    assert query.to_cypher() == "MATCH (p:Person)\nRETURN p.department, count(*) AS employees\nGROUP BY p.department"
