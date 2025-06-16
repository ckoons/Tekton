"""
Graph Database Adapters - Implementations for graph databases.

This package contains concrete implementations of the GraphDatabaseAdapter interface
for various graph database backends.
"""

# INTEGRATION TEST NOTE:
# During full Tekton stack integration testing, verify the following graph database
# implementations and their dependencies:
#
# 1. Neo4j Adapter (neo4j_adapter.py)
#    - Requires: pip install neo4j
#    - Configuration: Neo4j server URL, authentication credentials
#    - Used for knowledge representation and complex relationship queries
#
# 2. NetworkX Adapter (for in-memory graphs)
#    - Requires: pip install networkx
#    - Useful for temporary graph operations or small datasets
#
# 3. Additional potential graph databases to consider:
#    - Amazon Neptune
#    - DGraph
#    - TigerGraph
#
# The graph database is critical for Tekton's knowledge representation capabilities
# and should be thoroughly tested during integration.

# Re-export adapters for simplified imports
# (No adapters to export yet, need to create neo4j_adapter.py and other implementations)