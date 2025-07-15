"""
Unit tests for WITH clause implementation.
"""
import pytest
from super_sniffle import match, node

class TestBasicWith:
    def test_basic_with_projections(self):
        p = node("Person", variable="p")
        q = match(p).with_("p.name AS name").return_("name")
        result = q.to_cypher()
        expected = "MATCH (p:Person)\nWITH p.name AS name\nRETURN name"
        assert result == expected
