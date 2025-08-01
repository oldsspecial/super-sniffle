"""
Unit tests for path operator overloading functionality.
"""

import pytest
from super_sniffle.api import node, relationship, path, prop, literal
from super_sniffle.ast import PathPattern

class TestPathOperators:
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
        r = relationship("KNOWS", direction=">",variable= "r")
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
        r = relationship(">", "r", "KNOWS")
        
        # Should raise errors
        with pytest.raises(TypeError, match="Cannot add NodePattern to <class 'str'>"):
            n1 + "invalid"
            
        with pytest.raises(TypeError, match="Cannot add RelationshipPattern to <class 'int'>"):
            r + 42
            
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
