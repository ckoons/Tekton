#!/usr/bin/env python3
"""
Test script to verify Rhetor integration across all components.

This script tests that:
1. RhetorClient can be imported and initialized
2. Each component can communicate with Rhetor
3. Model selection works through Rhetor
"""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from shared.rhetor_client import RhetorClient


async def test_rhetor_client():
    """Test basic RhetorClient functionality."""
    print("Testing RhetorClient...")
    
    # Test different components
    components = ["metis", "sophia", "prometheus", "engram", "synthesis"]
    
    for component in components:
        print(f"\n--- Testing {component} ---")
        
        try:
            client = RhetorClient(component=component)
            
            # Test basic generation
            response = await client.generate(
                prompt="Test prompt",
                capability="reasoning",
                max_tokens=10
            )
            
            print(f"✓ {component}: Basic generation works")
            print(f"  Response preview: {response[:50]}..." if len(response) > 50 else f"  Response: {response}")
            
        except Exception as e:
            print(f"✗ {component}: Error - {e}")
    
    print("\n--- Testing specialized methods ---")
    
    # Test task decomposition
    try:
        client = RhetorClient(component="metis")
        result = await client.decompose_task(
            task_title="Test Task",
            task_description="This is a test task",
            max_subtasks=3
        )
        print(f"✓ Task decomposition: {result.get('success')}")
        if result.get('subtasks'):
            print(f"  Generated {len(result['subtasks'])} subtasks")
    except Exception as e:
        print(f"✗ Task decomposition: Error - {e}")
    
    # Test analysis
    try:
        client = RhetorClient(component="sophia")
        result = await client.analyze(
            data={"metric1": 100, "metric2": 200},
            analysis_type="performance"
        )
        print(f"✓ Analysis: Success")
        print(f"  Analysis keys: {list(result.keys())}")
    except Exception as e:
        print(f"✗ Analysis: Error - {e}")


async def test_component_imports():
    """Test that components can import and use RhetorClient."""
    print("\nTesting component imports...")
    
    test_cases = [
        ("Metis", "from Metis.metis.core.task_decomposer import TaskDecomposer"),
        ("Sophia", "from Sophia.sophia.core.recommendation_system import RecommendationStatus"),
        ("Prometheus", "from Prometheus.prometheus.api.endpoints.llm_integration import router"),
        ("Engram", "from Engram.engram.api.llm_endpoints import router"),
    ]
    
    for component, import_str in test_cases:
        try:
            exec(import_str)
            print(f"✓ {component}: Import successful")
        except ImportError as e:
            print(f"✗ {component}: Import failed - {e}")
        except Exception as e:
            print(f"⚠ {component}: Other error - {e}")


async def main():
    """Run all tests."""
    print("=" * 50)
    print("RHETOR INTEGRATION TEST")
    print("=" * 50)
    
    # Check if Rhetor is running
    import aiohttp
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8103/health") as resp:
                if resp.status == 200:
                    print("✓ Rhetor service is running on port 8103\n")
                else:
                    print(f"⚠ Rhetor responded with status {resp.status}\n")
    except Exception as e:
        print(f"⚠ Rhetor service not accessible: {e}")
        print("  Tests will fail if Rhetor is not running\n")
    
    # Run tests
    await test_component_imports()
    await test_rhetor_client()
    
    print("\n" + "=" * 50)
    print("TEST COMPLETE")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())