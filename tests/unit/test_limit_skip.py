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
            match(node("Person", variable="p"))
            .return_("p.name", "p.age")
            .limit(5)
        )
        result = query.to_cypher()
        expected = "MATCH (p:Person)\nRETURN p.name, p.age\nLIMIT 5"
