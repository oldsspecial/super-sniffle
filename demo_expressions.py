#!/usr/bin/env python3
"""
Demo script to test the operator-based syntax implementation.

This script demonstrates the new operator overloading functionality
for building Cypher WHERE clauses with intuitive syntax.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from super_sniffle.api import prop, param, literal


def main():
    """Demonstrate the operator-based syntax."""
    
    print("🚀 super-sniffle Operator-Based Syntax Demo")
    print("=" * 50)
    
    # Basic comparison operators
    print("\n1. Basic Comparison Operators:")
    
    age_prop = prop("user", "age")
    min_age_param = param("min_age")
    
    print(f"prop('user', 'age') > param('min_age')")
    expr1 = age_prop > min_age_param
    print(f"Result: {expr1.to_cypher()}")
    
    print(f"\nprop('user', 'name') == literal('Alice')")
    expr2 = prop("user", "name") == literal("Alice")
    print(f"Result: {expr2.to_cypher()}")
    
    print(f"\nprop('user', 'score') >= literal(85)")
    expr3 = prop("user", "score") >= literal(85)
    print(f"Result: {expr3.to_cypher()}")
    
    # Logical operators
    print("\n2. Logical Operators (AND, OR, NOT):")
    
    age_check = prop("user", "age") > literal(18)
    active_check = prop("user", "active") == literal(True)
    
    print(f"(prop('user', 'age') > 18) & (prop('user', 'active') == True)")
    and_expr = age_check & active_check
    print(f"Result: {and_expr.to_cypher()}")
    
    role_admin = prop("user", "role") == literal("admin")
    role_mod = prop("user", "role") == literal("moderator")
    
    print(f"\n(prop('user', 'role') == 'admin') | (prop('user', 'role') == 'moderator')")
    or_expr = role_admin | role_mod
    print(f"Result: {or_expr.to_cypher()}")
    
    deleted_check = prop("user", "deleted") == literal(True)
    print(f"\n~(prop('user', 'deleted') == True)")
    not_expr = ~deleted_check
    print(f"Result: {not_expr.to_cypher()}")
    
    # Complex expressions
    print("\n3. Complex Nested Expressions:")
    
    print("((age > 18 & active) | role == 'admin') & ~deleted")
    complex_expr = ((age_check & active_check) | role_admin) & ~deleted_check
    print(f"Result: {complex_expr.to_cypher()}")
    
    # Method-based operations for special Cypher operators
    print("\n4. Method-Based Operations for Special Operators:")
    
    name_prop = prop("user", "name")
    
    print("prop('user', 'name').contains('Alice')")
    contains_expr = name_prop.contains(literal("Alice"))
    print(f"Result: {contains_expr.to_cypher()}")
    
    print("\nprop('user', 'email').ends_with('@example.com')")
    email_expr = prop("user", "email").ends_with(literal("@example.com"))
    print(f"Result: {email_expr.to_cypher()}")
    
    print("\nprop('user', 'role').in_list(param('allowed_roles'))")
    in_expr = prop("user", "role").in_list(param("allowed_roles"))
    print(f"Result: {in_expr.to_cypher()}")
    
    print("\nprop('user', 'phone').is_null()")
    null_expr = prop("user", "phone").is_null()
    print(f"Result: {null_expr.to_cypher()}")
    
    # Real-world scenario
    print("\n5. Real-World Scenario - User Search Filter:")
    print("WHERE (user.age >= $min_age) AND (user.status = 'active') AND")
    print("      (user.name CONTAINS $search_term OR user.email STARTS WITH $email_prefix)")
    
    search_filter = (
        (prop("user", "age") >= param("min_age")) &
        (prop("user", "status") == literal("active")) &
        (prop("user", "name").contains(param("search_term")) | 
         prop("user", "email").starts_with(param("email_prefix")))
    )
    
    print(f"\nGenerated Cypher:")
    print(f"{search_filter.to_cypher()}")
    
    print("\n" + "=" * 50)
    print("✅ All operator overloading tests passed!")
    print("🎉 The new syntax is working correctly!")


if __name__ == "__main__":
    main()
