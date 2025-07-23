#!/usr/bin/env python3
"""Debug script to test Athena ingestion"""

import asyncio
import httpx
import json
from pathlib import Path

TEKTON_ROOT = Path(__file__).parent
LANDMARKS_DATA = TEKTON_ROOT / "landmarks" / "data"
ATHENA_API = "http://localhost:8005/api/v1"

async def test_athena_connection():
    """Test basic Athena connectivity"""
    print("Testing Athena connection...")
    
    async with httpx.AsyncClient() as client:
        # Test root
        try:
            resp = await client.get("http://localhost:8005/")
            print(f"Root endpoint: {resp.status_code}")
        except Exception as e:
            print(f"Root endpoint error: {e}")
            
        # Test knowledge endpoint
        try:
            resp = await client.get(f"{ATHENA_API}/knowledge")
            print(f"Knowledge endpoint: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                print(f"  Entities: {data.get('entity_count', 0)}")
                print(f"  Relationships: {data.get('relationship_count', 0)}")
        except Exception as e:
            print(f"Knowledge endpoint error: {e}")
            
        # Test entities endpoint
        try:
            resp = await client.get(f"{ATHENA_API}/entities")
            print(f"Entities endpoint: {resp.status_code}")
            if resp.status_code == 200:
                entities = resp.json()
                print(f"  Found {len(entities)} entities")
        except Exception as e:
            print(f"Entities endpoint error: {e}")

async def test_create_entity():
    """Test creating a simple entity"""
    print("\nTesting entity creation...")
    
    test_entity = {
        "name": "Test Component",
        "entity_type": "component",
        "properties": {
            "description": "A test component",
            "port": 9999
        }
    }
    
    async with httpx.AsyncClient() as client:
        try:
            # Try the correct endpoint
            resp = await client.post(
                f"{ATHENA_API}/entities",
                json=test_entity
            )
            print(f"Create entity response: {resp.status_code}")
            if resp.status_code == 200:
                result = resp.json()
                print(f"  Created entity ID: {result.get('id', 'unknown')}")
                return result.get('id')
            else:
                print(f"  Error: {resp.text}")
        except Exception as e:
            print(f"Create entity error: {e}")
    
    return None

async def check_landmarks():
    """Check if landmark files exist"""
    print("\nChecking landmark files...")
    
    registry_file = LANDMARKS_DATA / "registry.json"
    if not registry_file.exists():
        print("No registry.json found!")
        return
        
    with open(registry_file) as f:
        registry = json.load(f)
        
    landmark_ids = registry.get("landmark_ids", [])
    print(f"Found {len(landmark_ids)} landmarks in registry")
    
    # Check first few landmark files
    existing = 0
    for i, lid in enumerate(landmark_ids[:5]):
        landmark_file = LANDMARKS_DATA / f"{lid}.json"
        if landmark_file.exists():
            existing += 1
            with open(landmark_file) as f:
                lm = json.load(f)
                print(f"  - {lm.get('title', 'Unknown')} ({lm.get('type', 'unknown')})")
    
    print(f"Verified {existing} landmark files exist")

async def main():
    await test_athena_connection()
    entity_id = await test_create_entity()
    await check_landmarks()

if __name__ == "__main__":
    asyncio.run(main())