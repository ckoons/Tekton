#!/usr/bin/env python3
"""
Migrate existing AI registry to unified registry format.

This script reads the existing platform_ai_registry.json and converts it
to the new unified registry format.
"""

import json
import asyncio
from pathlib import Path
import sys

# Add Tekton to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.ai.unified_registry import UnifiedAIRegistry, AISpecialist, AIStatus
from shared.ai.registry_client import AIRegistryClient


async def migrate_registry():
    """Migrate existing registry to unified format."""
    print("Migrating AI registry to unified format...")
    
    # Read existing registry
    existing_path = Path.home() / '.tekton' / 'ai_registry' / 'platform_ai_registry.json'
    
    if not existing_path.exists():
        print(f"No existing registry found at {existing_path}")
        return
    
    with open(existing_path, 'r') as f:
        existing_data = json.load(f)
    
    print(f"Found {len(existing_data)} AIs in existing registry")
    
    # Create unified registry
    registry = UnifiedAIRegistry()
    await registry.start()
    
    # Migrate each AI
    for ai_id, ai_data in existing_data.items():
        try:
            # Extract data
            name = ai_data.get('name', ai_id)
            port = ai_data.get('port', 0)
            host = ai_data.get('host', 'localhost')
            model = ai_data.get('model', 'unknown')
            component = ai_data.get('component', '')
            capabilities = ai_data.get('capabilities', [])
            roles = ai_data.get('roles', [])
            
            # Skip if no port
            if not port:
                print(f"Skipping {ai_id} - no port specified")
                continue
            
            # Register in unified registry
            success = await registry.register(
                ai_id=ai_id,
                name=name,
                port=port,
                host=host,
                model=model,
                component=component,
                capabilities=capabilities,
                roles=roles,
                metadata={
                    'migrated_from': 'platform_ai_registry',
                    'original_data': ai_data
                }
            )
            
            if success:
                print(f"✓ Migrated {ai_id} on port {port}")
            else:
                print(f"✗ Failed to migrate {ai_id}")
                
        except Exception as e:
            print(f"Error migrating {ai_id}: {e}")
    
    # Save and stop
    await registry.stop()
    
    print("\nMigration complete!")
    print(f"Unified registry saved to: ~/.tekton/ai_registry/unified_registry.json")
    
    # Also check current status
    print("\nChecking AI status...")
    specialists = await registry.discover()
    
    healthy = sum(1 for s in specialists if s.status == AIStatus.HEALTHY)
    total = len(specialists)
    
    print(f"Total AIs: {total}")
    print(f"Healthy: {healthy}")
    

if __name__ == "__main__":
    asyncio.run(migrate_registry())