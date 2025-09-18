#!/usr/bin/env python3
"""
Test script demonstrating the complete sundown/sunrise flow.

This shows how:
1. CI outputs with sundown notes
2. Hooks validate and store them
3. Apollo would process them (simulated)
4. Rhetor would package them (simulated)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.ci_tools.sundown import prepare_sundown, CISundown
from shared.ci_tools.ci_wrapper_hooks import CIHookSystem


def simulate_ci_turn():
    """Simulate a CI completing a turn with sundown notes."""
    print("=" * 60)
    print("SIMULATING CI TURN")
    print("=" * 60)

    # CI completes task
    ci_output = """
I've successfully implemented the CI-side sundown mechanism. Here's what was accomplished:

1. Created the core sundown module with validation
2. Implemented automatic extraction and generation
3. Added mandatory hooks to the PTY wrapper
4. Documented the protocol for all CIs

The system now enforces sundown notes at the end of each turn, preventing memory overflow
by ensuring all data passed to CIs is under 128KB total.
"""

    print("\n[CI Output]:")
    print(ci_output)

    # CI prepares sundown notes
    sundown = prepare_sundown(
        todo_list=[
            {"task": "Implemented CI-side sundown mechanism", "status": "completed"},
            {"task": "Added hooks to PTY wrapper", "status": "completed"},
            {"task": "Created documentation", "status": "completed"},
            {"task": "Implement Apollo digest (<64KB)", "status": "pending"},
            {"task": "Create Rhetor optimizer (<64KB)", "status": "pending"}
        ],
        context_notes="""Working on: Memory overflow fix via sundown/sunrise
Completed: CI-side implementation with mandatory hooks
Next step: Apollo digest implementation with 85% relevance, 15% recency
Watch for: Memory operations must stay under 64KB limit""",
        open_questions=[
            "How to handle CI-specific state in sundown?",
            "Should hooks auto-retry on validation failure?"
        ],
        files_in_focus=[
            {"path": "/shared/ci_tools/sundown.py", "description": "core module"},
            {"path": "/shared/ci_tools/ci_wrapper_hooks.py", "description": "hook system"},
            {"path": "/shared/ci_tools/ci_pty_wrapper.py", "description": "enhanced wrapper"}
        ],
        ci_name="Amy"
    )

    full_output = ci_output + "\n\n" + sundown

    print("\n[With Sundown]:")
    print(sundown)

    return full_output


def simulate_hook_processing(output: str):
    """Simulate hook system processing the output."""
    print("\n" + "=" * 60)
    print("HOOK SYSTEM PROCESSING")
    print("=" * 60)

    hook_system = CIHookSystem("Amy")

    # Process through hooks
    context = {
        'output': output,
        'ci_name': 'Amy',
        'session_output': output
    }

    # Execute post-output hooks (includes sundown check)
    result = hook_system.execute_hooks('post_output', context)

    if result.get('sundown_detected'):
        print("✓ Sundown notes detected and validated")
        validation = result.get('sundown_validation', {})
        print(f"  Size: {validation.get('size_kb', 0):.1f}KB")
        if validation.get('warnings'):
            print(f"  Warnings: {', '.join(validation['warnings'])}")
    else:
        print("✗ No sundown notes detected")

    return result


def simulate_apollo_digest():
    """Simulate Apollo creating a memory digest."""
    print("\n" + "=" * 60)
    print("APOLLO DIGEST (SIMULATED)")
    print("=" * 60)

    # Apollo would query Engram and create digest
    # Prioritizing by 85% relevance, 15% recency

    digest = """# APOLLO MEMORY DIGEST
## Identity & Purpose
- CI Name: Amy
- Role: Coding CI for Tekton
- Project: Memory overflow fix

## Task Context (Medium-term)
- Implementing sundown/sunrise protocol
- Preventing memory overflow via 128KB limit
- Using hooks for mandatory operations

## Working Memory (Short-term)
- Just completed CI-side sundown implementation
- Added hooks to PTY wrapper
- Next: Apollo digest with relevance prioritization

## Memory Index
- Sundown notes: /engram/sundown/Amy_20240917_*.md
- Session history: /engram/sessions/Amy_current.json
- Code patterns: /engram/patterns/memory_management.json

[Size: 12.3KB of 64KB budget]"""

    print(digest)
    return digest


def simulate_rhetor_optimization(sundown: str, apollo_digest: str, new_task: str):
    """Simulate Rhetor optimizing the prompt."""
    print("\n" + "=" * 60)
    print("RHETOR OPTIMIZATION (SIMULATED)")
    print("=" * 60)

    # Parse sundown to get essential parts
    manager = CISundown("Amy")
    parsed = manager.parse_sundown_notes(sundown)

    # Rhetor would optimize and potentially summarize
    total_size = len((sundown + apollo_digest + new_task).encode('utf-8'))
    size_kb = total_size / 1024

    print(f"Initial size: {size_kb:.1f}KB")

    if size_kb > 64:
        print("Size exceeds 64KB, applying summary pass...")
        # Would summarize sundown notes here
        optimized = f"""# SUNRISE PROMPT
## Your Previous State (summarized)
Todos: {len(parsed['todo_list'])} items ({sum(1 for t in parsed['todo_list'] if t['status'] == 'completed')} complete)
Context: {parsed['context_notes'][:100]}...
Questions: {len(parsed['open_questions'])} pending

## Current Task
{new_task}

## Relevant Context (from Apollo)
{apollo_digest[:16000]}  # Truncated to fit

[TRUNCATED at 64KB limit]"""
    else:
        optimized = f"""# SUNRISE PROMPT
## Your Previous State
{sundown}

## Current Task
{new_task}

## Memory Context (from Apollo)
{apollo_digest}

[Size: {size_kb:.1f}KB of 64KB budget]"""

    print(f"Final size: {len(optimized.encode('utf-8')) / 1024:.1f}KB")
    print("\n[Optimized Package Preview]:")
    print(optimized[:500] + "...")

    return optimized


def main():
    """Run the complete flow simulation."""
    print("\n" + "=" * 70)
    print(" SUNDOWN/SUNRISE COMPLETE FLOW DEMONSTRATION")
    print("=" * 70)

    # Step 1: CI completes turn with sundown
    ci_output = simulate_ci_turn()

    # Step 2: Hooks process and validate
    hook_result = simulate_hook_processing(ci_output)

    # Step 3: Apollo creates digest (would happen between turns)
    apollo_digest = simulate_apollo_digest()

    # Step 4: Rhetor optimizes for next turn
    new_task = "Continue implementing Apollo's relevance-based memory prioritization"

    # Extract sundown from output
    manager = CISundown("Amy")
    sundown = manager.extract_sundown_notes(ci_output)

    if sundown:
        sunrise_package = simulate_rhetor_optimization(sundown, apollo_digest, new_task)

        print("\n" + "=" * 60)
        print("NEXT TURN: CI RECEIVES")
        print("=" * 60)
        print("CI receives pure markdown sunrise package:")
        print("- No JSON parsing required")
        print("- Complete context from sundown")
        print("- Relevant memories from Apollo")
        print("- Clear task from user")
        print("- Total size under 128KB")
        print("\n✓ Memory overflow prevented!")
        print("✓ Continuity maintained!")
        print("✓ CI can focus on reasoning, not data management!")


if __name__ == "__main__":
    main()