#!/usr/bin/env python3
"""
Example of using the enhanced LLM client in Hermes.

This example demonstrates how to use the tekton-llm-client based adapter
for message analysis, service analysis, and chat.
"""

import os
import sys
import json
import asyncio
import logging
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hermes.core.llm_client import LLMClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("llm_client_example")

async def message_analysis_example():
    """Example of using the LLM client for message analysis."""
    # Initialize the LLM client
    llm_client = LLMClient()
    
    # Example message to analyze
    message_content = """
    {
      "source": "engram.memory",
      "destination": "ergon.agent",
      "message_type": "memory_retrieval_response",
      "correlation_id": "87e6d20a-2b5a-4c1e-9c5f-6d9a6c843eb2",
      "timestamp": "2025-04-15T14:30:22Z",
      "priority": "normal",
      "payload": {
        "query_id": "Q2025-04125",
        "query": "project status meeting notes from last week",
        "results": [
          {
            "memory_id": "MEM-20250408-001",
            "title": "Weekly Project Status Meeting - April 8, 2025",
            "content_snippet": "Team reported backend API is 80% complete but frontend development is behind schedule...",
            "similarity_score": 0.92,
            "timestamp": "2025-04-08T10:15:00Z",
            "tags": ["meeting", "project-status", "milestone-review"]
          },
          {
            "memory_id": "MEM-20250408-002",
            "title": "Action Items from Project Status Meeting",
            "content_snippet": "1. John to expedite frontend development, 2. Sarah to update documentation...",
            "similarity_score": 0.87,
            "timestamp": "2025-04-08T11:30:00Z",
            "tags": ["action-items", "meeting", "tasks"]
          }
        ],
        "total_results": 2,
        "query_time_ms": 135
      }
    }
    """
    
    # Analyze the message
    print("Analyzing message...")
    result = await llm_client.analyze_message(message_content)
    
    print("\n=== Message Analysis Result ===")
    print(f"Purpose: {result.get('purpose')}")
    print(f"Components: {', '.join(result.get('components', []))}")
    print(f"Data Summary: {result.get('data_summary')}")
    print(f"Priority: {result.get('priority')}")
    print("\nSummary:")
    print(result.get('summary'))

async def service_analysis_example():
    """Example of using the LLM client for service analysis."""
    # Initialize the LLM client
    llm_client = LLMClient()
    
    # Example service registration to analyze
    service_data = {
        "component_id": "sophia.analytics",
        "version": "1.2.0",
        "description": "Advanced analytics and intelligence measurement service",
        "capabilities": [
            {
                "id": "analyze_performance",
                "description": "Analyze performance metrics of components and workflows",
                "parameters": ["component_id", "timeframe", "metrics"],
                "returns": ["performance_analysis", "bottlenecks", "recommendations"]
            },
            {
                "id": "intelligence_assessment",
                "description": "Assess intelligence capabilities of LLM-based components",
                "parameters": ["component_id", "test_scenarios", "criteria"],
                "returns": ["intelligence_score", "strengths", "weaknesses"]
            },
            {
                "id": "pattern_detection",
                "description": "Detect patterns in system behavior and usage",
                "parameters": ["data_source", "timeframe", "threshold"],
                "returns": ["patterns", "anomalies", "insights"]
            }
        ],
        "dependencies": ["hermes.core", "engram.memory", "prometheus.metrics"],
        "endpoints": {
            "http": "http://localhost:8006/api",
            "websocket": "ws://localhost:8006/ws",
            "events": "http://localhost:8006/events"
        },
        "status": "active",
        "metadata": {
            "team": "Intelligence Team",
            "priority": "high",
            "tags": ["analytics", "intelligence", "metrics"]
        }
    }
    
    # Analyze the service registration
    print("Analyzing service registration...")
    result = await llm_client.analyze_service(service_data)
    
    print("\n=== Service Analysis Result ===")
    print("Capabilities:")
    for capability in result.get('capabilities', []):
        print(f"- {capability}")
    
    print("\nDependencies:")
    for dependency in result.get('dependencies', []):
        print(f"- {dependency}")
    
    print("\nIntegration Points:")
    for integration in result.get('integration_points', []):
        print(f"- {integration}")
    
    print("\nUse Cases:")
    for use_case in result.get('use_cases', []):
        print(f"- {use_case}")
    
    print("\nSummary:")
    print(result.get('summary'))

async def chat_example():
    """Example of using the LLM client for chat."""
    # Initialize the LLM client
    llm_client = LLMClient()
    
    # Example chat interaction
    print("Starting chat with LLM...")
    
    # First message
    query = "How does Hermes handle message routing between components?"
    print(f"\nUser: {query}")
    
    response = await llm_client.chat(message=query)
    print(f"Assistant: {response.get('message')}")
    
    # Continue the conversation with chat history
    chat_history = [
        {"role": "user", "content": query},
        {"role": "assistant", "content": response.get('message')}
    ]
    
    follow_up = "What happens if a component is unavailable when a message is sent to it?"
    print(f"\nUser: {follow_up}")
    
    response = await llm_client.chat(
        message=follow_up,
        chat_history=chat_history
    )
    
    print(f"Assistant: {response.get('message')}")

async def streaming_chat_example():
    """Example of using the LLM client for streaming chat."""
    # Initialize the LLM client
    llm_client = LLMClient()
    
    # Callback to handle streaming chunks
    async def handle_chunk(chunk):
        if isinstance(chunk, dict) and "done" in chunk:
            print("\n[Stream complete]")
        elif isinstance(chunk, dict) and "chunk" in chunk:
            print(chunk["chunk"], end="", flush=True)
        elif isinstance(chunk, str):
            print(chunk, end="", flush=True)
    
    # Example streaming chat
    query = "Explain the service discovery process in Hermes and how components register themselves."
    print(f"\nUser: {query}")
    print("Assistant: ", end="", flush=True)
    
    # Start streaming chat
    await llm_client.streaming_chat(
        message=query,
        callback=handle_chunk
    )

async def template_example():
    """Example of using the LLM client with templates."""
    # Initialize the LLM client
    llm_client = LLMClient()
    
    # Custom template example
    custom_template = """
    Analyze the following Hermes component configuration:
    
    {{ config }}
    
    Please provide:
    1. Key configuration settings and their values
    2. Any potential issues or misconfigurations
    3. Recommendations for improvement
    """
    
    # Register the template
    llm_client.template_registry.register({
        "name": "config_analysis",
        "template": custom_template,
        "description": "Template for analyzing component configurations"
    })
    
    # Example configuration to analyze
    config = """
    hermes:
      port: 8002
      log_level: info
      message_retention: 7d
      services:
        registration_ttl: 3600
        health_check_interval: 60
        auto_deregister: true
      database:
        type: sqlite
        path: /data/hermes.db
        backup_interval: 24h
      metrics:
        enabled: true
        prometheus_endpoint: /metrics
    """
    
    # Generate with the template
    print("Analyzing configuration with template...")
    result = await llm_client.generate_with_template(
        template_name="config_analysis",
        variables={"config": config},
        temperature=0.3
    )
    
    print("\n=== Configuration Analysis Result ===")
    print(result)

async def main():
    """Run all examples."""
    try:
        await message_analysis_example()
        print("\n" + "="*60 + "\n")
        
        await service_analysis_example()
        print("\n" + "="*60 + "\n")
        
        await chat_example()
        print("\n" + "="*60 + "\n")
        
        await streaming_chat_example()
        print("\n" + "="*60 + "\n")
        
        await template_example()
        
    except Exception as e:
        logger.error(f"Error running examples: {e}")

if __name__ == "__main__":
    asyncio.run(main())