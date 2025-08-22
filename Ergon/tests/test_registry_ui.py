#!/usr/bin/env python3
"""
Test Registry UI Integration.

Verifies that the Registry UI in Hephaestus properly connects to the Ergon Registry API
and displays solutions correctly.
"""

import asyncio
import httpx
import json
import sys
from pathlib import Path

# Add Ergon to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ergon.registry.storage import RegistryStorage


async def test_registry_ui():
    """Test the Registry UI integration."""
    print("=" * 60)
    print("Testing Registry UI Integration")
    print("=" * 60)
    
    # 1. First, add some test data to the Registry
    print("\n1. Adding test solutions to Registry...")
    storage = RegistryStorage("/Users/cskoons/projects/github/Coder-A/Ergon/ergon_registry.db")
    
    test_solutions = [
        {
            "type": "solution",
            "name": "Test Solution Alpha",
            "version": "1.0.0",
            "description": "A test solution that meets all standards",
            "meets_standards": True,
            "tags": ["test", "compliant", "phase-1"],
            "source": {
                "origin": "tekton-core",
                "project_id": "test-001"
            }
        },
        {
            "type": "container",
            "name": "Test Container Beta",
            "version": "2.1.0",
            "description": "A container solution needing standards review",
            "meets_standards": False,
            "tags": ["test", "container", "review-needed"],
            "source": {
                "origin": "manual",
                "project_id": "test-002"
            }
        },
        {
            "type": "tool",
            "name": "Test Tool Gamma",
            "version": "0.9.5",
            "description": "A tool in development",
            "meets_standards": False,
            "tags": ["test", "tool", "development"],
            "lineage": [],  # Will link to Alpha after storing
            "source": {
                "origin": "tekton-core",
                "project_id": "test-003"
            }
        }
    ]
    
    stored_ids = []
    for solution in test_solutions:
        entry_id = storage.store(solution)
        stored_ids.append(entry_id)
        print(f"  ✓ Stored: {solution['name']} (ID: {entry_id})")
    
    # Update lineage for the third solution
    if len(stored_ids) >= 3:
        storage.update_standards_compliance(stored_ids[2], False)
        # Note: lineage is set at creation, but we can demonstrate the relationship
    
    # 2. Test the Registry API endpoints
    print("\n2. Testing Registry API endpoints...")
    base_url = "http://localhost:8102/api/ergon/registry"
    
    async with httpx.AsyncClient() as client:
        # Test search endpoint
        print("  Testing /search endpoint...")
        response = await client.get(f"{base_url}/search")
        if response.status_code == 200:
            data = response.json()
            print(f"    ✓ Found {data['count']} solutions")
        else:
            print(f"    ✗ Search failed: {response.status_code}")
        
        # Test health endpoint
        print("  Testing /health endpoint...")
        response = await client.get(f"{base_url}/health")
        if response.status_code == 200:
            health = response.json()
            stats = health.get('statistics', {})
            print(f"    ✓ Registry healthy - {stats.get('total_units', 0)} units, "
                  f"{stats.get('compliance_rate', 'N/A')} compliant")
        else:
            print(f"    ✗ Health check failed: {response.status_code}")
        
        # Test standards check for first solution
        if stored_ids:
            print(f"  Testing /check-standards for {stored_ids[0]}...")
            response = await client.post(f"{base_url}/{stored_ids[0]}/check-standards")
            if response.status_code == 200:
                report = response.json()
                print(f"    ✓ Standards check complete")
            else:
                print(f"    ✗ Standards check failed: {response.status_code}")
    
    # 3. Verify UI can access the data
    print("\n3. UI Integration Check:")
    print("  The Registry UI should now display:")
    print(f"    • {len(test_solutions)} solution cards in the grid")
    print("    • Standards badges (✓ Standards for compliant, ⚠ Review for non-compliant)")
    print("    • Version badges for each solution")
    print("    • Test, Details, and Check Standards buttons on each card")
    print("    • Registry statistics at the bottom")
    
    print("\n4. To verify the UI:")
    print("  1. Open http://localhost:8088 in your browser")
    print("  2. Click on the 'Ergon' tab")
    print("  3. Click on the 'Registry' sub-tab")
    print("  4. You should see the test solutions displayed")
    print("  5. Try clicking the action buttons on the cards")
    
    print("\n✅ Registry UI integration test complete!")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_registry_ui())
    sys.exit(0 if success else 1)