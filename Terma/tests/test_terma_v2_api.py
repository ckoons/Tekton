#!/usr/bin/env python3
"""
Test the new Terma v2 API - Clean native terminal orchestrator
"""

import httpx
import asyncio
import json
from datetime import datetime


async def test_terma_v2():
    """Test the clean Terma v2 API."""
    print("🧪 Testing Terma v2 - Native Terminal Orchestrator")
    print("=" * 60)
    
    base_url = "http://localhost:8004"
    
    async with httpx.AsyncClient() as client:
        # 1. Health Check
        print("\n1️⃣ Health Check")
        try:
            response = await client.get(f"{base_url}/health")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Service: {data.get('service', 'unknown')}")
                print(f"   Version: {data.get('version', 'unknown')}")
                print(f"   Platform: {data.get('platform', 'unknown')}")
                print(f"   Terminals available: {data.get('terminals_available', 0)}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            print("\n💡 Start Terma v2 with: cd Tekton/Terma && ./run_terma_v2.sh")
            return
        
        # 2. Discovery
        print("\n2️⃣ Service Discovery")
        try:
            response = await client.get(f"{base_url}/discovery")
            if response.status_code == 200:
                data = response.json()
                print(f"   Name: {data.get('name')}")
                print(f"   Description: {data.get('description')}")
                print(f"   Capabilities: {', '.join(data.get('capabilities', []))}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # 3. Terminal Types
        print("\n3️⃣ Available Terminal Types")
        try:
            response = await client.get(f"{base_url}/api/terminals/types")
            if response.status_code == 200:
                terminals = response.json()
                for term in terminals:
                    default = " ⭐" if term.get('is_default') else ""
                    print(f"   • {term['id']} - {term['display_name']}{default}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # 4. Templates
        print("\n4️⃣ Configuration Templates")
        try:
            response = await client.get(f"{base_url}/api/terminals/templates")
            if response.status_code == 200:
                templates = response.json()
                for name, info in templates.items():
                    print(f"   • {name}: {info['name']}")
                    if info.get('purpose'):
                        print(f"     Purpose: {info['purpose']}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # 5. Active Terminals
        print("\n5️⃣ Active Terminals")
        try:
            response = await client.get(f"{base_url}/api/terminals")
            if response.status_code == 200:
                data = response.json()
                print(f"   Count: {data['count']}")
                for term in data['terminals']:
                    print(f"   • PID {term['pid']}: {term['app']} - {term['status']}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # 6. Test Launch (dry run - don't actually launch)
        print("\n6️⃣ Launch Test (dry run)")
        print("   POST /api/terminals/launch")
        print("   Body: {")
        print('     "template": "development",')
        print('     "purpose": "Test launch from API"')
        print("   }")
        print("   (Not executing to avoid opening terminals)")
    
    print("\n" + "=" * 60)
    print("✅ Terma v2 API test complete!")
    print("\n📝 Key Differences from Old Terma:")
    print("   • No /api/sessions endpoints (no PTY sessions)")
    print("   • No WebSocket endpoints (no web terminals)")
    print("   • Only native terminal management")
    print("   • Clean, focused API")


async def main():
    """Run the test."""
    await test_terma_v2()


if __name__ == "__main__":
    asyncio.run(main())