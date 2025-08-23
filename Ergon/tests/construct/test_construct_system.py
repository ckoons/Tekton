#!/usr/bin/env python3
"""
Test script for the integrated Construct system.

Tests both CI (JSON) and human (text) interfaces.
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add both Ergon and shared to path
ergon_path = Path(__file__).parent
sys.path.insert(0, str(ergon_path))
sys.path.insert(0, str(ergon_path.parent))  # For shared module

from ergon.construct.integration import get_construct_system


async def test_ci_interface():
    """Test the CI JSON interface."""
    print("=" * 60)
    print("Testing CI Interface (JSON)")
    print("=" * 60)
    
    construct = get_construct_system()
    
    # 1. Compose a solution (CI sends JSON)
    print("\n1. CI composing solution...")
    compose_request = {
        "action": "compose",
        "sender_id": "test-ci",
        "components": [
            {
                "registry_id": "parser-abc123",
                "alias": "parser",
                "config": {"format": "json"}
            },
            {
                "registry_id": "analyzer-def456",
                "alias": "analyzer",
                "config": {"model": "gpt-4"}
            }
        ],
        "connections": [
            {
                "from": "parser.output",
                "to": "analyzer.input"
            }
        ],
        "constraints": {
            "max_memory": "2GB",
            "requires_standards": True
        }
    }
    
    response = await construct.process_json(compose_request)
    print(f"Response: {json.dumps(response, indent=2)}")
    workspace_id = response.get('workspace_id')
    
    # 2. Validate the composition
    print("\n2. CI validating composition...")
    validate_request = {
        "action": "validate",
        "sender_id": "test-ci",
        "workspace_id": workspace_id,
        "checks": ["connections", "dependencies", "standards"],
        "mode": "strict"
    }
    
    response = await construct.process_json(validate_request)
    print(f"Validation: {json.dumps(response, indent=2)}")
    
    # 3. Get workspace state
    print("\n3. CI checking workspace state...")
    state_request = {
        "action": "get_state",
        "sender_id": "test-ci",
        "workspace_id": workspace_id
    }
    
    response = await construct.process_json(state_request)
    print(f"State: {json.dumps(response.get('state', {}), indent=2)}")
    
    return workspace_id


async def test_human_interface(workspace_id=None):
    """Test the human text interface."""
    print("\n" + "=" * 60)
    print("Testing Human Interface (Natural Language)")
    print("=" * 60)
    
    construct = get_construct_system()
    
    # Test messages from a human
    messages = [
        "Help me build a data pipeline using Parser and Analyzer",
        "Validate my composition",
        "Test this solution with 60 second timeout",
        "How do I publish to Registry?"
    ]
    
    for msg in messages:
        print(f"\nHuman: {msg}")
        response = await construct.process(msg, sender_id="human-user")
        print(f"Ergon: {response}")


async def test_ci_collaboration():
    """Test multiple CIs collaborating."""
    print("\n" + "=" * 60)
    print("Testing CI Collaboration")
    print("=" * 60)
    
    construct = get_construct_system()
    
    # Amy-CI starts a composition
    print("\n1. Amy-CI creates initial composition...")
    amy_request = {
        "action": "compose",
        "sender_id": "amy-ci",
        "components": [
            {"registry_id": "api-gateway", "alias": "gateway"}
        ]
    }
    response = await construct.process_json(amy_request)
    workspace_id = response.get('workspace_id')
    print(f"Amy created workspace: {workspace_id[:8]}...")
    
    # Ani-CI adds components
    print("\n2. Ani-CI adds components...")
    ani_request = {
        "action": "compose",
        "sender_id": "ani-ci",
        "workspace_id": workspace_id,
        "components": [
            {"registry_id": "api-gateway", "alias": "gateway"},
            {"registry_id": "auth-service", "alias": "auth"}
        ],
        "connections": [
            {"from": "gateway.auth_check", "to": "auth.validate"}
        ]
    }
    response = await construct.process_json(ani_request)
    print(f"Ani updated composition: {response.get('status')}")
    
    # Check collaboration in state
    workspace = construct.get_workspace(workspace_id)
    if workspace:
        print(f"\n3. Workspace collaborators: {workspace.get('collaborators', [])}")
        print(f"   Current status: {workspace.get('status')}")


async def test_bilingual_detection():
    """Test automatic JSON/text detection."""
    print("\n" + "=" * 60)
    print("Testing Bilingual Detection")
    print("=" * 60)
    
    construct = get_construct_system()
    
    # Send JSON as string (like CI would via chat)
    json_msg = json.dumps({
        "action": "validate",
        "workspace_id": "test-123"
    })
    
    print(f"\n1. Sending JSON string: {json_msg}")
    response = await construct.process(json_msg, "ci-user")
    print(f"   Response type: {'JSON' if response.startswith('{') else 'Text'}")
    print(f"   Response: {response[:100]}...")
    
    # Send natural text
    text_msg = "Help me validate my composition"
    print(f"\n2. Sending text: {text_msg}")
    response = await construct.process(text_msg, "human-user")
    print(f"   Response type: {'JSON' if response.startswith('{') else 'Text'}")
    print(f"   Response: {response[:100]}...")


async def main():
    """Run all tests."""
    print("\n🚀 ERGON CONSTRUCT SYSTEM TEST\n")
    
    try:
        # Test CI interface
        workspace_id = await test_ci_interface()
        
        # Test human interface
        await test_human_interface(workspace_id)
        
        # Test CI collaboration
        await test_ci_collaboration()
        
        # Test bilingual detection
        await test_bilingual_detection()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
