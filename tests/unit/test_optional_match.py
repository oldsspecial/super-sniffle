import unittest
from super_sniffle.api import QueryBuilder, node, prop

class TestOptionalMatch(unittest.TestCase):
    def test_optional_match_single_node(self):
        query = QueryBuilder().optional_match(node("p", "Person"))
        cypher = query.to_cypher()
        self.assertEqual(cypher, "OPTIONAL MATCH (p:Person)")

    def test_optional_match_relationship(self):
        query = QueryBuilder().optional_match(
            node("p", "Person").relates_to(variable=None, rel_type="KNOWS", direction=">", target_node=node("f", "Person"))
        )
        cypher = query.to_cypher()
        self.assertEqual(cypher, "OPTIONAL MATCH (p:Person)-[:KNOWS]->(f:Person)")

    def test_optional_match_chained(self):
        query = QueryBuilder().optional_match(node("p", "Person")).where(prop("p", "age") > 30)
        cypher = query.to_cypher()
        self.assertEqual(cypher, "OPTIONAL MATCH (p:Person)\nWHERE p.age > 30")

    def test_optional_match_multiple_patterns(self):
        query = QueryBuilder().optional_match(
            node("a", "Person"),
            node("b", "Company")
        )
        cypher = query.to_cypher()
        self.assertEqual(cypher, "OPTIONAL MATCH (a:Person), (b:Company)")

    def test_optional_match_with_other_clauses(self):
        query = (
            QueryBuilder().optional_match(node("p", "Person"))
            .optional_match(node("p").relates_to(variable=None, rel_type="WORKS_AT", direction=">", target_node=node("c", "Company")))
            .return_("p", "c")
        )
        cypher = query.to_cypher()
        expected = (
            "OPTIONAL MATCH (p:Person)\n"
            "OPTIONAL MATCH (p)-[:WORKS_AT]->(c:Company)\n"
            "RETURN p, c"
        )
        self.assertEqual(cypher, expected)

if __name__ == '__main__':
    unittest.main()
