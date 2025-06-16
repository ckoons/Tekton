"""
Database API Package - REST API for Hermes Database Services.

This package provides a RESTful API for accessing Hermes database services,
including vector, graph, key-value, document, cache, and relational databases.
It also includes client libraries for easy integration.
"""

from fastapi import APIRouter
from hermes.api.database.routes import router

# Export router for use in main API
api_router = router

# Export client components for direct import
from hermes.api.database.client_base import BaseRequest
from hermes.api.database.vector_client import VectorDatabaseClient
from hermes.api.database.key_value_client import KeyValueDatabaseClient
from hermes.api.database.graph_client import GraphDatabaseClient
from hermes.api.database.document_client import DocumentDatabaseClient
from hermes.api.database.cache_client import CacheDatabaseClient
from hermes.api.database.relation_client import RelationalDatabaseClient