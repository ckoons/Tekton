#!/usr/bin/env python3
"""Test creating a real Construct session for Ergon/Kai."""

import json
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from rhetor.core.ci_manager import CIManager


def create_construct_session():
    """Create a Construct session for building a CSV batch processor."""
    
    print("Creating Ergon/Kai Construct Session")
    print("=" * 60)
    
    # Initialize CI Manager
    ci_manager = CIManager(enable_memory=True)
    
    # Create session with initial requirements
    session_id = ci_manager.create_ci_session(
        ci_name="ergon",
        task="construct",
        initial_context={
            "user_requirements": {
                "purpose": "Build a CSV batch processor with parallel processing",
                "functional_requirements": [
                    "Process large CSV files (100GB+)",
                    "Parallel processing with configurable workers",
                    "Progress tracking and monitoring",
                    "Error recovery and retry logic"
                ],
                "performance_targets": {
                    "throughput": "1M rows/sec",
                    "memory": "<16GB",
                    "latency": "<100ms per batch"
                },
                "deployment": "containerized",
                "preferred_stack": ["Python", "PostgreSQL"]
            },
            "current_phase": "discovery"
        }
    )
    
    print(f"✓ Created session: {session_id}\n")
    
    # Get the full prompt for the CI
    prompt = ci_manager.get_ci_prompt(session_id)
    
    print("System Prompt:")
    print("-" * 40)
    print(json.dumps(prompt["system_prompt"], indent=2))
    
    print("\nContext:")
    print("-" * 40)
    print(json.dumps(prompt["context"], indent=2))
    
    print("\nModel Assignment:")
    print("-" * 40)
    print(f"Model: {prompt['model']}")
    print(f"Task: {prompt['task']}")
    
    # Simulate user interaction
    print("\n" + "=" * 60)
    print("SIMULATING CONSTRUCT WORKFLOW")
    print("=" * 60)
    
    # Step 1: User asks for component suggestions
    ci_manager.add_message_to_session(
        session_id,
        role="user",
        content="What components from the Registry would you recommend for this CSV batch processor?"
    )
    
    # Step 2: Kai responds with suggestions
    ci_manager.add_message_to_session(
        session_id,
        role="assistant",
        content="""Based on your requirements, I recommend these Registry components:

1. **csv-chunker-v2** - High-performance CSV chunking with memory management
   - Registry ID: csv-chunker-001
   - Handles 100GB+ files efficiently
   
2. **parallel-processor-framework** - Configurable parallel processing engine
   - Registry ID: parallel-proc-002
   - Supports worker pools and batch distribution
   
3. **progress-tracker-service** - Real-time progress monitoring
   - Registry ID: progress-track-001
   - WebSocket-based updates with dashboard

4. **resilient-retry-handler** - Error recovery with exponential backoff
   - Registry ID: retry-handler-003
   - Circuit breaker and dead letter queue support

Shall I proceed with creating the integration architecture?"""
    )
    
    # Update context to design phase
    ci_manager.update_ci_context(
        session_id,
        {
            "current_phase": "design",
            "selected_components": [
                {"registry_id": "csv-chunker-001", "alias": "chunker"},
                {"registry_id": "parallel-proc-002", "alias": "processor"},
                {"registry_id": "progress-track-001", "alias": "tracker"},
                {"registry_id": "retry-handler-003", "alias": "retry"}
            ],
            "design_decisions": [
                "Use message queue for batch distribution",
                "Implement checkpoint recovery",
                "Add Prometheus metrics"
            ]
        }
    )
    
    # Get updated prompt with conversation
    final_prompt = ci_manager.get_ci_prompt(session_id)
    
    print("\n" + "=" * 60)
    print("SESSION STATE AFTER WORKFLOW")
    print("=" * 60)
    
    print(f"Current Phase: {final_prompt['context']['current_phase']}")
    print(f"Selected Components: {len(final_prompt['context']['selected_components'])}")
    print(f"Conversation Messages: {len(final_prompt.get('conversation_history', []))}")
    print(f"Design Decisions: {len(final_prompt['context'].get('design_decisions', []))}")
    
    # End session
    ci_manager.end_session(session_id)
    print("\n✓ Session ended and stored for future reference")
    
    return session_id


if __name__ == "__main__":
    session_id = create_construct_session()
    print(f"\n✨ Construct session {session_id} completed successfully!")