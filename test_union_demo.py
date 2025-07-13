"""
Demonstrates the usage of UNION and UNION ALL.
"""

from super_sniffle import match, node, prop, literal

def test_union_demo():
    """
    Demonstrates a simple UNION query.
    """
    # Find all people and movies, and return their names/titles
    people_query = match(node("p", "Person")).return_("p.name AS name")
    movies_query = match(node("m", "Movie")).return_("m.title AS name")

    # Combine the queries with UNION
    union_query = people_query.union(movies_query)

    # Print the generated Cypher
    print(union_query.to_cypher())

def test_union_all_demo():
    """
    Demonstrates a simple UNION ALL query.
    """
    # Find all people and movies, and return their names/titles
    people_query = match(node("p", "Person")).return_("p.name AS name")
    movies_query = match(node("m", "Movie")).return_("m.title AS name")

    # Combine the queries with UNION ALL
    union_all_query = people_query.union_all(movies_query)

    # Print the generated Cypher
    print(union_all_query.to_cypher())

if __name__ == "__main__":
    test_union_demo()
    print("\n" + "="*20 + "\n")
    test_union_all_demo()
