"""
Unit tests for pattern classes.

Tests the node, relationship, and path pattern classes with inline WHERE
conditions, ensuring proper Cypher generation and method chaining.
"""

import pytest
from super_sniffle.ast import NodePattern, RelationshipPattern, PathPattern
from super_sniffle.api import node, relationship, path, prop, param, literal


class TestNodePattern:
    """Test the NodePattern class and inline WHERE conditions."""
    
    def test_basic_node_creation(self):
        """Test basic node pattern creation."""
        n = NodePattern("p", ("Person",))
        assert n.variable == "p"
        assert n.labels == ("Person",)
        assert n.to_cypher() == "(p:Person)"
    
    def test_node_with_multiple_labels(self):
        """Test node with multiple labels."""
        n = NodePattern("u", ("User", "Admin"))
        assert n.to_cypher() == "(u:User:Admin)"
    
    def test_node_with_properties(self):
        """Test node with properties."""
        n = NodePattern("p", ("Person",), {"age": 30, "name": "Alice"})
        cypher = n.to_cypher()
        # Properties can be in any order
        assert cypher.startswith("(p:Person {")
        assert "age: 30" in cypher
        assert "name: 'Alice'" in cypher
        assert cypher.endswith("})")
    
    def test_node_with_inline_where_condition(self):
        """Test node with inline WHERE condition."""
        n = NodePattern("p", ("Person",)).where(prop("p", "age") > literal(18))
        assert n.to_cypher() == "(p:Person WHERE p.age > 18)"
    
    def test_node_with_complex_where_condition(self):
        """Test node with complex WHERE condition."""
        condition = (prop("p", "age") > literal(18)) & (prop("p", "active") == literal(True))
        n = NodePattern("p", ("Person",)).where(condition)
        expected = "(p:Person WHERE (p.age > 18) AND (p.active = true))"
        assert n.to_cypher() == expected
    
    def test_node_api_function(self):
        """Test the node() API function."""
        n = node("p", "Person", "User", age=30)
        assert isinstance(n, NodePattern)
        assert n.variable == "p"
        assert n.labels == ("Person", "User")
        assert n.properties == {"age": 30}
    
    def test_node_api_with_where(self):
        """Test the node() API function with where method."""
        n = node("p", "Person").where(prop("p", "age") > param("min_age"))
        assert n.to_cypher() == "(p:Person WHERE p.age > $min_age)"


class TestRelationshipPattern:
    """Test the RelationshipPattern class and inline WHERE conditions."""
    
    def test_basic_relationship_creation(self):
        """Test basic relationship pattern creation."""
        r = RelationshipPattern(">", "r", "KNOWS")
        assert r.direction == ">"
        assert r.variable == "r"
        assert r.type == "KNOWS"
        assert r.to_cypher() == "-[r:KNOWS]->"
    
    def test_relationship_directions(self):
        """Test all relationship directions."""
        # Outgoing
        r_out = RelationshipPattern(">", "r", "KNOWS")
        assert r_out.to_cypher() == "-[r:KNOWS]->"
        
        # Incoming
        r_in = RelationshipPattern("<", "r", "KNOWS")
        assert r_in.to_cypher() == "<-[r:KNOWS]-"
        
        # Undirected
        r_undir = RelationshipPattern("-", "r", "KNOWS")
        assert r_undir.to_cypher() == "-[r:KNOWS]-"
    
    def test_relationship_without_variable(self):
        """Test relationship without variable name."""
        r = RelationshipPattern(">", None, "KNOWS")
        assert r.to_cypher() == "-[:KNOWS]->"
    
    def test_relationship_with_single_type(self):
        """Test relationship with single type."""
        r = RelationshipPattern(">", "r", "KNOWS")
        assert r.to_cypher() == "-[r:KNOWS]->"
    
    def test_relationship_with_properties(self):
        """Test relationship with properties."""
        r = RelationshipPattern(">", "r", "KNOWS", {"since": 2020, "weight": 0.8})
        cypher = r.to_cypher()
        assert cypher.startswith("-[r:KNOWS {")
        assert "since: 2020" in cypher
        assert "weight: 0.8" in cypher
        assert cypher.endswith("}]->")
    
    def test_relationship_with_inline_where_condition(self):
        """Test relationship with inline WHERE condition."""
        r = RelationshipPattern(">", "r", "KNOWS").where(prop("r", "since") > literal(2020))
        assert r.to_cypher() == "-[r:KNOWS WHERE r.since > 2020]->"
    
    def test_relationship_with_complex_where_condition(self):
        """Test relationship with complex WHERE condition."""
        condition = (prop("r", "weight") > literal(0.5)) & (prop("r", "active") == literal(True))
        r = RelationshipPattern(">", "r", "KNOWS").where(condition)
        expected = "-[r:KNOWS WHERE (r.weight > 0.5) AND (r.active = true)]->"
        assert r.to_cypher() == expected
    
    def test_relationship_api_function(self):
        """Test the relationship() API function."""
        r = relationship(">", "r", "KNOWS", since=2020)
        assert isinstance(r, RelationshipPattern)
        assert r.direction == ">"
        assert r.variable == "r"
        assert r.type == "KNOWS"
        assert r.properties == {"since": 2020}
    
    def test_relationship_api_with_where(self):
        """Test the relationship() API function with where method."""
        r = relationship(">", "r", "KNOWS").where(prop("r", "since") > param("min_year"))
        assert r.to_cypher() == "-[r:KNOWS WHERE r.since > $min_year]->"


class TestPathPattern:
    """Test the PathPattern class."""
    
    def test_basic_path_creation(self):
        """Test basic path pattern creation."""
        elements = [
            NodePattern("p1", ("Person",)),
            RelationshipPattern(">", "r", "KNOWS"),
            NodePattern("p2", ("Person",))
        ]
        p = PathPattern(elements)
        assert p.to_cypher() == "(p1:Person)-[r:KNOWS]->(p2:Person)"
    
    def test_implicit_relationship_insertion(self):
        """Test that implicit relationships are inserted between consecutive nodes."""
        elements = [
            NodePattern("a", ("A",)),
            NodePattern("b", ("B",))
        ]
        p = PathPattern(elements)
        assert p.to_cypher() == "(a:A)-[]-(b:B)"
        
        # Test with three consecutive nodes
        elements = [
            NodePattern("a", ("A",)),
            NodePattern("b", ("B",)),
            NodePattern("c", ("C",))
        ]
        p = PathPattern(elements)
        assert p.to_cypher() == "(a:A)-[]-(b:B)-[]-(c:C)"
    
    def test_mixed_explicit_and_implicit_relationships(self):
        """Test paths with both explicit and implicit relationships."""
        elements = [
            NodePattern("a", ("A",)),
            RelationshipPattern(">", "r1", "REL1"),
            NodePattern("b", ("B",)),
            NodePattern("c", ("C",))
        ]
        p = PathPattern(elements)
        assert p.to_cypher() == "(a:A)-[r1:REL1]->(b:B)-[]-(c:C)"
    
    def test_path_with_inline_conditions(self):
        """Test path with inline WHERE conditions on multiple elements."""
        elements = [
            NodePattern("p1", ("Person",)).where(prop("p1", "active") == literal(True)),
            RelationshipPattern(">", "r", "KNOWS").where(prop("r", "since") > literal(2020)),
            NodePattern("p2", ("Person",)).where(prop("p2", "age") > literal(18))
        ]
        p = PathPattern(elements)
        expected = "(p1:Person WHERE p1.active = true)-[r:KNOWS WHERE r.since > 2020]->(p2:Person WHERE p2.age > 18)"
        assert p.to_cypher() == expected
    
    def test_path_api_function(self):
        """Test the path() API function."""
        p = path(
            node("p1", "Person"),
            relationship(">", "r", "KNOWS"),
            node("p2", "Person")
        )
        assert isinstance(p, PathPattern)
        assert len(p.elements) == 3
        assert p.to_cypher() == "(p1:Person)-[r:KNOWS]->(p2:Person)"
        
        # Test with consecutive nodes
        p = path(
            node("a", "A"),
            node("b", "B")
        )
        assert p.to_cypher() == "(a:A)-[]-(b:B)"
    
    def test_path_api_with_inline_conditions(self):
        """Test the path() API function with inline conditions."""
        p = path(
            node("p1", "Person").where(prop("p1", "active") == literal(True)),
            relationship(">", "r", "KNOWS").where(prop("r", "recent") == literal(True)),
            node("p2", "Person")
        )
        expected = "(p1:Person WHERE p1.active = true)-[r:KNOWS WHERE r.recent = true]->(p2:Person)"
        assert p.to_cypher() == expected
        
        # Test with consecutive nodes and conditions
        p = path(
            node("a", "A").where(prop("a", "active") == literal(True)),
            node("b", "B").where(prop("b", "active") == literal(True))
        )
        expected = "(a:A WHERE a.active = true)-[]-(b:B WHERE b.active = true)"
        assert p.to_cypher() == expected
    
    def test_path_where_method(self):
        """Test the where method on PathPattern."""
        p = path(
            node("p1", "Person"),
            relationship(">", "r", "KNOWS"),
            node("p2", "Person")
        )
        
        # Apply condition to the last element (p2)
        filtered_path = p.where(prop("p2", "age") > literal(18))
        expected = "(p1:Person)-[r:KNOWS]->(p2:Person WHERE p2.age > 18)"
        assert filtered_path.to_cypher() == expected
        
        # Test with consecutive nodes
        p = path(
            node("a", "A"),
            node("b", "B")
        )
        filtered_path = p.where(prop("b", "active") == literal(True))
        expected = "(a:A)-[]-(b:B WHERE b.active = true)"
        assert filtered_path.to_cypher() == expected
    
    def test_empty_path_where_raises_error(self):
        """Test that where() on empty path raises ValueError."""
        empty_path = PathPattern([])
        
        with pytest.raises(ValueError, match="Cannot add WHERE condition to empty path"):
            empty_path.where(prop("x", "y") > literal(1))


class TestPathConcatenation:
    """Test path concatenation functionality."""
    
    def test_basic_concatenation(self):
        """Test basic path concatenation."""
        path1 = PathPattern([
            node("a", "Person"),
            relationship(">", "r", "KNOWS"),
            node("b", "Person")
        ])
        
        path2 = PathPattern([
            node("c", "Company"),
            relationship("<", "w", "WORKS_AT"),
            node("b", "Person")
        ])
        
        combined = path1.concat(path2)
        cypher = combined.to_cypher()
        # Should have implicit relationship between b and c
        assert "(b:Person)-[]-(c:Company)" in cypher
        assert "(a:Person)-[r:KNOWS]->(b:Person)" in cypher
        assert "-[w:WORKS_AT]-(b:Person)" in cypher
    
    def test_operator_concatenation(self):
        """Test path concatenation using + operator."""
        part1 = path(
            node("start", "Point"),
            relationship(">", "r1", "ROAD"),
            node("mid", "Point")
        )
        
        part2 = path(
            node("mid", "Point"),
            relationship(">", "r2", "ROAD"),
            node("end", "Point")
        )
        
        full_path = part1 + part2
        cypher = full_path.to_cypher()
        assert "(start:Point)-[r1:ROAD]->(mid:Point)-[r2:ROAD]->(end:Point)" in cypher
    
    def test_variable_inheritance(self):
        """Test that concatenated path inherits variable from first path."""
        path1 = PathPattern([
            node("a", "A")
        ], variable="p1")
        
        path2 = PathPattern([
            node("b", "B")
        ], variable="p2")
        
        combined = path1.concat(path2)
        assert combined.variable == "p1"
        
        # Test with operator
        combined_op = path1 + path2
        assert combined_op.variable == "p1"
    
    def test_concat_with_empty_path(self):
        """Test concatenation with an empty path."""
        empty = PathPattern([])
        non_empty = PathPattern([node("a", "A")])
        
        # Concatenating with empty path should return the non-empty path
        assert empty.concat(non_empty) == non_empty
        assert non_empty.concat(empty) == non_empty
        
        # Test with operator
        assert empty + non_empty == non_empty
        assert non_empty + empty == non_empty
    
    def test_concatenation_with_quantified_paths(self):
        """Test concatenation of quantified paths."""
        base_path = path(
            node("a", "A"),
            node("b", "B")
        )
        
        # Create another path to concatenate
        end_path = path(
            node("c", "C")
        )
        
        # Concatenate first, then quantify
        full_path = base_path.concat(end_path).one_or_more()
        assert full_path.to_cypher() == "((a:A)-[]-(b:B)-[]-(c:C))+"


class TestRealWorldScenarios:
    """Test realistic usage scenarios."""
    
    def test_social_network_query(self):
        """Test a social network query pattern."""
        # Find active users connected by confirmed friendships
        pattern = path(
            node("user1", "User").where(
                (prop("user1", "active") == literal(True)) & 
                (prop("user1", "privacy") != literal("private"))
            ),
            relationship(">", "friendship", "FRIENDS").where(
                (prop("friendship", "status") == literal("confirmed")) &
                (prop("friendship", "created") > param("min_date"))
            ),
            node("user2", "User").where(prop("user2", "active") == literal(True))
        )
        
        cypher = pattern.to_cypher()
        assert "user1:User WHERE" in cypher
        assert "user1.active = true" in cypher
        assert "user1.privacy <> 'private'" in cypher
        assert "friendship:FRIENDS WHERE" in cypher
        assert "friendship.status = 'confirmed'" in cypher
        assert "friendship.created > $min_date" in cypher
        assert "user2:User WHERE user2.active = true" in cypher
    
    def test_employee_hierarchy_query(self):
        """Test an employee hierarchy query pattern."""
        # Find managers with direct reports
        pattern = path(
            node("manager", "Employee").where(
                (prop("manager", "role") == literal("manager")) &
                (prop("manager", "department") == param("dept"))
            ),
            relationship(">", "manages", "MANAGES").where(
                prop("manages", "direct") == literal(True)
            ),
            node("employee", "Employee").where(
                (prop("employee", "active") == literal(True)) &
                (prop("employee", "performance") >= literal(3))
            )
        )
        
        cypher = pattern.to_cypher()
        assert "manager:Employee WHERE" in cypher
        assert "manager.role = 'manager'" in cypher
        assert "manager.department = $dept" in cypher
        assert "manages:MANAGES WHERE manages.direct = true" in cypher
        assert "employee:Employee WHERE" in cypher
        assert "employee.active = true" in cypher
        assert "employee.performance >= 3" in cypher
    
    def test_product_recommendation_query(self):
        """Test a product recommendation query pattern."""
        # Find products bought together
        pattern = path(
            node("user", "User").where(prop("user", "segment") == param("target_segment")),
            relationship(">", "bought1", "BOUGHT").where(
                prop("bought1", "date") > param("recent_date")
            ),
            node("product1", "Product").where(
                (prop("product1", "category") == param("category")) &
                (prop("product1", "rating") >= literal(4.0))
            ),
            relationship("<", "bought2", "BOUGHT"),
            node("other_user", "User").where(prop("other_user", "id") != prop("user", "id")),
            relationship(">", "bought3", "BOUGHT"),
            node("product2", "Product").where(
                (prop("product2", "category") == param("category")) &
                (prop("product2", "available") == literal(True))
            )
        )
        
        cypher = pattern.to_cypher()
        # Verify the complex pattern generates properly
        assert cypher.count("User WHERE") == 2
        assert cypher.count("Product WHERE") == 2
        assert cypher.count("BOUGHT") == 3
        assert "user.segment = $target_segment" in cypher
        assert "product1.rating >= 4.0" in cypher
        assert "product2.available = true" in cypher


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_node_with_no_labels(self):
        """Test node with no labels."""
        n = NodePattern("x")
        assert n.to_cypher() == "(x)"
    
    def test_relationship_with_no_type(self):
        """Test relationship with no type."""
        r = RelationshipPattern(">", "r", "")
        assert r.to_cypher() == "-[r]->"
    
    def test_relationship_with_no_variable_or_types(self):
        """Test minimal relationship."""
        r = RelationshipPattern(">")
        assert r.to_cypher() == "-[]->"
    
    def test_string_escaping_in_properties(self):
        """Test proper escaping of string values in properties."""
        n = NodePattern("p", ("Person",), {"name": "O'Connor", "quote": "He said 'hello'"})
        cypher = n.to_cypher()
        assert "name: 'O\\'Connor'" in cypher
        assert "quote: 'He said \\'hello\\''" in cypher
    
    def test_boolean_and_null_formatting(self):
        """Test formatting of boolean and null values."""
        n = NodePattern("p", ("Person",), {
            "active": True,
            "deleted": False,
            "middle_name": None
        })
        cypher = n.to_cypher()
        assert "active: true" in cypher
        assert "deleted: false" in cypher
        assert "middle_name: null" in cypher
