#!/usr/bin/env python3
"""
Tests for Apollo-Rhetor CI coordination features in CI Registry.

Tests the new context state management methods that enable Apollo (forethought)
and Rhetor (presence) to coordinate CI prompts and analyze outputs.
"""

import pytest
import json
from typing import List, Dict, Optional

# Add parent paths for imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from shared.aish.src.registry.ci_registry import CIRegistry, get_registry


class TestApolloRhetorCoordination:
    """Test suite for Apollo-Rhetor coordination methods."""
    
    @pytest.fixture
    def registry(self):
        """Create a fresh registry for each test."""
        registry = CIRegistry()
        # Ensure registry is populated with CIs
        registry.refresh()
        return registry
    
    @pytest.fixture
    def sample_prompts(self):
        """Sample prompt data for testing."""
        return {
            'optimization': [
                {"role": "system", "content": "Focus on performance optimization"},
                {"role": "assistant", "content": "I'll analyze and optimize the code"}
            ],
            'safety': [
                {"role": "system", "content": "Priority: Safety and error handling"},
                {"role": "user", "content": "Ensure all operations are safe"}
            ],
            'analysis': [
                {"role": "system", "content": "Provide detailed analysis"},
                {"role": "assistant", "content": "I'll examine all aspects thoroughly"}
            ]
        }
    
    # Basic Functional Tests
    
    def test_set_staged_context_prompt_valid_ci(self, registry):
        """Test setting staged context prompt for valid CI."""
        prompt = [{"role": "system", "content": "Test prompt"}]
        result = registry.set_ci_staged_context_prompt('numa', prompt)
        assert result is True
        
        # Verify it was stored
        state = registry.get_ci_context_state('numa')
        assert state is not None
        assert state['staged_context_prompt'] == prompt
    
    def test_set_staged_context_prompt_invalid_ci(self, registry):
        """Test setting staged context prompt for non-existent CI."""
        prompt = [{"role": "system", "content": "Test prompt"}]
        result = registry.set_ci_staged_context_prompt('nonexistent', prompt)
        assert result is False
    
    def test_set_staged_context_prompt_clear_with_none(self, registry):
        """Test clearing staged prompt by setting None."""
        # First set a prompt
        prompt = [{"role": "system", "content": "Test prompt"}]
        registry.set_ci_staged_context_prompt('apollo', prompt)
        
        # Then clear it
        result = registry.set_ci_staged_context_prompt('apollo', None)
        assert result is True
        
        state = registry.get_ci_context_state('apollo')
        assert state['staged_context_prompt'] is None
    
    def test_set_next_context_prompt_valid_ci(self, registry):
        """Test setting next context prompt for valid CI."""
        prompt = [{"role": "user", "content": "Execute this immediately"}]
        result = registry.set_ci_next_context_prompt('rhetor', prompt)
        assert result is True
        
        state = registry.get_ci_context_state('rhetor')
        assert state['next_context_prompt'] == prompt
    
    def test_set_next_from_staged_success(self, registry):
        """Test promoting staged prompt to next prompt."""
        # Stage a prompt
        staged = [{"role": "system", "content": "Staged prompt"}]
        registry.set_ci_staged_context_prompt('metis', staged)
        
        # Promote it
        result = registry.set_ci_next_from_staged('metis')
        assert result is True
        
        # Verify the promotion
        state = registry.get_ci_context_state('metis')
        assert state['next_context_prompt'] == staged
        assert state['staged_context_prompt'] is None
    
    def test_set_next_from_staged_no_staged(self, registry):
        """Test promoting when no staged prompt exists."""
        result = registry.set_ci_next_from_staged('athena')
        assert result is False
    
    def test_update_ci_last_output_text(self, registry):
        """Test storing text output from CI."""
        output = "Analysis complete. Found 3 optimization opportunities."
        result = registry.update_ci_last_output('sophia', output)
        assert result is True
        
        retrieved = registry.get_ci_last_output('sophia')
        assert retrieved == output
    
    def test_update_ci_last_output_json(self, registry):
        """Test storing JSON output from CI."""
        output_dict = {
            "status": "success",
            "tokens_used": 1500,
            "response": "Task completed successfully",
            "metrics": {"accuracy": 0.95, "speed": "fast"}
        }
        output_json = json.dumps(output_dict)
        
        result = registry.update_ci_last_output('prometheus', output_json)
        assert result is True
        
        retrieved = registry.get_ci_last_output('prometheus')
        assert retrieved == output_json
        
        # Verify it can be parsed back to JSON
        parsed = json.loads(retrieved)
        assert parsed == output_dict
    
    def test_get_ci_last_output_not_set(self, registry):
        """Test getting output when none has been set."""
        output = registry.get_ci_last_output('harmonia')
        assert output is None
    
    def test_case_insensitive_ci_names(self, registry):
        """Test that CI names are case-insensitive."""
        prompt = [{"role": "system", "content": "Test"}]
        
        # Set with different cases
        registry.set_ci_staged_context_prompt('APOLLO', prompt)
        registry.set_ci_next_context_prompt('Apollo', prompt)
        registry.update_ci_last_output('apollo', "output")
        
        # All should refer to the same CI
        state = registry.get_ci_context_state('ApoLLo')
        assert state is not None
        assert state['staged_context_prompt'] == prompt
        assert state['next_context_prompt'] == prompt
        assert state['last_output'] == "output"
    
    def test_get_all_context_states(self, registry, sample_prompts):
        """Test getting all CI context states."""
        # Set various states
        registry.set_ci_staged_context_prompt('apollo', sample_prompts['optimization'])
        registry.set_ci_next_context_prompt('rhetor', sample_prompts['safety'])
        registry.update_ci_last_output('numa', "Test output")
        
        all_states = registry.get_all_context_states()
        
        assert 'apollo' in all_states
        assert 'rhetor' in all_states
        assert 'numa' in all_states
        
        assert all_states['apollo']['staged_context_prompt'] == sample_prompts['optimization']
        assert all_states['rhetor']['next_context_prompt'] == sample_prompts['safety']
        assert all_states['numa']['last_output'] == "Test output"
    
    # Integration Test: Complete Apollo-Rhetor Flow
    
    def test_apollo_rhetor_integration_flow(self, registry, sample_prompts):
        """
        Integration test simulating complete Apollo-Rhetor coordination flow.
        
        Scenario:
        1. Apollo analyzes system state and stages prompts for multiple CIs
        2. Apollo specifically prepares optimization for its own CI
        3. Rhetor evaluates current conditions
        4. Rhetor promotes Apollo's staged prompt
        5. CI executes with the prompt (simulated)
        6. Output is captured for analysis
        7. Apollo and Rhetor analyze the output
        """
        print("\n=== Apollo-Rhetor Integration Test Flow ===\n")
        
        # Step 1: Apollo stages prompts for multiple CIs based on predictions
        print("1. Apollo stages optimization prompts for multiple CIs:")
        staged_cis = ['apollo', 'numa', 'metis', 'sophia']
        for ci in staged_cis:
            success = registry.set_ci_staged_context_prompt(ci, sample_prompts['optimization'])
            assert success is True
            print(f"   ✓ Staged optimization prompt for {ci}")
        
        # Step 2: Apollo self-stages a specific analysis prompt
        print("\n2. Apollo stages analysis prompt for itself:")
        apollo_self_prompt = [
            {"role": "system", "content": "Analyze token usage patterns across all CIs"},
            {"role": "assistant", "content": "I'll analyze the token burn rates and predict optimization opportunities"}
        ]
        success = registry.set_ci_staged_context_prompt('apollo', apollo_self_prompt)
        assert success is True
        print("   ✓ Apollo staged self-analysis prompt")
        
        # Step 3: Rhetor evaluates current conditions
        print("\n3. Rhetor evaluates CI states and decides to promote Apollo's prompt:")
        
        # Check what's staged
        apollo_state = registry.get_ci_context_state('apollo')
        assert apollo_state['staged_context_prompt'] == apollo_self_prompt
        print(f"   ✓ Found staged prompt: {apollo_state['staged_context_prompt'][0]['content'][:50]}...")
        
        # Rhetor promotes Apollo's staged prompt
        success = registry.set_ci_next_from_staged('apollo')
        assert success is True
        print("   ✓ Rhetor promoted Apollo's staged → next prompt")
        
        # Verify promotion
        apollo_state = registry.get_ci_context_state('apollo')
        assert apollo_state['next_context_prompt'] == apollo_self_prompt
        assert apollo_state['staged_context_prompt'] is None
        
        # Step 4: Simulate Apollo CI execution with the prompt
        print("\n4. Apollo CI executes with the injected prompt (simulated):")
        
        # In real implementation, the CI would consume next_context_prompt
        # Here we simulate the output
        apollo_output = json.dumps({
            "status": "success",
            "analysis": {
                "total_cis": len(staged_cis),
                "token_usage": {
                    "apollo": 15000,
                    "numa": 8500,
                    "metis": 12000,
                    "sophia": 9200
                },
                "predictions": {
                    "high_usage_risk": ["apollo", "metis"],
                    "optimization_targets": ["apollo", "metis"],
                    "recommended_action": "context_compression"
                },
                "burn_rate": 450  # tokens/minute
            },
            "timestamp": "2024-01-29T15:30:00Z"
        })
        
        # Clear the next prompt (as CI would do) and store output
        registry.set_ci_next_context_prompt('apollo', None)
        success = registry.update_ci_last_output('apollo', apollo_output)
        assert success is True
        print("   ✓ Apollo completed analysis")
        print(f"   ✓ Output stored: {len(apollo_output)} bytes")
        
        # Step 5: Both Apollo and Rhetor can analyze the output
        print("\n5. Apollo and Rhetor analyze the output:")
        
        # Get Apollo's output
        output = registry.get_ci_last_output('apollo')
        assert output is not None
        
        # Parse and analyze
        analysis = json.loads(output)
        assert analysis['status'] == 'success'
        print(f"   ✓ Token burn rate: {analysis['analysis']['burn_rate']} tokens/min")
        print(f"   ✓ High usage CIs: {', '.join(analysis['analysis']['predictions']['high_usage_risk'])}")
        
        # Step 6: Rhetor takes immediate action based on analysis
        print("\n6. Rhetor takes immediate action based on Apollo's analysis:")
        
        # Rhetor decides to set compression prompts for high-usage CIs
        compression_prompt = [
            {"role": "system", "content": "URGENT: Enable context compression mode"},
            {"role": "assistant", "content": "I'll compress my context to optimize token usage"}
        ]
        
        for ci in analysis['analysis']['predictions']['high_usage_risk']:
            success = registry.set_ci_next_context_prompt(ci, compression_prompt)
            assert success is True
            print(f"   ✓ Set compression prompt for {ci}")
        
        # Step 7: Verify final state
        print("\n7. Final state verification:")
        all_states = registry.get_all_context_states()
        
        # Count CIs with context state
        cis_with_state = len(all_states)
        cis_with_next = sum(1 for s in all_states.values() if s.get('next_context_prompt'))
        cis_with_output = sum(1 for s in all_states.values() if s.get('last_output'))
        
        print(f"   ✓ CIs with context state: {cis_with_state}")
        print(f"   ✓ CIs with next prompt: {cis_with_next}")
        print(f"   ✓ CIs with last output: {cis_with_output}")
        
        # Verify Apollo's state
        assert 'apollo' in all_states
        assert all_states['apollo']['last_output'] == apollo_output
        assert all_states['apollo']['next_context_prompt'] == compression_prompt
        
        print("\n✅ Integration test completed successfully!")
        print("   Apollo planned → Rhetor executed → CIs responded → Both analyzed → Action taken")
    
    # Edge Cases and Error Handling
    
    def test_complex_prompt_structures(self, registry):
        """Test handling of complex prompt structures."""
        complex_prompt = [
            {"role": "system", "content": "Multi-line\ncontent\nwith special chars: @#$%"},
            {"role": "user", "content": "Unicode test: 你好 🌟 café"},
            {"role": "assistant", "content": '{"nested": {"json": "data"}}'},
            {"role": "user", "content": "Another message", "metadata": {"temperature": 0.7}}
        ]
        
        success = registry.set_ci_staged_context_prompt('ergon', complex_prompt)
        assert success is True
        
        retrieved = registry.get_ci_context_state('ergon')
        assert retrieved['staged_context_prompt'] == complex_prompt


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])