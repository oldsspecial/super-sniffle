"""
Unit tests for WITH clause implementation.

Tests the working WITH clause functionality including basic projections,
DISTINCT clause, aggregation, and query chaining capabilities.
"""

import pytest
from super_sniffle import match, node, prop, var, param, literal


class TestBasicWith:
    """Test basic WITH clause functionality."""
    
    def test_basic_with_projections(self):
        """Test basic WITH clause with projections."""
        person = node("p", "Person")
        query = (
            match(person)
            .with_("p.name AS name", "p.age AS age")
            .return_("name", "age")
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nWITH p.name AS name, p.age AS age\nRETURN name, age"
        assert result == expected

    def test_with_single_projection(self):
        """Test WITH clause with single projection."""
        person = node("p", "Person")
        query = (
            match(person)
            .with_("p")
            .return_("p.name")
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nWITH p\nRETURN p.name"
        assert result == expected

    def test_with_distinct(self):
        """Test WITH DISTINCT clause."""
        person = node("p", "Person")
        company = node("c", "Company")
        query = (
            match(person.relates_to("r", "WORKS_AT", ">", company))
            .with_("c.industry AS industry", distinct=True)
            .return_("industry")
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)-[r:WORKS_AT]->(c:Company)\nWITH DISTINCT c.industry AS industry\nRETURN industry"
        assert result == expected


class TestWithWhere:
    """Test WITH clause with WHERE functionality."""
    
    def test_with_followed_by_where(self):
        """Test WITH clause followed by WHERE."""
        person = node("p", "Person")
        query = (
            match(person)
            .with_("p")
            .where(prop("p", "age") > literal(30))
            .return_("p.name", "p.age")
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nWITH p\nWHERE p.age > 30\nRETURN p.name, p.age"
        assert result == expected

    def test_with_from_where_clause(self):
        """Test WITH clause from WHERE clause."""
        person = node("p", "Person")
        query = (
            match(person)
            .where(prop("p", "active") == literal(True))
            .with_("p.name AS name", "p.department AS dept")
            .return_("name", "dept")
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nWHERE p.active = true\nWITH p.name AS name, p.department AS dept\nRETURN name, dept"
        assert result == expected


class TestWithChaining:
    """Test WITH clause chaining capabilities."""
    
    def test_with_chaining_multiple_query_parts(self):
        """Test WITH clause chaining multiple query parts."""
        person = node("p", "Person")
        friend = node("friend", "Person")
        query = (
            match(person)
            .with_("p")
            .match(person.relates_to("r", "KNOWS", ">", friend))
            .return_("p.name", "friend.name")
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nWITH p\nMATCH (p:Person)-[r:KNOWS]->(friend:Person)\nRETURN p.name, friend.name"
        assert result == expected

    def test_multiple_with_clauses(self):
        """Test multiple WITH clauses in sequence."""
        person = node("p", "Person")
        friend = node("friend", "Person")
        query = (
            match(person)
            .where(prop("p", "age") > literal(30))
            .with_("p")
            .match(person.relates_to("r", "KNOWS", ">", friend))
            .with_("p", "collect(friend) AS friends", "size(collect(friend)) AS friendCount")
            .where(var("friendCount") > literal(3))
            .return_("p.name", "friendCount")
        )
        result = query.to_cypher()
        expected = ("MATCH (p:Person)\n"
                   "WHERE p.age > 30\n"
                   "WITH p\n"
                   "MATCH (p:Person)-[r:KNOWS]->(friend:Person)\n"
                   "WITH p, collect(friend) AS friends, size(collect(friend)) AS friendCount\n"
                   "WHERE friendCount > 3\n"
                   "RETURN p.name, friendCount")
        assert result == expected


class TestWithAggregation:
    """Test WITH clause with aggregation functionality."""
    
    def test_with_aggregation(self):
        """Test WITH clause with aggregation."""
        person = node("p", "Person")
        friend = node("friend", "Person")
        query = (
            match(person.relates_to("r", "KNOWS", ">", friend))
            .with_("p", "count(friend) AS friendCount")
            .where(var("friendCount") > literal(3))
            .return_("p.name", "friendCount")
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)-[r:KNOWS]->(friend:Person)\nWITH p, count(friend) AS friendCount\nWHERE friendCount > 3\nRETURN p.name, friendCount"
        assert result == expected

    def test_with_collect_aggregation(self):
        """Test WITH clause with collect aggregation."""
        person = node("p", "Person")
        friend = node("friend", "Person")
        query = (
            match(person.relates_to("r", "KNOWS", ">", friend))
            .with_("p", "collect(friend.name) AS friendNames")
            .return_("p.name", "friendNames")
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)-[r:KNOWS]->(friend:Person)\nWITH p, collect(friend.name) AS friendNames\nRETURN p.name, friendNames"
        assert result == expected


class TestWithTupleProjections:
    """Test WITH clause with tuple-based projections."""
    
    def test_with_tuple_projections(self):
        """Test WITH clause with tuple projections."""
        person = node("p", "Person")
        query = (
            match(person)
            .with_(("p.name", "personName"), ("p.age", "personAge"))
            .return_("personName", "personAge")
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nWITH p.name AS personName, p.age AS personAge\nRETURN personName, personAge"
        assert result == expected

    def test_with_mixed_projections(self):
        """Test WITH clause with mixed string and tuple projections."""
        person = node("p", "Person")
        query = (
            match(person)
            .with_("p", ("p.name", "name"), ("p.age", "age"))
            .return_("p.id", "name", "age")
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nWITH p, p.name AS name, p.age AS age\nRETURN p.id, name, age"
        assert result == expected

    def test_with_distinct_using_tuples(self):
        """Test WITH DISTINCT using tuples."""
        person = node("p", "Person")
        query = (
            match(person)
            .with_(("p.department", "dept"), distinct=True)
            .return_("dept")
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nWITH DISTINCT p.department AS dept\nRETURN dept"
        assert result == expected


class TestRealWorldExamples:
    """Test real-world usage examples."""
    
    def test_complex_query_with_multiple_with_clauses(self):
        """Test complex query with multiple WITH clauses."""
        person = node("p", "Person")
        friend = node("f", "Person")
        
        query = (
            match(person.relates_to("r1", "KNOWS", ">", friend))
            .with_("p", "count(f) AS friendCount")
            .where(var("friendCount") > literal(5))
            .with_("p")
            .match(person.relates_to("r2", "KNOWS", ">", node("f2", "Person")))
            .return_("p.name", "f2.name")
        )
        
        result = query.to_cypher()
        
        # Check that all expected parts are present
        expected_parts = [
            "MATCH (p:Person)-[r1:KNOWS]->(f:Person)",
            "WITH p, count(f) AS friendCount",
            "WHERE friendCount > 5",
            "WITH p",
            "MATCH (p:Person)-[r2:KNOWS]->(f2:Person)",
            "RETURN p.name, f2.name"
        ]
        
        for part in expected_parts:
            assert part in result, f"Expected '{part}' to be in the result"

    def test_employee_aggregation_example(self):
        """Test employee aggregation real-world example."""
        employee = node("e", "Employee")
        department = node("d", "Department")
        query = (
            match(employee.relates_to("works_in", "WORKS_IN", ">", department))
            .with_("d.name AS deptName", "count(e) AS employeeCount", "avg(e.salary) AS avgSalary")
            .where(var("employeeCount") > literal(10))
            .return_("deptName", "employeeCount", "avgSalary")
        )
        result = query.to_cypher()
        
        assert "MATCH (e:Employee)-[works_in:WORKS_IN]->(d:Department)" in result
        assert "WITH d.name AS deptName, count(e) AS employeeCount, avg(e.salary) AS avgSalary" in result
        assert "WHERE employeeCount > 10" in result
        assert "RETURN deptName, employeeCount, avgSalary" in result


class TestWithStyles:
    """Test different WITH clause styles."""
    
    def test_basic_projections_with_aliasing(self):
        """Test basic projections with aliasing."""
        query = (
            match(node("p", "Person"))
            .with_("p.name AS fullName", "p.age AS years")
            .return_("fullName", "years")
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nWITH p.name AS fullName, p.age AS years\nRETURN fullName, years"
        assert result == expected

    def test_pass_through_without_transformation(self):
        """Test pass-through without transformation."""
        query = (
            match(node("p", "Person"))
            .with_("p")
            .return_("p.name")
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nWITH p\nRETURN p.name"
        assert result == expected

    def test_with_distinct_style(self):
        """Test WITH DISTINCT style."""
        query = (
            match(node("p", "Person"))
            .with_("p.department AS dept", distinct=True)
            .return_("dept")
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nWITH DISTINCT p.department AS dept\nRETURN dept"
        assert result == expected

    def test_with_followed_by_where_style(self):
        """Test WITH followed by WHERE style."""
        query = (
            match(node("p", "Person"))
            .with_("p.name AS name", "p.salary AS salary")
            .where(var("salary") > literal(50000))
            .return_("name", "salary")
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nWITH p.name AS name, p.salary AS salary\nWHERE salary > 50000\nRETURN name, salary"
        assert result == expected

    def test_chaining_query_parts_style(self):
        """Test chaining query parts style."""
        query = (
            match(node("p", "Person"))
            .with_("p")
            .match(node("p").relates_to("r", "WORKS_AT", ">", node("c", "Company")))
            .return_("p.name", "c.name")
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nWITH p\nMATCH (p)-[r:WORKS_AT]->(c:Company)\nRETURN p.name, c.name"
        assert result == expected


class TestWithEdgeCases:
    """Test edge cases for WITH clause."""
    
    def test_with_empty_projection(self):
        """Test WITH with minimal projections."""
        query = (
            match(node("n"))
            .with_("n")
            .return_("n")
        )
        result = query.to_cypher()
        expected = "MATCH (n)\nWITH n\nRETURN n"
        assert result == expected

    def test_with_complex_expressions(self):
        """Test WITH with complex expressions."""
        query = (
            match(node("p", "Person"))
            .with_("p.name AS name", "p.age * 365 AS ageInDays", "size(p.hobbies) AS hobbyCount")
            .return_("name", "ageInDays", "hobbyCount")
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nWITH p.name AS name, p.age * 365 AS ageInDays, size(p.hobbies) AS hobbyCount\nRETURN name, ageInDays, hobbyCount"
        assert result == expected

    def test_with_parameter_references(self):
        """Test WITH with parameter references."""
        query = (
            match(node("p", "Person"))
            .with_("p", "p.age + $bonus AS adjustedAge")
            .return_("p.name", "adjustedAge")
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nWITH p, p.age + $bonus AS adjustedAge\nRETURN p.name, adjustedAge"
        assert result == expected
