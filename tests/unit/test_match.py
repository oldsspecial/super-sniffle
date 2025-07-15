"""
Unit tests for MATCH clause implementation.

Tests the working MATCH clause functionality including basic patterns,
relationships, inline conditions, and complex path construction.
"""

import pytest
from super_sniffle import match, node, relationship, path, prop, param, literal
import logging
logging.basicConfig(level=logging.INFO)


class TestBasicMatch:
    """Test basic MATCH clause functionality."""
    
    def test_basic_match_single_node(self):
        """Test basic MATCH clause with a single node."""
        query = match(node("Person", variable="p"))
        result = query.to_cypher()
        expected = "MATCH (p:Person)"
        assert result == expected

    def test_match_with_relates_to(self):
        """Test MATCH with relates_to method."""
        person = node("Person", variable="p")
        friend = node("Person", variable="f")
        query = match(person.relates_to("r", "KNOWS", ">", friend))
        result = query.to_cypher()
        expected = "MATCH (p:Person)-[r:KNOWS]->(f:Person)"
        assert result == expected

    def test_match_with_inline_conditions(self):
        """Test MATCH with inline WHERE conditions."""
        person = node("Person", variable="p").where(prop("p", "age") > literal(18))
        query = match(person)
        result = query.to_cypher()
        expected = "MATCH (p:Person WHERE p.age > 18)"
        assert result == expected

    def test_multiple_match_clauses(self):
        """Test chaining multiple MATCH clauses."""
        query = (
            match(node("Person", variable="p"))
            .match(node("Company", variable="c"))
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nMATCH (c:Company)"
        assert result == expected


class TestComplexPaths:
    """Test complex path construction."""
    
    def test_complex_path_with_conditions(self):
        """Test complex path with inline conditions."""
        complex_path = path(
            node("Person", variable="p1").where(prop("p1", "active") == literal(True)),
            relationship(">", "r", "KNOWS").where(prop("r", "since") > literal(2020)),
            node("Person", variable="p2")
        )
        query = match(complex_path)
        result = query.to_cypher()
        expected = "MATCH (p1:Person WHERE p1.active = true)-[r:KNOWS WHERE r.since > 2020]->(p2:Person)"
        assert result == expected

    def test_relates_to_with_properties(self):
        """Test relates_to with relationship properties."""
        person = node("Person", variable="p")
        friend = node("Person", variable="f")
        query = match(person.relates_to("r", "KNOWS", ">", friend, since=2020))
        result = query.to_cypher()
        expected = "MATCH (p:Person)-[r:KNOWS {since: 2020}]->(f:Person)"
        assert result == expected


class TestRelationshipDirections:
    """Test relates_to with different directions."""
    
    def test_outgoing_relationship(self):
        """Test outgoing relationship direction."""
        person = node("Person", variable="p")
        friend = node("Person", variable="f")
        query = match(person.relates_to("r", "KNOWS", ">", friend))
        result = query.to_cypher()
        expected = "MATCH (p:Person)-[r:KNOWS]->(f:Person)"
        assert result == expected
    
    def test_incoming_relationship(self):
        """Test incoming relationship direction."""
        person = node("Person", variable="p")
        friend = node("Person", variable="f")
        query = match(person.relates_to("r", "KNOWS", "<", friend))
        result = query.to_cypher()
        expected = "MATCH (p:Person)<-[r:KNOWS]-(f:Person)"
        assert result == expected
    
    def test_undirected_relationship(self):
        """Test undirected relationship (using default)."""
        person = node("Person", variable="p")
        friend = node("Person", variable="f")
        query = match(person.relates_to("r", "KNOWS", target_node=friend))
        result = query.to_cypher()
        expected = "MATCH (p:Person)-[r:KNOWS]-(f:Person)"
        assert result == expected


class TestImmutability:
    """Test that objects remain immutable."""
    
    def test_node_pattern_immutability_with_relates_to(self):
        """Test NodePattern immutability with relates_to."""
        original_person = node("Person", variable="p")
        friend = node("Person", variable="f")
        path_result = original_person.relates_to("r", "KNOWS", ">", friend)
        
        # Original should be unchanged
        assert original_person.to_cypher() == "(p:Person)"
        # Path should be created correctly
        assert path_result.to_cypher() == "(p:Person)-[r:KNOWS]->(f:Person)"
    
    def test_match_clause_immutability(self):
        """Test MatchClause immutability."""
        original_query = match(node("Person", variable="p"))
        new_query = original_query.match(node("Company", variable="c"))
        
        # Original should be unchanged
        assert original_query.to_cypher() == "MATCH (p:Person)"
        # New query should have both
        assert new_query.to_cypher() == "MATCH (p:Person)\nMATCH (c:Company)"


class TestRealWorldExamples:
    """Test real-world usage examples."""
    
    def test_complex_nested_relationships(self):
        """Test finding active people who know someone in a specific city."""
        p_node = node("Person", variable="p").where(prop("p", "active") == literal(True))
        f_node = node("Person", variable="f")
        c_node = node("City", variable="c").where( prop("c", "name") == param("city_name"))

        # Create relationships
        knows_rel = relationship(">", "r", "KNOWS")
        lives_in_rel = relationship(">", "lives", "LIVES_IN")

        # Build path pattern
        query = match(path(p_node, knows_rel, f_node, lives_in_rel, c_node) )

        
        result = query.to_cypher()
        
        # Check that all expected parts are in the result
        expected_parts = [
            "MATCH (p:Person WHERE p.active = true)",
            "-[r:KNOWS]->",
            "(f:Person)",
            "-[lives:LIVES_IN]->",
            "(c:City WHERE c.name = $city_name)"
        ]
        import sys
        logging.info("\n\n\n\n\n")
        logging.info('\n'.join(expected_parts))
        logging.info(result)
        logging.info("\n\n\n\n\n")
        sys.stdout.flush()
        for part in expected_parts:
            assert part in result, f"Expected '{part}' to be in the result"
        
    def test_simple_friend_relationship(self):
        """Test simple friend relationship query."""
        query = match(
            node("Person", variable="user").relates_to("friendship", "FRIENDS_WITH", "-", node("Person", variable="friend"))
        )
        result = query.to_cypher()
        expected = "MATCH (user:Person)-[friendship:FRIENDS_WITH]-(friend:Person)"
        assert result == expected

    def test_employee_company_relationship(self):
        """Test employee-company relationship query."""
        query = match(
            node("Employee", variable="emp").relates_to("employment", "WORKS_FOR", ">", node("Company", variable="comp"))
        )
        result = query.to_cypher()
        expected = "MATCH (emp:Employee)-[employment:WORKS_FOR]->(comp:Company)"
        assert result == expected


class TestMatchWithConditions:
    """Test MATCH clauses with various condition types."""
    
    def test_match_with_property_condition(self):
        """Test MATCH with property-based condition."""
        query = match(
            node("Person", variable="p").where(prop("p", "age") >= literal(21))
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person WHERE p.age >= 21)"
        assert result == expected

    def test_match_with_parameter_condition(self):
        """Test MATCH with parameter-based condition."""
        query = match(
            node("Person", variable="p").where(prop("p", "name") == param("user_name"))
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person WHERE p.name = $user_name)"
        assert result == expected

    def test_match_with_complex_condition(self):
        """Test MATCH with complex logical condition."""
        query = match(
            node("Person", variable="p").where(
                (prop("p", "age") > literal(18)) & (prop("p", "active") == literal(True))
            )
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person WHERE (p.age > 18) AND (p.active = true))"
        assert result == expected


class TestMatchChaining:
    """Test MATCH clause chaining capabilities."""
    
    def test_multiple_match_different_patterns(self):
        """Test multiple MATCH clauses with different patterns."""
        query = (
            match(node("Person", variable="p"))
            .match(node("Company", variable="c").where(prop("c", "industry") == literal("Technology")))
            .match(node("Department", variable="d"))
        )
        result = query.to_cypher()
        
        assert "MATCH (p:Person)" in result
        assert "MATCH (c:Company WHERE c.industry = 'Technology')" in result
        assert "MATCH (d:Department)" in result

    def test_match_with_relationship_chaining(self):
        """Test MATCH clauses that can be chained with relationships."""
        first_match = match(node("Person", variable="p"))
        second_match = first_match.match(
            node(variable="p").relates_to("works", "WORKS_FOR", ">", node("Company", variable="c"))
        )
        
        result = second_match.to_cypher()
        
        assert "MATCH (p:Person)" in result
        assert "MATCH (p)-[works:WORKS_FOR]->(c:Company)" in result


class TestEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_match_with_no_label(self):
        """Test MATCH with node that has no label."""
        query = match(node(variable="n"))
        result = query.to_cypher()
        expected = "MATCH (n)"
        assert result == expected

    def test_match_with_empty_variable_name(self):
        """Test MATCH with minimal variable name."""
        query = match(node("Person", variable="a"))
        result = query.to_cypher()
        expected = "MATCH (a:Person)"
        assert result == expected

    def test_match_relationship_no_variable(self):
        """Test relationship without variable name."""
        query = match(
            node("Person", variable="p").relates_to("", "KNOWS", ">", node("Person", variable="f"))
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)-[:KNOWS]->(f:Person)"
        assert result == expected
