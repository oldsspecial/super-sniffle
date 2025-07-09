#!/usr/bin/env python3
"""
Demo script for ORDER BY clause functionality and improved WITH clause.

This script demonstrates the new ORDER BY implementation with asc() and desc() functions,
as well as the improved WITH clause that supports tuple-based projections.
"""

from super_sniffle import (
    match, node, prop, literal, var, asc, desc
)

def demo_order_by_with_return():
    """Demonstrate ORDER BY with RETURN clause."""
    print("=== ORDER BY with RETURN ===")
    
    # Basic ascending sort (string)
    query1 = (
        match(node("p", "Person"))
        .return_("p.name", "p.age")
        .order_by("p.age")
    )
    print("Basic ascending sort:")
    print(query1.to_cypher())
    print()
    
    # Mixed string and expression sorts
    query2 = (
        match(node("p", "Person"))
        .return_("p.name", "p.age")
        .order_by("p.name", desc("p.age"))
    )
    print("Mixed string and expression sorts:")
    print(query2.to_cypher())
    print()
    
    # Multiple expression sorts
    query3 = (
        match(node("p", "Person"))
        .return_("p.name", "p.age", "p.city")
        .order_by(asc("p.city"), desc("p.age"), asc("p.name"))
    )
    print("Multiple expression sorts:")
    print(query3.to_cypher())
    print()

def demo_order_by_with_with():
    """Demonstrate ORDER BY with WITH clause using tuple projections."""
    print("=== ORDER BY with WITH (tuple projections) ===")
    
    # WITH using tuple projections, then ORDER BY
    query1 = (
        match(node("p", "Person"))
        .with_(("p.name", "name"), ("p.age", "age"), ("p.city", "city"))
        .order_by("name", desc("age"))
    )
    print("WITH tuple projections then ORDER BY:")
    print(query1.to_cypher())
    print()
    
    # Mixed string and tuple projections in WITH
    query2 = (
        match(node("p", "Person"))
        .with_("p", ("count(*)", "total"))
        .order_by(desc("total"))
    )
    print("Mixed string and tuple projections:")
    print(query2.to_cypher())
    print()
    
    # Complex aggregation with ORDER BY
    query3 = (
        match(node("p", "Person").relates_to(">", "KNOWS", node("f", "Person")))
        .with_(("p.name", "personName"), ("count(f)", "friendCount"))
        .order_by(desc("friendCount"), "personName")
    )
    print("Complex aggregation with ORDER BY:")
    print(query3.to_cypher())
    print()

def demo_order_by_chain():
    """Demonstrate ORDER BY in complex query chains."""
    print("=== ORDER BY in complex chains ===")
    
    # MATCH → WHERE → WITH → ORDER BY → RETURN
    query1 = (
        match(node("p", "Person"))
        .where(prop("p", "age") > literal(18))
        .with_(("p.name", "name"), ("p.age", "age"))
        .order_by(desc("age"))
        .return_("name", "age")
    )
    print("MATCH → WHERE → WITH → ORDER BY → RETURN:")
    print(query1.to_cypher())
    print()

def demo_with_clause_improvements():
    """Demonstrate the improved WITH clause tuple functionality."""
    print("=== Improved WITH clause (tuple projections) ===")
    
    # Simple tuple projections
    query1 = (
        match(node("p", "Person"))
        .with_(("p.name", "personName"), ("p.age", "personAge"))
        .return_("personName", "personAge")
    )
    print("Simple tuple projections:")
    print(query1.to_cypher())
    print()
    
    # Mixed projections
    query2 = (
        match(node("p", "Person"))
        .with_("p", ("p.name", "name"), ("p.age", "age"))
        .return_("p.id", "name", "age")
    )
    print("Mixed string and tuple projections:")
    print(query2.to_cypher())
    print()
    
    # WITH DISTINCT using tuples
    query3 = (
        match(node("p", "Person"))
        .with_(("p.department", "dept"), distinct=True)
        .return_("dept")
    )
    print("WITH DISTINCT using tuples:")
    print(query3.to_cypher())
    print()
    
    # Complex expressions in tuples
    query4 = (
        match(node("p", "Person").relates_to(">", "WORKS_FOR", node("c", "Company")))
        .with_(("p.name", "employeeName"), ("c.name", "companyName"), ("p.salary * 12", "annualSalary"))
        .order_by(desc("annualSalary"))
        .return_("employeeName", "companyName", "annualSalary")
    )
    print("Complex expressions in tuple projections:")
    print(query4.to_cypher())
    print()

def demo_real_world_examples():
    """Demonstrate real-world usage examples."""
    print("=== Real-world examples ===")
    
    # Find top 5 most connected people
    query1 = (
        match(node("p", "Person").relates_to("-", "KNOWS", node("friend", "Person")))
        .with_(("p.name", "personName"), ("count(friend)", "friendCount"))
        .order_by(desc("friendCount"), "personName")
        # .limit(5)  # TODO: Implement LIMIT
        .return_("personName", "friendCount")
    )
    print("Top most connected people:")
    print(query1.to_cypher())
    print()
    
    # Employee rankings by salary within departments
    query2 = (
        match(node("e", "Employee").relates_to(">", "WORKS_IN", node("d", "Department")))
        .with_(("e.name", "employeeName"), ("d.name", "deptName"), ("e.salary", "salary"))
        .order_by("deptName", desc("salary"))
        .return_("deptName", "employeeName", "salary")
    )
    print("Employee rankings by salary within departments:")
    print(query2.to_cypher())
    print()

if __name__ == "__main__":
    print("Testing ORDER BY clause and improved WITH clause functionality\n")
    
    demo_order_by_with_return()
    demo_order_by_with_with()
    demo_order_by_chain()
    demo_with_clause_improvements()
    demo_real_world_examples()
    
    print("All demos completed successfully! 🎉")
