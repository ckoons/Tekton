#!/usr/bin/env python3
"""
Set up test data in Registry for integration testing.
"""

import sys
from pathlib import Path
import uuid

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ergon.registry.storage import RegistryStorage


def setup_test_components():
    """Create test components in Registry."""
    
    # Initialize Registry
    registry = RegistryStorage()
    
    # Create test API component
    api_component = {
        'type': 'container',
        'name': 'Test API Service',
        'version': '1.0.0',
        'description': 'Test REST API service',
        'meets_standards': True,
        'lineage': [],
        'source': {
            'origin': 'test',
            'author': 'test-setup'
        },
        'content': {
            'interfaces': [
                {
                    'name': 'input',
                    'type': 'http',
                    'schema': {'port': 8080},
                    'direction': 'input'
                },
                {
                    'name': 'output',
                    'type': 'sql',
                    'schema': {'protocol': 'postgres'},
                    'direction': 'output'
                }
            ],
            'requirements': {
                'memory': '256MB',
                'cpu': '0.5'
            },
            'capabilities': ['api', 'rest', 'http']
        },
        'tags': ['api', 'test']
    }
    
    # Create test database component
    db_component = {
        'type': 'container',
        'name': 'Test Database',
        'version': '1.0.0',
        'description': 'Test PostgreSQL database',
        'meets_standards': True,
        'lineage': [],
        'source': {
            'origin': 'test',
            'author': 'test-setup'
        },
        'content': {
            'interfaces': [
                {
                    'name': 'input',
                    'type': 'sql',
                    'schema': {'protocol': 'postgres'},
                    'direction': 'input'
                },
                {
                    'name': 'query',
                    'type': 'sql',
                    'schema': {'protocol': 'postgres'},
                    'direction': 'bidirectional'
                }
            ],
            'requirements': {
                'memory': '512MB',
                'cpu': '1.0',
                'disk': '10GB'
            },
            'capabilities': ['storage', 'database', 'postgres', 'sql']
        },
        'tags': ['database', 'storage', 'test']
    }
    
    # Store new entries and get their IDs
    api_id = registry.store(api_component)
    db_id = registry.store(db_component)
    
    print(f"Created test API component: {api_id}")
    print(f"Created test DB component: {db_id}")
    
    # Verify they're stored
    api_check = registry.retrieve(api_id)
    db_check = registry.retrieve(db_id)
    
    if api_check and db_check:
        print("✓ Test components successfully stored in Registry")
    else:
        print("✗ Failed to store test components")
    
    return api_id, db_id


if __name__ == "__main__":
    setup_test_components()