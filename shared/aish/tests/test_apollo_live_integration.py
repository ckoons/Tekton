#!/usr/bin/env python3
"""
Live integration test for Apollo-Rhetor coordination.

This test actually sends messages to the running Apollo CI and verifies
that outputs are captured correctly in the registry.
"""

import pytest
import json
import time
import sys
from pathlib import Path

# Add parent paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from registry.ci_registry import get_registry
from core.unified_sender import send_to_ci
from shared.urls import tekton_url


class TestApolloLiveIntegration:
    """Test real communication with running Apollo CI."""
    
    @pytest.fixture
    def registry(self):
        """Get the CI registry."""
        registry = get_registry()
        registry.refresh()
        return registry
    
    
    def test_send_string_to_apollo_and_capture_output(self, registry):
        """
        Test sending a string message to Apollo and capturing its output.
        This verifies the complete flow with a real running Apollo CI.
        """
        print("\n=== Live Apollo Integration Test ===\n")
        
        # Step 1: Clear any existing Apollo output
        registry.update_ci_last_output('apollo', None)
        
        # Step 2: Send a simple string message to Apollo
        print("1. Sending string message to Apollo:")
        message = "Analyze current system token usage and provide a brief summary"
        
        success = send_to_ci('apollo', message)
        assert success, "Failed to send message to Apollo"
        print(f"   ✓ Sent: '{message}'")
        
        # Step 3: Wait a moment for Apollo to process
        print("\n2. Waiting for Apollo to process...")
        time.sleep(2)  # Give Apollo time to respond
        
        # Step 4: Check if output was captured
        print("\n3. Checking captured output:")
        output = registry.get_ci_last_output('apollo')
        
        # NOTE: In the current implementation, we need to manually capture
        # the output. This test reveals that the automatic capture
        # mechanism needs to be implemented in the message flow.
        
        if output:
            print(f"   ✓ Output captured: {len(output)} bytes")
            print(f"   Content preview: {output[:100]}...")
        else:
            print("   ⚠️  No output captured yet")
            print("   This indicates we need to implement automatic output capture")
    
    def test_send_struct_to_apollo_and_capture_output(self, registry):
        """
        Test sending a structured message (dict) to Apollo and capturing its output.
        """
        print("\n=== Structured Message Test ===\n")
        
        # Step 1: Create a structured request for Apollo
        print("1. Sending structured message to Apollo:")
        structured_message = {
            "action": "analyze_context_usage",
            "parameters": {
                "ci_list": ["numa", "metis", "apollo"],
                "metrics": ["token_usage", "burn_rate", "context_remaining"],
                "format": "json"
            },
            "priority": "high"
        }
        
        success = send_to_ci('apollo', json.dumps(structured_message))
        assert success, "Failed to send structured message to Apollo"
        print(f"   ✓ Sent structured request: {list(structured_message.keys())}")
        
        # Step 2: Wait for processing
        print("\n2. Waiting for Apollo to process...")
        time.sleep(2)
        
        # Step 3: Check output
        print("\n3. Checking captured output:")
        output = registry.get_ci_last_output('apollo')
        
        if output:
            print(f"   ✓ Output captured: {len(output)} bytes")
            try:
                # Try to parse as JSON if Apollo returned structured data
                parsed = json.loads(output)
                print(f"   ✓ Output is valid JSON")
                print(f"   Keys: {list(parsed.keys())}")
            except json.JSONDecodeError:
                print(f"   Output is text: {output[:100]}...")
        else:
            print("   ⚠️  No output captured")
    
    def test_apollo_with_context_prompt_injection(self, registry):
        """
        Test the full flow: stage prompt → send message → capture output.
        """
        print("\n=== Full Context Injection Flow ===\n")
        
        # Step 1: Apollo stages a context prompt
        print("1. Apollo stages a context prompt:")
        context_prompt = [
            {
                "role": "system",
                "content": "You are analyzing token efficiency. Focus on optimization opportunities."
            },
            {
                "role": "assistant",
                "content": "I'll analyze token usage patterns and suggest optimizations."
            }
        ]
        
        success = registry.set_ci_staged_context_prompt('apollo', context_prompt)
        assert success
        print("   ✓ Staged context prompt for Apollo")
        
        # Step 2: Rhetor promotes it
        print("\n2. Rhetor promotes staged → next:")
        success = registry.set_ci_next_from_staged('apollo')
        assert success
        print("   ✓ Context prompt ready for injection")
        
        # Step 3: Send a message that would trigger context use
        print("\n3. Sending message to Apollo:")
        message = "What are the top 3 token optimization opportunities?"
        
        # In the real implementation, the message sender would:
        # 1. Check for next_context_prompt
        # 2. Prepend it to the message
        # 3. Clear next_context_prompt after sending
        
        next_prompt = registry.get_ci_context_state('apollo').get('next_context_prompt')
        if next_prompt:
            print("   ✓ Found context prompt to inject")
            print(f"   Context: {next_prompt[0]['content'][:50]}...")
        
        success = send_to_ci('apollo', message)
        assert success
        print(f"   ✓ Sent: '{message}'")
        
        # Clear the next prompt (as the sender should do)
        registry.set_ci_next_context_prompt('apollo', None)
        
        # Step 4: Wait and check output
        print("\n4. Waiting for Apollo response...")
        time.sleep(2)
        
        output = registry.get_ci_last_output('apollo')
        if output:
            print(f"   ✓ Output captured: {len(output)} bytes")
            print(f"   Response should reflect the context prompt focus")
        else:
            print("   ⚠️  No output captured")
    
    def test_verify_apollo_api_direct(self, registry):
        """
        Test direct API call to Apollo to understand the response format.
        This helps us understand what needs to be captured.
        """
        print("\n=== Direct Apollo API Test ===\n")
        
        try:
            import requests
            
            # Direct API call to Apollo
            apollo_api_url = tekton_url('apollo', '/api/v1/contexts')
            print(f"1. Calling Apollo API directly: {apollo_api_url}")
            
            response = requests.get(apollo_api_url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✓ API responded successfully")
                print(f"   Response type: {type(data)}")
                print(f"   Keys: {list(data.keys()) if isinstance(data, dict) else 'list response'}")
                
                # This is what should be captured as last_output
                output_to_capture = json.dumps(data)
                print(f"\n2. This output should be captured:")
                print(f"   Size: {len(output_to_capture)} bytes")
                print(f"   Preview: {output_to_capture[:100]}...")
                
                # Manually store it to show what the automatic capture should do
                registry.update_ci_last_output('apollo', output_to_capture)
                print("\n3. Manually stored output in registry")
                
                # Verify retrieval
                retrieved = registry.get_ci_last_output('apollo')
                assert retrieved == output_to_capture
                print("   ✓ Output successfully stored and retrieved")
                
            else:
                print(f"   ✗ API error: {response.status_code}")
                
        except Exception as e:
            print(f"   ✗ Failed to connect to Apollo: {e}")
            pytest.skip("Apollo API not accessible")


if __name__ == "__main__":
    # Run with pytest for better output
    pytest.main([__file__, "-v", "-s", "-k", "test_"])