#!/usr/bin/env python3
"""Test LLM connection for Metis"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from metis.core.llm_adapter import MetisLLMAdapter

async def test_connection():
    """Test the LLM adapter connection"""
    print("Testing Metis LLM Adapter connection...")
    print("-" * 50)
    
    # Create adapter
    adapter = MetisLLMAdapter()
    print(f"Adapter URL: {adapter.adapter_url}")
    print(f"Default Provider: {adapter.default_provider}")
    print(f"Default Model: {adapter.default_model}")
    print()
    
    # Test connection
    print("Testing connection to Rhetor...")
    result = await adapter.test_connection()
    
    if result.get("connected"):
        print("✓ Connection successful!")
        print(f"  Response: {result.get('response')}")
        print(f"  Model: {result.get('model')}")
        print(f"  Provider: {result.get('provider')}")
    else:
        print("✗ Connection failed!")
        print(f"  Error: {result.get('error')}")
        return False
    
    print("\n" + "-" * 50)
    
    # Test task decomposition
    print("Testing task decomposition...")
    decompose_result = await adapter.decompose_task(
        task_title="Create a simple TODO app",
        task_description="Build a web-based TODO application with basic CRUD operations",
        depth=2,
        max_subtasks=5
    )
    
    if decompose_result.get("success"):
        print("✓ Task decomposition successful!")
        print(f"  Model: {decompose_result.get('model')}")
        print(f"  Provider: {decompose_result.get('provider')}")
        print(f"  Subtasks generated: {len(decompose_result.get('subtasks', []))}")
        
        for i, subtask in enumerate(decompose_result.get("subtasks", []), 1):
            print(f"\n  Subtask {i}: {subtask.get('title')}")
            print(f"    Hours: {subtask.get('estimated_hours')}")
            print(f"    Complexity: {subtask.get('complexity')}")
    else:
        print("✗ Task decomposition failed!")
        print(f"  Error: {decompose_result.get('error')}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)