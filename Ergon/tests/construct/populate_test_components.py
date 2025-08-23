#!/usr/bin/env python3
"""
Populate Registry with test components for Construct system testing.
"""

import sys
import os
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from ergon.registry.storage import RegistryStorage


def populate_test_components():
    """Add test components to Registry."""
    
    storage = RegistryStorage()
    
    # Test components with proper interfaces
    components = [
        {
            "id": "parser-abc123",
            "type": "solution",
            "name": "JSON Parser",
            "version": "1.0.0",
            "content": {
                "description": "Parses JSON data",
                "code": "def parse(data): return json.loads(data)",
                "interfaces": {
                    "inputs": [
                        {"name": "input", "type": "text", "required": True}
                    ],
                    "outputs": [
                        {"name": "output", "type": "json"}
                    ]
                },
                "capabilities": ["parsing", "json"],
                "requirements": {
                    "memory": "512MB",
                    "dependencies": ["json"]
                }
            }
        },
        {
            "id": "analyzer-def456",
            "type": "solution",
            "name": "Data Analyzer",
            "version": "1.0.0",
            "content": {
                "description": "Analyzes structured data",
                "code": "def analyze(data): return {'insights': []}",
                "interfaces": {
                    "inputs": [
                        {"name": "input", "type": "json", "required": True}
                    ],
                    "outputs": [
                        {"name": "results", "type": "json"}
                    ]
                },
                "capabilities": ["analysis", "ml"],
                "requirements": {
                    "memory": "2GB",
                    "dependencies": ["numpy", "pandas"]
                }
            }
        },
        {
            "id": "api-gateway",
            "type": "solution",
            "name": "API Gateway",
            "version": "2.0.0",
            "content": {
                "description": "Routes API requests",
                "interfaces": {
                    "inputs": [
                        {"name": "request", "type": "http"}
                    ],
                    "outputs": [
                        {"name": "response", "type": "http"},
                        {"name": "auth_check", "type": "json"}
                    ]
                },
                "capabilities": ["routing", "api", "gateway"]
            }
        },
        {
            "id": "auth-service",
            "type": "solution",
            "name": "Authentication Service",
            "version": "1.5.0",
            "content": {
                "description": "Handles authentication",
                "interfaces": {
                    "inputs": [
                        {"name": "validate", "type": "json", "required": True}
                    ],
                    "outputs": [
                        {"name": "authorized", "type": "boolean"},
                        {"name": "token", "type": "string"}
                    ]
                },
                "capabilities": ["authentication", "security"]
            }
        }
    ]
    
    print("Populating Registry with test components...")
    
    for comp in components:
        try:
            # Store with explicit ID
            comp_id = comp['id']
            storage.store(comp)
            print(f"✓ Added {comp['name']} ({comp_id})")
        except Exception as e:
            print(f"✗ Failed to add {comp['name']}: {e}")
    
    # Verify
    print("\nVerifying Registry contents...")
    all_entries = storage.search(limit=100)
    print(f"Total entries in Registry: {len(all_entries)}")
    
    for entry in all_entries:
        if entry['id'] in ['parser-abc123', 'analyzer-def456', 'api-gateway', 'auth-service']:
            print(f"  - {entry['name']} ({entry['id'][:8]}...)")


if __name__ == "__main__":
    populate_test_components()
