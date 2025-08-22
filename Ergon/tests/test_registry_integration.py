#!/usr/bin/env python3
"""
Integration test for Registry API endpoints.
Tests the full stack: API -> Schema -> Storage
"""

import asyncio
import httpx
import json
from datetime import datetime

# Base URL for Ergon API (Coder-A environment uses port 8102)
BASE_URL = "http://localhost:8102/api/ergon/registry"


async def test_registry_integration():
    """Test Registry API endpoints with schema validation."""
    
    print("Testing Registry API Integration...")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        
        # Test 1: Store a valid deployable unit
        print("\n1. Testing POST /store with valid data...")
        valid_unit = {
            "type": "container",
            "version": "1.0.0",
            "name": "nginx-web-server",
            "meets_standards": True,
            "source": {
                "project_id": "tekton-proj-001",
                "sprint_id": "deploy-sprint-001",
                "location": "github.com/tekton/solutions"
            },
            "content": {
                "dockerfile": "FROM nginx:alpine",
                "config": {
                    "port": 80,
                    "ssl": False
                },
                "documentation": "Production-ready nginx container",
                "tests": ["test_container.py", "test_endpoints.py"]
            }
        }
        
        response = await client.post(f"{BASE_URL}/store", json=valid_unit)
        if response.status_code == 200:
            data = response.json()
            unit_id = data["id"]
            print(f"   ✅ Stored unit with ID: {unit_id}")
        else:
            print(f"   ❌ Failed: {response.status_code} - {response.text}")
            return
        
        # Test 2: Retrieve the stored unit
        print("\n2. Testing GET /{id}...")
        response = await client.get(f"{BASE_URL}/{unit_id}")
        if response.status_code == 200:
            retrieved = response.json()
            print(f"   ✅ Retrieved: {retrieved['name']} v{retrieved['version']}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
        
        # Test 3: Search with filters
        print("\n3. Testing GET /search with filters...")
        response = await client.get(f"{BASE_URL}/search", params={
            "type": "container",
            "meets_standards": True
        })
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Found {data['count']} matching unit(s)")
        else:
            print(f"   ❌ Failed: {response.status_code}")
        
        # Test 4: List types
        print("\n4. Testing GET /types...")
        response = await client.get(f"{BASE_URL}/types")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Available types: {data['types']}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
        
        # Test 5: Check standards
        print("\n5. Testing POST /{id}/check-standards...")
        response = await client.post(f"{BASE_URL}/{unit_id}/check-standards")
        if response.status_code == 200:
            data = response.json()
            report = data["report"]
            print(f"   ✅ Compliance score: {report['compliance_score']:.0%}")
            print(f"      - Has documentation: {report['checks']['has_documentation']}")
            print(f"      - Has tests: {report['checks']['has_tests']}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
        
        # Test 6: Store a derived unit with lineage
        print("\n6. Testing lineage with derived unit...")
        derived_unit = {
            "type": "container",
            "version": "1.1.0",
            "name": "nginx-web-server-enhanced",
            "meets_standards": False,
            "lineage": [unit_id],
            "source": {
                "project_id": "tekton-proj-002",
                "sprint_id": "refactor-sprint-001",
                "location": "github.com/tekton/solutions"
            },
            "content": {
                "dockerfile": "FROM nginx:alpine\nRUN apk add --no-cache curl",
                "config": {
                    "port": 443,
                    "ssl": True
                }
            }
        }
        
        response = await client.post(f"{BASE_URL}/store", json=derived_unit)
        if response.status_code == 200:
            derived_id = response.json()["id"]
            print(f"   ✅ Stored derived unit: {derived_id}")
            
            # Get lineage
            response = await client.get(f"{BASE_URL}/{derived_id}/lineage")
            if response.status_code == 200:
                lineage_data = response.json()
                print(f"   ✅ Lineage depth: {lineage_data['depth']}")
                if lineage_data['lineage']:
                    print(f"      Parent: {lineage_data['lineage'][0]['name']}")
        else:
            print(f"   ❌ Failed to store derived unit: {response.status_code}")
        
        # Test 7: Health check
        print("\n7. Testing GET /health...")
        response = await client.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"   ✅ Registry status: {health['status']}")
            if 'statistics' in health:
                stats = health['statistics']
                print(f"      Total units: {stats['total_units']}")
                print(f"      Compliance rate: {stats['compliance_rate']}")
        else:
            print(f"   ❌ Failed: {response.status_code}")
        
        # Test 8: Delete (with safeguards)
        print("\n8. Testing DELETE with safeguards...")
        # Try to delete parent (should fail due to dependent)
        response = await client.delete(f"{BASE_URL}/{unit_id}")
        if response.status_code == 409:
            print(f"   ✅ Safeguard working: Cannot delete unit with dependents")
        else:
            print(f"   ❌ Safeguard failed: {response.status_code}")
        
        # Delete derived first
        if 'derived_id' in locals():
            response = await client.delete(f"{BASE_URL}/{derived_id}")
            if response.status_code == 200:
                print(f"   ✅ Deleted derived unit")
        
        # Now delete parent
        response = await client.delete(f"{BASE_URL}/{unit_id}")
        if response.status_code == 200:
            print(f"   ✅ Deleted parent unit")
        
        print("\n" + "=" * 50)
        print("✅ Registry API Integration Test Complete!")


if __name__ == "__main__":
    print("\n⚠️  Make sure Ergon is running on port 8102 before running this test!")
    print("   Run: cd /Users/cskoons/projects/github/Coder-A/Ergon && python -m ergon")
    print("\nStarting tests...")
    
    asyncio.run(test_registry_integration())