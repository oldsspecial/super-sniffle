"""
Basic usage examples for super-sniffle.

This file demonstrates how to use super-sniffle to build Cypher queries
in a functional and composable way.

Note: These examples represent the planned API and are not yet functional.
The actual implementation is still in development.
"""

from super_sniffle import match, node, relationship, prop, param


def simple_person_query():
    """
    Build a simple query to find people older than a certain age.
    
    Returns:
        A query object that would generate:
        MATCH (p:Person)
        WHERE p.age > $min_age
        RETURN p.name, p.age
        ORDER BY p.age
        LIMIT 10
    """
    return (
        match(node("p", "Person"))
        .where(prop("p", "age").gt(param("min_age")))
        .return_("p.name", "p.age")
        .order_by("p.age")
        .limit(10)
    )


def relationship_query():
    """
    Build a query with relationships to find friends living in a specific city.
    
    Returns:
        A query object that would generate:
        MATCH (p:Person)-[:KNOWS]->(f:Person)-[:LIVES_IN]->(c:City)
        WHERE p.age > $min_age AND c.name = $city_name
        RETURN p.name, f.name, c.name
    """
    return (
        match(
            node("p", "Person")
            .relates_to(">", "KNOWS", node("f", "Person"))
            .relates_to(">", "LIVES_IN", node("c", "City"))
        )
        .where(
            prop("p", "age").gt(param("min_age"))
            .and_(prop("c", "name").equals(param("city_name")))
        )
        .return_("p.name", "f.name", "c.name")
    )


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
    return (
        match(
            node("p", "Person")
            .relates_to(">", "WORKS_FOR", node("company", "Company"))
        )
        .match(
            node("p")
            .relates_to(">", "LIVES_IN", node("city", "City"))
        )
        .where(
            prop("p", "age").between(param("min_age"), param("max_age"))
            .and_(prop("company", "industry").equals(param("industry")))
            .and_(prop("city", "population").gt(param("min_population")))
        )
        .return_("p.name", "company.name", "city.name")
        .order_by("p.age DESC", "company.name ASC")
        .limit(param("limit"))
    )


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
    return (
        match(
            node("p", "Person")
            .relates_to(">", "WORKS_FOR", node("c", "Company"))
        )
        .where(prop("c", "industry").equals(param("industry")))
        .return_(
            "c.name",
            "COUNT(p) as employee_count",
            "AVG(p.age) as avg_age"
        )
        .order_by("employee_count DESC")
        .limit(5)
    )


if __name__ == "__main__":
    # When the library is implemented, these would work:
    
    print("Simple person query:")
    try:
        query = simple_person_query()
        print(query.to_cypher())
    except NotImplementedError:
        print("Not yet implemented - showing planned API")
    
    print("\nRelationship query:")
    try:
        query = relationship_query()
        print(query.to_cypher())
    except NotImplementedError:
        print("Not yet implemented - showing planned API")
    
    print("\nComplex pattern query:")
    try:
        query = complex_pattern_query()
        print(query.to_cypher())
    except NotImplementedError:
        print("Not yet implemented - showing planned API")
    
    print("\nAggregation query:")
    try:
        query = with_aggregation_query()
        print(query.to_cypher())
    except NotImplementedError:
        print("Not yet implemented - showing planned API")
