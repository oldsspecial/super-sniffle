"""
Unit tests for ORDER BY clause functionality and improved WITH clause.

Tests the implementation of ORDER BY clauses with asc() and desc() functions,
as well as the improved WITH clause that supports tuple-based projections.
"""

import pytest
from super_sniffle import (
    match, node, prop, literal, var, asc, desc
)


class TestOrderByClause:
    """Test the OrderByClause implementation."""
    
    def test_basic_ascending_sort(self):
        """Test basic ascending sort with string."""
        query = (
            match(node("Person", variable="p"))
            .return_("p.name", "p.age")
            .order_by("p.age")
        )
        cypher = query.to_cypher()
        assert "ORDER BY p.age" in cypher
        assert "MATCH (p:Person)" in cypher
        assert "RETURN p.name, p.age" in cypher
    
    def test_mixed_string_and_expression_sorts(self):
        """Test mixed string and expression sorts."""
        query = (
            match(node("Person", variable="p"))
            .return_("p.name", "p.age")
            .order_by("p.name", desc("p.age"))
        )
        cypher = query.to_cypher()
        assert "ORDER BY p.name, p.age DESC" in cypher
        
    def test_multiple_expression_sorts(self):
        """Test multiple expression sorts."""
        query = (
            match(node("Person", variable="p"))
            .return_("p.name", "p.age", "p.city")
            .order_by(asc("p.city"), desc("p.age"), asc("p.name"))
        )
        cypher = query.to_cypher()
        assert "ORDER BY p.city, p.age DESC, p.name" in cypher

    def test_order_by_with_limit(self):
        """Test ORDER BY with LIMIT functionality."""
        query = (
            match(node("Person", variable="p"))
            .return_("p.name", "p.age")
            .order_by(desc("p.age"))
            .limit(5)
        )
        cypher = query.to_cypher()
        assert "ORDER BY p.age DESC" in cypher
        assert "LIMIT 5" in cypher


class TestOrderByWithTupleProjections:
    """Test ORDER BY with WITH clause using tuple projections."""
    
    def test_with_tuple_projections_then_order_by(self):
        """Test WITH using tuple projections, then ORDER BY."""
        query = (
            match(node("Person", variable="p"))
            .with_(("p.name", "name"), ("p.age", "age"), ("p.city", "city"))
            .order_by("name", desc("age"))
        )
        cypher = query.to_cypher()
        assert "WITH p.name AS name, p.age AS age, p.city AS city" in cypher
        assert "ORDER BY name, age DESC" in cypher
        
    def test_mixed_string_and_tuple_projections(self):
        """Test mixed string and tuple projections in WITH."""
        query = (
            match(node("Person", variable="p"))
            .with_("p", ("count(*)", "total"))
            .order_by(desc("total"))
        )
        cypher = query.to_cypher()
        assert "WITH p, count(*) AS total" in cypher
        assert "ORDER BY total DESC" in cypher
        
    def test_complex_aggregation_with_order_by(self):
        """Test complex aggregation with ORDER BY."""
        query = (
            match(node("Person", variable="p").relationship(">", "KNOWS", target_node=node("Person", variable="f")))
            .with_(("p.name", "personName"), ("count(f)", "friendCount"))
            .order_by(desc("friendCount"), "personName")
        )
        cypher = query.to_cypher()
        assert "WITH p.name AS personName, count(f) AS friendCount" in cypher
        assert "ORDER BY friendCount DESC, personName" in cypher


class TestOrderByInComplexChains:
    """Test ORDER BY in complex query chains."""
    
    def test_match_where_with_order_return_chain(self):
        """Test MATCH → WHERE → WITH → ORDER BY → RETURN chain."""
        query = (
            match(node("Person", variable="p"))
            .where(prop("p", "age") > literal(18))
            .with_(("p.name", "name"), ("p.age", "age"))
            .order_by(desc("age"))
            .return_("name", "age")
        )
        cypher = query.to_cypher()
        assert "MATCH (p:Person)" in cypher
        assert "WHERE p.age > 18" in cypher
        assert "WITH p.name AS name, p.age AS age" in cypher
        assert "ORDER BY age DESC" in cypher
        assert "RETURN name, age" in cypher


class TestImprovedWithClause:
    """Test the improved WITH clause tuple functionality."""
    
    def test_simple_tuple_projections(self):
        """Test simple tuple projections."""
        query = (
            match(node("Person", variable="p"))
            .with_(("p.name", "personName"), ("p.age", "personAge"))
            .return_("personName", "personAge")
        )
        cypher = query.to_cypher()
        assert "WITH p.name AS personName, p.age AS personAge" in cypher
        assert "RETURN personName, personAge" in cypher
        
    def test_mixed_projections(self):
        """Test mixed string and tuple projections."""
        query = (
            match(node("Person", variable="p"))
            .with_("p", ("p.name", "name"), ("p.age", "age"))
            .return_("p.id", "name", "age")
        )
        cypher = query.to_cypher()
        assert "WITH p, p.name AS name, p.age AS age" in cypher
        assert "RETURN p.id, name, age" in cypher
        
    def test_with_distinct_using_tuples(self):
        """Test WITH DISTINCT using tuples."""
        query = (
            match(node("Person", variable="p"))
            .with_(("p.department", "dept"), distinct=True)
            .return_("dept")
        )
        cypher = query.to_cypher()
        assert "WITH DISTINCT p.department AS dept" in cypher
        assert "RETURN dept" in cypher
        
    def test_complex_expressions_in_tuples(self):
        """Test complex expressions in tuple projections."""
        query = (
            match(node("Person", variable="p").relationship(">", "WORKS_FOR", target_node=node("Company", variable="c")))
            .with_(("p.name", "employeeName"), ("c.name", "companyName"), ("p.salary * 12", "annualSalary"))
            .order_by(desc("annualSalary"))
            .return_("employeeName", "companyName", "annualSalary")
        )
        cypher = query.to_cypher()
        assert "WITH p.name AS employeeName, c.name AS companyName, p.salary * 12 AS annualSalary" in cypher
        assert "ORDER BY annualSalary DESC" in cypher
        assert "RETURN employeeName, companyName, annualSalary" in cypher


class TestRealWorldExamples:
    """Test real-world usage examples."""
    
    def test_top_most_connected_people(self):
        """Test finding top 5 most connected people."""
        query = (
            match(node("Person", variable="p").relationship("-", "KNOWS", target_node=node("Person", variable="friend")))
            .with_(("p.name", "personName"), ("count(friend)", "friendCount"))
            .order_by(desc("friendCount"), "personName")
            .limit(5)
            .return_("personName", "friendCount")
        )
        cypher = query.to_cypher()
        assert "MATCH" in cypher
        assert "WITH p.name AS personName, count(friend) AS friendCount" in cypher
        assert "ORDER BY friendCount DESC, personName" in cypher
        assert "LIMIT 5" in cypher
        assert "RETURN personName, friendCount" in cypher
        
    def test_employee_rankings_by_salary(self):
        """Test employee rankings by salary within departments."""
        query = (
            match(node("Employee", variable="e").relationship(">", "WORKS_IN", target_node=node("Department", variable="d")))
            .with_(("e.name", "employeeName"), ("d.name", "deptName"), ("e.salary", "salary"))
            .order_by("deptName", desc("salary"))
            .return_("deptName", "employeeName", "salary")
        )
        cypher = query.to_cypher()
        assert "MATCH" in cypher
        assert "WITH e.name AS employeeName, d.name AS deptName, e.salary AS salary" in cypher
        assert "ORDER BY deptName, salary DESC" in cypher
        assert "RETURN deptName, employeeName, salary" in cypher


class TestAscDescFunctions:
    """Test the asc() and desc() helper functions."""
    
    def test_asc_function(self):
        """Test the asc() function."""
        query = (
            match(node("Person", variable="p"))
            .return_("p.name")
            .order_by(asc("p.name"))
        )
        cypher = query.to_cypher()
        assert "ORDER BY p.name" in cypher  # ASC is default, so it's omitted
        
    def test_desc_function(self):
        """Test the desc() function."""
        query = (
            match(node("Person", variable="p"))
            .return_("p.name")
            .order_by(desc("p.name"))
        )
        cypher = query.to_cypher()
        assert "ORDER BY p.name DESC" in cypher
        
    def test_mixed_asc_desc(self):
        """Test mixed asc() and desc() in same ORDER BY."""
        query = (
            match(node("Person", variable="p"))
            .return_("p.name", "p.age")
            .order_by(asc("p.name"), desc("p.age"))
        )
        cypher = query.to_cypher()
        assert "ORDER BY p.name, p.age DESC" in cypher


class TestOrderByEdgeCases:
    """Test edge cases and error conditions for ORDER BY."""
    
    def test_order_by_with_single_field(self):
        """Test ORDER BY with single field."""
        query = (
            match(node("Person", variable="p"))
            .return_("p.name")
            .order_by("p.name")
        )
        cypher = query.to_cypher()
        assert "ORDER BY p.name" in cypher
        
    def test_order_by_with_many_fields(self):
        """Test ORDER BY with many fields."""
        query = (
            match(node("Person", variable="p"))
            .return_("p.name", "p.age", "p.city", "p.country")
            .order_by("p.country", "p.city", desc("p.age"), asc("p.name"))
        )
        cypher = query.to_cypher()
        assert "ORDER BY p.country, p.city, p.age DESC, p.name" in cypher
