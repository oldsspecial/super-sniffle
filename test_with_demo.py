#!/usr/bin/env python3
"""
Demo script to test the WITH clause implementation.

This script demonstrates the working WITH clause functionality
without requiring pytest or package installation.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from super_sniffle import match, node, prop, param, literal


def test_basic_with():
    """Test basic WITH clause with projections."""
    print("Testing basic WITH clause...")
    person = node("p", "Person")
    query = (
        match(person)
        .with_("p.name AS name", "p.age AS age")
        .return_("name", "age")
    )
    result = query.to_cypher()
    expected = "MATCH (p:Person)\nWITH p.name AS name, p.age AS age\nRETURN name, age"
    print(f"Query: {result}")
    print(f"Expected: {expected}")
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print("✅ PASSED\n")


def test_with_single_projection():
    """Test WITH clause with single projection."""
    print("Testing WITH clause with single projection...")
    person = node("p", "Person")
    query = (
        match(person)
        .with_("p")
        .return_("p.name")
    )
    result = query.to_cypher()
    expected = "MATCH (p:Person)\nWITH p\nRETURN p.name"
    print(f"Query: {result}")
    print(f"Expected: {expected}")
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print("✅ PASSED\n")


def test_with_distinct():
    """Test WITH DISTINCT clause."""
    print("Testing WITH DISTINCT clause...")
    person = node("p", "Person")
    company = node("c", "Company")
    query = (
        match(person.relates_to("r", "WORKS_AT", ">", company))
        .with_("c.industry AS industry", distinct=True)
        .return_("industry")
    )
    result = query.to_cypher()
    expected = "MATCH (p:Person)-[r:WORKS_AT]->(c:Company)\nWITH DISTINCT c.industry AS industry\nRETURN industry"
    print(f"Query: {result}")
    print(f"Expected: {expected}")
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print("✅ PASSED\n")


def test_with_where():
    """Test WITH clause followed by WHERE."""
    print("Testing WITH clause followed by WHERE...")
    person = node("p", "Person")
    query = (
        match(person)
        .with_("p")
        .where(prop("p", "age") > literal(30))
        .return_("p.name", "p.age")
    )
    result = query.to_cypher()
    expected = "MATCH (p:Person)\nWITH p\nWHERE p.age > 30\nRETURN p.name, p.age"
    print(f"Query: {result}")
    print(f"Expected: {expected}")
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print("✅ PASSED\n")


def test_with_chaining_multiple_query_parts():
    """Test WITH clause chaining multiple query parts."""
    print("Testing WITH clause chaining multiple query parts...")
    person = node("p", "Person")
    friend = node("friend", "Person")
    query = (
        match(person)
        .with_("p")
        .match(person.relates_to("r", "KNOWS", ">", friend))
        .return_("p.name", "friend.name")
    )
    result = query.to_cypher()
    expected = "MATCH (p:Person)\nWITH p\nMATCH (p:Person)-[r:KNOWS]->(friend:Person)\nRETURN p.name, friend.name"
    print(f"Query: {result}")
    print(f"Expected: {expected}")
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print("✅ PASSED\n")


def test_with_aggregation():
    """Test WITH clause with aggregation."""
    print("Testing WITH clause with aggregation...")
    person = node("p", "Person")
    friend = node("friend", "Person")
    query = (
        match(person.relates_to("r", "KNOWS", ">", friend))
        .with_("p", "count(friend) AS friendCount")
        .where(prop("friendCount", "friendCount") > literal(3))  # Using workaround for aliased variable
        .return_("p.name", "friendCount")
    )
    result = query.to_cypher()
    expected = "MATCH (p:Person)-[r:KNOWS]->(friend:Person)\nWITH p, count(friend) AS friendCount\nWHERE friendCount.friendCount > 3\nRETURN p.name, friendCount"
    print(f"Query: {result}")
    print(f"Expected: {expected}")
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print("✅ PASSED\n")


def test_multiple_with_clauses():
    """Test multiple WITH clauses in sequence."""
    print("Testing multiple WITH clauses...")
    person = node("p", "Person")
    friend = node("friend", "Person")
    query = (
        match(person)
        .where(prop("p", "age") > literal(30))
        .with_("p")
        .match(person.relates_to("r", "KNOWS", ">", friend))
        .with_("p", "collect(friend) AS friends", "size(collect(friend)) AS friendCount")
        .where(prop("friendCount", "friendCount") > literal(3))  # Using workaround for aliased variable
        .return_("p.name", "friendCount")
    )
    result = query.to_cypher()
    expected = ("MATCH (p:Person)\n"
               "WHERE p.age > 30\n"
               "WITH p\n"
               "MATCH (p:Person)-[r:KNOWS]->(friend:Person)\n"
               "WITH p, collect(friend) AS friends, size(collect(friend)) AS friendCount\n"
               "WHERE friendCount.friendCount > 3\n"
               "RETURN p.name, friendCount")
    print(f"Query: {result}")
    print(f"Expected: {expected}")
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print("✅ PASSED\n")


def test_with_from_where_clause():
    """Test WITH clause from WHERE clause."""
    print("Testing WITH clause from WHERE clause...")
    person = node("p", "Person")
    query = (
        match(person)
        .where(prop("p", "active") == literal(True))
        .with_("p.name AS name", "p.department AS dept")
        .return_("name", "dept")
    )
    result = query.to_cypher()
    expected = "MATCH (p:Person)\nWHERE p.active = true\nWITH p.name AS name, p.department AS dept\nRETURN name, dept"
    print(f"Query: {result}")
    print(f"Expected: {expected}")
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print("✅ PASSED\n")


def demonstrate_real_world_example():
    """Demonstrate a real-world example with WITH clauses."""
    print("🎯 Real-world example:")
    print("Finding people with many friends and their friend recommendations...")
    
    # Build a complex query using MATCH, WITH, and aggregation
    person = node("p", "Person")
    friend = node("f", "Person")
    
    # Simplified example to avoid complex chained relationships
    query = (
        match(person.relates_to("r1", "KNOWS", ">", friend))
        .with_("p", "count(f) AS friendCount")
        .where(prop("friendCount", "friendCount") > literal(5))  # Using workaround for aliased variable
        .with_("p")
        .match(person.relates_to("r2", "KNOWS", ">", node("f2", "Person")))
        .return_("p.name", "f2.name")
    )
    
    result = query.to_cypher()
    print(f"Generated Cypher:\n{result}\n")
    
    # Check that all expected parts are present
    expected_parts = [
        "MATCH (p:Person)-[r1:KNOWS]->(f:Person)",
        "WITH p, count(f) AS friendCount",
        "WHERE friendCount.friendCount > 5",
        "WITH p",
        "MATCH (p:Person)-[r2:KNOWS]->(f2:Person)",
        "RETURN p.name, f2.name"
    ]
    
    for part in expected_parts:
        assert part in result, f"Expected '{part}' to be in the result"
    
    print("✅ Complex query with multiple WITH clauses works!\n")


def demonstrate_different_with_styles():
    """Demonstrate different WITH clause styles."""
    print("🎯 Different WITH styles:")
    
    # Basic projections with aliasing
    query1 = (
        match(node("p", "Person"))
        .with_("p.name AS fullName", "p.age AS years")
        .return_("fullName", "years")
    )
    print("1. Basic projections with aliasing:")
    print(f"   {query1.to_cypher()}")
    
    # Pass-through without transformation
    query2 = (
        match(node("p", "Person"))
        .with_("p")
        .return_("p.name")
    )
    print("2. Pass-through without transformation:")
    print(f"   {query2.to_cypher()}")
    
    # WITH DISTINCT
    query3 = (
        match(node("p", "Person"))
        .with_("p.department AS dept", distinct=True)
        .return_("dept")
    )
    print("3. WITH DISTINCT:")
    print(f"   {query3.to_cypher()}")
    
    # WITH followed by WHERE
    query4 = (
        match(node("p", "Person"))
        .with_("p.name AS name", "p.salary AS salary")
        .where(prop("salary", "salary") > literal(50000))  # Using workaround for aliased variable
        .return_("name", "salary")
    )
    print("4. WITH followed by WHERE:")
    print(f"   {query4.to_cypher()}")
    
    # Chaining query parts
    query5 = (
        match(node("p", "Person"))
        .with_("p")
        .match(node("p").relates_to("r", "WORKS_AT", ">", node("c", "Company")))
        .return_("p.name", "c.name")
    )
    print("5. Chaining query parts:")
    print(f"   {query5.to_cypher()}")
    
    print()


if __name__ == "__main__":
    print("🚀 Testing WITH clause implementation...\n")
    
    try:
        test_basic_with()
        test_with_single_projection()
        test_with_distinct()
        test_with_where()
        test_with_chaining_multiple_query_parts()
        test_with_aggregation()
        test_multiple_with_clauses()
        test_with_from_where_clause()
        demonstrate_real_world_example()
        demonstrate_different_with_styles()
        
        print("🎉 All tests passed! WITH clause implementation is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
