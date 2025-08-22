#!/usr/bin/env python3
"""
Test the integrated Construct system with a sample composition.
"""

import asyncio
import json
import logging
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ergon.construct.integration import ConstructSystem

logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_composition():
    """Test creating a composition through the integrated system."""
    
    # Initialize the integrated system
    logger.info("Initializing Construct system...")
    construct = ConstructSystem()
    
    # Sample composition request from Ani
    request = {
        "action": "compose",
        "sender_id": "test-ci",
        "name": "API with database",
        "components": [
            {
                "registry_id": "46815e41-bd52-4213-a718-f11ff8a7d78d",
                "alias": "api",
                "config": {"port": 8080}
            },
            {
                "registry_id": "8a819b9b-0aca-4762-83f4-d555773d275f", 
                "alias": "database",
                "config": {"type": "postgres"}
            }
        ],
        "connections": [
            {
                "from": "api.output",
                "to": "database.input",
                "protocol": "sql"
            }
        ],
        "constraints": {
            "max_memory": "2GB",
            "environment": "development"
        }
    }
    
    logger.info("=" * 60)
    logger.info("Testing COMPOSE operation")
    logger.info("=" * 60)
    
    # Process the composition request
    result = await construct.process_json(request)
    
    logger.info(f"Compose result: {json.dumps(result, indent=2)}")
    
    if result.get('status') == 'success' and result.get('workspace_id'):
        workspace_id = result['workspace_id']
        logger.info(f"✓ Workspace created: {workspace_id}")
        
        # Check persistence
        workspace = construct.get_workspace(workspace_id)
        if workspace:
            logger.info(f"✓ Workspace persisted to state")
            logger.info(f"  Status: {workspace.get('status')}")
            logger.info(f"  Components: {len(workspace['composition']['components'])}")
            logger.info(f"  Connections: {len(workspace['composition']['connections'])}")
        
        # Test VALIDATE operation
        logger.info("=" * 60)
        logger.info("Testing VALIDATE operation")
        logger.info("=" * 60)
        
        validate_request = {
            "action": "validate",
            "workspace_id": workspace_id,
            "sender_id": "test-ci",
            "checks": ["connections", "dependencies", "resources"]
        }
        
        validate_result = await construct.process_json(validate_request)
        logger.info(f"Validate result: {json.dumps(validate_result, indent=2)}")
        
        if 'validation' in validate_result:
            validation = validate_result['validation']
            if 'scores' in validation:
                logger.info("Connection compatibility scores:")
                for conn, score in validation['scores'].items():
                    logger.info(f"  {conn}: {score}")
        
        # Test workspace listing
        logger.info("=" * 60)
        logger.info("Testing workspace listing")
        logger.info("=" * 60)
        
        workspaces = construct.list_workspaces(ci_id="test-ci")
        logger.info(f"Found {len(workspaces)} workspace(s) for test-ci")
        for ws in workspaces:
            logger.info(f"  - {ws['workspace_id']}: {ws['status']}")
        
        # Test component suggestions
        logger.info("=" * 60)
        logger.info("Testing component suggestions")
        logger.info("=" * 60)
        
        suggestions = await construct.suggest_components("I need an API with storage and authentication")
        logger.info(f"Suggestions: {json.dumps(suggestions, indent=2)}")
        
        # Test PUBLISH operation (would need real Registry entries)
        logger.info("=" * 60)
        logger.info("Testing PUBLISH operation")
        logger.info("=" * 60)
        
        publish_request = {
            "action": "publish",
            "workspace_id": workspace_id,
            "sender_id": "test-ci",
            "metadata": {
                "name": "test-api-db-solution",
                "version": "1.0.0",
                "description": "Test API with database composition",
                "tags": ["test", "api", "database"]
            },
            "options": {
                "auto_test": False,  # Skip for now since components don't exist
                "check_standards": True
            }
        }
        
        publish_result = await construct.process_json(publish_request)
        logger.info(f"Publish result: {json.dumps(publish_result, indent=2)}")
        
    else:
        logger.error("Composition failed!")
        
    logger.info("=" * 60)
    logger.info("Test complete!")
    

async def test_chat_interface():
    """Test the bilingual chat interface."""
    logger.info("=" * 60)
    logger.info("Testing chat interface")
    logger.info("=" * 60)
    
    construct = ConstructSystem()
    
    # Test JSON detection
    json_message = json.dumps({
        "action": "compose",
        "components": []
    })
    
    response = await construct.process(json_message, "test-ci")
    logger.info(f"JSON response: {response}")
    
    # Test natural language
    text_message = "Create a new composition with an API and database"
    response = await construct.process(text_message, "human-user")
    logger.info(f"Text response: {response}")


if __name__ == "__main__":
    # Run tests
    asyncio.run(test_composition())
    # asyncio.run(test_chat_interface())