"""
Register Athena capabilities with Hermes service registry.

This script registers enhanced LightRAG-inspired capabilities with the Hermes
service registry to make them available to other Tekton components.
"""

import os
import asyncio
import logging
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("athena.register_capabilities")

try:
    from hermes.api.client import HermesClient
except ImportError:
    logger.warning("Hermes client not available, using mock client")
    
    class HermesClient:
        """Mock Hermes client for testing."""
        
        async def register_component(self, *args, **kwargs) -> Dict[str, Any]:
            """Mock register component."""
            logger.info(f"Mock registering component: {args} {kwargs}")
            return {"success": True, "id": "mock-id"}
            
        async def register_capability(self, *args, **kwargs) -> Dict[str, Any]:
            """Mock register capability."""
            logger.info(f"Mock registering capability: {args} {kwargs}")
            return {"success": True, "id": "mock-id"}

HERMES_URL = os.environ.get("HERMES_URL", "http://localhost:8000")

async def register_capabilities():
    """Register Athena capabilities with Hermes."""
    client = HermesClient(HERMES_URL)
    
    # Register component
    component_response = await client.register_component(
        name="athena",
        description="Knowledge graph service with enhanced retrieval capabilities inspired by LightRAG",
        version="1.0.0",
        base_url=os.environ.get("ATHENA_URL", "http://localhost:8001")
    )
    
    logger.info(f"Component registration: {component_response}")
    
    # Register capabilities
    capabilities = [
        # Query modes
        {
            "name": "query_naive",
            "description": "Simple keyword-based search without advanced knowledge graph integration",
            "type": "query",
            "endpoint": "/query",
            "parameters": {
                "mode": "naive"
            }
        },
        {
            "name": "query_local",
            "description": "Entity-focused retrieval that prioritizes relevant entities",
            "type": "query",
            "endpoint": "/query",
            "parameters": {
                "mode": "local"
            }
        },
        {
            "name": "query_global",
            "description": "Relationship-focused retrieval for understanding connections",
            "type": "query",
            "endpoint": "/query",
            "parameters": {
                "mode": "global"
            }
        },
        {
            "name": "query_hybrid",
            "description": "Combined entity and relationship retrieval",
            "type": "query",
            "endpoint": "/query",
            "parameters": {
                "mode": "hybrid"
            }
        },
        {
            "name": "query_mix",
            "description": "Integrated graph and vector retrieval (most advanced)",
            "type": "query",
            "endpoint": "/query",
            "parameters": {
                "mode": "mix"
            }
        },
        
        # Entity management
        {
            "name": "entity_merge",
            "description": "Merge multiple entities with configurable strategies",
            "type": "entity_management",
            "endpoint": "/entities/merge",
            "method": "POST"
        },
        {
            "name": "find_duplicates",
            "description": "Find potential duplicate entities in the knowledge graph",
            "type": "entity_management",
            "endpoint": "/entities/duplicates",
            "method": "GET"
        }
    ]
    
    # Register each capability
    for capability in capabilities:
        capability_response = await client.register_capability(
            component_name="athena",
            **capability
        )
        
        logger.info(f"Capability registration ({capability['name']}): {capability_response}")
        
    logger.info("All capabilities registered successfully")

if __name__ == "__main__":
    asyncio.run(register_capabilities())