"""
Unit tests for quantified path patterns.
"""

import pytest
from super_sniffle import match, node, path

class TestQuantifiedPaths:
    """Test quantified path pattern functionality."""

    def test_one_or_more(self):
        """Test one or more quantifier."""
        p = path(node("p", "Person"), node("f", "Person")).one_or_more()
        query = match(p).return_("p", "f")
        result = query.to_cypher()
        expected = "MATCH ((p:Person)-[]-(f:Person))+\nRETURN p, f"
        assert result == expected

    def test_zero_or_more(self):
        """Test zero or more quantifier."""
        p = path(node("p", "Person"), node("f", "Person")).zero_or_more()
        query = match(p).return_("p", "f")
        result = query.to_cypher()
        expected = "MATCH ((p:Person)-[]-(f:Person))*\nRETURN p, f"
        assert result == expected

    def test_fixed_quantifier(self):
        """Test fixed quantifier."""
        p = path(node("p", "Person"), node("f", "Person")).quantify(min_hops=2, max_hops=2)
        query = match(p).return_("p", "f")
        result = query.to_cypher()
        expected = "MATCH ((p:Person)-[]-(f:Person)){2, 2}\nRETURN p, f"
        assert result == expected

    def test_bounded_quantifier(self):
        """Test bounded quantifier."""
        p = path(node("p", "Person"), node("f", "Person")).quantify(min_hops=2, max_hops=5)
        query = match(p).return_("p", "f")
        result = query.to_cypher()
        expected = "MATCH ((p:Person)-[]-(f:Person)){2, 5}\nRETURN p, f"
        assert result == expected

    def test_unbounded_quantifier(self):
        """Test unbounded quantifier."""
        p = path(node("p", "Person"), node("f", "Person")).quantify(min_hops=2)
        query = match(p).return_("p", "f")
        result = query.to_cypher()
        expected = "MATCH ((p:Person)-[]-(f:Person)){2, }\nRETURN p, f"
        assert result == expected
