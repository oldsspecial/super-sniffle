"""
Unit tests for RETURN clause implementation.

Tests the working RETURN clause functionality including basic projections,
DISTINCT clause, and integration with other query clauses.
"""

import pytest
from super_sniffle import match, node, prop, param, literal


class TestBasicReturn:
    """Test basic RETURN clause functionality."""
    
    def test_basic_return_projections(self):
        """Test basic RETURN clause with projections."""
        person = node("Person", variable="p")
        query = match(person).return_("p.name", "p.age")
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nRETURN p.name, p.age"
        assert result == expected

    def test_return_everything_no_args(self):
        """Test RETURN * clause using no arguments."""
        person = node("Person", variable="p")
        query = match(person).return_()
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nRETURN *"
        assert result == expected

    def test_return_everything_explicit(self):
        """Test RETURN * clause using explicit asterisk."""
        person = node("Person", variable="p")
        query = match(person).return_("*")
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nRETURN *"
        assert result == expected

    def test_return_single_projection(self):
        """Test RETURN clause with single projection."""
        person = node("Person", variable="p")
        query = match(person).return_("p.name")
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nRETURN p.name"
        assert result == expected


class TestReturnDistinct:
    """Test RETURN DISTINCT functionality."""
    
    def test_return_distinct_projections(self):
        """Test RETURN DISTINCT with projections."""
        person = node("Person", variable="p")
        query = match(person).return_("p.name", distinct=True)
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nRETURN DISTINCT p.name"
        assert result == expected

    def test_return_distinct_everything(self):
        """Test RETURN DISTINCT everything."""
        person = node("Person", variable="p")
        query = match(person).return_(distinct=True)
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nRETURN DISTINCT *"
        assert result == expected

    def test_return_distinct_multiple_projections(self):
        """Test RETURN DISTINCT with multiple projections."""
        person = node("Person", variable="p")
        query = match(person).return_("p.name", "p.age", distinct=True)
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nRETURN DISTINCT p.name, p.age"
        assert result == expected


class TestReturnWithWhere:
    """Test RETURN clause integration with WHERE."""
    
    def test_return_after_where(self):
        """Test RETURN clause after WHERE."""
        person = node("Person", variable="p")
        query = (
            match(person)
            .where(prop("p", "age") > literal(30))
            .return_("p.name", "p.age")
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nWHERE p.age > 30\nRETURN p.name, p.age"
        assert result == expected

    def test_return_with_complex_where(self):
        """Test RETURN with complex WHERE conditions."""
        person = node("Person", variable="p")
        query = (
            match(person)
            .where(
                (prop("p", "age") > literal(25)) & 
                (prop("p", "active") == literal(True))
            )
            .return_("p.name", "p.age", "p.active")
        )
        result = query.to_cypher()
        
        assert "MATCH (p:Person)" in result
        assert "WHERE" in result
        assert "p.age > 25" in result
        assert "p.active = true" in result
        assert "AND" in result
        assert "RETURN p.name, p.age, p.active" in result


class TestReturnWithRelationships:
    """Test RETURN clause with relationship patterns."""
    
    def test_return_with_relationship_pattern(self):
        """Test RETURN clause with relationship patterns."""
        person = node("Person", variable="p")
        friend = node("Person", variable="f")
        query = (
            match(person.relates_to("r", "KNOWS", ">", friend))
            .where(prop("p", "age") > literal(25))
            .return_("p.name", "f.name", "r.since")
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)-[r:KNOWS]->(f:Person)\nWHERE p.age > 25\nRETURN p.name, f.name, r.since"
        assert result == expected

    def test_return_with_multiple_relationships(self):
        """Test RETURN with multiple relationship paths."""
        person = node("Person", variable="p")
        friend = node("Person", variable="f")
        company = node("Company", variable="c")
        query = (
            match(person.relates_to("knows", "KNOWS", ">", friend))
            .match(person.relates_to("works", "WORKS_FOR", ">", company))
            .return_("p.name", "f.name", "c.name")
        )
        result = query.to_cypher()
        
        assert "MATCH (p:Person)-[knows:KNOWS]->(f:Person)" in result
        assert "MATCH (p:Person)-[works:WORKS_FOR]->(c:Company)" in result
        assert "RETURN p.name, f.name, c.name" in result


class TestReturnWithMultipleMatch:
    """Test RETURN clause with multiple MATCH clauses."""
    
    def test_return_with_multiple_match(self):
        """Test RETURN clause with multiple MATCH clauses."""
        query = (
            match(node("Person", variable="p"))
            .match(node("Company", variable="c"))
            .where(prop("p", "works_at") == prop("c", "id"))
            .return_("p.name", "c.name")
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nMATCH (c:Company)\nWHERE p.works_at = c.id\nRETURN p.name, c.name"
        assert result == expected

    def test_return_with_multiple_match_and_conditions(self):
        """Test RETURN with multiple MATCH clauses and conditions."""
        query = (
            match(node("Person", variable="p"))
            .match(node("Company", variable="c"))
            .match(node("Department", variable="d"))
            .where(
                (prop("p", "company_id") == prop("c", "id")) &
                (prop("p", "dept_id") == prop("d", "id"))
            )
            .return_("p.name", "c.name", "d.name")
        )
        result = query.to_cypher()
        
        assert "MATCH (p:Person)" in result
        assert "MATCH (c:Company)" in result
        assert "MATCH (d:Department)" in result
        assert "WHERE" in result
        assert "RETURN p.name, c.name, d.name" in result


class TestReturnWithParameters:
    """Test RETURN clause with parameters and expressions."""
    
    def test_return_with_parameters(self):
        """Test RETURN clause with parameters and expressions."""
        person = node("Person", variable="p")
        query = (
            match(person)
            .where(prop("p", "name").contains(param("search_term")))
            .return_("p.name", "p.age", "p.email")
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nWHERE p.name CONTAINS $search_term\nRETURN p.name, p.age, p.email"
        assert result == expected

    def test_return_with_parameter_conditions(self):
        """Test RETURN with parameter-based conditions."""
        person = node("Person", variable="p")
        query = (
            match(person)
            .where(prop("p", "age") >= param("min_age"))
            .return_("p.name", "p.age", distinct=True)
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nWHERE p.age >= $min_age\nRETURN DISTINCT p.name, p.age"
        assert result == expected


class TestRealWorldExamples:
    """Test real-world usage examples."""
    
    def test_complex_query_with_complete_clause_chain(self):
        """Test complex query with complete clause chain."""
        person = node("Person", variable="p")
        friend = node("Person", variable="f")
        query = (
            match(person.relates_to("r", "KNOWS", ">", friend))
            .where(
                (prop("p", "active") == literal(True)) &
                (prop("p", "age") > literal(25)) &
                (prop("f", "age") < literal(35))
            )
            .return_("p.name", "f.name", "r.since", "p.age", "f.age")
        )
        
        result = query.to_cypher()
        
        expected_parts = [
            "MATCH (p:Person)-[r:KNOWS]->(f:Person)",
            "RETURN p.name, f.name, r.since, p.age, f.age"
        ]
        
        # Check that all expected parts are present
        for part in expected_parts:
            assert part in result, f"Expected '{part}' to be in the result"
        
        # Check that WHERE clause contains the expected conditions
        assert "WHERE" in result
        assert "p.active = true" in result
        assert "p.age > 25" in result
        assert "f.age < 35" in result
        assert "AND" in result

    def test_employee_search_example(self):
        """Test employee search real-world example."""
        employee = node("Employee", variable="e")
        department = node("Department", variable="d")
        query = (
            match(employee.relates_to("works_in", "WORKS_IN", ">", department))
            .where(
                (prop("d", "name") == param("dept_name")) &
                (prop("e", "salary") > param("min_salary"))
            )
            .return_("e.name", "e.salary", "d.name", distinct=True)
        )
        result = query.to_cypher()
        
        assert "MATCH (e:Employee)-[works_in:WORKS_IN]->(d:Department)" in result
        assert "WHERE (d.name = $dept_name) AND (e.salary > $min_salary)" in result
        assert "RETURN DISTINCT e.name, e.salary, d.name" in result


class TestReturnStyles:
    """Test different RETURN clause styles."""
    
    def test_basic_projections_style(self):
        """Test basic projections style."""
        query = match(node("Person", variable="p")).return_("p.name", "p.age")
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nRETURN p.name, p.age"
        assert result == expected

    def test_return_everything_style(self):
        """Test return everything style."""
        query = match(node("Person", variable="p")).return_()
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nRETURN *"
        assert result == expected

    def test_return_distinct_projections_style(self):
        """Test return distinct projections style."""
        query = match(node("Person", variable="p")).return_("p.name", distinct=True)
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nRETURN DISTINCT p.name"
        assert result == expected

    def test_complex_return_with_where_and_distinct(self):
        """Test complex return with WHERE and DISTINCT."""
        query = (
            match(node("Person", variable="p"))
            .where(prop("p", "age") > literal(30))
            .return_("p.name", "p.age", "p.email", distinct=True)
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nWHERE p.age > 30\nRETURN DISTINCT p.name, p.age, p.email"
        assert result == expected


class TestReturnEdgeCases:
    """Test edge cases for RETURN clause."""
    
    def test_return_with_minimal_match(self):
        """Test RETURN with minimal MATCH."""
        query = match(node(variable="n")).return_("n")
        result = query.to_cypher()
        expected = "MATCH (n)\nRETURN n"
        assert result == expected

    def test_return_with_complex_property_access(self):
        """Test RETURN with complex property access."""
        query = (
            match(node("Person", variable="p"))
            .return_("p.name", "p.address.city", "p.contact.email")
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nRETURN p.name, p.address.city, p.contact.email"
        assert result == expected

    def test_return_with_aggregation_functions(self):
        """Test RETURN with aggregation functions."""
        query = (
            match(node("Person", variable="p"))
            .return_("count(p)", "avg(p.age)", "max(p.salary)")
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nRETURN count(p), avg(p.age), max(p.salary)"
        assert result == expected
