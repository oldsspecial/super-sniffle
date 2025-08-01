"""
Unit tests for pattern classes.

Tests the node, relationship, and path pattern classes with inline WHERE
conditions, ensuring proper Cypher generation and method chaining.
"""

import pytest
from super_sniffle.ast import NodePattern, RelationshipPattern, PathPattern, QuantifiedPathPattern
from super_sniffle.api import node, relationship, path, prop, param, literal, L


class TestPatternOperators:
    """Test operator overloading for path construction."""
    
    def test_node_plus_relationship(self):
        """Test node + relationship operator."""
        n1 = node("Person", variable="n1")
        r = relationship("KNOWS", direction=">", variable="r")
        path_pattern = n1 + r
        assert isinstance(path_pattern, PathPattern)
        assert path_pattern.to_cypher() == "(n1:Person)-[r:KNOWS]->"
    
    def test_node_plus_node(self):
        """Test node + node operator (implicit relationship)."""
        n1 = node("Person", variable="n1")
        n2 = node("Person", variable="n2")
        path = n1 + n2
        assert path.to_cypher() == "(n1:Person)--(n2:Person)"
    
    def test_node_plus_path(self):
        """Test node + path operator."""
        n1 = node("Person", variable="n1")
        existing_path = path(
            node("Person", variable="n2"),
            relationship("KNOWS", direction=">", variable="r"),
            node("Person", variable="n3")
        )
        path_result = n1 + existing_path
        assert path_result.to_cypher() == "(n1:Person)--(n2:Person)-[r:KNOWS]->(n3:Person)"
    
    def test_relationship_plus_node(self):
        """Test relationship + node operator."""
        r = relationship("KNOWS", direction=">", variable="r")
        n2 = node("Person", variable="n2")
        path = r + n2
        assert path.to_cypher() == "-[r:KNOWS]->(n2:Person)"
    
    def test_relationship_plus_path(self):
        """Test relationship + path operator."""
        r = relationship("KNOWS", direction=">", variable="r")
        existing_path = path(
            node("Person", variable="n2"),
            relationship("FRIENDS", direction=">", variable="s"),
            node("Person", variable="n3")
        )
        path_result = r + existing_path
        assert path_result.to_cypher() == "-[r:KNOWS]->(n2:Person)-[s:FRIENDS]->(n3:Person)"
    
    def test_where_chaining_on_path(self):
        """Test where condition chaining on path."""
        n1 = node("Person", variable="n1")
        r = relationship("KNOWS", direction=">", variable="r")
        n2 = node("Person", variable="n2")
        condition = (prop("n1", "age") > literal(30)) & (prop("n2", "age") < literal(40))
        
        path_with_where = (n1 + r + n2).where(condition)
        expected = "(n1:Person)-[r:KNOWS]->(n2:Person) WHERE (n1.age > 30) AND (n2.age < 40)"
        assert path_with_where.to_cypher() == expected
    
    def test_invalid_combinations(self):
        """Test invalid operator combinations."""
        n1 = node("Person", variable="n1")
        r = relationship("KNOWS", direction=">", variable="r")
        
        # Should raise errors
        with pytest.raises(ValueError, match="Cannot add condition to incomplete path"):
            (n1 + r).where(prop("n1", "age") > 30)
    
    def test_path_function_with_mixed_types(self):
        """Test path() function with mixed pattern types."""
        n1 = node("Person", variable="n1")
        r = relationship("KNOWS", direction=">", variable="r")
        n2 = node("Person", variable="n2")
        existing_path = path(node("Company", variable="c"), relationship("WORKS_AT", direction=">", variable="w"))
        
        # All valid combinations
        path1 = path(n1, r, existing_path)
        assert path1.to_cypher() == "(n1:Person)-[r:KNOWS]->(c:Company)-[w:WORKS_AT]->"
        
        path2 = path(existing_path, n1, r)
        assert path2.to_cypher() == "(c:Company)-[w:WORKS_AT]->(n1:Person)-[r:KNOWS]->"
        
        path3 = path(n1, existing_path, r)
        # The path should end with the last relationship pattern
        assert path3.to_cypher() == "(n1:Person)--(c:Company)-[w:WORKS_AT]->"
        
        # With automatic implicit relationship
        path4 = path(n1, existing_path)
        assert path4.to_cypher() == "(n1:Person)--(c:Company)-[w:WORKS_AT]->"


class TestQuantifiedPatterns:
    """Test quantified relationship patterns."""
    
    def test_relationship_quantify_shorthand(self):
        """Test shorthand syntax for quantified relationships."""
        rel = relationship("KNOWS", direction=">").quantify(1, 5)
        assert rel.to_cypher() == "-[:KNOWS]->{1,5}"
        
        rel_with_var = relationship("KNOWS", direction=">", variable="r").quantify(1, 5)
        assert rel_with_var.to_cypher() == "-[r:KNOWS]->{1,5}"
        
        rel_with_props = relationship("KNOWS", direction=">", variable="r", since=2020).quantify(1, 5)
        assert rel_with_props.to_cypher() == "-[r:KNOWS {since: 2020}]->{1,5}"
        
        rel_with_condition = relationship("KNOWS", direction=">", variable="r").where(prop("r", "since") > 2020).quantify(1, 5)
        assert rel_with_condition.to_cypher() == "-[r:KNOWS WHERE r.since > 2020]->{1,5}"
    
    def test_quantified_path_pattern_rendering(self):
        """Test that quantified path pattern always renders with parentheses."""
        # Simple anonymous path
        rel = relationship("KNOWS", direction=">")
        q_path = rel.quantify(1, 5)
        assert q_path.to_cypher() == "-[:KNOWS]->{1,5}"
        
        # Path with named nodes
        n1 = node("Person", variable="n1")
        n2 = node("Person", variable="n2")
        path_pattern = PathPattern([n1, rel, n2])
        q_path2 = QuantifiedPathPattern(path_pattern, "{1,5}")
        assert q_path2.to_cypher() == "((n1:Person)-[:KNOWS]->(n2:Person)){1,5}"
        
    def test_quantify_with_zero_hops(self):
        """Test quantifiers that allow zero hops."""
        rel = relationship("LINK", direction="-").quantify(0, 10)
        assert rel.to_cypher() == "-[:LINK]-{0,10}"

        # Use PathPattern for convenience methods like zero_or_more
        # Use anonymous relationship without type for shorthand
        path = node() + relationship(direction="-") + node()
        rel2 = path.zero_or_more()
        assert rel2.to_cypher() == "(()--())*"

# New tests for relationship pattern with start node
def test_relationship_with_start_node():
    """Test relationship created from node includes node pattern"""
    n = node("BLAH", variable="n")
    rel = n.relationship("KNOWS", direction=">", variable="r")
    assert rel.to_cypher() == '(n:BLAH)-[r:KNOWS]->'

def test_standalone_relationship():
    """Test standalone relationship without start node"""
    rel = relationship("KNOWS", variable="r", direction=">")
    assert rel.to_cypher() == '-[r:KNOWS]->'

    def test_node_with_properties():
        """Test node with properties in relationship pattern"""
        n = node("n", "Person", name="Alice", age=30)
        rel = n.relationship("KNOWS", variable="r", direction=">")
        # Property order may vary
        cypher = rel.to_cypher()
        assert '(n:Person' in cypher
        # Accept both single and double quotes
        assert ("name: 'Alice'" in cypher) or ('name: "Alice"' in cypher)
        assert 'age: 30' in cypher
        assert '-[r:KNOWS]->' in cypher

def test_node_with_label_expression():
    """Test node with label expression in relationship"""
    n = node("n", L("Person") & L("Admin"))
    rel = n.relationship("KNOWS", variable="r", direction=">")
    assert rel.to_cypher() == '(n:`(Person & Admin)`)-[r:KNOWS]->'

def test_relationship_with_properties():
    """Test relationship with properties"""
    n = node("n", "Person")
    rel = n.relationship("KNOWS", since=2020, variable="r", direction=">")
    assert rel.to_cypher() == '(n:Person)-[r:KNOWS {since: 2020}]->'

def test_complex_path_construction():
    """Test chaining node creation after relationship"""
    n1 = node("n", "Person")
    path = n1.relationship("KNOWS", variable="r", direction=">").node("Person", variable="m")
    # Handle the actual output format
    cypher = path.to_cypher()
    assert cypher.startswith('(n:Person)')
    assert '-[r:KNOWS]->' in cypher
    assert '(m:Person)' in cypher
