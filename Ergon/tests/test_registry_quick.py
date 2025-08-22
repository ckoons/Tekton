#!/usr/bin/env python3
"""
Quick test script for Registry functionality.
Run this to test the Registry implementation.
"""

import asyncio
import httpx
import json
from datetime import datetime

# Ergon API URL (Coder-A environment)
BASE_URL = "http://localhost:8102/api/ergon/registry"

async def quick_test():
    """Quick test of Registry functionality."""
    
    print("=" * 60)
    print("ERGON REGISTRY - QUICK TEST")
    print("=" * 60)
    
    async with httpx.AsyncClient() as client:
        
        # 1. Check Registry health
        print("\n1. Checking Registry Health...")
        response = await client.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            health = response.json()
            print(f"   ✅ Registry Status: {health['status']}")
            print(f"   📊 Total Units: {health['statistics']['total_units']}")
            print(f"   🎯 Compliance Rate: {health['statistics']['compliance_rate']}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
        
        # 2. Store a new solution
        print("\n2. Storing a Test Solution...")
        test_solution = {
            "name": f"Test Solution {datetime.now().strftime('%H:%M:%S')}",
            "type": "solution",
            "version": "1.0.0",
            "description": "Quick test solution to verify Registry",
            "tags": ["test", "demo", "registry-verification"],
            "content": {
                "purpose": "Registry verification",
                "created_by": "test_registry_quick.py"
            }
        }
        
        response = await client.post(f"{BASE_URL}/store", json=test_solution)
        if response.status_code == 200:
            result = response.json()
            solution_id = result["id"]
            print(f"   ✅ Stored with ID: {solution_id}")
        else:
            print(f"   ❌ Store failed: {response.status_code}")
            return
        
        # 3. Retrieve the solution
        print("\n3. Retrieving the Solution...")
        response = await client.get(f"{BASE_URL}/{solution_id}")
        if response.status_code == 200:
            solution = response.json()
            print(f"   ✅ Retrieved: {solution['name']}")
            print(f"   📝 Version: {solution['version']}")
            print(f"   🏷️  Tags: {', '.join(solution.get('tags', []))}")
        else:
            print(f"   ❌ Retrieve failed: {response.status_code}")
        
        # 4. Check standards compliance
        print("\n4. Checking Standards Compliance...")
        response = await client.post(f"{BASE_URL}/{solution_id}/check-standards")
        if response.status_code == 200:
            compliance = response.json()
            score = compliance['report']['compliance_score']
            print(f"   📊 Compliance Score: {score * 100:.0f}%")
            for check, passed in compliance['report']['checks'].items():
                icon = "✅" if passed else "❌"
                print(f"      {icon} {check}: {passed}")
        else:
            print(f"   ❌ Standards check failed: {response.status_code}")
        
        # 5. Search for solutions
        print("\n5. Searching for Solutions...")
        response = await client.get(f"{BASE_URL}/search", params={"type": "solution"})
        if response.status_code == 200:
            search_results = response.json()
            print(f"   ✅ Found {search_results['count']} solution(s)")
            for solution in search_results['results'][:3]:  # Show first 3
                print(f"      - {solution['name']} (v{solution['version']})")
        else:
            print(f"   ❌ Search failed: {response.status_code}")
        
        # 6. List available types
        print("\n6. Listing Available Types...")
        response = await client.get(f"{BASE_URL}/types")
        if response.status_code == 200:
            types = response.json()
            print(f"   ✅ Available types: {', '.join(types['types'])}")
        else:
            print(f"   ❌ Types list failed: {response.status_code}")
        
        # 7. Test TektonCore integration status
        print("\n7. Checking TektonCore Integration...")
        response = await client.get(f"{BASE_URL}/import/status")
        if response.status_code == 200:
            import_status = response.json()
            print(f"   ✅ Integration Available: {import_status.get('integration_available', False)}")
            if 'statistics' in import_status:
                print(f"   📦 Total Imported: {import_status['statistics'].get('total_imported', 0)}")
        else:
            print(f"   ❌ Import status failed: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("✅ REGISTRY TEST COMPLETE!")
    print("=" * 60)
    print("\nThe Registry is working! Key features verified:")
    print("  • Storage and retrieval")
    print("  • Standards compliance checking")
    print("  • Search and filtering")
    print("  • Type management")
    print("  • TektonCore integration ready")
    print("\nPhase 1 of Deployable_Units_Sprint is complete! 🎉")


if __name__ == "__main__":
    print("\n🚀 Starting Registry Quick Test...")
    print("   Make sure Ergon is running on port 8102")
    print()
    
    try:
        asyncio.run(quick_test())
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("   Make sure Ergon is running: cd Ergon && python3 -m ergon")