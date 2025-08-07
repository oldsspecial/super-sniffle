"""
Unit tests for lazy variable generation in NodePattern.

Tests the new functionality where nodes can be created without explicit variables
and get automatically generated variables only when referenced in queries.
"""

import pytest
from super_sniffle.api import node, match, literal
from super_sniffle.ast.patterns.node_pattern import (
    NodePattern, 
    _get_next_variable_name, 
    _reset_variable_counter,
    _JAZZ_MUSICIANS
)


class TestLazyVariableGeneration:
    """Test lazy variable generation for anonymous nodes."""
    
    def setup_method(self):
        """Reset the global counter before each test."""
        _reset_variable_counter()
    
    def test_anonymous_node_creation(self):
        """Test that nodes can be created without variables."""
        person = node("Person")
        assert person.variable is None
        assert person._lazy_variable is None
        assert person.labels is not None
    
    def test_anonymous_node_to_cypher_stays_anonymous(self):
        """Test that anonymous nodes stay anonymous in to_cypher() until referenced."""
        person = node("Person")
        cypher = person.to_cypher()
        assert cypher == "(:Person)"
        # Should still be anonymous
        assert person._lazy_variable is None
    
    def test_anonymous_node_gets_variable_when_referenced(self):
        """Test that anonymous nodes get variables when referenced."""
        person = node("Person")
        # Reference the node - this should generate a variable
        var_name = str(person)
        assert var_name == "_node_bolden"
        assert person._lazy_variable == "_node_bolden"
    
    def test_multiple_anonymous_nodes_get_different_variables(self):
        """Test that multiple anonymous nodes get different jazz musician variables."""
        person1 = node("Person")
        person2 = node("Company")
        person3 = node("User")
        
        # Reference them in order
        var1 = str(person1)
        var2 = str(person2)
        var3 = str(person3)
        
        assert var1 == "_node_bolden"
        assert var2 == "_node_morton" 
        assert var3 == "_node_oliver"
        
        # Each should have their own lazy variable
        assert person1._lazy_variable == "_node_bolden"
        assert person2._lazy_variable == "_node_morton"
        assert person3._lazy_variable == "_node_oliver"
    
    def test_anonymous_node_prop_generates_variable(self):
        """Test that accessing properties generates a variable."""
        person = node("Person")
        assert person._lazy_variable is None
        
        # Access a property - should generate variable
        age_prop = person.prop("age")
        assert person._lazy_variable == "_node_bolden"
        assert age_prop.variable == "_node_bolden"
        assert age_prop.name == "age"
    
    def test_anonymous_node_consistent_variable_generation(self):
        """Test that the same node always gets the same variable."""
        person = node("Person")
        
        # Multiple references should return the same variable
        var1 = str(person)
        var2 = str(person)
        prop_var = person.prop("age").variable
        
        assert var1 == var2 == prop_var == "_node_bolden"
        assert person._lazy_variable == "_node_bolden"
    
    def test_explicit_variable_takes_precedence(self):
        """Test that explicit variables are used instead of lazy generation."""
        person = node("Person", variable="p")
        
        # Should use explicit variable
        assert str(person) == "p"
        assert person.prop("age").variable == "p"
        assert person._lazy_variable is None  # No lazy variable generated
    
    def test_anonymous_node_in_return_statement(self):
        """Test anonymous nodes work in return statements."""
        person = node("Person")
        query = match(person).return_(person)
        cypher = query.to_cypher()
        
        expected = "MATCH (_node_bolden:Person)\nRETURN _node_bolden"
        assert cypher == expected
        assert person._lazy_variable == "_node_bolden"
    
    def test_anonymous_node_in_where_clause(self):
        """Test anonymous nodes work in where clauses."""
        person = node("Person")
        query = match(person).where(person.prop("age") > literal(25))
        cypher = query.to_cypher()
        
        expected = "MATCH (_node_bolden:Person)\nWHERE _node_bolden.age > 25"
        assert cypher == expected
        assert person._lazy_variable == "_node_bolden"
    
    def test_mixed_anonymous_and_explicit_nodes(self):
        """Test mixing anonymous and explicitly named nodes."""
        anonymous = node("Person")
        explicit = node("Company", variable="c")
        
        query = match(anonymous, explicit).return_(anonymous, explicit)
        cypher = query.to_cypher()
        
        expected = "MATCH (_node_bolden:Person), (c:Company)\nRETURN _node_bolden, c"
        assert cypher == expected
        assert anonymous._lazy_variable == "_node_bolden"
        assert explicit._lazy_variable is None
    
    def test_anonymous_node_stays_anonymous_when_not_referenced(self):
        """Test that nodes only used in MATCH stay anonymous."""
        person = node("Person")
        query = match(person)
        cypher = query.to_cypher()
        
        # Should stay anonymous since not referenced elsewhere
        assert cypher == "MATCH (:Person)"
        assert person._lazy_variable is None
    
    def test_jazz_musician_variable_names(self):
        """Test that jazz musician names are used correctly."""
        # Reset counter
        _reset_variable_counter()
        
        expected_names = ["bolden", "morton", "oliver", "armstrong", "bechet"]
        nodes = [node("Person") for _ in range(5)]
        
        # Reference each node to generate variables
        for i, n in enumerate(nodes):
            var_name = str(n)
            expected = f"_node_{expected_names[i]}"
            assert var_name == expected
    
    def test_fallback_after_exhausting_jazz_musicians(self):
        """Test fallback naming when all jazz musician names are used."""
        # Set counter to beyond the list
        import super_sniffle.ast.patterns.node_pattern as np_module
        np_module._node_counter = len(_JAZZ_MUSICIANS)
        
        person = node("Person")
        var_name = str(person)
        
        assert var_name == "_node_jazzcat1"
    
    def test_anonymous_node_with_properties(self):
        """Test anonymous nodes with properties."""
        person = node("Person", age=30, name="Alice")
        
        # Should stay anonymous in pattern
        cypher = person.to_cypher()
        assert cypher == "(:Person {age: 30, name: 'Alice'})"
        assert person._lazy_variable is None
        
        # Should get variable when referenced
        query = match(person).return_(person)
        cypher = query.to_cypher()
        expected = 'MATCH (_node_bolden:Person {age: 30, name: "Alice"})\nRETURN _node_bolden'
        assert cypher == expected
    
    def test_anonymous_node_with_multiple_labels(self):
        """Test anonymous nodes with multiple labels."""
        multi = node("Person", "Employee")
        
        # Should stay anonymous with label arithmetic format
        cypher = multi.to_cypher()
        assert "(:`(Person & Employee)`)" in cypher
        assert multi._lazy_variable is None
        
        # Should get variable when referenced
        var_name = str(multi)
        assert var_name == "_node_bolden"
    
    def test_complex_query_with_multiple_anonymous_nodes(self):
        """Test complex query with multiple anonymous nodes."""
        user = node("User")
        post = node("Post") 
        tag = node("Tag")
        
        query = (match(user, post, tag)
                .where(user.prop("active") == literal(True))
                .where(post.prop("published") == literal(True))
                .return_(user, post.prop("title"), tag))
        
        cypher = query.to_cypher()
        
        # Should have generated variables for referenced nodes
        assert "_node_bolden" in cypher  # user
        assert "_node_morton" in cypher  # post
        assert "_node_oliver" in cypher  # tag
        
        # Verify the structure
        lines = cypher.split('\n')
        assert "MATCH (_node_bolden:User), (_node_morton:Post), (_node_oliver:Tag)" in lines[0]
        assert "WHERE _node_bolden.active = true" in lines[1]
        assert "WHERE _node_morton.published = true" in lines[2]
        assert "RETURN _node_bolden, _node_morton.title, _node_oliver" in lines[3]


class TestVariableNameGeneration:
    """Test the variable name generation function itself."""
    
    def setup_method(self):
        """Reset the global counter before each test."""
        _reset_variable_counter()
    
    def test_variable_name_format(self):
        """Test that variable names follow the correct format."""
        name = _get_next_variable_name()
        assert name.startswith("_node_")
        assert name == "_node_bolden"
    
    def test_variable_name_uniqueness(self):
        """Test that each call generates a unique name."""
        names = [_get_next_variable_name() for _ in range(10)]
        assert len(set(names)) == 10  # All unique
    
    def test_jazz_musician_names_used_in_order(self):
        """Test that jazz musician names are used in the correct order."""
        expected_start = ["bolden", "morton", "oliver", "armstrong", "bechet"]
        
        for expected in expected_start:
            name = _get_next_variable_name()
            assert name == f"_node_{expected}"
    
    def test_fallback_naming(self):
        """Test fallback naming when musician list is exhausted."""
        # Exhaust the musician list
        import super_sniffle.ast.patterns.node_pattern as np_module
        np_module._node_counter = len(_JAZZ_MUSICIANS)
        
        # Should use fallback
        name1 = _get_next_variable_name()
        name2 = _get_next_variable_name()
        
        assert name1 == "_node_jazzcat1"
        assert name2 == "_node_jazzcat2"


class TestBackwardCompatibility:
    """Test that existing functionality still works."""
    
    def setup_method(self):
        """Reset the global counter before each test."""
        _reset_variable_counter()
    
    def test_explicit_variables_still_work(self):
        """Test that explicitly named nodes work as before."""
        person = node("Person", variable="p")
        query = match(person).return_(person)
        cypher = query.to_cypher()
        
        expected = "MATCH (p:Person)\nRETURN p"
        assert cypher == expected
    
    def test_property_access_with_explicit_variables(self):
        """Test property access with explicit variables."""
        person = node("Person", variable="p")
        age_prop = person.prop("age")
        
        assert age_prop.variable == "p"
        assert age_prop.name == "age"
        assert person._lazy_variable is None
    
    def test_degree_constraints_require_explicit_variables(self):
        """Test that degree constraints still require explicit variables."""
        with pytest.raises(ValueError, match="Variable name is required"):
            node("Person", max_degree=5)
    
    def test_existing_query_patterns_unchanged(self):
        """Test that existing query patterns produce the same output."""
        person = node("Person", variable="p")
        query = (match(person)
                .where(person.prop("age") > literal(25))
                .return_(person, ("person.name", "name")))
        
        cypher = query.to_cypher()
        
        # Should be identical to previous behavior
        expected_lines = [
            "MATCH (p:Person)",
            "WHERE p.age > 25", 
            "RETURN p, person.name AS name"
        ]
        assert cypher == "\n".join(expected_lines)