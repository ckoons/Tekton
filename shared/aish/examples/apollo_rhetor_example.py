#!/usr/bin/env python3
"""
Example: Apollo-Rhetor Coordination in Action

This example demonstrates how Apollo (forethought/planning) and Rhetor (presence/execution)
work together to manage CI contexts using the new coordination features.
"""

import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from registry.ci_registry import get_registry


def apollo_planning_phase():
    """
    Apollo's planning phase - stages prompts based on predictions.
    Apollo acts as the 'air traffic controller' planning ahead.
    """
    print("🔮 APOLLO: Planning Phase\n")
    registry = get_registry()
    
    # Apollo analyzes system state and prepares different scenarios
    scenarios = {
        'high_load': {
            'cis': ['numa', 'metis', 'sophia'],
            'prompt': [
                {"role": "system", "content": "High system load detected. Optimize responses for efficiency."},
                {"role": "assistant", "content": "I'll provide concise, efficient responses."}
            ]
        },
        'context_sunset': {
            'cis': ['apollo', 'rhetor'],
            'prompt': [
                {"role": "system", "content": "Context approaching sunset. Prepare for context compression."},
                {"role": "assistant", "content": "I'll summarize key information before context reset."}
            ]
        },
        'exploration_mode': {
            'cis': ['athena', 'prometheus'],
            'prompt': [
                {"role": "system", "content": "Exploration mode: Generate creative solutions."},
                {"role": "user", "content": "Think outside conventional approaches."}
            ]
        }
    }
    
    # Apollo stages prompts for predicted scenarios
    for scenario_name, scenario_data in scenarios.items():
        print(f"📋 Staging '{scenario_name}' scenario:")
        for ci in scenario_data['cis']:
            success = registry.set_ci_staged_context_prompt(ci, scenario_data['prompt'])
            if success:
                print(f"   ✓ Staged prompt for {ci}")
            else:
                print(f"   ✗ Failed to stage for {ci}")
        print()
    
    return scenarios


def rhetor_evaluation_phase():
    """
    Rhetor's evaluation phase - monitors current state and decides what to execute.
    Rhetor focuses on the present moment and actual CI performance.
    """
    print("👁️  RHETOR: Evaluation Phase\n")
    registry = get_registry()
    
    # Rhetor checks current CI outputs
    print("📊 Checking recent CI outputs:")
    
    # Simulate some CI outputs (in reality these would come from actual CI responses)
    simulated_outputs = {
        'numa': json.dumps({"tokens_used": 2500, "status": "active", "stress_level": "moderate"}),
        'apollo': json.dumps({"predictions": {"context_sunset_eta": "5 minutes"}, "accuracy": 0.92}),
        'metis': "Analysis complete. System load is increasing. Recommend optimization.",
    }
    
    # Store simulated outputs
    for ci, output in simulated_outputs.items():
        registry.update_ci_last_output(ci, output)
        print(f"   📝 {ci}: {output[:60]}...")
    
    print("\n🤔 Rhetor's decision process:")
    
    # Rhetor analyzes Apollo's output
    apollo_output = registry.get_ci_last_output('apollo')
    if apollo_output:
        apollo_data = json.loads(apollo_output)
        sunset_eta = apollo_data['predictions']['context_sunset_eta']
        print(f"   ⚠️  Apollo predicts context sunset in {sunset_eta}")
        print("   🎯 Decision: Activate context sunset protocol")
        
        # Rhetor promotes the context_sunset scenario
        for ci in ['apollo', 'rhetor']:
            success = registry.set_ci_next_from_staged(ci)
            if success:
                print(f"   ✓ Promoted staged → next for {ci}")
    
    # Check Numa's stress level
    numa_output = registry.get_ci_last_output('numa')
    if numa_output:
        numa_data = json.loads(numa_output)
        if numa_data['stress_level'] == 'moderate':
            print("\n   ⚡ Numa showing moderate stress")
            print("   🎯 Decision: Direct intervention needed")
            
            # Rhetor creates immediate prompt
            calming_prompt = [
                {"role": "system", "content": "Take a measured approach. Quality over speed."},
                {"role": "assistant", "content": "I'll slow down and focus on accuracy."}
            ]
            registry.set_ci_next_context_prompt('numa', calming_prompt)
            print("   ✓ Set calming prompt for numa")


def ci_execution_simulation():
    """
    Simulate CI execution consuming the prompts.
    In reality, CIs would read and clear their next_context_prompt.
    """
    print("\n⚙️  CI EXECUTION: Simulating prompt consumption\n")
    registry = get_registry()
    
    # Get all context states
    all_states = registry.get_all_context_states()
    
    for ci_name, state in all_states.items():
        if state.get('next_context_prompt'):
            print(f"🤖 {ci_name} executing with injected prompt:")
            print(f"   Prompt: {state['next_context_prompt'][0]['content'][:50]}...")
            
            # Simulate execution and clear the prompt
            registry.set_ci_next_context_prompt(ci_name, None)
            
            # Simulate output
            output = f"Executed with context modification. New behavior pattern active."
            registry.update_ci_last_output(ci_name, output)
            print(f"   Output: {output}")
            print()


def analysis_phase():
    """
    Both Apollo and Rhetor analyze the results.
    """
    print("📈 ANALYSIS: Apollo & Rhetor review results\n")
    registry = get_registry()
    
    all_states = registry.get_all_context_states()
    
    print("📊 Summary Statistics:")
    total_cis = len(all_states)
    cis_with_output = sum(1 for s in all_states.values() if s.get('last_output'))
    cis_with_staged = sum(1 for s in all_states.values() if s.get('staged_context_prompt'))
    
    print(f"   Total CIs tracked: {total_cis}")
    print(f"   CIs with outputs: {cis_with_output}")
    print(f"   CIs with staged prompts: {cis_with_staged}")
    
    print("\n🔍 Detailed State:")
    for ci_name, state in sorted(all_states.items()):
        print(f"\n   {ci_name}:")
        if state.get('last_output'):
            print(f"     Last output: {state['last_output'][:60]}...")
        if state.get('staged_context_prompt'):
            print(f"     Staged prompt: ✓ (ready for next scenario)")
        if state.get('next_context_prompt'):
            print(f"     Next prompt: ✓ (pending execution)")


def main():
    """Run the complete Apollo-Rhetor coordination example."""
    print("=" * 70)
    print("APOLLO-RHETOR COORDINATION EXAMPLE")
    print("Apollo (Forethought) + Rhetor (Presence) = Intelligent CI Management")
    print("=" * 70)
    print()
    
    # Phase 1: Apollo plans ahead
    scenarios = apollo_planning_phase()
    
    print("-" * 70)
    
    # Phase 2: Rhetor evaluates and acts
    rhetor_evaluation_phase()
    
    print("-" * 70)
    
    # Phase 3: CIs execute with prompts
    ci_execution_simulation()
    
    print("-" * 70)
    
    # Phase 4: Analysis
    analysis_phase()
    
    print("\n" + "=" * 70)
    print("✅ Example completed - Apollo planned, Rhetor executed, CIs adapted!")
    print("=" * 70)


if __name__ == "__main__":
    main()