"""
Hermes API - Client library and REST API for Hermes services.

This module provides client libraries and REST API endpoints for Tekton 
components to interact with Hermes services, including registration, 
messaging, and database access.
"""

from hermes.api.client import HermesClient
from hermes.api.app import app, run_server
from hermes.api.database_client import DatabaseClient

__all__ = ["HermesClient", "DatabaseClient", "app", "run_server"]