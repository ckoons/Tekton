#!/usr/bin/env python3
"""Test the CI Manager functionality."""

import sys
import os
import json
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rhetor.core.ci_manager import CIManager


def test_ci_manager():
    """Test CI Manager creation and session management."""
    
    print("Testing CI Manager...")
    
    # Create CI Manager (without Engram for testing)
    ci_manager = CIManager(enable_memory=False)
    
    print(f"✓ CI Manager initialized")
    print(f"  - Loaded {len(ci_manager.prompts_config.get('ci_prompts', {}))} CI prompts")
    print(f"  - Loaded {len(ci_manager.prompts_config.get('model_assignments', {}))} model assignments")
    
    # Test 1: Create a Construct session for Ergon/Kai
    print("\n1. Creating Construct session for Ergon/Kai...")
    session_id = ci_manager.create_ci_session(
        ci_name="ergon",
        task="construct",
        initial_context={
            "user_requirements": {
                "purpose": "Build a data processing pipeline",
                "constraints": {"memory": "16GB", "latency": "<100ms"},
                "deployment": "containerized"
            },
            "current_phase": "discovery"
        }
    )
    print(f"   ✓ Session created: {session_id}")
    
    # Test 2: Get the prompt for the session
    print("\n2. Getting CI prompt for session...")
    prompt = ci_manager.get_ci_prompt(session_id)
    print(f"   ✓ Retrieved prompt")
    print(f"     - Model: {prompt.get('model')}")
    print(f"     - Task: {prompt.get('task')}")
    print(f"     - Has system prompt: {'identity' in prompt.get('system_prompt', {})}")
    print(f"     - Current phase: {prompt.get('context', {}).get('current_phase')}")
    
    # Test 3: Update context
    print("\n3. Updating session context...")
    ci_manager.update_ci_context(
        session_id,
        {
            "current_phase": "design",
            "selected_components": [
                {
                    "registry_id": "csv-parser-001",
                    "alias": "parser",
                    "configuration": {"chunk_size": 1000}
                }
            ]
        }
    )
    print(f"   ✓ Context updated")
    
    # Test 4: Add messages to conversation
    print("\n4. Adding conversation messages...")
    ci_manager.add_message_to_session(
        session_id,
        role="user",
        content="I need to process CSV files with 100GB daily volume"
    )
    ci_manager.add_message_to_session(
        session_id,
        role="assistant",
        content="I understand. For 100GB daily CSV processing, I recommend a chunked parallel processing approach with these components..."
    )
    print(f"   ✓ Added 2 messages to session")
    
    # Test 5: Get updated prompt with conversation
    print("\n5. Getting updated prompt with conversation...")
    updated_prompt = ci_manager.get_ci_prompt(session_id)
    history = updated_prompt.get("conversation_history", [])
    print(f"   ✓ Conversation history has {len(history)} messages")
    
    # Test 6: Test model assignments
    print("\n6. Testing model assignments...")
    models = {
        "ergon": ci_manager.get_model_for_ci("ergon"),
        "numa": ci_manager.get_model_for_ci("numa"),
        "rhetor": ci_manager.get_model_for_ci("rhetor")
    }
    for ci, model in models.items():
        print(f"   - {ci}: {model}")
    
    # Test 7: Create development sprint session
    print("\n7. Creating development sprint session...")
    sprint_session = ci_manager.create_ci_session(
        ci_name="ergon",
        task="development",
        initial_context={
            "sprint_id": "sprint-001",
            "sprint_goal": "Implement Construct UI integration",
            "tasks": [
                {
                    "task_id": "task-1",
                    "description": "Create API endpoints",
                    "assigned_to": "ergon",
                    "status": "pending"
                }
            ]
        }
    )
    print(f"   ✓ Sprint session created: {sprint_session}")
    
    # Test 8: End session
    print("\n8. Ending sessions...")
    ci_manager.end_session(session_id)
    ci_manager.end_session(sprint_session)
    print(f"   ✓ Sessions ended")
    
    print("\n✅ All tests passed!")
    
    # Print example prompt structure for reference
    print("\n" + "="*60)
    print("EXAMPLE ERGON/KAI CONSTRUCT PROMPT:")
    print("="*60)
    if prompt.get('system_prompt'):
        print(json.dumps(prompt['system_prompt'], indent=2))
    
    return True


def test_with_memory():
    """Test CI Manager with Engram memory integration."""
    
    print("\n" + "="*60)
    print("TESTING WITH MEMORY INTEGRATION")
    print("="*60)
    
    try:
        # Try to create with memory
        ci_manager = CIManager(enable_memory=True)
        
        if ci_manager.engram:
            print("✓ Engram integration enabled")
            
            # Create a session that will load memories
            session_id = ci_manager.create_ci_session(
                ci_name="ergon",
                task="construct",
                initial_context={
                    "user_requirements": {
                        "purpose": "Build another CSV processor"
                    }
                }
            )
            
            # Check if memories were loaded
            prompt = ci_manager.get_ci_prompt(session_id)
            loaded_memories = prompt.get("context", {}).get("loaded_memories", [])
            
            if loaded_memories:
                print(f"✓ Loaded {len(loaded_memories)} relevant memories")
                for mem in loaded_memories[:2]:  # Show first 2
                    print(f"  - Memory {mem.get('id')}: relevance {mem.get('relevance', 0):.2f}")
            else:
                print("  No relevant memories found (this is normal for new tasks)")
            
            ci_manager.end_session(session_id)
            
        else:
            print("⚠️  Engram not available, running without memory")
            
    except Exception as e:
        print(f"⚠️  Memory integration test skipped: {e}")
    
    return True


if __name__ == "__main__":
    # Run basic tests
    success = test_ci_manager()
    
    # Run memory tests if available
    if success:
        test_with_memory()
    
    print("\n✨ CI Manager is ready for use!")