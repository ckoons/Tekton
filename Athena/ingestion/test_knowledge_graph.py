#!/usr/bin/env python3
"""
Test script to verify Athena Knowledge Graph is working correctly
"""

import httpx
import json

try:
    from shared.urls import athena_url
    BASE_URL = athena_url("/api/v1")
except ImportError:
    # Fallback if shared module not available
    from shared.env import TektonEnviron
    port = TektonEnviron.get("ATHENA_PORT", "8105")
    BASE_URL = f"http://localhost:{port}/api/v1"

def test_endpoints():
    """Test various Athena endpoints"""
    
    print("Testing Athena Knowledge Graph API...")
    print("=" * 50)
    
    # Test 1: Check stats
    print("\n1. Checking knowledge graph stats:")
    try:
        response = httpx.get(f"{BASE_URL}/knowledge/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✓ Entities: {stats['entity_count']}")
            print(f"   ✓ Relationships: {stats['relationship_count']}")
            print(f"   ✓ Adapter: {stats['adapter_type']}")
        else:
            print(f"   ✗ Failed: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 2: Search for components
    print("\n2. Searching for component entities:")
    try:
        response = httpx.get(f"{BASE_URL}/entities?entity_type=component&limit=5", 
                           follow_redirects=True)
        if response.status_code == 200:
            entities = response.json()
            print(f"   ✓ Found {len(entities)} components:")
            for entity in entities[:5]:
                print(f"     - {entity['name']} (ID: {entity['entityId']})")
        else:
            print(f"   ✗ Failed: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 3: Search for landmarks
    print("\n3. Searching for landmark entities:")
    try:
        response = httpx.get(f"{BASE_URL}/entities?query=landmark&limit=3", 
                           follow_redirects=True)
        if response.status_code == 200:
            entities = response.json()
            print(f"   ✓ Found {len(entities)} landmarks")
            for entity in entities[:3]:
                print(f"     - {entity['name']} ({entity['entityType']})")
        else:
            print(f"   ✗ Failed: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 4: Query example
    print("\n4. Testing query - finding architectural decisions:")
    try:
        response = httpx.get(f"{BASE_URL}/entities?entity_type=landmark_architectural_decision&limit=3",
                           follow_redirects=True)
        if response.status_code == 200:
            entities = response.json()
            print(f"   ✓ Found {len(entities)} architectural decisions:")
            for entity in entities[:3]:
                print(f"     - {entity['name']}")
                if 'properties' in entity and 'description' in entity['properties']:
                    print(f"       {entity['properties']['description'][:80]}...")
        else:
            print(f"   ✗ Failed: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Knowledge Graph API test complete!")


if __name__ == "__main__":
    test_endpoints()