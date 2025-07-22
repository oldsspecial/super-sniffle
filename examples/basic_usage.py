"""
Basic usage examples for super-sniffle.

This file demonstrates how to use super-sniffle to build Cypher queries
in a functional and composable way.

Note: Some of these examples represent the planned API and are not yet functional.
The MATCH clause and pattern system are now working!
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from super_sniffle import prop, param, literal, node, relationship, path, match


def demonstrate_operator_syntax():
    """
    Demonstrate the new operator-based syntax for WHERE clauses.
    
    This shows how the new syntax makes conditions more readable and intuitive.
    """
    print("🚀 New Operator-Based Syntax Examples")
    print("=" * 50)
    
    # Basic comparisons
    print("\n1. Basic Comparisons:")
    age_filter = prop("p", "age") > param("min_age")
    print(f"prop('p', 'age') > param('min_age')")
    print(f"Cypher: {age_filter.to_cypher()}")
    
    name_filter = prop("p", "name") == literal("Alice")
    print(f"\nprop('p', 'name') == literal('Alice')")
    print(f"Cypher: {name_filter.to_cypher()}")
    
    # Logical combinations
    print("\n2. Logical Combinations:")
    complex_filter = (prop("p", "age") >= literal(18)) & (prop("p", "active") == literal(True))
    print("(prop('p', 'age') >= 18) & (prop('p', 'active') == True)")
    print(f"Cypher: {complex_filter.to_cypher()}")
    
    # String operations
    print("\n3. String Operations:")
    contains_filter = prop("p", "name").contains(param("search_term"))
    print("prop('p', 'name').contains(param('search_term'))")
    print(f"Cypher: {contains_filter.to_cypher()}")
    
    return {
        "age_filter": age_filter,
        "name_filter": name_filter, 
        "complex_filter": complex_filter,
        "contains_filter": contains_filter
    }


def simple_person_query():
    """
    Build a simple query to find people older than a certain age.
    
    Using the new operator syntax for WHERE clauses and MATCH clause.
    
    Currently generates:
        MATCH (p:Person WHERE p.age > $min_age)
    
    Future implementation will add WHERE, RETURN, ORDER BY, LIMIT clauses.
    """
    # Using inline WHERE condition - this is working now!
    query = match(node("p", "Person").where(prop("p", "age") > param("min_age")))
    
    print(f"MATCH query: {query.to_cypher()}")
    
    # TODO: Complete query when WHERE/RETURN clauses are implemented
    # return (
    #     match(node("p", "Person"))
    #     .where(prop("p", "age") > param("min_age"))
    #     .return_("p.name", "p.age")
    #     .order_by("p.age")
    #     .limit(10)
    # )
    
    return query


def relationship_query():
    """
    Build a query with relationships to find friends living in a specific city.
    
    Using the new operator syntax for complex WHERE conditions.
    
    Now generates:
        MATCH (p:Person)-[:KNOWS]->(f:Person)-[:LIVES_IN]->(c:City)
        WHERE (p.age > $min_age) AND (c.name = $city_name)
    """
    # Create the query with MATCH and WHERE clauses
    person = node("p", "Person")
    friend = node("f", "Person")
    city = node("c", "City")
    
    # Build the complete path pattern using the path() constructor
    complex_path = path(
        person,
        relationship("KNOWS", direction=">", variable="r1"),
        friend,
        relationship("LIVES_IN", direction=">", variable="r2"),
        city
    )
    
    # Create the WHERE condition
    where_condition = (
        (prop("p", "age") > param("min_age")) & 
        (prop("c", "name") == param("city_name"))
    )
    
    # Build the complete query
    query = match(complex_path).where(where_condition)
    
    print(f"Complete query: {query.to_cypher()}")
    
    # TODO: Add RETURN clause when implemented
    # return query.return_("p.name", "f.name", "c.name")
    
    return query


def complex_pattern_query():
    """
    Build a more complex query with multiple patterns and conditions.
    
    Returns:
        A query object that would generate:
        MATCH (p:Person)-[:WORKS_FOR]->(company:Company)
        MATCH (p)-[:LIVES_IN]->(city:City)
        WHERE p.age BETWEEN $min_age AND $max_age
          AND company.industry = $industry
          AND city.population > $min_population
        RETURN p.name, company.name, city.name
        ORDER BY p.age DESC, company.name ASC
        LIMIT $limit
    """
    # TODO: Uncomment when match() is implemented
    # return (
    #     match(
    #         node("p", "Person")
    #         .relates_to(">", "WORKS_FOR", node("company", "Company"))
    #     )
    #     .match(
    #         node("p")
    #         .relates_to(">", "LIVES_IN", node("city", "City"))
    #     )
    #     .where(
    #         prop("p", "age").between(param("min_age"), param("max_age"))
    #         .and_(prop("company", "industry").equals(param("industry")))
    #         .and_(prop("city", "population").gt(param("min_population")))
    #     )
    #     .return_("p.name", "company.name", "city.name")
    #     .order_by("p.age DESC", "company.name ASC")
    #     .limit(param("limit"))
    # )
    pass


def with_aggregation_query():
    """
    Build a query with aggregation functions.
    
    Returns:
        A query object that would generate:
        MATCH (p:Person)-[:WORKS_FOR]->(c:Company)
        WHERE c.industry = $industry
        RETURN c.name, COUNT(p) as employee_count, AVG(p.age) as avg_age
        ORDER BY employee_count DESC
        LIMIT 5
    """
    # TODO: Uncomment when match() is implemented
    # return (
    #     match(
    #         node("p", "Person")
    #         .relates_to(">", "WORKS_FOR", node("c", "Company"))
    #     )
    #     .where(prop("c", "industry").equals(param("industry")))
    #     .return_(
    #         "c.name",
    #         "COUNT(p) as employee_count",
    #         "AVG(p.age) as avg_age"
    #     )
    #     .order_by("employee_count DESC")
    #     .limit(5)
    # )
    pass


def demonstrate_patterns():
    """
    Demonstrate the new pattern system with inline conditions.
    """
    print("\n🚀 Pattern System with Inline Conditions")
    print("=" * 50)
    
    # Basic node patterns
    print("\n1. Basic Node Patterns:")
    person_node = node("p", "Person")
    print(f"node('p', 'Person')")
    print(f"Cypher: {person_node.to_cypher()}")
    
    # Node with inline condition
    print("\n2. Node with Inline Condition:")
    adult_person = node("p", "Person").where(prop("p", "age") > literal(18))
    print("node('p', 'Person').where(prop('p', 'age') > 18)")
    print(f"Cypher: {adult_person.to_cypher()}")
    
    # Basic relationship patterns
    print("\n3. Basic Relationship Patterns:")
    knows_rel = relationship("KNOWS", direction=">", variable="r")
    print("relationship('KNOWS', direction='>', variable='r')")
    print(f"Cypher: {knows_rel.to_cypher()}")
    
    # Relationship with inline condition
    print("\n4. Relationship with Inline Condition:")
    recent_knows = relationship("KNOWS", direction=">", variable="r").where(prop("r", "since") > literal(2020))
    print("relationship('KNOWS', direction='>', variable='r').where(prop('r', 'since') > 2020)")
    print(f"Cypher: {recent_knows.to_cypher()}")
    
    # Path patterns
    print("\n5. Path Patterns:")
    friend_path = path(
        node("p1", "Person"),
        relationship("KNOWS", direction=">", variable="r"),
        node("p2", "Person")
    )
    print("path(node('p1', 'Person'), relationship('>', 'r', 'KNOWS'), node('p2', 'Person'))")
    print(f"Cypher: {friend_path.to_cypher()}")
    
    # Complex path with multiple inline conditions
    print("\n6. Complex Path with Multiple Inline Conditions:")
    complex_path = path(
        node("p1", "Person").where(prop("p1", "active") == literal(True)),
        relationship("KNOWS", direction=">", variable="r").where(prop("r", "since") > literal(2020)),
        node("p2", "Person").where(prop("p2", "age") > literal(18))
    )
    print("Complex path with inline conditions:")
    print(f"Cypher: {complex_path.to_cypher()}")


def demonstrate_where_clause():
    """
    Demonstrate the new WHERE clause functionality.
    """
    print("\n🚀 WHERE Clause Examples (NEW!)")
    print("=" * 50)
    
    # Basic WHERE
    print("\n1. Basic WHERE:")
    query1 = match(node("p", "Person")).where(prop("p", "age") > literal(30))
    print("match(node('p', 'Person')).where(prop('p', 'age') > literal(30))")
    print(f"Cypher: {query1.to_cypher()}")
    
    # WHERE with complex conditions
    print("\n2. WHERE with Complex Conditions:")
    condition = (prop("p", "age") > literal(25)) & (prop("p", "active") == literal(True))
    query2 = match(node("p", "Person")).where(condition)
    print("Complex condition with logical operators:")
    print(f"Cypher: {query2.to_cypher()}")
    
    # WHERE with parameters
    print("\n3. WHERE with Parameters:")
    query3 = match(node("p", "Person")).where(prop("p", "name").contains(param("search_term")))
    print("match(node('p', 'Person')).where(prop('p', 'name').contains(param('search_term')))")
    print(f"Cypher: {query3.to_cypher()}")
    
    # WHERE with multiple MATCH clauses
    print("\n4. WHERE with Multiple MATCH:")
    query4 = (
        match(node("p", "Person"))
        .match(node("c", "Company"))
        .where(prop("p", "works_at") == prop("c", "id"))
    )
    print("WHERE applied to multiple MATCH clauses:")
    print(f"Cypher: {query4.to_cypher()}")
    
    # WHERE with relationship patterns
    print("\n5. WHERE with Relationship Patterns:")
    person = node("p", "Person")
    friend = node("f", "Person")
    query5 = (
        match(person.relates_to("r", "KNOWS", ">", friend))
        .where((prop("p", "age") > literal(25)) & (prop("f", "age") < literal(35)))
    )
    print("WHERE with relationship patterns:")
    print(f"Cypher: {query5.to_cypher()}")


def demonstrate_match_clause():
    """
    Demonstrate the new MATCH clause functionality.
    """
    print("\n🚀 MATCH Clause Examples")
    print("=" * 50)
    
    # Basic MATCH
    print("\n1. Basic MATCH:")
    query1 = match(node("p", "Person"))
    print("match(node('p', 'Person'))")
    print(f"Cypher: {query1.to_cypher()}")
    
    # MATCH with inline condition
    print("\n2. MATCH with Inline Condition:")
    query2 = match(node("p", "Person").where(prop("p", "age") > literal(25)))
    print("match(node('p', 'Person').where(prop('p', 'age') > 25))")
    print(f"Cypher: {query2.to_cypher()}")
    
    # MATCH with relationships using path() and relationship()
    print("\n3. MATCH with path() and relationship():")
    person = node("p", "Person")
    friend = node("f", "Person")
    query3 = match(path(person, relationship("KNOWS", direction=">", variable="r"), friend))
    print("match(path(person, relationship('KNOWS', direction='>', variable='r'), friend))")
    print(f"Cypher: {query3.to_cypher()}")
    
    # Multiple MATCH clauses
    print("\n4. Multiple MATCH Clauses:")
    query4 = (
        match(node("p", "Person"))
        .match(node("c", "Company"))
    )
    print("match(node('p', 'Person')).match(node('c', 'Company'))")
    print(f"Cypher: {query4.to_cypher()}")
    
    # Complex path with path() and relationship()
    print("\n5. Complex Path with path() and relationship():")
    query5 = match(
        path(
            node("p", "Person").where(prop("p", "active") == literal(True)),
            relationship("KNOWS", direction=">", variable="r"),
            node("f", "Person"),
            relationship("LIVES_IN", direction=">", variable="lives"),
            node("c", "City").where(prop("c", "name") == param("city_name"))
        )
    )
    print("Complex chained relates_to:")
    print(f"Cypher: {query5.to_cypher()}")


if __name__ == "__main__":
    # Demonstrate the working parts of the library
    
    print("🎯 Working Features - Operator Syntax:")
    demonstrate_operator_syntax()
    
    print("\n🎯 Working Features - Pattern System:")
    demonstrate_patterns()
    
    print("\n🎯 Working Features - MATCH Clause:")
    demonstrate_match_clause()
    
    print("\n🎯 Working Features - WHERE Clause:")
    demonstrate_where_clause()
    
    print("\n📋 Current Features in Action:")
    print("Simple person query:")
    try:
        query = simple_person_query()
        print(f"Generated: {query.to_cypher()}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\nRelationship query (WHERE condition only):")
    try:
        condition = relationship_query()
        print(f"WHERE condition: {condition.to_cypher()}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n📋 Future Features (WHERE, RETURN, ORDER BY, LIMIT clauses):")
    print("- WHERE clause for filtering after MATCH")
    print("- RETURN clause for selecting output")
    print("- ORDER BY clause for sorting")
    print("- LIMIT clause for pagination")
    print("- WITH clause for chaining queries")
    print("- CREATE/UPDATE/DELETE operations")
