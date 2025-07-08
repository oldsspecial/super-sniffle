#!/usr/bin/env python3
"""
Demo script to test the RETURN clause implementation.

This script demonstrates the working RETURN clause functionality
without requiring pytest or package installation.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from super_sniffle import match, node, prop, param, literal


def test_basic_return():
    """Test basic RETURN clause with projections."""
    print("Testing basic RETURN clause...")
    person = node("p", "Person")
    query = match(person).return_("p.name", "p.age")
    result = query.to_cypher()
    expected = "MATCH (p:Person)\nRETURN p.name, p.age"
    print(f"Query: {result}")
    print(f"Expected: {expected}")
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print("✅ PASSED\n")


def test_return_everything():
    """Test RETURN * clause."""
    print("Testing RETURN * clause...")
    
    # Using no arguments
    person = node("p", "Person")
    query1 = match(person).return_()
    result1 = query1.to_cypher()
    expected1 = "MATCH (p:Person)\nRETURN *"
    print(f"Query (no args): {result1}")
    print(f"Expected: {expected1}")
    assert result1 == expected1, f"Expected '{expected1}', got '{result1}'"
    
    # Using "*" explicitly
    query2 = match(person).return_("*")
    result2 = query2.to_cypher()
    expected2 = "MATCH (p:Person)\nRETURN *"
    print(f"Query (explicit *): {result2}")
    print(f"Expected: {expected2}")
    assert result2 == expected2, f"Expected '{expected2}', got '{result2}'"
    print("✅ PASSED\n")


def test_return_distinct():
    """Test RETURN DISTINCT clause."""
    print("Testing RETURN DISTINCT clause...")
    
    # RETURN DISTINCT with projections
    person = node("p", "Person")
    query1 = match(person).return_("p.name", distinct=True)
    result1 = query1.to_cypher()
    expected1 = "MATCH (p:Person)\nRETURN DISTINCT p.name"
    print(f"Query (distinct projections): {result1}")
    print(f"Expected: {expected1}")
    assert result1 == expected1, f"Expected '{expected1}', got '{result1}'"
    
    # RETURN DISTINCT everything
    query2 = match(person).return_(distinct=True)
    result2 = query2.to_cypher()
    expected2 = "MATCH (p:Person)\nRETURN DISTINCT *"
    print(f"Query (distinct everything): {result2}")
    print(f"Expected: {expected2}")
    assert result2 == expected2, f"Expected '{expected2}', got '{result2}'"
    print("✅ PASSED\n")


def test_return_with_where():
    """Test RETURN clause after WHERE."""
    print("Testing RETURN clause after WHERE...")
    person = node("p", "Person")
    query = (
        match(person)
        .where(prop("p", "age") > literal(30))
        .return_("p.name", "p.age")
    )
    result = query.to_cypher()
    expected = "MATCH (p:Person)\nWHERE p.age > 30\nRETURN p.name, p.age"
    print(f"Query: {result}")
    print(f"Expected: {expected}")
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print("✅ PASSED\n")


def test_return_with_relationship_pattern():
    """Test RETURN clause with relationship patterns."""
    print("Testing RETURN clause with relationship patterns...")
    person = node("p", "Person")
    friend = node("f", "Person")
    query = (
        match(person.relates_to("r", "KNOWS", ">", friend))
        .where(prop("p", "age") > literal(25))
        .return_("p.name", "f.name", "r.since")
    )
    result = query.to_cypher()
    expected = "MATCH (p:Person)-[r:KNOWS]->(f:Person)\nWHERE p.age > 25\nRETURN p.name, f.name, r.since"
    print(f"Query: {result}")
    print(f"Expected: {expected}")
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print("✅ PASSED\n")


def test_return_with_multiple_match():
    """Test RETURN clause with multiple MATCH clauses."""
    print("Testing RETURN clause with multiple MATCH clauses...")
    query = (
        match(node("p", "Person"))
        .match(node("c", "Company"))
        .where(prop("p", "works_at") == prop("c", "id"))
        .return_("p.name", "c.name")
    )
    result = query.to_cypher()
    expected = "MATCH (p:Person)\nMATCH (c:Company)\nWHERE p.works_at = c.id\nRETURN p.name, c.name"
    print(f"Query: {result}")
    print(f"Expected: {expected}")
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print("✅ PASSED\n")


def test_return_with_parameters():
    """Test RETURN clause with parameters and expressions."""
    print("Testing RETURN clause with parameters and expressions...")
    person = node("p", "Person")
    query = (
        match(person)
        .where(prop("p", "name").contains(param("search_term")))
        .return_("p.name", "p.age", "p.email")
    )
    result = query.to_cypher()
    expected = "MATCH (p:Person)\nWHERE p.name CONTAINS $search_term\nRETURN p.name, p.age, p.email"
    print(f"Query: {result}")
    print(f"Expected: {expected}")
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print("✅ PASSED\n")


def demonstrate_real_world_example():
    """Demonstrate a real-world example query with complete clause chain."""
    print("🎯 Real-world example:")
    print("Finding active people older than 25 and their friends...")
    
    # Build a complex query using MATCH, WHERE, and RETURN clauses
    person = node("p", "Person")
    friend = node("f", "Person")
    query = (
        match(person.relates_to("r", "KNOWS", ">", friend))
        .where(
            (prop("p", "active") == literal(True)) &
            (prop("p", "age") > literal(25)) &
            (prop("f", "age") < literal(35))
        )
        .return_("p.name", "f.name", "r.since", "p.age", "f.age")
    )
    
    result = query.to_cypher()
    print(f"Generated Cypher:\n{result}\n")
    
    expected_parts = [
        "MATCH (p:Person)-[r:KNOWS]->(f:Person)",
        "RETURN p.name, f.name, r.since, p.age, f.age"
    ]
    
    # Check that all expected parts are present
    for part in expected_parts:
        assert part in result, f"Expected '{part}' to be in the result"
    
    # Check that WHERE clause contains the expected conditions (allow flexible parentheses grouping)
    assert "WHERE" in result, "Expected WHERE clause to be present"
    assert "p.active = true" in result, "Expected p.active = true condition"
    assert "p.age > 25" in result, "Expected p.age > 25 condition" 
    assert "f.age < 35" in result, "Expected f.age < 35 condition"
    assert "AND" in result, "Expected AND operators in WHERE clause"
    
    print("✅ Complete query with MATCH, WHERE, and RETURN works!\n")


def demonstrate_different_return_styles():
    """Demonstrate different RETURN clause styles."""
    print("🎯 Different RETURN styles:")
    
    # Basic projections
    query1 = match(node("p", "Person")).return_("p.name", "p.age")
    print("1. Basic projections:")
    print(f"   {query1.to_cypher()}")
    
    # Return everything
    query2 = match(node("p", "Person")).return_()
    print("2. Return everything (no args):")
    print(f"   {query2.to_cypher()}")
    
    # Return everything (explicit)
    query3 = match(node("p", "Person")).return_("*")
    print("3. Return everything (explicit):")
    print(f"   {query3.to_cypher()}")
    
    # Return distinct projections
    query4 = match(node("p", "Person")).return_("p.name", distinct=True)
    print("4. Return distinct projections:")
    print(f"   {query4.to_cypher()}")
    
    # Return distinct everything
    query5 = match(node("p", "Person")).return_(distinct=True)
    print("5. Return distinct everything:")
    print(f"   {query5.to_cypher()}")
    
    # Complex return with WHERE
    query6 = (
        match(node("p", "Person"))
        .where(prop("p", "age") > literal(30))
        .return_("p.name", "p.age", "p.email", distinct=True)
    )
    print("6. Complex return with WHERE and DISTINCT:")
    print(f"   {query6.to_cypher()}")
    
    print()


if __name__ == "__main__":
    print("🚀 Testing RETURN clause implementation...\n")
    
    try:
        test_basic_return()
        test_return_everything()
        test_return_distinct()
        test_return_with_where()
        test_return_with_relationship_pattern()
        test_return_with_multiple_match()
        test_return_with_parameters()
        demonstrate_real_world_example()
        demonstrate_different_return_styles()
        
        print("🎉 All tests passed! RETURN clause implementation is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
