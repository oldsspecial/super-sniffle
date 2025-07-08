"""
Unit tests for expression classes.

Tests the operator overloading functionality and Cypher string generation
for property comparisons and logical operations.
"""

import pytest
from super_sniffle.ast import (
    Property,
    Parameter,
    Literal,
    ComparisonExpression,
    LogicalExpression,
    NotExpression,
)
from super_sniffle.api import prop, param, literal


class TestProperty:
    """Test the Property class and its operator overloading."""
    
    def test_property_creation(self):
        """Test basic property creation."""
        p = Property("user", "age")
        assert p.variable == "user"
        assert p.name == "age"
        assert p.to_cypher() == "user.age"
    
    def test_equality_operator(self):
        """Test == operator creates correct comparison."""
        p = prop("user", "name")
        param_ref = param("user_name")
        
        expr = p == param_ref
        assert isinstance(expr, ComparisonExpression)
        assert expr.left == p
        assert expr.operator == "="
        assert expr.right == param_ref
        assert expr.to_cypher() == "user.name = $user_name"
    
    def test_inequality_operator(self):
        """Test != operator creates correct comparison."""
        p = prop("user", "name")
        lit = literal("Alice")
        
        expr = p != lit
        assert isinstance(expr, ComparisonExpression)
        assert expr.operator == "<>"
        assert expr.to_cypher() == "user.name <> 'Alice'"
    
    def test_greater_than_operator(self):
        """Test > operator creates correct comparison."""
        p = prop("user", "age")
        lit = literal(30)
        
        expr = p > lit
        assert isinstance(expr, ComparisonExpression)
        assert expr.operator == ">"
        assert expr.to_cypher() == "user.age > 30"
    
    def test_less_than_operator(self):
        """Test < operator creates correct comparison."""
        p = prop("user", "age")
        param_ref = param("max_age")
        
        expr = p < param_ref
        assert isinstance(expr, ComparisonExpression)
        assert expr.operator == "<"
        assert expr.to_cypher() == "user.age < $max_age"
    
    def test_greater_equal_operator(self):
        """Test >= operator creates correct comparison."""
        p = prop("user", "score")
        lit = literal(85)
        
        expr = p >= lit
        assert isinstance(expr, ComparisonExpression)
        assert expr.operator == ">="
        assert expr.to_cypher() == "user.score >= 85"
    
    def test_less_equal_operator(self):
        """Test <= operator creates correct comparison."""
        p = prop("user", "score")
        lit = literal(100)
        
        expr = p <= lit
        assert isinstance(expr, ComparisonExpression)
        assert expr.operator == "<="
        assert expr.to_cypher() == "user.score <= 100"
    
    def test_method_based_operations(self):
        """Test method-based operations for special Cypher operators."""
        p = prop("user", "name")
        
        # Test CONTAINS
        contains_expr = p.contains(literal("Alice"))
        assert contains_expr.operator == "CONTAINS"
        assert contains_expr.to_cypher() == "user.name CONTAINS 'Alice'"
        
        # Test STARTS WITH
        starts_expr = p.starts_with(param("prefix"))
        assert starts_expr.operator == "STARTS WITH"
        assert starts_expr.to_cypher() == "user.name STARTS WITH $prefix"
        
        # Test ENDS WITH
        ends_expr = p.ends_with(literal("@example.com"))
        assert ends_expr.operator == "ENDS WITH"
        assert ends_expr.to_cypher() == "user.name ENDS WITH '@example.com'"
        
        # Test IN
        in_expr = p.in_list(param("name_list"))
        assert in_expr.operator == "IN"
        assert in_expr.to_cypher() == "user.name IN $name_list"
        
        # Test IS NULL
        null_expr = p.is_null()
        assert null_expr.operator == "IS"
        assert null_expr.to_cypher() == "user.name IS NULL"
        
        # Test IS NOT NULL
        not_null_expr = p.is_not_null()
        assert not_null_expr.operator == "IS NOT"
        assert not_null_expr.to_cypher() == "user.name IS NOT NULL"


class TestParameter:
    """Test the Parameter class."""
    
    def test_parameter_creation(self):
        """Test basic parameter creation."""
        p = Parameter("min_age")
        assert p.name == "min_age"
        assert p.to_cypher() == "$min_age"
    
    def test_param_function(self):
        """Test the param() helper function."""
        p = param("user_id")
        assert isinstance(p, Parameter)
        assert p.name == "user_id"
        assert p.to_cypher() == "$user_id"


class TestLiteral:
    """Test the Literal class."""
    
    def test_string_literal(self):
        """Test string literal conversion."""
        lit = Literal("Hello World")
        assert lit.to_cypher() == "'Hello World'"
    
    def test_string_with_quotes_literal(self):
        """Test string literal with single quotes."""
        lit = Literal("It's a test")
        assert lit.to_cypher() == "'It\\'s a test'"
    
    def test_number_literal(self):
        """Test number literal conversion."""
        lit = Literal(42)
        assert lit.to_cypher() == "42"
        
        lit_float = Literal(3.14)
        assert lit_float.to_cypher() == "3.14"
    
    def test_boolean_literal(self):
        """Test boolean literal conversion."""
        lit_true = Literal(True)
        assert lit_true.to_cypher() == "true"
        
        lit_false = Literal(False)
        assert lit_false.to_cypher() == "false"
    
    def test_none_literal(self):
        """Test None/null literal conversion."""
        lit = Literal(None)
        assert lit.to_cypher() == "null"
    
    def test_literal_function(self):
        """Test the literal() helper function."""
        lit = literal("test")
        assert isinstance(lit, Literal)
        assert lit.value == "test"
        assert lit.to_cypher() == "'test'"


class TestLogicalExpressions:
    """Test logical expression combinations using operators."""
    
    def test_and_operator(self):
        """Test & operator for AND logic."""
        expr1 = prop("user", "age") > literal(18)
        expr2 = prop("user", "active") == literal(True)
        
        combined = expr1 & expr2
        assert isinstance(combined, LogicalExpression)
        assert combined.operator == "AND"
        assert combined.to_cypher() == "(user.age > 18) AND (user.active = true)"
    
    def test_or_operator(self):
        """Test | operator for OR logic."""
        expr1 = prop("user", "role") == literal("admin")
        expr2 = prop("user", "role") == literal("moderator")
        
        combined = expr1 | expr2
        assert isinstance(combined, LogicalExpression)
        assert combined.operator == "OR"
        assert combined.to_cypher() == "(user.role = 'admin') OR (user.role = 'moderator')"
    
    def test_not_operator(self):
        """Test ~ operator for NOT logic."""
        expr = prop("user", "deleted") == literal(True)
        negated = ~expr
        
        assert isinstance(negated, NotExpression)
        assert negated.to_cypher() == "NOT (user.deleted = true)"
    
    def test_complex_expression(self):
        """Test complex expression with multiple operators."""
        # (user.age > 18 AND user.active = true) OR user.role = 'admin'
        age_check = prop("user", "age") > literal(18)
        active_check = prop("user", "active") == literal(True)
        role_check = prop("user", "role") == literal("admin")
        
        complex_expr = (age_check & active_check) | role_check
        
        expected = "((user.age > 18) AND (user.active = true)) OR (user.role = 'admin')"
        assert complex_expr.to_cypher() == expected
    
    def test_nested_not_expression(self):
        """Test NOT with nested expressions."""
        # NOT (user.age < 18 OR user.banned = true)
        age_check = prop("user", "age") < literal(18)
        banned_check = prop("user", "banned") == literal(True)
        
        nested_expr = ~(age_check | banned_check)
        
        expected = "NOT ((user.age < 18) OR (user.banned = true))"
        assert nested_expr.to_cypher() == expected


class TestAPIFunctions:
    """Test the public API functions."""
    
    def test_prop_function(self):
        """Test the prop() function."""
        p = prop("node", "property")
        assert isinstance(p, Property)
        assert p.variable == "node"
        assert p.name == "property"
    
    def test_param_function(self):
        """Test the param() function."""
        p = param("parameter_name")
        assert isinstance(p, Parameter)
        assert p.name == "parameter_name"
    
    def test_literal_function(self):
        """Test the literal() function."""
        lit = literal("value")
        assert isinstance(lit, Literal)
        assert lit.value == "value"


class TestRealWorldScenarios:
    """Test realistic usage scenarios."""
    
    def test_user_age_and_status_filter(self):
        """Test a realistic user filtering scenario."""
        # WHERE user.age >= 18 AND user.status = 'active'
        expr = (prop("user", "age") >= param("min_age")) & (prop("user", "status") == literal("active"))
        
        expected = "(user.age >= $min_age) AND (user.status = 'active')"
        assert expr.to_cypher() == expected
    
    def test_product_search_filter(self):
        """Test a product search scenario."""
        # WHERE (product.name CONTAINS 'laptop' OR product.category = 'electronics') 
        # AND product.price <= 1000 AND product.in_stock = true
        name_search = prop("product", "name").contains(param("search_term"))
        category_filter = prop("product", "category") == literal("electronics")
        price_filter = prop("product", "price") <= param("max_price")
        stock_filter = prop("product", "in_stock") == literal(True)
        
        expr = (name_search | category_filter) & price_filter & stock_filter
        
        expected = (
            "((product.name CONTAINS $search_term) OR (product.category = 'electronics')) "
            "AND (product.price <= $max_price) AND (product.in_stock = true)"
        )
        assert expr.to_cypher() == expected
    
    def test_null_checks(self):
        """Test NULL checking scenarios."""
        # WHERE user.email IS NOT NULL AND user.phone IS NULL
        email_check = prop("user", "email").is_not_null()
        phone_check = prop("user", "phone").is_null()
        
        expr = email_check & phone_check
        
        expected = "(user.email IS NOT NULL) AND (user.phone IS NULL)"
        assert expr.to_cypher() == expected
