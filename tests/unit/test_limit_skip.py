"""
Unit tests for LIMIT and SKIP clause implementations.

Tests the working LIMIT and SKIP clause functionality including basic usage,
pagination patterns, and integration with other query clauses.
"""

import pytest
from super_sniffle import match, node, prop, var, literal, asc, desc


class TestBasicLimit:
    """Test basic LIMIT clause functionality."""
    
    def test_basic_limit_with_integer(self):
        """Test basic LIMIT clause with integer value."""
        query = (
            match(node("p", "Person"))
            .return_("p.name", "p.age")
            .limit(5)
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nRETURN p.name, p.age\nLIMIT 5"
        assert result == expected

    def test_basic_limit_with_string(self):
        """Test basic LIMIT clause with string parameter."""
        query = (
            match(node("p", "Person"))
            .return_("p.name", "p.age")
            .limit("$maxResults")
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nRETURN p.name, p.age\nLIMIT $maxResults"
        assert result == expected

    def test_limit_from_match_clause(self):
        """Test LIMIT called directly from MATCH clause."""
        query = (
            match(node("p", "Person"))
            .limit(10)
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nLIMIT 10\nRETURN *"
        assert result == expected

    def test_limit_with_return_after(self):
        """Test LIMIT with RETURN called after."""
        query = (
            match(node("p", "Person"))
            .limit(3)
            .return_("p.name")
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nLIMIT 3\nRETURN p.name"
        assert result == expected


class TestBasicSkip:
    """Test basic SKIP clause functionality."""
    
    def test_basic_skip_with_integer(self):
        """Test basic SKIP clause with integer value."""
        query = (
            match(node("p", "Person"))
            .return_("p.name", "p.age")
            .skip(10)
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nRETURN p.name, p.age\nSKIP 10"
        assert result == expected

    def test_basic_skip_with_string(self):
        """Test basic SKIP clause with string parameter."""
        query = (
            match(node("p", "Person"))
            .return_("p.name", "p.age")
            .skip("$offset")
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nRETURN p.name, p.age\nSKIP $offset"
        assert result == expected

    def test_skip_from_match_clause(self):
        """Test SKIP called directly from MATCH clause."""
        query = (
            match(node("p", "Person"))
            .skip(5)
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nSKIP 5\nRETURN *"
        assert result == expected

    def test_skip_with_return_after(self):
        """Test SKIP with RETURN called after."""
        query = (
            match(node("p", "Person"))
            .skip(20)
            .return_("p.name")
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nSKIP 20\nRETURN p.name"
        assert result == expected


class TestSkipLimitPagination:
    """Test SKIP and LIMIT together for pagination."""
    
    def test_skip_then_limit(self):
        """Test SKIP followed by LIMIT for pagination."""
        query = (
            match(node("p", "Person"))
            .return_("p.name", "p.age")
            .skip(10)
            .limit(5)
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nRETURN p.name, p.age\nSKIP 10\nLIMIT 5"
        assert result == expected

    def test_limit_then_skip(self):
        """Test LIMIT followed by SKIP for pagination."""
        query = (
            match(node("p", "Person"))
            .return_("p.name", "p.age")
            .limit(5)
            .skip(10)
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nRETURN p.name, p.age\nSKIP 10\nLIMIT 5"
        assert result == expected

    def test_pagination_with_parameters(self):
        """Test pagination with parameter values."""
        query = (
            match(node("p", "Person"))
            .return_("p.name", "p.age")
            .skip("$offset")
            .limit("$pageSize")
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nRETURN p.name, p.age\nSKIP $offset\nLIMIT $pageSize"
        assert result == expected

    def test_pagination_from_match(self):
        """Test pagination called directly from MATCH."""
        query = (
            match(node("p", "Person"))
            .skip(20)
            .limit(10)
            .return_("p.name")
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nSKIP 20\nLIMIT 10\nRETURN p.name"
        assert result == expected


class TestLimitSkipWithOtherClauses:
    """Test LIMIT and SKIP integration with other clauses."""
    
    def test_with_where_clause(self):
        """Test LIMIT/SKIP with WHERE clause."""
        query = (
            match(node("p", "Person"))
            .where(prop("p", "age") > literal(25))
            .skip(5)
            .limit(10)
            .return_("p.name", "p.age")
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nWHERE p.age > 25\nSKIP 5\nLIMIT 10\nRETURN p.name, p.age"
        assert result == expected

    def test_with_order_by_clause(self):
        """Test LIMIT/SKIP with ORDER BY clause."""
        query = (
            match(node("p", "Person"))
            .return_("p.name", "p.age")
            .order_by(desc("p.age"))
            .skip(3)
            .limit(7)
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nRETURN p.name, p.age\nORDER BY p.age DESC\nSKIP 3\nLIMIT 7"
        assert result == expected

    def test_with_with_clause(self):
        """Test LIMIT/SKIP with WITH clause."""
        query = (
            match(node("p", "Person"))
            .with_("p.name AS name", "p.age AS age")
            .where(var("age") > literal(30))
            .skip(2)
            .limit(5)
            .return_("name", "age")
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nWITH p.name AS name, p.age AS age\nWHERE age > 30\nSKIP 2\nLIMIT 5\nRETURN name, age"
        assert result == expected


class TestComplexQueryChains:
    """Test LIMIT/SKIP in complex query chains."""
    
    def test_full_query_chain(self):
        """Test MATCH → WHERE → WITH → ORDER BY → SKIP → LIMIT → RETURN chain."""
        query = (
            match(node("p", "Person"))
            .where(prop("p", "active") == literal(True))
            .with_("p.name AS name", "p.age AS age", "p.salary AS salary")
            .order_by(desc("salary"), "name")
            .skip(10)
            .limit(20)
            .return_("name", "age", "salary")
        )
        result = query.to_cypher()
        
        expected_parts = [
            "MATCH (p:Person)",
            "WHERE p.active = true",
            "WITH p.name AS name, p.age AS age, p.salary AS salary",
            "ORDER BY salary DESC, name",
            "SKIP 10",
            "LIMIT 20",
            "RETURN name, age, salary"
        ]
        
        for part in expected_parts:
            assert part in result, f"Expected '{part}' to be in the result"

    def test_relationship_query_with_pagination(self):
        """Test relationship query with pagination."""
        query = (
            match(node("p", "Person").relates_to("r", "KNOWS", ">", node("f", "Person")))
            .where(prop("r", "since") > literal(2020))
            .return_("p.name", "f.name", "r.since")
            .order_by("p.name", desc("r.since"))
            .skip(5)
            .limit(15)
        )
        result = query.to_cypher()
        
        assert "MATCH (p:Person)-[r:KNOWS]->(f:Person)" in result
        assert "WHERE r.since > 2020" in result
        assert "RETURN p.name, f.name, r.since" in result
        assert "ORDER BY p.name, r.since DESC" in result
        assert "SKIP 5" in result
        assert "LIMIT 15" in result


class TestRealWorldExamples:
    """Test real-world usage examples."""
    
    def test_top_n_query(self):
        """Test top N results query pattern."""
        query = (
            match(node("p", "Person").relates_to("r", "KNOWS", ">", node("f", "Person")))
            .with_("p.name AS personName", "count(f) AS friendCount")
            .order_by(desc("friendCount"), "personName")
            .limit(10)
            .return_("personName", "friendCount")
        )
        result = query.to_cypher()
        
        assert "WITH p.name AS personName, count(f) AS friendCount" in result
        assert "ORDER BY friendCount DESC, personName" in result
        assert "LIMIT 10" in result
        assert "RETURN personName, friendCount" in result

    def test_pagination_pattern(self):
        """Test typical pagination pattern."""
        query = (
            match(node("e", "Employee"))
            .where(prop("e", "department") == literal("Engineering"))
            .return_("e.name", "e.salary", "e.startDate")
            .order_by("e.name")
            .skip(50)
            .limit(25)
        )
        result = query.to_cypher()
        
        assert "MATCH (e:Employee)" in result
        assert "WHERE e.department = 'Engineering'" in result
        assert "RETURN e.name, e.salary, e.startDate" in result
        assert "ORDER BY e.name" in result
        assert "SKIP 50" in result
        assert "LIMIT 25" in result

    def test_batch_processing_pattern(self):
        """Test batch processing pattern with LIMIT."""
        query = (
            match(node("n", "Node"))
            .where(prop("n", "processed") == literal(False))
            .return_("n.id", "n.data")
            .order_by("n.createdAt")
            .limit(100)
        )
        result = query.to_cypher()
        
        assert "MATCH (n:Node)" in result
        assert "WHERE n.processed = false" in result
        assert "RETURN n.id, n.data" in result
        assert "ORDER BY n.createdAt" in result
        assert "LIMIT 100" in result


class TestEdgeCases:
    """Test edge cases for LIMIT and SKIP."""
    
    def test_limit_zero(self):
        """Test LIMIT with zero value."""
        query = (
            match(node("p", "Person"))
            .return_("p.name")
            .limit(0)
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nRETURN p.name\nLIMIT 0"
        assert result == expected

    def test_skip_zero(self):
        """Test SKIP with zero value."""
        query = (
            match(node("p", "Person"))
            .return_("p.name")
            .skip(0)
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nRETURN p.name\nSKIP 0"
        assert result == expected

    def test_multiple_limit_calls(self):
        """Test that multiple LIMIT calls override each other."""
        query = (
            match(node("p", "Person"))
            .limit(10)
            .limit(5)
            .return_("p.name")
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nLIMIT 5\nRETURN p.name"
        assert result == expected

    def test_multiple_skip_calls(self):
        """Test that multiple SKIP calls override each other."""
        query = (
            match(node("p", "Person"))
            .skip(10)
            .skip(20)
            .return_("p.name")
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nSKIP 20\nRETURN p.name"
        assert result == expected

    def test_limit_with_large_number(self):
        """Test LIMIT with large number."""
        query = (
            match(node("p", "Person"))
            .return_("p.name")
            .limit(1000000)
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nRETURN p.name\nLIMIT 1000000"
        assert result == expected


class TestMethodChaining:
    """Test method chaining capabilities."""
    
    def test_limit_chaining_methods(self):
        """Test LIMIT clause method chaining."""
        query = (
            match(node("p", "Person"))
            .limit(5)
        )
        
        # Test that we can call other methods after limit
        query_with_return = query.return_("p.name")
        query_with_skip = query.skip(10)
        
        assert "LIMIT 5" in query_with_return.to_cypher()
        assert "RETURN p.name" in query_with_return.to_cypher()
        assert "SKIP 10" in query_with_skip.to_cypher()
        assert "LIMIT 5" in query_with_skip.to_cypher()

    def test_skip_chaining_methods(self):
        """Test SKIP clause method chaining."""
        query = (
            match(node("p", "Person"))
            .skip(10)
        )
        
        # Test that we can call other methods after skip
        query_with_return = query.return_("p.name")
        query_with_limit = query.limit(5)
        
        assert "SKIP 10" in query_with_return.to_cypher()
        assert "RETURN p.name" in query_with_return.to_cypher()
        assert "LIMIT 5" in query_with_limit.to_cypher()
        assert "SKIP 10" in query_with_limit.to_cypher()

    def test_order_by_limit_skip_chaining(self):
        """Test ORDER BY with LIMIT and SKIP chaining."""
        base_query = (
            match(node("p", "Person"))
            .return_("p.name", "p.age")
            .order_by(desc("p.age"))
        )
        
        # Test chaining limit and skip from order by
        query_with_limit = base_query.limit(10)
        query_with_skip = base_query.skip(5)
        query_with_both = base_query.skip(5).limit(10)
        
        assert "ORDER BY p.age DESC" in query_with_limit.to_cypher()
        assert "LIMIT 10" in query_with_limit.to_cypher()
        
        assert "ORDER BY p.age DESC" in query_with_skip.to_cypher()
        assert "SKIP 5" in query_with_skip.to_cypher()
        
        assert "ORDER BY p.age DESC" in query_with_both.to_cypher()
        assert "SKIP 5" in query_with_both.to_cypher()
        assert "LIMIT 10" in query_with_both.to_cypher()
