"""
MCP Capabilities - Database capability definitions for MCP protocol.

This module defines the capabilities offered by the Database MCP Adapter,
providing a structured definition of available operations.
"""

from typing import Dict, List, Any


def generate_capabilities() -> Dict[str, Any]:
    """
    Generate the capability manifest for Hermes database services.
    
    Returns:
        A dictionary describing available capabilities
    """
    return {
        # Vector database capabilities
        "vector_store": {
            "description": "Store vectors in the database",
            "parameters": {
                "vectors": {"type": "array", "description": "List of vectors to store"},
                "metadatas": {"type": "array", "description": "List of metadata for the vectors", "optional": True},
                "ids": {"type": "array", "description": "List of IDs for the vectors", "optional": True},
                "namespace": {"type": "string", "description": "Namespace to store vectors in", "default": "default"},
                "backend": {"type": "string", "description": "Vector database backend to use", "optional": True}
            },
            "returns": {"type": "object", "description": "Result of vector storage operation"}
        },
        "vector_search": {
            "description": "Search for vectors in the database",
            "parameters": {
                "query_vector": {"type": "array", "description": "Query vector to search for"},
                "top_k": {"type": "integer", "description": "Number of results to return", "default": 5},
                "namespace": {"type": "string", "description": "Namespace to search in", "default": "default"},
                "filter": {"type": "object", "description": "Metadata filter for search", "optional": True},
                "backend": {"type": "string", "description": "Vector database backend to use", "optional": True}
            },
            "returns": {"type": "object", "description": "Search results with scores and metadata"}
        },
        "vector_delete": {
            "description": "Delete vectors from the database",
            "parameters": {
                "ids": {"type": "array", "description": "List of IDs to delete"},
                "namespace": {"type": "string", "description": "Namespace containing the vectors", "default": "default"},
                "backend": {"type": "string", "description": "Vector database backend to use", "optional": True}
            },
            "returns": {"type": "object", "description": "Result of delete operation"}
        },
        
        # Key-value database capabilities
        "kv_set": {
            "description": "Set a key-value pair in the database",
            "parameters": {
                "key": {"type": "string", "description": "Key to set"},
                "value": {"type": "any", "description": "Value to store"},
                "namespace": {"type": "string", "description": "Namespace for the data", "default": "default"},
                "ttl": {"type": "integer", "description": "Time-to-live in seconds", "optional": True},
                "backend": {"type": "string", "description": "Key-value database backend to use", "optional": True}
            },
            "returns": {"type": "object", "description": "Result of set operation"}
        },
        "kv_get": {
            "description": "Get a value from the database",
            "parameters": {
                "key": {"type": "string", "description": "Key to get"},
                "namespace": {"type": "string", "description": "Namespace for the data", "default": "default"},
                "backend": {"type": "string", "description": "Key-value database backend to use", "optional": True}
            },
            "returns": {"type": "object", "description": "Value associated with the key"}
        },
        "kv_delete": {
            "description": "Delete a key from the database",
            "parameters": {
                "key": {"type": "string", "description": "Key to delete"},
                "namespace": {"type": "string", "description": "Namespace for the data", "default": "default"},
                "backend": {"type": "string", "description": "Key-value database backend to use", "optional": True}
            },
            "returns": {"type": "object", "description": "Result of delete operation"}
        },
        
        # Graph database capabilities
        "graph_add_node": {
            "description": "Add a node to the graph database",
            "parameters": {
                "node_id": {"type": "string", "description": "ID for the node"},
                "labels": {"type": "array", "description": "List of labels for the node"},
                "properties": {"type": "object", "description": "Properties for the node"},
                "namespace": {"type": "string", "description": "Namespace for the data", "default": "default"},
                "backend": {"type": "string", "description": "Graph database backend to use", "optional": True}
            },
            "returns": {"type": "object", "description": "Result of node addition"}
        },
        "graph_add_relationship": {
            "description": "Add a relationship between nodes",
            "parameters": {
                "source_id": {"type": "string", "description": "Source node ID"},
                "target_id": {"type": "string", "description": "Target node ID"},
                "type": {"type": "string", "description": "Relationship type"},
                "properties": {"type": "object", "description": "Properties for the relationship", "optional": True},
                "namespace": {"type": "string", "description": "Namespace for the data", "default": "default"},
                "backend": {"type": "string", "description": "Graph database backend to use", "optional": True}
            },
            "returns": {"type": "object", "description": "Result of relationship addition"}
        },
        "graph_query": {
            "description": "Query the graph database",
            "parameters": {
                "query": {"type": "string", "description": "Query string (Cypher for Neo4j)"},
                "parameters": {"type": "object", "description": "Query parameters", "optional": True},
                "namespace": {"type": "string", "description": "Namespace for the data", "default": "default"},
                "backend": {"type": "string", "description": "Graph database backend to use", "optional": True}
            },
            "returns": {"type": "object", "description": "Query results"}
        },
        
        # Document database capabilities
        "document_insert": {
            "description": "Insert a document into the database",
            "parameters": {
                "collection": {"type": "string", "description": "Collection to insert into"},
                "document": {"type": "object", "description": "Document to insert"},
                "namespace": {"type": "string", "description": "Namespace for the data", "default": "default"},
                "backend": {"type": "string", "description": "Document database backend to use", "optional": True}
            },
            "returns": {"type": "object", "description": "Result of insertion with document ID"}
        },
        "document_find": {
            "description": "Find documents in the database",
            "parameters": {
                "collection": {"type": "string", "description": "Collection to search in"},
                "query": {"type": "object", "description": "Query filter"},
                "limit": {"type": "integer", "description": "Maximum number of results", "default": 10},
                "namespace": {"type": "string", "description": "Namespace for the data", "default": "default"},
                "backend": {"type": "string", "description": "Document database backend to use", "optional": True}
            },
            "returns": {"type": "object", "description": "Documents matching the query"}
        },
        "document_update": {
            "description": "Update documents in the database",
            "parameters": {
                "collection": {"type": "string", "description": "Collection to update in"},
                "query": {"type": "object", "description": "Query filter for documents to update"},
                "update": {"type": "object", "description": "Update operations to apply"},
                "namespace": {"type": "string", "description": "Namespace for the data", "default": "default"},
                "backend": {"type": "string", "description": "Document database backend to use", "optional": True}
            },
            "returns": {"type": "object", "description": "Result of update operation"}
        },
        
        # Cache database capabilities
        "cache_set": {
            "description": "Set a value in the cache",
            "parameters": {
                "key": {"type": "string", "description": "Key to set"},
                "value": {"type": "any", "description": "Value to cache"},
                "ttl": {"type": "integer", "description": "Time-to-live in seconds", "default": 3600},
                "namespace": {"type": "string", "description": "Namespace for the data", "default": "default"},
                "backend": {"type": "string", "description": "Cache backend to use", "optional": True}
            },
            "returns": {"type": "object", "description": "Result of cache set operation"}
        },
        "cache_get": {
            "description": "Get a value from the cache",
            "parameters": {
                "key": {"type": "string", "description": "Key to get"},
                "namespace": {"type": "string", "description": "Namespace for the data", "default": "default"},
                "backend": {"type": "string", "description": "Cache backend to use", "optional": True}
            },
            "returns": {"type": "object", "description": "Cached value if available"}
        },
        
        # Relational database capabilities
        "sql_execute": {
            "description": "Execute SQL query on the database",
            "parameters": {
                "query": {"type": "string", "description": "SQL query to execute"},
                "parameters": {"type": "array", "description": "Query parameters", "optional": True},
                "namespace": {"type": "string", "description": "Namespace for the data", "default": "default"},
                "backend": {"type": "string", "description": "Relational database backend to use", "optional": True}
            },
            "returns": {"type": "object", "description": "Query results"}
        }
    }