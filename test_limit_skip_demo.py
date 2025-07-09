#!/usr/bin/env python3
"""
Demo script for LIMIT and SKIP clause functionality.

This script demonstrates the new LIMIT and SKIP implementations for pagination
and result limiting in Cypher queries.
"""

from super_sniffle import (
    match, node, prop, literal, var, asc, desc
)

def demo_limit_basic():
    """Demonstrate basic LIMIT clause usage."""
    print("=== Basic LIMIT Usage ===")
    
    # Simple LIMIT with RETURN
    query1 = (
        match(node("p", "Person"))
        .return_("p.name", "p.age")
        .limit(10)
    )
    print("Simple LIMIT with RETURN:")
    print(query1.to_cypher())
    print()
    
    # LIMIT with ORDER BY
    query2 = (
        match(node("p", "Person"))
        .return_("p.name", "p.age")
        .order_by(desc("p.age"))
        .limit(5)
    )
    print("LIMIT with ORDER BY:")
    print(query2.to_cypher())
    print()
    
    # LIMIT with string parameter
    query3 = (
        match(node("p", "Person"))
        .return_("p.name", "p.age")
        .limit("$maxResults")
    )
    print("LIMIT with string parameter:")
    print(query3.to_cypher())
    print()

def demo_skip_basic():
    """Demonstrate basic SKIP clause usage."""
    print("=== Basic SKIP Usage ===")
    
    # Simple SKIP with RETURN
    query1 = (
        match(node("p", "Person"))
        .return_("p.name", "p.age")
        .skip(10)
    )
    print("Simple SKIP with RETURN:")
    print(query1.to_cypher())
    print()
    
    # SKIP with ORDER BY
    query2 = (
        match(node("p", "Person"))
        .return_("p.name", "p.age")
        .order_by(desc("p.age"))
        .skip(5)
    )
    print("SKIP with ORDER BY:")
    print(query2.to_cypher())
    print()
    
    # SKIP with string parameter
    query3 = (
        match(node("p", "Person"))
        .return_("p.name", "p.age")
        .skip("$offset")
    )
    print("SKIP with string parameter:")
    print(query3.to_cypher())
    print()

def demo_pagination():
    """Demonstrate pagination with SKIP and LIMIT."""
    print("=== Pagination with SKIP and LIMIT ===")
    
    # SKIP and LIMIT for pagination (common order)
    query1 = (
        match(node("p", "Person"))
        .return_("p.name", "p.age")
        .order_by("p.name")
        .skip(10)
        .limit(5)
    )
    print("SKIP then LIMIT for pagination:")
    print(query1.to_cypher())
    print()
    
    # LIMIT and SKIP (reverse order)
    query2 = (
        match(node("p", "Person"))
        .return_("p.name", "p.age")
        .order_by("p.name")
        .limit(15)
        .skip(10)
    )
    print("LIMIT then SKIP (reverse order):")
    print(query2.to_cypher())
    print()
    
    # Pagination with parameters
    query3 = (
        match(node("p", "Person"))
        .return_("p.name", "p.age")
        .order_by("p.name")
        .skip("$pageSize * ($pageNumber - 1)")
        .limit("$pageSize")
    )
    print("Pagination with parameters:")
    print(query3.to_cypher())
    print()

def demo_complex_chains():
    """Demonstrate LIMIT and SKIP in complex query chains."""
    print("=== LIMIT and SKIP in Complex Chains ===")
    
    # MATCH → WHERE → WITH → ORDER BY → LIMIT
    query1 = (
        match(node("p", "Person"))
        .where(prop("p", "age") > literal(18))
        .with_(("p.name", "name"), ("p.age", "age"))
        .order_by(desc("age"))
        .limit(10)
        .return_("name", "age")
    )
    print("MATCH → WHERE → WITH → ORDER BY → LIMIT → RETURN:")
    print(query1.to_cypher())
    print()
    
    # MATCH → WHERE → WITH → ORDER BY → SKIP → LIMIT
    query2 = (
        match(node("p", "Person"))
        .where(prop("p", "age") > literal(18))
        .with_(("p.name", "name"), ("p.age", "age"))
        .order_by(desc("age"))
        .skip(5)
        .limit(10)
        .return_("name", "age")
    )
    print("MATCH → WHERE → WITH → ORDER BY → SKIP → LIMIT → RETURN:")
    print(query2.to_cypher())
    print()
    
    # Complex chain with relationships
    query3 = (
        match(node("p", "Person").relates_to(">", "WORKS_FOR", node("c", "Company")))
        .where(prop("c", "industry") == literal("Technology"))
        .with_(("p.name", "employeeName"), ("c.name", "companyName"), ("p.salary", "salary"))
        .order_by(desc("salary"))
        .skip(10)
        .limit(5)
        .return_("employeeName", "companyName", "salary")
    )
    print("Complex chain with relationships:")
    print(query3.to_cypher())
    print()

def demo_from_different_clauses():
    """Demonstrate LIMIT and SKIP starting from different clause types."""
    print("=== LIMIT and SKIP from Different Clause Types ===")
    
    # From MATCH clause
    query1 = (
        match(node("p", "Person"))
        .limit(10)
    )
    print("LIMIT from MATCH clause:")
    print(query1.to_cypher())
    print()
    
    # From ORDER BY clause
    query2 = (
        match(node("p", "Person"))
        .return_("p.name", "p.age")
        .order_by("p.age")
        .skip(5)
        .limit(10)
    )
    print("SKIP and LIMIT from ORDER BY clause:")
    print(query2.to_cypher())
    print()
    
    # Chaining SKIP after LIMIT
    query3 = (
        match(node("p", "Person"))
        .return_("p.name", "p.age")
        .limit(20)
        .skip(5)
    )
    print("SKIP after LIMIT:")
    print(query3.to_cypher())
    print()
    
    # Chaining LIMIT after SKIP
    query4 = (
        match(node("p", "Person"))
        .return_("p.name", "p.age")
        .skip(5)
        .limit(10)
    )
    print("LIMIT after SKIP:")
    print(query4.to_cypher())
    print()

def demo_real_world_examples():
    """Demonstrate real-world usage examples."""
    print("=== Real-world Examples ===")
    
    # Find top 5 most connected people
    query1 = (
        match(node("p", "Person").relates_to("-", "KNOWS", node("friend", "Person")))
        .with_(("p.name", "personName"), ("count(friend)", "friendCount"))
        .order_by(desc("friendCount"), "personName")
        .limit(5)
        .return_("personName", "friendCount")
    )
    print("Top 5 most connected people:")
    print(query1.to_cypher())
    print()
    
    # Paginated results for a dashboard (page 3, 10 per page)
    query2 = (
        match(node("e", "Employee").relates_to(">", "WORKS_IN", node("d", "Department")))
        .with_(("e.name", "employeeName"), ("d.name", "deptName"), ("e.salary", "salary"))
        .order_by("deptName", desc("salary"))
        .skip(20)  # Skip first 20 results (pages 1 and 2)
        .limit(10)  # Show 10 results per page
        .return_("deptName", "employeeName", "salary")
    )
    print("Paginated results for a dashboard (page 3, 10 per page):")
    print(query2.to_cypher())
    print()
    
    # Recent activity feed (last 15 items, skip the first 5)
    query3 = (
        match(node("u", "User").relates_to(">", "PERFORMED", node("a", "Activity")))
        .where(prop("a", "timestamp") > literal("2023-01-01"))
        .with_(("u.name", "userName"), ("a.type", "activityType"), ("a.timestamp", "when"))
        .order_by(desc("when"))
        .skip(5)
        .limit(15)
        .return_("userName", "activityType", "when")
    )
    print("Recent activity feed (skip first 5, show next 15):")
    print(query3.to_cypher())
    print()
    
    # Sample data for testing (first 100 records)
    query4 = (
        match(node("n"))
        .return_("n")
        .limit(100)
    )
    print("Sample data for testing (first 100 records):")
    print(query4.to_cypher())
    print()
    
    # Batch processing with offset
    query5 = (
        match(node("p", "Product"))
        .where(prop("p", "needsUpdate") == literal(True))
        .with_("p")
        .order_by("p.id")
        .skip("$batchOffset")
        .limit("$batchSize")
        .return_("p.id", "p.name")
    )
    print("Batch processing with offset:")
    print(query5.to_cypher())
    print()

if __name__ == "__main__":
    print("Testing LIMIT and SKIP clause functionality\n")
    
    demo_limit_basic()
    demo_skip_basic()
    demo_pagination()
    demo_complex_chains()
    demo_from_different_clauses()
    demo_real_world_examples()
    
    print("All demos completed successfully! 🎉")
