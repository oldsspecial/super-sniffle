"""
Unit tests for UNION and UNION ALL compound queries.
"""

import pytest
from super_sniffle import match, node, prop, literal

class TestUnion:
    """Test UNION functionality."""

    def test_simple_union(self):
        """Test a simple UNION of two queries."""
        query1 = match(node("p", "Person")).return_("p.name")
        query2 = match(node("m", "Movie")).return_("m.title")
        
        union_query = query1.union(query2)
        
        result = union_query.to_cypher()
        expected = "MATCH (p:Person)\nRETURN p.name\nUNION\nMATCH (m:Movie)\nRETURN m.title"
        assert result == expected

    def test_simple_union_all(self):
        """Test a simple UNION ALL of two queries."""
        query1 = match(node("p", "Person")).return_("p.name")
        query2 = match(node("m", "Movie")).return_("m.title")
        
        union_query = query1.union_all(query2)
        
        result = union_query.to_cypher()
        expected = "MATCH (p:Person)\nRETURN p.name\nUNION ALL\nMATCH (m:Movie)\nRETURN m.title"
        assert result == expected

    def test_multiple_unions(self):
        """Test chaining multiple UNION clauses."""
        query1 = match(node("p", "Person")).return_("p.name AS name")
        query2 = match(node("m", "Movie")).return_("m.title AS name")
        query3 = match(node("c", "Company")).return_("c.name AS name")

        union_query = query1.union(query2).union_all(query3)

        result = union_query.to_cypher()
        expected = (
            "MATCH (p:Person)\nRETURN p.name AS name\n"
            "UNION\n"
            "MATCH (m:Movie)\nRETURN m.title AS name\n"
            "UNION ALL\n"
            "MATCH (c:Company)\nRETURN c.name AS name"
        )
        assert result == expected

    def test_union_with_where_clauses(self):
        """Test UNION with WHERE clauses in subqueries."""
        query1 = (
            match(node("p", "Person"))
            .where(prop("p", "age") > literal(30))
            .return_("p.name")
        )
        query2 = (
            match(node("p", "Person"))
            .where(prop("p", "age") < literal(20))
            .return_("p.name")
        )

        union_query = query1.union(query2)

        result = union_query.to_cypher()
        expected = (
            "MATCH (p:Person)\nWHERE p.age > 30\nRETURN p.name\n"
            "UNION\n"
            "MATCH (p:Person)\nWHERE p.age < 20\nRETURN p.name"
        )
        assert result == expected
