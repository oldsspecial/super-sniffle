#!/usr/bin/env python3
"""
Script to run unit tests for super-sniffle components.

This script runs basic functionality tests for all major components
without requiring pytest or package installation.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_basic_functionality():
    """Test basic functionality of all major components."""
    print("🚀 Testing basic functionality of all components...\n")
    
    try:
        # Import all components
        from super_sniffle import (
            match, node, prop, var, literal, asc, desc, param
        )
        print("✅ All imports successful")
        
        # Test basic MATCH
        query1 = match(node("Person", variable="p")).return_("p.name")
        result1 = query1.to_cypher()
        expected1 = "MATCH (p:Person)\nRETURN p.name"
        assert result1 == expected1
        print("✅ Basic MATCH works")
        
        # Test WHERE clause
        query2 = (
            match(node("Person", variable="p"))
            .where(prop("p", "age") > literal(25))
            .return_("p.name", "p.age")
        )
        result2 = query2.to_cypher()
        assert "WHERE p.age > 25" in result2
        print("✅ WHERE clause works")
        
        # Test WITH clause
        query3 = (
            match(node("Person", variable="p"))
            .with_("p.name AS name", "p.age AS age")
            .return_("name", "age")
        )
        result3 = query3.to_cypher()
        assert "WITH p.name AS name, p.age AS age" in result3
        print("✅ WITH clause works")
        
        # Test ORDER BY clause
        query4 = (
            match(node("Person", variable="p"))
            .return_("p.name", "p.age")
            .order_by(desc("p.age"))
        )
        result4 = query4.to_cypher()
        assert "ORDER BY p.age DESC" in result4
        print("✅ ORDER BY clause works")
        
        # Test LIMIT and SKIP
        query5 = (
            match(node("Person", variable="p"))
            .return_("p.name", "p.age")
            .skip(10)
            .limit(5)
        )
        result5 = query5.to_cypher()
        assert "SKIP 10" in result5
        assert "LIMIT 5" in result5
        print("✅ LIMIT and SKIP clauses work")
        
        # Test complex query chain
        query6 = (
            match(node("Person", variable="p"))
            .where(prop("p", "active") == literal(True))
            .with_("p.name AS name", "p.age AS age")
            .order_by(desc("age"))
            .skip(5)
            .limit(10)
            .return_("name", "age")
        )
        result6 = query6.to_cypher()
        expected_parts = [
            "MATCH (p:Person)",
            "WHERE p.active = true",
            "WITH p.name AS name, p.age AS age",
            "ORDER BY age DESC",
            "SKIP 5",
            "LIMIT 10",
            "RETURN name, age"
        ]
        for part in expected_parts:
            assert part in result6, f"Expected '{part}' in result"
        print("✅ Complex query chain works")
        
        # Test relationships
        query7 = (
            match(node("Person", variable="p").relates_to("r", "KNOWS", ">", node("Person", variable="f")))
            .return_("p.name", "f.name")
        )
        result7 = query7.to_cypher()
        assert "MATCH (p:Person)-[r:KNOWS]->(f:Person)" in result7
        print("✅ Relationship patterns work")
        
        # Test tuple projections in WITH
        query8 = (
            match(node("Person", variable="p"))
            .with_(("p.name", "personName"), ("p.age", "personAge"))
            .return_("personName", "personAge")
        )
        result8 = query8.to_cypher()
        assert "WITH p.name AS personName, p.age AS personAge" in result8
        print("✅ Tuple projections in WITH work")
        
        print("\n🎉 All basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_real_world_examples():
    """Test some real-world example queries."""
    print("\n🎯 Testing real-world examples...\n")
    
    try:
        from super_sniffle import (
            match, node, prop, var, literal, asc, desc, param
        )
        
        # Example 1: Find top friends
        query1 = (
            match(node("Person", variable="p").relates_to("r", "KNOWS", ">", node("Person", variable="f")))
            .with_(("p.name", "personName"), ("count(f)", "friendCount"))
            .order_by(desc("friendCount"), "personName")
            .limit(10)
            .return_("personName", "friendCount")
        )
        result1 = query1.to_cypher()
        print("✅ Top friends query generated successfully")
        
        # Example 2: Employee pagination
        query2 = (
            match(node("Employee", variable="e"))
            .where(prop("e", "department") == param("dept_name"))
            .return_("e.name", "e.salary", "e.startDate")
            .order_by("e.name")
            .skip("$offset")
            .limit("$page_size")
        )
        result2 = query2.to_cypher()
        print(f"DEBUG: Employee pagination query result:\n{result2}\n")
        assert "$dept_name" in result2
        assert "$offset" in result2
        assert "$page_size" in result2
        print("✅ Employee pagination query with parameters works")
        
        # Example 3: Complex aggregation
        query3 = (
            match(node("Person", variable="p"))
            .where(prop("p", "age") > literal(18))
            .with_("p.department AS dept", "count(p) AS count", "avg(p.salary) AS avgSalary")
            .where(var("count") > literal(5))
            .order_by(desc("avgSalary"))
            .return_("dept", "count", "avgSalary")
        )
        result3 = query3.to_cypher()
        print("✅ Complex aggregation query works")
        
        print("\n🎉 All real-world examples work correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Real-world example failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🧪 Running super-sniffle unit tests...\n")
    
    success1 = test_basic_functionality()
    success2 = test_real_world_examples()
    
    if success1 and success2:
        print("\n✨ All tests passed! The super-sniffle implementation is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed.")
        sys.exit(1)
