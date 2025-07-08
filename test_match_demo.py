#!/usr/bin/env python3
"""
Demo script to test the MATCH clause implementation.

This script demonstrates the working MATCH clause functionality
without requiring pytest or package installation.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from super_sniffle import match, node, relationship, path, prop, param, literal


def test_basic_match():
    """Test basic MATCH clause with a single node."""
    print("Testing basic MATCH clause...")
    query = match(node("p", "Person"))
    result = query.to_cypher()
    expected = "MATCH (p:Person)"
    print(f"Query: {result}")
    print(f"Expected: {expected}")
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print("✅ PASSED\n")


def test_match_with_relates_to():
    """Test MATCH with relates_to method."""
    print("Testing MATCH with relates_to...")
    person = node("p", "Person")
    friend = node("f", "Person")
    query = match(person.relates_to("r", "KNOWS", ">", friend))
    result = query.to_cypher()
    expected = "MATCH (p:Person)-[r:KNOWS]->(f:Person)"
    print(f"Query: {result}")
    print(f"Expected: {expected}")
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print("✅ PASSED\n")


def test_match_with_inline_conditions():
    """Test MATCH with inline WHERE conditions."""
    print("Testing MATCH with inline conditions...")
    person = node("p", "Person").where(prop("p", "age") > literal(18))
    query = match(person)
    result = query.to_cypher()
    expected = "MATCH (p:Person WHERE p.age > 18)"
    print(f"Query: {result}")
    print(f"Expected: {expected}")
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print("✅ PASSED\n")


def test_multiple_match_clauses():
    """Test chaining multiple MATCH clauses."""
    print("Testing multiple MATCH clauses...")
    query = (
        match(node("p", "Person"))
        .match(node("c", "Company"))
    )
    result = query.to_cypher()
    expected = "MATCH (p:Person)\nMATCH (c:Company)"
    print(f"Query: {result}")
    print(f"Expected: {expected}")
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print("✅ PASSED\n")


def test_complex_path_with_conditions():
    """Test complex path with inline conditions."""
    print("Testing complex path with conditions...")
    complex_path = path(
        node("p1", "Person").where(prop("p1", "active") == literal(True)),
        relationship(">", "r", "KNOWS").where(prop("r", "since") > literal(2020)),
        node("p2", "Person")
    )
    query = match(complex_path)
    result = query.to_cypher()
    expected = "MATCH (p1:Person WHERE p1.active = true)-[r:KNOWS WHERE r.since > 2020]->(p2:Person)"
    print(f"Query: {result}")
    print(f"Expected: {expected}")
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print("✅ PASSED\n")


def test_relates_to_with_properties():
    """Test relates_to with relationship properties."""
    print("Testing relates_to with properties...")
    person = node("p", "Person")
    friend = node("f", "Person")
    query = match(person.relates_to("r", "KNOWS", ">", friend, since=2020))
    result = query.to_cypher()
    expected = "MATCH (p:Person)-[r:KNOWS {since: 2020}]->(f:Person)"
    print(f"Query: {result}")
    print(f"Expected: {expected}")
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print("✅ PASSED\n")


def test_relates_to_directions():
    """Test relates_to with different directions."""
    print("Testing relates_to with different directions...")
    
    # Outgoing
    person = node("p", "Person")
    friend = node("f", "Person")
    query1 = match(person.relates_to("r", "KNOWS", ">", friend))
    result1 = query1.to_cypher()
    expected1 = "MATCH (p:Person)-[r:KNOWS]->(f:Person)"
    print(f"Outgoing: {result1}")
    assert result1 == expected1
    
    # Incoming
    query2 = match(person.relates_to("r", "KNOWS", "<", friend))
    result2 = query2.to_cypher()
    expected2 = "MATCH (p:Person)<-[r:KNOWS]-(f:Person)"
    print(f"Incoming: {result2}")
    assert result2 == expected2
    
    # Undirected (using default)
    query3 = match(person.relates_to("r", "KNOWS", target_node=friend))
    result3 = query3.to_cypher()
    expected3 = "MATCH (p:Person)-[r:KNOWS]-(f:Person)"
    print(f"Undirected: {result3}")
    assert result3 == expected3
    
    print("✅ PASSED\n")


def test_immutability():
    """Test that objects remain immutable."""
    print("Testing immutability...")
    
    # Test NodePattern immutability with relates_to
    original_person = node("p", "Person")
    friend = node("f", "Person")
    path_result = original_person.relates_to("r", "KNOWS", ">", friend)
    
    # Original should be unchanged
    assert original_person.to_cypher() == "(p:Person)"
    # Path should be created correctly
    assert path_result.to_cypher() == "(p:Person)-[r:KNOWS]->(f:Person)"
    
    # Test MatchClause immutability
    original_query = match(node("p", "Person"))
    new_query = original_query.match(node("c", "Company"))
    
    # Original should be unchanged
    assert original_query.to_cypher() == "MATCH (p:Person)"
    # New query should have both
    assert new_query.to_cypher() == "MATCH (p:Person)\nMATCH (c:Company)"
    
    print("✅ PASSED\n")


def demonstrate_real_world_example():
    """Demonstrate a real-world example query."""
    print("🎯 Real-world example:")
    print("Finding active people who know someone in a specific city...")
    
    # Build a complex query using the new features
    query = match(
        node("p", "Person").where(prop("p", "active") == literal(True))
        .relates_to("r", "KNOWS", ">", 
                   node("f", "Person")
                   .relates_to("lives", "LIVES_IN", ">", 
                              node("c", "City").where(prop("c", "name") == param("city_name"))))
    )
    
    result = query.to_cypher()
    print(f"Generated Cypher:\n{result}\n")
    
    expected_parts = [
        "MATCH (p:Person WHERE p.active = true)",
        "-[r:KNOWS]->",
        "(f:Person)",
        "-[lives:LIVES_IN]->",
        "(c:City WHERE c.name = $city_name)"
    ]
    
    for part in expected_parts:
        assert part in result, f"Expected '{part}' to be in the result"
    
    print("✅ Complex query generation works!\n")


if __name__ == "__main__":
    print("🚀 Testing MATCH clause implementation...\n")
    
    try:
        test_basic_match()
        test_match_with_relates_to()
        test_match_with_inline_conditions()
        test_multiple_match_clauses()
        test_complex_path_with_conditions()
        test_relates_to_with_properties()
        test_relates_to_directions()
        test_immutability()
        demonstrate_real_world_example()
        
        print("🎉 All tests passed! MATCH clause implementation is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
