#!/usr/bin/env python3
"""
Test the Construct questions system.

Tests both direct Python access and simulated CI interaction.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add Ergon to path
sys.path.insert(0, str(Path(__file__).parent))

from ergon.construct.mcp_questions import ConstructQuestionsMCP


async def test_ci_interaction():
    """Simulate a CI interacting with the questions."""
    print("=" * 60)
    print("TEST: CI Interaction with Construct Questions")
    print("=" * 60)
    
    # Initialize the MCP tool
    mcp = ConstructQuestionsMCP()
    
    # Simulate CI responses
    ci_responses = {
        'purpose': 'I want to build a data processing pipeline that takes JSON files, validates them, transforms the data, and outputs analysis results',
        'components': 'parser-abc123, analyzer-def456',
        'dataflow': 'JSON files input -> parse -> validate schema -> transform fields -> analyze patterns -> output insights as JSON',
        'deployment': 'containerized',
        'container': 'yes',
        'ci_association': 'container',  # CI will manage the container
        'constraints': '2GB memory limit, must process files under 10 seconds',
        'testing': 'unit tests for parser, integration tests for pipeline, performance benchmarks',
        'monitoring': 'ci_managed',
        'evolution': 'ci_guided'
    }
    
    print("\n1. CI Getting All Questions")
    print("-" * 40)
    result = await mcp.handle_tool_call('get_all')
    print(f"Found {len(result['questions'])} questions")
    
    print("\n2. CI Answering Questions")
    print("-" * 40)
    
    # Answer each question
    for question in result['questions']:
        q_id = question['id']
        if q_id in ci_responses:
            print(f"\nQuestion: {question['question']}")
            print(f"CI Answer: {ci_responses[q_id]}")
            
            # Submit answer
            answer_result = await mcp.handle_tool_call(
                'submit_answer',
                question_id=q_id,
                answer=ci_responses[q_id]
            )
            print(f"Status: {answer_result.get('status', 'unknown')}")
            
            # Get suggestions for next question
            if q_id in ['deployment', 'container']:
                suggest_result = await mcp.handle_tool_call(
                    'get_suggestions',
                    question_id='ci_association'
                )
                if suggest_result.get('suggestions'):
                    print(f"CI Suggestion: {suggest_result['suggestions'][0]}")
    
    print("\n3. Building Final Workspace")
    print("-" * 40)
    workspace_result = await mcp.handle_tool_call('build_workspace')
    workspace = workspace_result['workspace']
    
    print(json.dumps(workspace, indent=2))
    
    print("\n4. Creating Construct Request")
    print("-" * 40)
    
    # Build the actual Construct request
    construct_request = {
        "action": "compose",
        "sender_id": "test-ci",
        "components": workspace['components'],
        "connections": [
            {"from": "parser-abc123.output", "to": "analyzer-def456.input"}
        ],
        "constraints": workspace['constraints'],
        "metadata": workspace['metadata']
    }
    
    print("Construct Request:")
    print(json.dumps(construct_request, indent=2))
    
    # Check if we need to create a CI
    if workspace['metadata']['ci_type'] == 'container':
        print("\n5. CI Creation Command")
        print("-" * 40)
        ci_command = f"aish container create --name data-pipeline --ci-managed --purpose '{ci_responses['purpose']}'"
        print(f"Command: {ci_command}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE: CI successfully built composition")
    print("=" * 60)


async def test_human_interaction():
    """Simulate human interaction through UI."""
    print("\n" + "=" * 60)
    print("TEST: Human Interaction Simulation")
    print("=" * 60)
    
    mcp = ConstructQuestionsMCP()
    
    # Simulate human giving a long answer that covers multiple questions
    long_answer = """
    I need a system to monitor our microservices. It should use the api-gateway 
    component to collect metrics, the monitoring-service to process them, and 
    store everything in a time-series database. The data flows from services 
    through the gateway, gets aggregated, and then stored. This needs to be 
    containerized for our Kubernetes cluster with a CI to manage it. 
    Memory limit is 4GB and it needs to handle 1000 requests per second.
    """
    
    print("\nHuman provides comprehensive answer:")
    print(long_answer)
    
    # The dialog system would parse this and pre-fill multiple fields
    result = await mcp.handle_tool_call(
        'submit_answer',
        question_id='purpose',
        answer=long_answer
    )
    
    print("\nParsed from comprehensive answer:")
    print(f"- Purpose: monitoring microservices")
    print(f"- Components detected: api-gateway, monitoring-service")
    print(f"- Deployment: containerized (Kubernetes mentioned)")
    print(f"- Container: yes")
    print(f"- Memory constraint: 4GB")
    print(f"- Performance: 1000 req/s")
    
    print("\n" + "=" * 60)
    print("Human gets pre-filled answers and confirms/adjusts")
    print("=" * 60)


async def main():
    """Run all tests."""
    await test_ci_interaction()
    await test_human_interaction()


if __name__ == "__main__":
    asyncio.run(main())