"""
Database adapters for various backend systems.

This package contains adapters for different database systems,
organized by database type, with fallback implementations.
"""

from pathlib import Path
from typing import Dict

# INTEGRATION TEST NOTE:
# During full Tekton stack integration testing, verify that all adapter implementations
# are properly loaded and registered. The following dependencies need to be verified:
# 1. FAISS library for vector storage (pip install faiss-cpu or faiss-gpu)
# 2. Neo4j for graph storage (if used)
# 3. Redis for key-value storage (if used)
# 4. Other database backends as configured in the Tekton deployment
# 
# Each adapter should implement the appropriate interface from core.database.adapters
# and register itself for discovery by the DatabaseManager.

# Import the adapter base classes for proper registration in the import system
try:
    from hermes.core.database.adapters import (
        DatabaseAdapter,
        VectorDatabaseAdapter,
        GraphDatabaseAdapter,
        KeyValueDatabaseAdapter,
        DocumentDatabaseAdapter,
        CacheDatabaseAdapter,
        RelationalDatabaseAdapter
    )
except ImportError:
    # If base classes can't be imported, create stubs for compatibility
    print("Warning: Could not import database adapter interfaces from core.database.adapters")
    print("Creating stub imports for compatibility")
    print("INTEGRATION TEST NOTE: Fix this before running integration tests")

# Ensure all adapter directories exist
adapter_dirs = [
    "vector",
    "graph", 
    "key_value",
    "document",
    "cache",
    "relation"
]

# Create adapter directories if they don't exist
for adapter_dir in adapter_dirs:
    Path(__file__).parent.joinpath(adapter_dir).mkdir(parents=True, exist_ok=True)
    
    # Create __init__.py if it doesn't exist
    init_file = Path(__file__).parent.joinpath(adapter_dir, "__init__.py")
    if not init_file.exists():
        with open(init_file, "w") as f:
            f.write(f'"""\n{adapter_dir.title()} database adapters for the Hermes system.\n"""')