import unittest
from super_sniffle import node, relationship, optional_match, prop, literal

class TestOptionalMatchClause(unittest.TestCase):
    def test_basic_optional_match(self):
        q = optional_match(node("p", "Person"))
        self.assertEqual(q.to_cypher(), "OPTIONAL MATCH (p:Person)")
        
    def test_optional_match_with_relationship(self):
        q = optional_match(node("p", "Person") + relationship("KNOWS", direction=">") + node("f", "Person"))
        self.assertEqual(q.to_cypher(), "OPTIONAL MATCH (p:Person)-[:KNOWS]->(f:Person)")
        
    def test_optional_match_with_where(self):
        q = optional_match(node("p", "Person") + relationship("KNOWS", direction=">") + node("f", "Person"))
        q = q.where(prop("p", "age") > literal(30))
        self.assertEqual(q.to_cypher(), "OPTIONAL MATCH (p:Person)-[:KNOWS]->(f:Person)\nWHERE p.age > 30")
        
    def test_chained_with_regular_match(self):
        q = optional_match(node("p", "Person"))
        q = q.optional_match(node("p") + relationship("KNOWS", direction=">") + node("f", "Person"))
        expected = "OPTIONAL MATCH (p:Person)\nOPTIONAL MATCH (p)-[:KNOWS]->(f:Person)"
        self.assertEqual(q.to_cypher(), expected)
        
    def test_optional_match_with_quantified_path(self):
        path = (node("p", "Person") + relationship("KNOWS", direction=">") + node("f", "Person")).one_or_more()
        q = optional_match(path)
        self.assertEqual(q.to_cypher(), "OPTIONAL MATCH ((p:Person)-[:KNOWS]->(f:Person))+")
        
    def test_optional_match_in_complex_query(self):
        q = optional_match(node("p", "Person"))
        q = q.where(prop("p", "name") == literal("Alice"))
        q = q.optional_match(node("p") + relationship("KNOWS", direction=">") + node("f", "Person"))
        q = q.return_("p", "f")
        expected = "OPTIONAL MATCH (p:Person)\nWHERE p.name = 'Alice'\nOPTIONAL MATCH (p)-[:KNOWS]->(f:Person)\nRETURN p, f"
        self.assertEqual(q.to_cypher(), expected)

if __name__ == "__main__":
    unittest.main()
