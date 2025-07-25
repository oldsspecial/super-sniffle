"""
Unit tests for CALL subquery clause functionality.

Tests the implementation of CALL subquery with variable scoping
following the modern Neo4j Cypher syntax.
"""

import pytest
from super_sniffle import (
    match, node, prop, literal, var, call_subquery, path, relationship
)
from super_sniffle.api import optional_call_subquery


class TestCallSubqueryClause:
    """Test the CallSubqueryClause implementation."""
    
    def test_basic_subquery_no_variables(self):
        """Test basic subquery without variable scoping."""
        subquery = match(node("p", "Person")).return_("p.name")
        query = call_subquery(subquery)
        cypher = query.to_cypher()
        expected = "CALL() {\n  MATCH (p:Person)\n  RETURN p.name\n}"
        assert cypher == expected
    
    def test_subquery_with_single_variable(self):
        """Test subquery with single variable scoping."""
        subquery = match(node("p", "Person")).where(prop("p", "team") == var("t")).return_("p")
        query = call_subquery(subquery, variables="t")
        cypher = query.to_cypher()
        expected = "CALL(t) {\n  MATCH (p:Person)\n  WHERE p.team = t\n  RETURN p\n}"
        assert cypher == expected
    
    def test_subquery_with_multiple_variables(self):
        """Test subquery with multiple variable scoping."""
        subquery = match(node("p", "Person")).return_("p")
        query = call_subquery(subquery, variables=["t", "u"])
        cypher = query.to_cypher()
        expected = "CALL(t, u) {\n  MATCH (p:Person)\n  RETURN p\n}"
        assert cypher == expected
    
    def test_subquery_with_all_variables(self):
        """Test subquery with all variables scoping (*)."""
        subquery = match(node("p", "Person")).return_("p")
        query = call_subquery(subquery, variables="*")
        cypher = query.to_cypher()
        expected = "CALL(*) {\n  MATCH (p:Person)\n  RETURN p\n}"
        assert cypher == expected
    
    def test_subquery_chained_with_match(self):
        """Test subquery chained with MATCH clause."""
        subquery = match(node("p", "Player")).where(prop("p", "team") == var("t")).return_("collect(p) as players")
        query = (
            match(node("t", "Team"))
            .call_subquery(subquery, variables="t")
            .return_("t", "players")
        )
        cypher = query.to_cypher()
        expected = (
            "MATCH (t:Team)\n"
            "CALL(t) {\n"
            "  MATCH (p:Player)\n"
            "  WHERE p.team = t\n"
            "  RETURN collect(p) as players\n"
            "}\n"
            "RETURN t, players"
        )
        assert cypher == expected
    
    def test_complex_subquery_with_where_and_order(self):
        """Test complex subquery with WHERE and ORDER BY."""
        subquery = (
            match(node("p", "Person"))
            .where(prop("p", "age") > literal(18))
            .return_("p.name", "p.age")
            .order_by("p.age")
            .limit(5)
        )
        query = call_subquery(subquery, variables=["t", "u"])
        cypher = query.to_cypher()
        expected = (
            "CALL(t, u) {\n"
            "  MATCH (p:Person)\n"
            "  WHERE p.age > 18\n"
            "  RETURN p.name, p.age\n"
            "  ORDER BY p.age\n"
            "  LIMIT 5\n"
            "}"
        )
        assert cypher == expected
    
    def test_nested_subqueries(self):
        """Test nested subqueries."""
        inner_subquery = match(node("c", "Company")).return_("c.name")
        outer_subquery = call_subquery(inner_subquery)
        query = call_subquery(outer_subquery)
        cypher = query.to_cypher()
        expected = (
            "CALL() {\n"
            "  CALL() {\n"
            "    MATCH (c:Company)\n"
            "    RETURN c.name\n"
            "  }\n"
            "}"
        )
        assert cypher == expected
    
    def test_subquery_with_optional_match(self):
        """Test subquery with OPTIONAL MATCH."""
        subquery = (
            match(node("Team", variable="t"))
            .optional_match(path(node("Player", variable="p"), relationship("PLAYS_FOR", direction=">"), node("t")))
            .return_("t.name", "count(p) as player_count")
        )
        query = call_subquery(subquery)
        cypher = query.to_cypher()
        expected = (
            "CALL() {\n"
            "  MATCH (t:Team)\n"
            "  OPTIONAL MATCH (p:Player)-[:PLAYS_FOR]->(t)\n"
            "  RETURN t.name, count(p) as player_count\n"
            "}"
        )
        assert cypher == expected
        
    def test_subquery_with_with_clause(self):
        """Test subquery with WITH clause."""
        subquery = (
            match(node("p", "Person"))
            .with_(("p.name", "name"), ("p.age", "age"))
            .return_("name", "age")
        )
        query = call_subquery(subquery, variables="*")
        cypher = query.to_cypher()
        expected = (
            "CALL(*) {\n"
            "  MATCH (p:Person)\n"
            "  WITH p.name AS name, p.age AS age\n"
            "  RETURN name, age\n"
            "}"
        )
        assert cypher == expected
    
    def test_real_world_team_players_example(self):
        """Test a real-world team players example."""
        subquery = (
            match(path(node("p", "Player"), relationship(">", "PLAYS_FOR"), node("t")))
            .return_("collect(p.name) as players")
        )
        query = (
            match(node("t", "Team"))
            .call_subquery(subquery, variables="t")
            .return_("t.name", "players")
        )
        cypher = query.to_cypher()
        expected = (
            "MATCH (t:Team)\n"
            "CALL(t) {\n"
            "  MATCH (p:Player)-[:>|PLAYS_FOR]-(t)\n"
            "  RETURN collect(p.name) as players\n"
            "}\n"
            "RETURN t.name, players"
        )
        assert cypher == expected
    
    def test_subquery_with_aggregation(self):
        """Test subquery with aggregation functions."""
        subquery = (
            match(path(node("Order", variable="o"), relationship("CONTAINS", direction=">"), node("i", "Item")))
            .return_("sum(i.price) as total_value")
        )
        query = call_subquery(subquery, variables="c")
        cypher = query.to_cypher()
        expected = (
            "CALL(c) {\n"
            "  MATCH (o:Order)-[:CONTAINS]->(i:Item)\n"
            "  RETURN sum(i.price) as total_value\n"
            "}"
        )
        assert cypher == expected
    
    def test_empty_variable_list(self):
        """Test subquery with empty variable list (should behave like None)."""
        subquery = match(node("p", "Person")).return_("p")
        query = call_subquery(subquery, variables=[])
        cypher = query.to_cypher()
        expected = "CALL() {\n  MATCH (p:Person)\n  RETURN p\n}"
        assert cypher == expected


class TestCallSubqueryStandaloneFunction:
    """Test the standalone call_subquery function."""
    
    def test_standalone_function_no_variables(self):
        """Test standalone call_subquery function without variables."""
        subquery = match(node("p", "Person")).return_("p.name")
        query = call_subquery(subquery)
        assert isinstance(query.to_cypher(), str)
    
    def test_standalone_function_with_variables(self):
        """Test standalone call_subquery function with variables."""
        subquery = match(node("p", "Person")).return_("p")
        query = call_subquery(subquery, variables=["a", "b"])
        assert "CALL(a, b)" in query.to_cypher()
    
    def test_standalone_function_with_star(self):
        """Test standalone call_subquery function with star."""
        subquery = match(node("p", "Person")).return_("p")
        query = call_subquery(subquery, variables="*")
        assert "CALL(*)" in query.to_cypher()


class TestCallSubqueryIntegration:
    """Test integration with other query components."""
    
    def test_subquery_with_limit_and_skip(self):
        """Test subquery integrated with LIMIT and SKIP."""
        subquery = match(node("p", "Person")).return_("p.name")
        query = (
            call_subquery(subquery)
            .skip(10)
            .limit(5)
        )
        cypher = query.to_cypher()
        expected = (
            "CALL() {\n"
            "  MATCH (p:Person)\n"
            "  RETURN p.name\n"
            "}\n"
            "SKIP 10\n"
            "LIMIT 5"
        )
        assert cypher == expected
    
    def test_subquery_with_order_by(self):
        """Test subquery with ORDER BY."""
        subquery = match(node("p", "Person")).return_("p.name")
        query = (
            call_subquery(subquery)
            .order_by("p.name")
        )
        cypher = query.to_cypher()
        expected = (
            "CALL() {\n"
            "  MATCH (p:Person)\n"
            "  RETURN p.name\n"
            "}\n"
            "ORDER BY p.name"
        )
        assert cypher == expected
    
    def test_subquery_with_where_clause(self):
        """Test subquery followed by WHERE clause."""
        subquery = match(node("p", "Person")).return_("p.name as name")
        query = (
            call_subquery(subquery)
            .where(var("name") == literal("Alice"))
            .return_("name")
        )
        cypher = query.to_cypher()
        expected = (
            "CALL() {\n"
            "  MATCH (p:Person)\n"
            "  RETURN p.name as name\n"
            "}\n"
            "WHERE name = 'Alice'\n"
            "RETURN name"
        )
        assert cypher == expected


class TestOptionalCallSubquery:
    """Test the OPTIONAL CALL subquery functionality."""
    
    def test_basic_optional_call_no_variables(self):
        """Test basic OPTIONAL CALL without variable scoping."""
        subquery = match(node("p", "Person")).return_("p.name")
        query = optional_call_subquery(subquery)
        cypher = query.to_cypher()
        expected = "OPTIONAL CALL() {\n  MATCH (p:Person)\n  RETURN p.name\n}"
        assert cypher == expected
    
    def test_optional_call_with_variables(self):
        """Test OPTIONAL CALL with variable scoping."""
        subquery = match(node("p", "Person")).return_("p")
        query = optional_call_subquery(subquery, variables=["t", "u"])
        cypher = query.to_cypher()
        expected = "OPTIONAL CALL(t, u) {\n  MATCH (p:Person)\n  RETURN p\n}"
        assert cypher == expected
    
    def test_optional_call_with_star(self):
        """Test OPTIONAL CALL with all variables scoping."""
        subquery = match(node("p", "Person")).return_("p")
        query = optional_call_subquery(subquery, variables="*")
        cypher = query.to_cypher()
        expected = "OPTIONAL CALL(*) {\n  MATCH (p:Person)\n  RETURN p\n}"
        assert cypher == expected
    
    def test_optional_call_chained_with_match(self):
        """Test OPTIONAL CALL chained with MATCH clause."""
        subquery = match(node("p", "Player")).where(prop("p", "team") == var("t")).return_("collect(p) as players")
        query = (
            match(node("t", "Team"))
            .optional_call_subquery(subquery, variables="t")
            .return_("t", "players")
        )
        cypher = query.to_cypher()
        expected = (
            "MATCH (t:Team)\n"
            "OPTIONAL CALL(t) {\n"
            "  MATCH (p:Player)\n"
            "  WHERE p.team = t\n"
            "  RETURN collect(p) as players\n"
            "}\n"
            "RETURN t, players"
        )
        assert cypher == expected
