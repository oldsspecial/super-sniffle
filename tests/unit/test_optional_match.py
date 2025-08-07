import unittest
from super_sniffle.api import QueryBuilder, node, prop

class TestOptionalMatch(unittest.TestCase):
    def test_optional_match_single_node(self):
        query = QueryBuilder().optional_match(node("Person", variable="p"))
        cypher = query.to_cypher()
        self.assertEqual(cypher, "OPTIONAL MATCH (p:Person)")

    def test_optional_match_relationship(self):
        # Create a path pattern: (p:Person)-[:KNOWS]->(f:Person)
        path_pattern = node("Person", variable="p").relationship("KNOWS", direction=">", variable=None) + node("Person", variable="f")
        query = QueryBuilder().optional_match(path_pattern)
        cypher = query.to_cypher()
        self.assertEqual(cypher, "OPTIONAL MATCH (p:Person)-[:KNOWS]->(f:Person)")

    def test_optional_match_chained(self):
        query = QueryBuilder().optional_match(node("Person", variable="p")).where(prop("p", "age") > 30)
        cypher = query.to_cypher()
        self.assertEqual(cypher, "OPTIONAL MATCH (p:Person)\nWHERE p.age > 30")

    def test_optional_match_multiple_patterns(self):
        query = QueryBuilder().optional_match(
            node("Person", variable="a"),
            node("Company", variable="b")
        )
        cypher = query.to_cypher()
        self.assertEqual(cypher, "OPTIONAL MATCH (a:Person), (b:Company)")

    def test_optional_match_with_other_clauses(self):
        # First optional match: (p:Person)
        query = QueryBuilder().optional_match(node("Person", variable="p"))
        # Second optional match: (p)-[:WORKS_AT]->(c:Company)
        path_pattern = node(variable="p").relationship("WORKS_AT", direction=">", variable=None) + node("Company", variable="c")
        query = query.optional_match(path_pattern)
        query = query.return_("p", "c")
        cypher = query.to_cypher()
        expected = (
            "OPTIONAL MATCH (p:Person)\n"
            "OPTIONAL MATCH (p)-[:WORKS_AT]->(c:Company)\n"
            "RETURN p, c"
        )
        self.assertEqual(cypher, expected)

if __name__ == '__main__':
    unittest.main()
