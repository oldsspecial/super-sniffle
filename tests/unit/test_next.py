import pytest
from super_sniffle.clauses.next_ import NextClause
from super_sniffle.api import match, node, relationship

def test_next_clause_to_cypher():
    next_clause = NextClause()
    assert next_clause.to_cypher() == "NEXT"
    assert next_clause.to_cypher(indent="  ") == "  NEXT"

def test_next_clause_in_query_builder():
    from super_sniffle.api import path
    
    query = (
        match(node("c", "Customer"))
        .return_("c AS customer")
        .next()
        .match(path(
            node("customer"),
            relationship("BUYS", direction=">"),
            node("Product", name="Chocolate")
        ))
        .return_("customer.firstName AS chocolateCustomer")
    )
    
    cypher = query.to_cypher()
    expected = (
        "MATCH (c:Customer)\n"
        "RETURN c AS customer\n"
        "NEXT\n"
        "MATCH (customer)-[:BUYS]->(Product {name: 'Chocolate'})\n"
        "RETURN customer.firstName AS chocolateCustomer"
    )
    assert cypher == expected

def test_next_clause_with_multiple_segments():
    query = (
        match(node("a", "A"))
        .return_("a")
        .next()
        .match(node("b", "B"))
        .return_("b")
        .next()
        .match(node("c", "C"))
        .return_("c")
    )
    
    cypher = query.to_cypher()
    expected = (
        "MATCH (a:A)\n"
        "RETURN a\n"
        "NEXT\n"
        "MATCH (b:B)\n"
        "RETURN b\n"
        "NEXT\n"
        "MATCH (c:C)\n"
        "RETURN c"
    )
    assert cypher == expected
