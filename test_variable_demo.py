#!/usr/bin/env python3
"""
Demo script to test the new var() function for Variable expressions.

This script demonstrates the working Variable implementation.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from super_sniffle import var, literal


def test_variable_creation():
    """Test basic Variable creation."""
    print("Testing basic Variable creation...")
    
    # Create a variable
    count_var = var("friendCount")
    
    # Test to_cypher() method
    result = count_var.to_cypher()
    expected = "friendCount"
    print(f"Variable cypher: {result}")
    print(f"Expected: {expected}")
    assert result == expected, f"Expected '{expected}', got '{result}'"
    print("✅ Variable creation works!\n")


def test_variable_comparison_operators():
    """Test Variable comparison operators."""
    print("Testing Variable comparison operators...")
    
    count_var = var("friendCount")
    
    # Test equality
    expr1 = count_var == literal(5)
    result1 = expr1.to_cypher()
    expected1 = "friendCount = 5"
    print(f"Equality: {result1}")
    assert result1 == expected1, f"Expected '{expected1}', got '{result1}'"
    
    # Test greater than
    expr2 = count_var > literal(3)
    result2 = expr2.to_cypher()
    expected2 = "friendCount > 3"
    print(f"Greater than: {result2}")
    assert result2 == expected2, f"Expected '{expected2}', got '{result2}'"
    
    # Test less than or equal
    expr3 = count_var <= literal(10)
    result3 = expr3.to_cypher()
    expected3 = "friendCount <= 10"
    print(f"Less than or equal: {result3}")
    assert result3 == expected3, f"Expected '{expected3}', got '{result3}'"
    
    print("✅ Variable comparison operators work!\n")


def test_variable_special_operations():
    """Test Variable special operations."""
    print("Testing Variable special operations...")
    
    name_var = var("name")
    
    # Test contains
    expr1 = name_var.contains(literal("Alice"))
    result1 = expr1.to_cypher()
    expected1 = "name CONTAINS 'Alice'"
    print(f"Contains: {result1}")
    assert result1 == expected1, f"Expected '{expected1}', got '{result1}'"
    
    # Test starts_with
    expr2 = name_var.starts_with(literal("Mr"))
    result2 = expr2.to_cypher()
    expected2 = "name STARTS WITH 'Mr'"
    print(f"Starts with: {result2}")
    assert result2 == expected2, f"Expected '{expected2}', got '{result2}'"
    
    # Test is_null
    expr3 = name_var.is_null()
    result3 = expr3.to_cypher()
    expected3 = "name IS NULL"
    print(f"Is null: {result3}")
    assert result3 == expected3, f"Expected '{expected3}', got '{result3}'"
    
    print("✅ Variable special operations work!\n")


def test_variable_logical_operations():
    """Test Variable logical operations."""
    print("Testing Variable logical operations...")
    
    count_var = var("friendCount")
    age_var = var("age")
    
    # Test AND
    expr1 = (count_var > literal(3)) & (age_var >= literal(18))
    result1 = expr1.to_cypher()
    expected1 = "(friendCount > 3) AND (age >= 18)"
    print(f"AND: {result1}")
    assert result1 == expected1, f"Expected '{expected1}', got '{result1}'"
    
    # Test OR
    expr2 = (count_var == literal(0)) | (age_var < literal(13))
    result2 = expr2.to_cypher()
    expected2 = "(friendCount = 0) OR (age < 13)"
    print(f"OR: {result2}")
    assert result2 == expected2, f"Expected '{expected2}', got '{result2}'"
    
    # Test NOT
    expr3 = ~(count_var > literal(10))
    result3 = expr3.to_cypher()
    expected3 = "NOT (friendCount > 10)"
    print(f"NOT: {result3}")
    assert result3 == expected3, f"Expected '{expected3}', got '{result3}'"
    
    print("✅ Variable logical operations work!\n")


if __name__ == "__main__":
    print("🚀 Testing Variable expression implementation...\n")
    
    try:
        test_variable_creation()
        test_variable_comparison_operators()
        test_variable_special_operations()
        test_variable_logical_operations()
        
        print("🎉 All Variable tests passed! The var() function is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
