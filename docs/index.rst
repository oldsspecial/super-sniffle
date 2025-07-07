super-sniffle documentation
============================

Welcome to super-sniffle's documentation!

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   quickstart
   api
   examples
   development

Overview
--------

super-sniffle is a Python library for generating Neo4j Cypher queries in a functional and flexible way. It provides a clean, type-safe, and maintainable way to generate complex Neo4j Cypher READ queries programmatically, eliminating the need for error-prone string concatenation.

Features
--------

* **Functional API**: Build queries using composable functions and method chaining
* **Type Safety**: Comprehensive type hints for excellent IDE support
* **CYPHER25 Compliance**: Strict adherence to the CYPHER25 specification
* **Immutable Objects**: Safe composition without side effects
* **Well-Formatted Output**: Generates readable, properly indented Cypher queries
* **Zero Dependencies**: Minimal external dependencies for easy installation

Installation
------------

Install super-sniffle using pip:

.. code-block:: bash

   pip install super-sniffle

For development installation:

.. code-block:: bash

   git clone https://github.com/oldsspecial/super-sniffle.git
   cd super-sniffle
   poetry install

Quick Start
-----------

.. note::
   super-sniffle is currently in early development. The API shown below represents the planned interface and is not yet implemented.

.. code-block:: python

   from super_sniffle import match, node, relationship, prop, param

   # Build a simple query
   query = (
       match(node("p", "Person"))
       .where(prop("p", "age").gt(param("min_age")))
       .return_("p.name", "p.age")
       .order_by("p.age")
       .limit(10)
       .to_cypher()
   )

   print(query)
   # Output:
   # MATCH (p:Person)
   # WHERE p.age > $min_age
   # RETURN p.name, p.age
   # ORDER BY p.age
   # LIMIT 10

API Reference
-------------

.. automodule:: super_sniffle
   :members:

.. automodule:: super_sniffle.api
   :members:

Development Status
------------------

super-sniffle is currently in the initial planning and development phase. The project structure and architecture have been established, and we're working on implementing the core components.

Current Progress:

* ✅ Project structure and configuration
* ✅ Architecture design and documentation
* 🔄 Core AST components (in progress)
* ⬜ Basic query clauses (MATCH, WHERE, RETURN)
* ⬜ String generation
* ⬜ Advanced Cypher features
* ⬜ Documentation and examples

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
