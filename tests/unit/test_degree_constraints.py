"""
Unit tests for degree constraint functionality in node patterns.
"""

import pytest
from super_sniffle import node
from super_sniffle.ast.expressions import Literal
from super_sniffle.ast.patterns.node_pattern import NodePattern

def test_basic_degree_constraint():
    """Test basic max_degree constraint."""
    pattern = node("Person", variable="p", max_degree=5)
    assert pattern.to_cypher() == "(p:Person WHERE apoc.node.degree(p) < 5)"

def test_direction_constraint():
    """Test degree constraint with direction."""
    pattern = node("Person", variable="p", max_degree=3, degree_direction="out")
    assert pattern.to_cypher() == "(p:Person WHERE apoc.node.degree.out(p) < 3)"

def test_rel_type_constraint():
    """Test degree constraint with relationship type."""
    pattern = node("Person", variable="p", max_degree=5, degree_rel_type="KNOWS")
    assert pattern.to_cypher() == "(p:Person WHERE apoc.node.degree(p, 'KNOWS') < 5)"

def test_direction_and_rel_type_constraint():
    """Test combined direction and relationship type constraints."""
    pattern = node("Person", variable="p", max_degree=2, 
                   degree_direction="in", degree_rel_type="FOLLOWS")
    assert pattern.to_cypher() == "(p:Person WHERE apoc.node.degree.in(p, 'FOLLOWS') < 2)"

def test_combined_with_properties():
    """Test degree constraint combined with node properties."""
    pattern = node("Person", variable="p", max_degree=4, name="Alice", age=30)
    result = pattern.to_cypher()
    assert result.startswith("(p:Person {")
    assert "name: 'Alice'" in result
    assert "age: 30" in result
    assert "WHERE apoc.node.degree(p) < 4" in result

def test_combined_with_where_condition():
    """Test degree constraint combined with explicit WHERE condition."""
    from super_sniffle import prop, literal
    pattern = node("Person", variable="p", max_degree=5).where(
        prop("p", "age") > literal(18)
    )
    result = pattern.to_cypher()
    assert "WHERE p.age > 18 AND apoc.node.degree(p) < 5" in result

def test_missing_variable_error():
    """Test error when variable is missing with degree constraints."""
    with pytest.raises(ValueError) as excinfo:
        node(max_degree=5)
    assert "Variable name is required" in str(excinfo.value)

def test_missing_max_degree_error():
    """Test error when max_degree is missing with other degree params."""
    with pytest.raises(ValueError) as excinfo:
        node("Person", variable="p", degree_direction="out")
    assert "max_degree must be provided" in str(excinfo.value)

def test_degree_without_constraints():
    """Test node without degree constraints remains unchanged."""
    pattern = node("Person", variable="p", name="Alice")
    assert pattern.to_cypher() == "(p:Person {name: 'Alice'})"

def test_complex_label_expression():
    """Test degree constraint with complex label expression."""
    from super_sniffle import L
    pattern = node(L("Person") & L("Admin"), variable="a", max_degree=3)
    result = pattern.to_cypher()
    assert "a:`(Person & Admin)`" in result
    assert "WHERE apoc.node.degree(a) < 3" in result
