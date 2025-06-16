# Synthesis Integration Guide

This guide explains how to integrate the Synthesis component with other Tekton components and external systems.

## Table of Contents
- [Introduction](#introduction)
- [Integration with Tekton Components](#integration-with-tekton-components)
- [External System Integration](#external-system-integration)
- [API Integration Patterns](#api-integration-patterns)
- [WebSocket Integration Patterns](#websocket-integration-patterns)
- [Event-Based Integration](#event-based-integration)
- [LLM Integration](#llm-integration)
- [Authentication and Security](#authentication-and-security)
- [Deployment Considerations](#deployment-considerations)
- [Troubleshooting](#troubleshooting)

## Introduction

Synthesis serves as the execution and integration engine for the Tekton ecosystem. It provides capabilities for:

1. Executing multi-step processes with dependencies, conditions, and loops
2. Integrating with external systems via CLI, API, and Machine Control Protocol (MCP)
3. Orchestrating workflows involving multiple Tekton components
4. Providing real-time feedback on execution progress
5. Managing system integrations with a standardized adapter pattern

This guide covers best practices for integrating with Synthesis from both Tekton components and external systems.

## Integration with Tekton Components

Synthesis provides deep integration with other Tekton components through specialized adapters.

### Hermes Integration

Synthesis registers with Hermes for service discovery and component coordination:

```python
from tekton.utils.hermes_registration import register_with_hermes

def register_synthesis():
    register_with_hermes(
        component_name="synthesis",
        capabilities=["execution", "integration", "workflow"],
        api_url="http://localhost:8009/api",
        ws_url="ws://localhost:8009/ws",
        health_url="http://localhost:8009/health",
        capabilities_map={
            "execution": "/api/executions",
            "integration": "/api/integrations",
            "workflow": "/api/plans"
        }
    )
```

### Prometheus Integration

Synthesis integrates with Prometheus for executing plans and coordinating with planning functions:

#### Plan Execution

```python
from synthesis.client import SynthesisClient
from prometheus.client import PrometheusClient

async def execute_prometheus_plan(plan_id):
    prometheus_client = PrometheusClient()
    synthesis_client = SynthesisClient()
    
    # Retrieve plan from Prometheus
    plan = await prometheus_client.get_plan(plan_id)
    
    # Convert to Synthesis execution format
    execution_plan = {
        "name": plan["name"],
        "description": plan["description"],
        "steps": convert_prometheus_steps(plan["steps"]),
        "metadata": {
            "prometheus_plan_id": plan_id,
            "tags": plan.get("tags", []) + ["prometheus"]
        }
    }
    
    # Execute the plan
    execution_id = await synthesis_client.execute_plan(execution_plan)
    
    # Link the execution with Prometheus
    await prometheus_client.link_execution(plan_id, execution_id)
    
    return execution_id
```

#### Result Reporting

```python
from synthesis.client import SynthesisClient
from prometheus.client import PrometheusClient

async def report_execution_results(execution_id):
    synthesis_client = SynthesisClient()
    prometheus_client = PrometheusClient()
    
    # Get execution details
    execution = await synthesis_client.get_execution(execution_id)
    
    # Extract prometheus plan ID
    prometheus_plan_id = execution["metadata"].get("prometheus_plan_id")
    if not prometheus_plan_id:
        return
    
    # Report results to Prometheus
    await prometheus_client.update_plan_execution(
        prometheus_plan_id,
        {
            "status": execution["status"],
            "duration_ms": execution["duration_ms"],
            "completed_at": execution["completed_at"],
            "success_rate": calculate_success_rate(execution)
        }
    )
```

### Athena Integration

Synthesis integrates with Athena to retrieve contextual knowledge for executions:

```python
from synthesis.client import SynthesisClient
from athena.client import AthenaClient

async def get_execution_context(entity_id):
    athena_client = AthenaClient()
    
    # Query Athena for entity context
    entity = await athena_client.get_entity(entity_id)
    
    # Get related entities
    related = await athena_client.get_related_entities(
        entity_id, 
        relationship_types=["requires", "depends_on", "implements"]
    )
    
    # Create context from entity data
    context = {
        "entity": {
            "id": entity["id"],
            "name": entity["name"],
            "type": entity["type"],
            "properties": entity["properties"]
        },
        "related_entities": [
            {
                "id": rel["id"],
                "name": rel["name"],
                "type": rel["type"],
                "relationship": rel["relationship"]
            }
            for rel in related
        ]
    }
    
    return context
```

### Engram Integration

Synthesis integrates with Engram for persistent memory storage:

```python
from synthesis.client import SynthesisClient
from engram.client import EngramClient

async def store_execution_in_memory(execution_id):
    synthesis_client = SynthesisClient()
    engram_client = EngramClient()
    
    # Get execution details
    execution = await synthesis_client.get_execution(execution_id)
    
    # Store in Engram's structured memory
    memory_id = await engram_client.store_memory(
        content=execution,
        memory_type="execution",
        metadata={
            "execution_id": execution["execution_id"],
            "name": execution["plan"]["name"],
            "status": execution["status"],
            "tags": execution["metadata"].get("tags", [])
        }
    )
    
    return memory_id
```

### Rhetor Integration

Synthesis integrates with Rhetor via the tekton-llm-client for LLM capabilities:

```python
from synthesis.client import SynthesisClient
from tekton_llm_client import TektonLLMClient

async def enhance_execution_with_llm(execution_plan):
    llm_client = TektonLLMClient()
    
    # Generate step descriptions
    for step in execution_plan["steps"]:
        if "description" not in step:
            step_description = await llm_client.generate_text(
                f"Generate a concise description for this execution step: {step}",
                max_tokens=100
            )
            step["description"] = step_description.strip()
    
    # Analyze plan for potential issues
    plan_analysis = await llm_client.generate_text(
        f"Analyze this execution plan for potential issues or optimizations: {execution_plan}",
        max_tokens=500
    )
    
    # Add analysis to plan metadata
    if "metadata" not in execution_plan:
        execution_plan["metadata"] = {}
    execution_plan["metadata"]["llm_analysis"] = plan_analysis.strip()
    
    return execution_plan
```

## External System Integration

Synthesis can integrate with external systems using various methods.

### CLI Integration

Execute commands on the local system:

```python
from synthesis.client import SynthesisClient

async def execute_cli_command():
    client = SynthesisClient()
    
    # Create execution plan with CLI command
    execution_id = await client.execute_plan({
        "name": "CLI Integration Example",
        "description": "Example of CLI integration",
        "steps": [
            {
                "id": "cli_step",
                "type": "command",
                "parameters": {
                    "command": "echo 'Hello from CLI integration'",
                    "working_directory": "/tmp",
                    "timeout": 30
                }
            }
        ]
    })
    
    # Wait for completion
    result = await client.wait_for_execution(execution_id)
    
    return result
```

### API Integration

Make HTTP requests to external APIs:

```python
from synthesis.client import SynthesisClient

async def execute_api_request():
    client = SynthesisClient()
    
    # Create execution plan with API request
    execution_id = await client.execute_plan({
        "name": "API Integration Example",
        "description": "Example of API integration",
        "steps": [
            {
                "id": "api_step",
                "type": "api",
                "parameters": {
                    "method": "GET",
                    "url": "https://api.example.com/data",
                    "headers": {
                        "Authorization": "Bearer ${API_TOKEN}"
                    },
                    "timeout": 30
                }
            },
            {
                "id": "process_step",
                "type": "function",
                "parameters": {
                    "function": "process_data",
                    "args": {
                        "data": "${api_step.response.body}"
                    }
                },
                "dependencies": ["api_step"]
            }
        ],
        "variables": {
            "API_TOKEN": "your-api-token"
        }
    })
    
    # Wait for completion
    result = await client.wait_for_execution(execution_id)
    
    return result
```

### MCP Integration

Integrate with Machine Control Protocol systems:

```python
from synthesis.client import SynthesisClient

async def execute_mcp_command():
    client = SynthesisClient()
    
    # Create execution plan with MCP command
    execution_id = await client.execute_plan({
        "name": "MCP Integration Example",
        "description": "Example of MCP integration",
        "steps": [
            {
                "id": "mcp_connect",
                "type": "integration",
                "parameters": {
                    "integration": "mcp",
                    "capability": "connect",
                    "params": {
                        "endpoint": "mcp://example.com:9000",
                        "auth_token": "${MCP_TOKEN}"
                    }
                }
            },
            {
                "id": "mcp_command",
                "type": "integration",
                "parameters": {
                    "integration": "mcp",
                    "capability": "send_command",
                    "params": {
                        "command": "GET_STATUS",
                        "args": {
                            "component": "system"
                        }
                    }
                },
                "dependencies": ["mcp_connect"]
            },
            {
                "id": "mcp_disconnect",
                "type": "integration",
                "parameters": {
                    "integration": "mcp",
                    "capability": "disconnect",
                    "params": {}
                },
                "dependencies": ["mcp_command"]
            }
        ],
        "variables": {
            "MCP_TOKEN": "your-mcp-token"
        }
    })
    
    # Wait for completion
    result = await client.wait_for_execution(execution_id)
    
    return result
```

## API Integration Patterns

Synthesis provides a RESTful API that follows standard integration patterns.

### Client Library Usage

The recommended way to integrate with Synthesis is using the client library:

```python
from synthesis.client import SynthesisClient
import asyncio

async def synthesis_client_example():
    # Create client
    client = SynthesisClient(base_url="http://localhost:8009")
    
    try:
        # Check health
        health = await client.get_health()
        print(f"Synthesis health: {health['status']}")
        
        # Create and execute a plan
        execution_id = await client.execute_plan({
            "name": "API Example Plan",
            "description": "Example plan created through API",
            "steps": [
                {
                    "id": "step1",
                    "type": "command",
                    "parameters": {
                        "command": "echo 'Step 1 output'"
                    }
                },
                {
                    "id": "step2",
                    "type": "command",
                    "parameters": {
                        "command": "echo 'Processing ${step1.output}'"
                    },
                    "dependencies": ["step1"]
                }
            ]
        })
        
        print(f"Created execution: {execution_id}")
        
        # Wait for completion
        result = await client.wait_for_execution(execution_id)
        print(f"Execution completed with status: {result['status']}")
        
        # Get step outputs
        steps = await client.get_execution_steps(execution_id)
        for step in steps["steps"]:
            print(f"Step {step['id']} output: {step['output']}")
    
    finally:
        # Close client
        await client.close()

# Run the example
asyncio.run(synthesis_client_example())
```

### Direct HTTP Integration

You can also integrate directly with the HTTP API:

```python
import httpx
import json

async def direct_api_integration():
    async with httpx.AsyncClient(base_url="http://localhost:8009") as client:
        # Create a plan
        plan_response = await client.post("/api/plans", json={
            "name": "Direct API Plan",
            "description": "Plan created through direct API",
            "steps": [
                {
                    "id": "step1",
                    "type": "command",
                    "parameters": {
                        "command": "echo 'Direct API step'"
                    }
                }
            ]
        })
        
        plan_data = plan_response.json()
        plan_id = plan_data["plan_id"]
        
        # Execute the plan
        execute_response = await client.post(f"/api/plans/{plan_id}/execute", json={
            "variables": {},
            "metadata": {
                "source": "direct_api_example"
            }
        })
        
        execution_data = execute_response.json()
        execution_id = execution_data["execution_id"]
        
        # Poll for completion
        while True:
            status_response = await client.get(f"/api/executions/{execution_id}")
            status_data = status_response.json()
            
            if status_data["status"] in ["completed", "failed", "cancelled"]:
                break
                
            await asyncio.sleep(1)
        
        return status_data
```

## WebSocket Integration Patterns

For real-time updates, Synthesis provides WebSocket endpoints.

### Execution Monitoring

Monitor execution progress in real-time:

```javascript
// JavaScript WebSocket client example
function monitorExecution(executionId) {
    const ws = new WebSocket(`ws://localhost:8009/ws/executions/${executionId}`);
    
    ws.onopen = function() {
        console.log(`Connected to execution ${executionId}`);
    };
    
    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        console.log(`Event: ${data.type}`);
        
        switch (data.type) {
            case 'execution_started':
                console.log(`Execution started: ${data.data.name}`);
                break;
                
            case 'step_started':
                console.log(`Step started: ${data.data.step_id}`);
                break;
                
            case 'step_output':
                console.log(`Output from ${data.data.step_id}: ${data.data.output}`);
                break;
                
            case 'step_completed':
                console.log(`Step ${data.data.step_id} completed with status: ${data.data.status}`);
                break;
                
            case 'execution_completed':
                console.log(`Execution completed with status: ${data.data.status}`);
                ws.close();
                break;
        }
    };
    
    ws.onerror = function(error) {
        console.error('WebSocket error:', error);
    };
    
    ws.onclose = function() {
        console.log('Connection closed');
    };
    
    return ws;
}
```

### Event Subscription

Subscribe to system events:

```javascript
// JavaScript WebSocket event subscription example
function subscribeToEvents(eventTypes = ['execution_started', 'execution_completed']) {
    const ws = new WebSocket('ws://localhost:8009/ws/events');
    
    ws.onopen = function() {
        console.log('Connected to event stream');
        
        // Subscribe to specific event types
        ws.send(JSON.stringify({
            type: 'subscribe',
            event_types: eventTypes
        }));
    };
    
    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        console.log(`Event received: ${data.type}`, data);
    };
    
    ws.onerror = function(error) {
        console.error('WebSocket error:', error);
    };
    
    ws.onclose = function() {
        console.log('Connection closed');
    };
    
    return ws;
}
```

## Event-Based Integration

Synthesis provides an event-based integration pattern through HTTP callbacks.

### Event Subscription

Subscribe to events using the API:

```python
import httpx

async def subscribe_to_events():
    async with httpx.AsyncClient(base_url="http://localhost:8009") as client:
        response = await client.post("/api/events/subscriptions", json={
            "types": ["execution_started", "execution_completed", "step_completed"],
            "filter": {
                "tags": ["important"]
            },
            "callback_url": "https://your-service.example.com/events/synthesis",
            "expiration": "2025-12-31T23:59:59Z"
        })
        
        subscription_data = response.json()
        subscription_id = subscription_data["subscription_id"]
        
        print(f"Created subscription: {subscription_id}")
        return subscription_id
```

### Event Handler

Implement an event handler for callbacks:

```python
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/events/synthesis")
async def handle_synthesis_event(request: Request):
    event_data = await request.json()
    
    event_type = event_data["type"]
    event_timestamp = event_data["timestamp"]
    
    if event_type == "execution_started":
        execution_id = event_data["payload"]["execution_id"]
        plan_name = event_data["payload"]["name"]
        print(f"Execution started: {plan_name} ({execution_id})")
        
    elif event_type == "execution_completed":
        execution_id = event_data["payload"]["execution_id"]
        status = event_data["payload"]["status"]
        duration_ms = event_data["payload"]["duration_ms"]
        print(f"Execution {execution_id} completed with status {status} in {duration_ms}ms")
        
    elif event_type == "step_completed":
        execution_id = event_data["payload"]["execution_id"]
        step_id = event_data["payload"]["step_id"]
        status = event_data["payload"]["status"]
        print(f"Step {step_id} in execution {execution_id} completed with status {status}")
    
    return {"status": "processed"}
```

## LLM Integration

Synthesis provides deep integration with LLMs through the tekton-llm-client.

### LLM Step Type

Use the LLM step type in execution plans:

```python
from synthesis.client import SynthesisClient

async def llm_integration_example():
    client = SynthesisClient()
    
    # Create execution plan with LLM step
    execution_id = await client.execute_plan({
        "name": "LLM Integration Example",
        "description": "Example of LLM integration",
        "steps": [
            {
                "id": "data_collection",
                "type": "command",
                "parameters": {
                    "command": "cat /tmp/sample_data.json"
                }
            },
            {
                "id": "llm_analysis",
                "type": "llm",
                "parameters": {
                    "model": "claude-3-sonnet-20240229",
                    "prompt": "Analyze the following JSON data and provide insights:\n\n${data_collection.output}",
                    "max_tokens": 1000,
                    "temperature": 0.7
                },
                "dependencies": ["data_collection"]
            },
            {
                "id": "save_analysis",
                "type": "command",
                "parameters": {
                    "command": "echo '${llm_analysis.output}' > /tmp/analysis_results.txt"
                },
                "dependencies": ["llm_analysis"]
            }
        ]
    })
    
    # Wait for completion
    result = await client.wait_for_execution(execution_id)
    
    return result
```

### LLM-Enhanced Execution

Use LLMs to enhance execution plans:

```python
from synthesis.client import SynthesisClient
from tekton_llm_client import TektonLLMClient

async def enhance_plan_with_llm(plan):
    llm_client = TektonLLMClient()
    
    # Generate enhanced plan using LLM
    prompt = f"""
    Enhance the following execution plan by:
    1. Adding detailed descriptions to each step
    2. Adding appropriate error handling
    3. Adding validation steps where needed
    4. Adding appropriate tags
    
    Original plan:
    {plan}
    
    Provide the enhanced plan as valid JSON.
    """
    
    enhanced_plan_json = await llm_client.generate_text(
        prompt=prompt,
        max_tokens=4000,
        stop=None,
        temperature=0.2
    )
    
    # Parse the enhanced plan
    try:
        import json
        enhanced_plan = json.loads(enhanced_plan_json)
        return enhanced_plan
    except json.JSONDecodeError:
        print("Failed to parse LLM output as JSON, using original plan")
        return plan
```

## Authentication and Security

Synthesis implements standard authentication mechanisms.

### Token Authentication

Use token authentication for API requests:

```python
from synthesis.client import SynthesisClient

# Create client with authentication token
client = SynthesisClient(
    base_url="http://localhost:8009",
    auth_token="your-auth-token"
)
```

For direct HTTP requests:

```python
import httpx

async def authenticated_request():
    headers = {
        "Authorization": "Bearer your-auth-token",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(base_url="http://localhost:8009", headers=headers) as client:
        response = await client.get("/api/executions")
        return response.json()
```

### Secure Integration

Follow these guidelines for secure integration:

1. Always use HTTPS for production deployments
2. Store authentication tokens securely
3. Use environment variables or secret management systems for sensitive configuration
4. Implement proper error handling to prevent information leakage
5. Validate and sanitize all inputs
6. Follow the principle of least privilege for integrations

## Deployment Considerations

Consider these factors when deploying Synthesis in an integrated environment.

### Environment Variables

Synthesis uses these environment variables for configuration:

```bash
# Core configuration
SYNTHESIS_PORT=8009                 # API port (follows Single Port Architecture)
SYNTHESIS_HOST=0.0.0.0              # Listen interface
SYNTHESIS_LOG_LEVEL=info            # Logging level
SYNTHESIS_STORAGE_TYPE=file         # Storage type (memory, file, database)
SYNTHESIS_STORAGE_PATH=/data        # Storage path for file-based storage

# Integration configuration
SYNTHESIS_HERMES_URL=http://localhost:8000  # Hermes URL for registration
SYNTHESIS_PROMETHEUS_URL=http://localhost:8001  # Prometheus URL
SYNTHESIS_ATHENA_URL=http://localhost:8002  # Athena URL
SYNTHESIS_ENGRAM_URL=http://localhost:8003  # Engram URL
SYNTHESIS_RHETOR_URL=http://localhost:8005  # Rhetor URL

# Security configuration
SYNTHESIS_AUTH_ENABLED=true         # Enable authentication
SYNTHESIS_AUTH_SECRET=your-secret   # Authentication secret
```

### Load Balancing

For high-availability deployments, consider:

1. Deploying multiple Synthesis instances
2. Using a load balancer to distribute requests
3. Configuring shared storage for execution state
4. Implementing a distributed event system

### Integration Testing

To ensure proper integration:

1. Test with realistic workloads
2. Verify error handling and recovery
3. Test performance under load
4. Validate security measures
5. Verify graceful degradation when dependencies are unavailable

## Troubleshooting

Common integration issues and solutions:

### Connection Issues

**Problem**: Unable to connect to Synthesis API
**Solution**:
1. Verify Synthesis is running with `tekton-status`
2. Check the correct port (8009) is being used
3. Ensure network connectivity between systems
4. Verify firewall rules allow the connection

### Authentication Issues

**Problem**: Authentication failures
**Solution**:
1. Verify the authentication token is correct
2. Check token expiration
3. Ensure the token has the necessary permissions
4. Verify authentication is properly configured in Synthesis

### Execution Issues

**Problem**: Executions fail or timeout
**Solution**:
1. Check execution logs for specific error messages
2. Verify all required dependencies are available
3. Check resource constraints (memory, CPU)
4. Test steps individually to isolate the issue
5. Increase timeouts for long-running operations

### Event Issues

**Problem**: Not receiving expected events
**Solution**:
1. Verify subscription is active
2. Check event filtering conditions
3. Ensure callback URL is accessible
4. Test WebSocket connection directly
5. Check for network issues between systems

### Integration Logs

To troubleshoot integration issues, check these logs:

```bash
# View Synthesis logs
tail -f /var/log/tekton/synthesis.log

# Filter for specific integration errors
grep "integration error" /var/log/tekton/synthesis.log

# Check execution logs
grep "execution_id=your-execution-id" /var/log/tekton/synthesis.log

# View WebSocket connection logs
grep "websocket" /var/log/tekton/synthesis.log
```