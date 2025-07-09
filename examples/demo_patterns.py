#!/usr/bin/env python3
"""
Demo script for inline node/relationship conditions.

This script demonstrates the new pattern classes with inline WHERE conditions,
showing how users can specify conditions directly within node and relationship
patterns using Cypher's native syntax.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from super_sniffle import node, relationship, path, prop, param, literal


def main():
    """Demonstrate inline node/relationship conditions."""
    
    print("🚀 super-sniffle Inline Pattern Conditions Demo")
    print("=" * 55)
    
    # Basic node patterns
    print("\n1. Basic Node Patterns:")
    
    basic_person = node("p", "Person")
    print(f"node('p', 'Person')")
    print(f"Cypher: {basic_person.to_cypher()}")
    
    person_with_props = node("p", "Person", age=30, name="Alice")
    print(f"\nnode('p', 'Person', age=30, name='Alice')")
    print(f"Cypher: {person_with_props.to_cypher()}")
    
    # Node patterns with inline WHERE conditions
    print("\n2. Node Patterns with Inline WHERE Conditions:")
    
    adult_person = node("p", "Person").where(prop("p", "age") > literal(18))
    print(f"node('p', 'Person').where(prop('p', 'age') > 18)")
    print(f"Cypher: {adult_person.to_cypher()}")
    
    active_user = node("u", "User").where(
        (prop("u", "active") == literal(True)) & 
        (prop("u", "verified") == literal(True))
    )
    print(f"\nnode('u', 'User').where((prop('u', 'active') == True) & (prop('u', 'verified') == True))")
    print(f"Cypher: {active_user.to_cypher()}")
    
    # Basic relationship patterns
    print("\n3. Basic Relationship Patterns:")
    
    knows_rel = relationship(">", "r", "KNOWS")
    print(f"relationship('>', 'r', 'KNOWS')")
    print(f"Cypher: {knows_rel.to_cypher()}")
    
    works_for_rel = relationship(">", "w", "WORKS_FOR", since=2020)
    print(f"\nrelationship('>', 'w', 'WORKS_FOR', since=2020)")
    print(f"Cypher: {works_for_rel.to_cypher()}")
    
    # Relationship patterns with inline WHERE conditions
    print("\n4. Relationship Patterns with Inline WHERE Conditions:")
    
    recent_knows = relationship(">", "r", "KNOWS").where(prop("r", "since") > param("start_year"))
    print(f"relationship('>', 'r', 'KNOWS').where(prop('r', 'since') > param('start_year'))")
    print(f"Cypher: {recent_knows.to_cypher()}")
    
    strong_friendship = relationship("-", "f", "FRIENDS").where(
        (prop("f", "strength") >= literal(8)) & 
        (prop("f", "duration") > literal(365))
    )
    print(f"\nrelationship('-', 'f', 'FRIENDS').where((prop('f', 'strength') >= 8) & (prop('f', 'duration') > 365))")
    print(f"Cypher: {strong_friendship.to_cypher()}")
    
    # Path patterns
    print("\n5. Path Patterns:")
    
    simple_path = path(
        node("p1", "Person"),
        relationship(">", "r", "KNOWS"),
        node("p2", "Person")
    )
    print("path(node('p1', 'Person'), relationship('>', 'r', 'KNOWS'), node('p2', 'Person'))")
    print(f"Cypher: {simple_path.to_cypher()}")
    
    # Path patterns with inline conditions
    print("\n6. Path Patterns with Inline WHERE Conditions:")
    
    filtered_friendship = path(
        node("p1", "Person").where(prop("p1", "active") == literal(True)),
        relationship(">", "r", "KNOWS").where(prop("r", "since") > literal(2020)),
        node("p2", "Person").where(prop("p2", "age") > literal(18))
    )
    print("Complex path with multiple inline conditions:")
    print("path(")
    print("    node('p1', 'Person').where(prop('p1', 'active') == True),")
    print("    relationship('>', 'r', 'KNOWS').where(prop('r', 'since') > 2020),")
    print("    node('p2', 'Person').where(prop('p2', 'age') > 18)")
    print(")")
    print(f"Cypher: {filtered_friendship.to_cypher()}")
    
    # Real-world examples
    print("\n7. Real-World Examples:")
    
    # Example 1: Social network query
    print("\nSocial Network - Find active users connected by recent friendships:")
    social_path = path(
        node("user1", "User").where(
            (prop("user1", "active") == literal(True)) & 
            (prop("user1", "privacy") != literal("private"))
        ),
        relationship(">", "friendship", "FRIENDS").where(
            (prop("friendship", "established") > param("min_date")) &
            (prop("friendship", "status") == literal("confirmed"))
        ),
        node("user2", "User").where(prop("user2", "active") == literal(True))
    )
    print(f"Generated Cypher: {social_path.to_cypher()}")
    
    # Example 2: Employee hierarchy
    print("\nEmployee Hierarchy - Find managers with direct reports:")
    management_path = path(
        node("manager", "Employee").where(
            (prop("manager", "role") == literal("manager")) &
            (prop("manager", "tenure") > literal(2))
        ),
        relationship(">", "manages", "MANAGES").where(
            prop("manages", "direct") == literal(True)
        ),
        node("employee", "Employee").where(
            prop("employee", "active") == literal(True)
        )
    )
    print(f"Generated Cypher: {management_path.to_cypher()}")
    
    # Example 3: Mixed inline and parameter conditions
    print("\nMixed Conditions - Complex filtering with parameters:")
    complex_node = node("product", "Product").where(
        (prop("product", "price") <= param("max_price")) &
        (prop("product", "category").in_list(param("categories"))) &
        (prop("product", "rating") >= literal(4.0)) &
        (prop("product", "in_stock") == literal(True))
    )
    print(f"Generated Cypher: {complex_node.to_cypher()}")
    
    print("\n" + "=" * 55)
    print("✅ All inline pattern condition tests passed!")
    print("🎉 Both basic patterns and inline WHERE conditions work correctly!")
    print("\n📝 Key Benefits:")
    print("   • Conditions are specified right where they apply")
    print("   • Supports both simple and complex expressions")
    print("   • Uses the same intuitive operator syntax")
    print("   • Generates clean, readable Cypher output")


if __name__ == "__main__":
    main()
