#!/usr/bin/env python3
"""
Simple test runner for Variable tests that doesn't require pytest.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from super_sniffle.ast.expressions import Variable
from super_sniffle import var, literal, prop


def test_variable_creation():
    """Test Variable object creation."""
    print("Testing Variable creation...")
    variable = Variable("friendCount")
    assert variable.name == "friendCount"
    print("✅ Variable creation works")


def test_variable_to_cypher():
    """Test Variable to_cypher method."""
    print("Testing Variable to_cypher...")
    variable = Variable("friendCount")
    assert variable.to_cypher() == "friendCount"
    
    # Test with different variable names
    assert Variable("totalCount").to_cypher() == "totalCount"
    assert Variable("user").to_cypher() == "user"
    print("✅ Variable to_cypher works")


def test_variable_equality_comparison():
    """Test Variable equality comparison."""
    print("Testing Variable equality comparison...")
    variable = Variable("count")
    
    # Test with literal
    expr = variable == literal(5)
    assert expr.to_cypher() == "count = 5"
    
    # Test with another variable
    other_var = Variable("limit")
    expr2 = variable == other_var
    assert expr2.to_cypher() == "count = limit"
    print("✅ Variable equality comparison works")


def test_variable_inequality_comparison():
    """Test Variable inequality comparison."""
    print("Testing Variable inequality comparison...")
    variable = Variable("count")
    
    expr = variable != literal(0)
    assert expr.to_cypher() == "count <> 0"
    print("✅ Variable inequality comparison works")


def test_variable_numeric_comparisons():
    """Test Variable numeric comparison operators."""
    print("Testing Variable numeric comparisons...")
    variable = Variable("score")
    
    # Greater than
    expr1 = variable > literal(10)
    assert expr1.to_cypher() == "score > 10"
    
    # Less than
    expr2 = variable < literal(100)
    assert expr2.to_cypher() == "score < 100"
    
    # Greater than or equal
    expr3 = variable >= literal(50)
    assert expr3.to_cypher() == "score >= 50"
    
    # Less than or equal
    expr4 = variable <= literal(75)
    assert expr4.to_cypher() == "score <= 75"
    print("✅ Variable numeric comparisons work")


def test_variable_string_operations():
    """Test Variable string operations."""
    print("Testing Variable string operations...")
    variable = Variable("name")
    
    # Contains
    expr1 = variable.contains(literal("Alice"))
    assert expr1.to_cypher() == "name CONTAINS 'Alice'"
    
    # Starts with
    expr2 = variable.starts_with(literal("Mr"))
    assert expr2.to_cypher() == "name STARTS WITH 'Mr'"
    
    # Ends with
    expr3 = variable.ends_with(literal("son"))
    assert expr3.to_cypher() == "name ENDS WITH 'son'"
    print("✅ Variable string operations work")


def test_variable_list_operations():
    """Test Variable list operations."""
    print("Testing Variable list operations...")
    variable = Variable("category")
    
    # In list
    expr = variable.in_list(literal(["A", "B", "C"]))
    assert expr.to_cypher() == "category IN ['A', 'B', 'C']"
    print("✅ Variable list operations work")


def test_variable_null_operations():
    """Test Variable NULL operations."""
    print("Testing Variable NULL operations...")
    variable = Variable("optionalField")
    
    # Is null
    expr1 = variable.is_null()
    assert expr1.to_cypher() == "optionalField IS NULL"
    
    # Is not null
    expr2 = variable.is_not_null()
    assert expr2.to_cypher() == "optionalField IS NOT NULL"
    print("✅ Variable NULL operations work")


def test_variable_logical_operations():
    """Test Variable logical operations."""
    print("Testing Variable logical operations...")
    var1 = Variable("count")
    var2 = Variable("score")
    
    # AND
    expr1 = (var1 > literal(5)) & (var2 < literal(100))
    assert expr1.to_cypher() == "(count > 5) AND (score < 100)"
    
    # OR
    expr2 = (var1 == literal(0)) | (var2 >= literal(90))
    assert expr2.to_cypher() == "(count = 0) OR (score >= 90)"
    
    # NOT
    expr3 = ~(var1 > literal(10))
    assert expr3.to_cypher() == "NOT (count > 10)"
    print("✅ Variable logical operations work")


def test_var_function_creates_variable():
    """Test that var() function creates Variable instances."""
    print("Testing var() function creates Variable...")
    variable = var("friendCount")
    assert isinstance(variable, Variable)
    assert variable.name == "friendCount"
    print("✅ var() function creates Variable")


def test_var_function_cypher_output():
    """Test var() function Cypher output."""
    print("Testing var() function Cypher output...")
    variable = var("totalUsers")
    assert variable.to_cypher() == "totalUsers"
    print("✅ var() function Cypher output works")


def test_var_function_with_comparisons():
    """Test var() function with comparison operations."""
    print("Testing var() function with comparisons...")
    count_var = var("friendCount")
    
    # Test chaining operations
    expr = count_var > literal(3)
    assert expr.to_cypher() == "friendCount > 3"
    print("✅ var() function with comparisons works")


def test_var_function_with_logical_operations():
    """Test var() function with logical operations."""
    print("Testing var() function with logical operations...")
    count_var = var("friendCount")
    age_var = var("userAge")
    
    # Test complex expression
    expr = (count_var > literal(5)) & (age_var >= literal(18))
    assert expr.to_cypher() == "(friendCount > 5) AND (userAge >= 18)"
    print("✅ var() function with logical operations works")


def test_variable_with_literals():
    """Test Variable used with different literal types."""
    print("Testing Variable with different literals...")
    variable = Variable("value")
    
    # String literal
    expr1 = variable == literal("test")
    assert expr1.to_cypher() == "value = 'test'"
    
    # Number literal
    expr2 = variable > literal(42)
    assert expr2.to_cypher() == "value > 42"
    
    # Boolean literal
    expr3 = variable == literal(True)
    assert expr3.to_cypher() == "value = true"
    
    # Null literal
    expr4 = variable == literal(None)
    assert expr4.to_cypher() == "value = null"
    print("✅ Variable with different literals works")


def test_variable_mixed_expressions():
    """Test Variable in mixed expressions with properties."""
    print("Testing Variable in mixed expressions...")
    count_var = var("friendCount")
    age_prop = prop("p", "age")
    
    # Mix variable and property in expression
    expr = (count_var > literal(3)) & (age_prop >= literal(18))
    expected = "(friendCount > 3) AND (p.age >= 18)"
    assert expr.to_cypher() == expected
    print("✅ Variable in mixed expressions works")


if __name__ == "__main__":
    print("🚀 Running Variable unit tests...\n")
    
    try:
        test_variable_creation()
        test_variable_to_cypher()
        test_variable_equality_comparison()
        test_variable_inequality_comparison()
        test_variable_numeric_comparisons()
        test_variable_string_operations()
        test_variable_list_operations()
        test_variable_null_operations()
        test_variable_logical_operations()
        test_var_function_creates_variable()
        test_var_function_cypher_output()
        test_var_function_with_comparisons()
        test_var_function_with_logical_operations()
        test_variable_with_literals()
        test_variable_mixed_expressions()
        
        print("\n🎉 All Variable unit tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
