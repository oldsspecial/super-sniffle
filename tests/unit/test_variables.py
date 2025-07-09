"""
Unit tests for Variable expressions.

Tests the Variable class and var() function for handling variables
introduced by WITH clauses and other query constructs.
"""

import pytest
from super_sniffle.ast.expressions import Variable
from super_sniffle import var, literal


class TestVariable:
    """Test Variable expression class."""
    
    def test_variable_creation(self):
        """Test Variable object creation."""
        variable = Variable("friendCount")
        assert variable.name == "friendCount"
    
    def test_variable_to_cypher(self):
        """Test Variable to_cypher method."""
        variable = Variable("friendCount")
        assert variable.to_cypher() == "friendCount"
        
        # Test with different variable names
        assert Variable("totalCount").to_cypher() == "totalCount"
        assert Variable("user").to_cypher() == "user"
    
    def test_variable_equality_comparison(self):
        """Test Variable equality comparison."""
        variable = Variable("count")
        
        # Test with literal
        expr = variable == literal(5)
        assert expr.to_cypher() == "count = 5"
        
        # Test with another variable
        other_var = Variable("limit")
        expr2 = variable == other_var
        assert expr2.to_cypher() == "count = limit"
    
    def test_variable_inequality_comparison(self):
        """Test Variable inequality comparison."""
        variable = Variable("count")
        
        expr = variable != literal(0)
        assert expr.to_cypher() == "count <> 0"
    
    def test_variable_numeric_comparisons(self):
        """Test Variable numeric comparison operators."""
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
    
    def test_variable_string_operations(self):
        """Test Variable string operations."""
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
    
    def test_variable_list_operations(self):
        """Test Variable list operations."""
        variable = Variable("category")
        
        # In list
        expr = variable.in_list(literal(["A", "B", "C"]))
        assert expr.to_cypher() == "category IN ['A', 'B', 'C']"
    
    def test_variable_null_operations(self):
        """Test Variable NULL operations."""
        variable = Variable("optionalField")
        
        # Is null
        expr1 = variable.is_null()
        assert expr1.to_cypher() == "optionalField IS NULL"
        
        # Is not null
        expr2 = variable.is_not_null()
        assert expr2.to_cypher() == "optionalField IS NOT NULL"
    
    def test_variable_logical_operations(self):
        """Test Variable logical operations."""
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


class TestVarFunction:
    """Test var() function."""
    
    def test_var_function_creates_variable(self):
        """Test that var() function creates Variable instances."""
        variable = var("friendCount")
        assert isinstance(variable, Variable)
        assert variable.name == "friendCount"
    
    def test_var_function_cypher_output(self):
        """Test var() function Cypher output."""
        variable = var("totalUsers")
        assert variable.to_cypher() == "totalUsers"
    
    def test_var_function_with_comparisons(self):
        """Test var() function with comparison operations."""
        count_var = var("friendCount")
        
        # Test chaining operations
        expr = count_var > literal(3)
        assert expr.to_cypher() == "friendCount > 3"
    
    def test_var_function_with_logical_operations(self):
        """Test var() function with logical operations."""
        count_var = var("friendCount")
        age_var = var("userAge")
        
        # Test complex expression
        expr = (count_var > literal(5)) & (age_var >= literal(18))
        assert expr.to_cypher() == "(friendCount > 5) AND (userAge >= 18)"
    
    def test_var_function_edge_cases(self):
        """Test var() function with edge cases."""
        # Test with empty string (though not recommended)
        empty_var = var("")
        assert empty_var.to_cypher() == ""
        
        # Test with special characters in name
        special_var = var("user_count_2")
        assert special_var.to_cypher() == "user_count_2"
        
        # Test with camelCase
        camel_var = var("friendCount")
        assert camel_var.to_cypher() == "friendCount"


class TestVariableIntegration:
    """Test Variable integration with other components."""
    
    def test_variable_with_literals(self):
        """Test Variable used with different literal types."""
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
    
    def test_variable_mixed_expressions(self):
        """Test Variable in mixed expressions with properties."""
        from super_sniffle import prop
        
        count_var = var("friendCount")
        age_prop = prop("p", "age")
        
        # Mix variable and property in expression
        expr = (count_var > literal(3)) & (age_prop >= literal(18))
        expected = "(friendCount > 3) AND (p.age >= 18)"
        assert expr.to_cypher() == expected
