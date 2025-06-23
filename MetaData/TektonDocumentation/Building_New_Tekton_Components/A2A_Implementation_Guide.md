# A2A Protocol Implementation Guide

## Overview

This guide provides step-by-step instructions for implementing A2A Protocol features in Tekton components. The A2A Protocol enables standardized agent-to-agent communication with support for tasks, conversations, workflows, and secure messaging.

## Table of Contents

1. [Setting Up A2A in Your Component](#setting-up-a2a-in-your-component)
2. [Implementing an A2A Agent](#implementing-an-a2a-agent)
3. [Working with Tasks](#working-with-tasks)
4. [Multi-Agent Conversations](#multi-agent-conversations)
5. [Building Workflows](#building-workflows)
6. [Security Implementation](#security-implementation)
7. [Testing A2A Features](#testing-a2a-features)
8. [Best Practices](#best-practices)

## Setting Up A2A in Your Component

### 1. Install Dependencies

Add the Tekton A2A dependencies to your component:

```python
# In your requirements.txt or setup.py
tekton-core>=0.1.0
```

### 2. Initialize A2A Client

```python
from tekton.a2a.client import A2AClient
from tekton.a2a.agent import AgentCard

# Create your agent card
agent_card = AgentCard(
    name="MyComponent",
    description="Component that does amazing things",
    version="1.0.0",
    capabilities=["data_processing", "analysis"],
    supported_methods=["process.data", "analyze.results"],
    endpoint="http://localhost:8010/"
)

# Initialize client
a2a_client = A2AClient(
    hermes_url="http://localhost:8001",
    agent_card=agent_card
)

# Register with Hermes
agent_id = await a2a_client.register()
```

## Implementing an A2A Agent

### Basic Agent Structure

```python
from tekton.a2a.agent import Agent, AgentCard
from tekton.a2a.methods import MethodDispatcher
import asyncio

class MyAgent(Agent):
    def __init__(self):
        # Define agent card
        card = AgentCard(
            name="DataProcessor",
            description="Processes various data formats",
            version="1.0.0",
            capabilities=["csv_processing", "json_processing"],
            supported_methods=["process.csv", "process.json"]
        )
        super().__init__(card)
        
        # Set up method dispatcher
        self.dispatcher = MethodDispatcher()
        self._register_methods()
    
    def _register_methods(self):
        """Register custom methods"""
        self.dispatcher.register("process.csv", self.process_csv)
        self.dispatcher.register("process.json", self.process_json)
    
    async def process_csv(self, file_path: str, **kwargs):
        """Process CSV file"""
        # Implementation here
        return {"status": "processed", "rows": 100}
    
    async def process_json(self, data: dict, **kwargs):
        """Process JSON data"""
        # Implementation here
        return {"status": "processed", "items": len(data)}
    
    async def start(self):
        """Start the agent"""
        # Register with Hermes
        await self.register()
        
        # Start heartbeat loop
        asyncio.create_task(self.heartbeat_loop())
        
        # Start processing requests
        await self.listen_for_requests()
```

### Handling Incoming Requests

```python
async def handle_request(self, request: JSONRPCRequest):
    """Handle incoming JSON-RPC request"""
    try:
        # Check if we support the method
        if request.method in self.dispatcher.methods:
            result = await self.dispatcher.dispatch(request)
            return create_success_response(request.id, result)
        else:
            # Forward to Hermes if we don't support it
            return await self.a2a_client.forward_request(request)
    except Exception as e:
        return create_error_response(
            request.id, 
            InternalError(str(e))
        )
```

## Working with Tasks

### Creating Tasks

```python
# Create a task
task_id = await a2a_client.create_task(
    name="Process Customer Data",
    description="Validate and transform customer records",
    priority="high",
    metadata={
        "source": "crm_system",
        "record_count": 5000
    }
)

# Monitor task with SSE
async for event in a2a_client.stream_task_events(task_id):
    if event.type == "task.state_changed":
        print(f"Task state: {event.data['new_state']}")
    elif event.type == "task.progress":
        print(f"Progress: {event.data['progress']}%")
```

### Processing Assigned Tasks

```python
class TaskProcessor:
    def __init__(self, a2a_client):
        self.a2a_client = a2a_client
        self.running_tasks = {}
    
    async def start_processing(self):
        """Start processing assigned tasks"""
        # Subscribe to task assignments
        async for event in self.a2a_client.stream_events(
            event_type="task.assigned",
            agent_id=self.a2a_client.agent_id
        ):
            task_id = event.data["task_id"]
            asyncio.create_task(self.process_task(task_id))
    
    async def process_task(self, task_id: str):
        """Process a single task"""
        try:
            # Get task details
            task = await self.a2a_client.get_task(task_id)
            
            # Update state to in_progress
            await self.a2a_client.update_task_state(
                task_id, "in_progress"
            )
            
            # Process based on task type
            if task.name.startswith("Process"):
                result = await self.process_data(task)
            else:
                result = await self.analyze_data(task)
            
            # Complete the task
            await self.a2a_client.complete_task(
                task_id, result=result
            )
            
        except Exception as e:
            # Fail the task
            await self.a2a_client.fail_task(
                task_id, error=str(e)
            )
    
    async def process_data(self, task):
        """Process data task"""
        total_items = task.metadata.get("record_count", 0)
        
        for i in range(0, total_items, 100):
            # Process batch
            await asyncio.sleep(0.1)  # Simulate work
            
            # Update progress
            progress = (i / total_items) * 100
            await self.a2a_client.update_task_progress(
                task.id, progress
            )
        
        return {"processed": total_items}
```

## Multi-Agent Conversations

### Creating and Managing Conversations

```python
from tekton.a2a.conversation import ConversationManager

class CollaborativeAgent:
    def __init__(self, a2a_client):
        self.a2a_client = a2a_client
        self.conversations = {}
    
    async def start_design_discussion(self, topic: str):
        """Start a design discussion with other agents"""
        # Create conversation
        conv_id = await self.a2a_client.create_conversation(
            topic=topic,
            description="Collaborative design session",
            turn_taking_mode="round_robin"
        )
        
        # Invite specific agents
        agents = await self.a2a_client.find_agents_by_capability(
            "system_design"
        )
        
        for agent_id in agents[:3]:  # Invite first 3
            await self.invite_to_conversation(conv_id, agent_id)
        
        # Start participating
        await self.participate_in_conversation(conv_id)
    
    async def participate_in_conversation(self, conv_id: str):
        """Actively participate in a conversation"""
        # Join the conversation
        await self.a2a_client.join_conversation(
            conv_id, role="participant"
        )
        
        # Listen for messages
        async for event in self.a2a_client.stream_conversation_events(conv_id):
            if event.type == "conversation.message":
                await self.handle_message(conv_id, event.data)
            elif event.type == "conversation.turn_granted":
                await self.take_turn(conv_id)
    
    async def handle_message(self, conv_id: str, message: dict):
        """Process incoming conversation message"""
        content = message["content"]
        sender = message["sender_id"]
        
        # Analyze message with NLP (example)
        if "proposal" in content.lower():
            # Store proposal for later response
            self.conversations[conv_id] = {
                "proposal": content,
                "proposer": sender
            }
    
    async def take_turn(self, conv_id: str):
        """Take our turn to speak"""
        conv_data = self.conversations.get(conv_id, {})
        
        if "proposal" in conv_data:
            # Respond to proposal
            response = f"I analyzed the proposal and suggest: ..."
            await self.a2a_client.send_conversation_message(
                conv_id, response
            )
```

### Implementing Turn-Taking Modes

```python
class ModeratedDiscussion:
    """Handle moderated conversations"""
    
    async def moderate_conversation(self, conv_id: str):
        """Act as conversation moderator"""
        participants = []
        pending_requests = []
        
        async for event in self.a2a_client.stream_conversation_events(conv_id):
            if event.type == "conversation.turn_requested":
                agent_id = event.data["agent_id"]
                pending_requests.append(agent_id)
                
                # Grant turns in order
                if len(pending_requests) == 1:
                    await self.a2a_client.grant_turn(conv_id, agent_id)
            
            elif event.type == "conversation.turn_completed":
                # Remove from pending and grant next
                if pending_requests:
                    pending_requests.pop(0)
                    if pending_requests:
                        next_agent = pending_requests[0]
                        await self.a2a_client.grant_turn(
                            conv_id, next_agent
                        )
```

## Building Workflows

### Creating Complex Workflows

```python
from tekton.a2a.task_coordination import TaskCoordinator, TaskDependency

class WorkflowBuilder:
    def __init__(self, a2a_client):
        self.a2a_client = a2a_client
    
    async def create_data_pipeline(self, data_source: str):
        """Create a data processing pipeline"""
        # Create individual tasks
        extract_task = await self.a2a_client.create_task(
            name="Extract Data",
            metadata={"source": data_source}
        )
        
        validate_task = await self.a2a_client.create_task(
            name="Validate Data",
            metadata={"rules": ["schema", "completeness"]}
        )
        
        transform_task = await self.a2a_client.create_task(
            name="Transform Data",
            metadata={"format": "normalized"}
        )
        
        load_task = await self.a2a_client.create_task(
            name="Load Data",
            metadata={"destination": "warehouse"}
        )
        
        # Create pipeline workflow
        workflow_id = await self.a2a_client.create_pipeline_workflow(
            name="ETL Pipeline",
            stages=["extraction", "validation", "transformation", "loading"]
        )
        
        # Add tasks with dependencies
        await self.a2a_client.add_workflow_task(
            workflow_id, extract_task, stage="extraction"
        )
        
        await self.a2a_client.add_workflow_task(
            workflow_id, validate_task, 
            stage="validation",
            dependencies=[{
                "predecessor_id": extract_task,
                "type": "finish_to_start"
            }]
        )
        
        await self.a2a_client.add_workflow_task(
            workflow_id, transform_task,
            stage="transformation", 
            dependencies=[{
                "predecessor_id": validate_task,
                "type": "finish_to_start"
            }]
        )
        
        await self.a2a_client.add_workflow_task(
            workflow_id, load_task,
            stage="loading",
            dependencies=[{
                "predecessor_id": transform_task,
                "type": "finish_to_start"
            }]
        )
        
        # Start the workflow
        await self.a2a_client.start_workflow(workflow_id)
        
        return workflow_id
```

### Conditional Workflows

```python
async def create_conditional_workflow(self):
    """Create workflow with conditional branches"""
    # Create workflow with conditional pattern
    workflow_id = await self.a2a_client.create_workflow(
        name="Conditional Processing",
        pattern="conditional"
    )
    
    # Add initial analysis task
    analysis_task = await self.a2a_client.create_task(
        name="Analyze Data Quality"
    )
    
    await self.a2a_client.add_workflow_task(
        workflow_id, analysis_task
    )
    
    # Add conditional rule
    rule = {
        "condition": "task_result.quality_score > 0.8",
        "true_action": "proceed_to_processing",
        "false_action": "data_cleanup_required"
    }
    
    await self.a2a_client.add_workflow_rule(
        workflow_id, rule, after_task=analysis_task
    )
    
    # Add conditional branches
    process_task = await self.a2a_client.create_task(
        name="Process High Quality Data"
    )
    
    cleanup_task = await self.a2a_client.create_task(
        name="Clean and Repair Data"
    )
    
    # Link tasks based on conditions
    await self.a2a_client.add_conditional_task(
        workflow_id, process_task, 
        condition="proceed_to_processing"
    )
    
    await self.a2a_client.add_conditional_task(
        workflow_id, cleanup_task,
        condition="data_cleanup_required"
    )
```

## Security Implementation

### Setting Up Authentication

```python
from tekton.a2a.security import TokenManager, SecurityContext

class SecureAgent:
    def __init__(self):
        self.token_manager = TokenManager()
        self.access_token = None
        self.refresh_token = None
    
    async def authenticate(self):
        """Authenticate with Hermes"""
        response = await self.a2a_client.request(
            "auth.login",
            agent_id=self.agent_id,
            password=self.agent_password
        )
        
        self.access_token = response["access_token"]
        self.refresh_token = response["refresh_token"]
        
        # Set token in client
        self.a2a_client.set_auth_token(self.access_token)
        
        # Schedule token refresh
        asyncio.create_task(self.refresh_token_periodically())
    
    async def refresh_token_periodically(self):
        """Refresh token before expiry"""
        while True:
            # Wait 23 hours (token expires in 24)
            await asyncio.sleep(23 * 60 * 60)
            
            try:
                response = await self.a2a_client.request(
                    "auth.refresh",
                    refresh_token=self.refresh_token
                )
                
                self.access_token = response["access_token"]
                self.refresh_token = response["refresh_token"]
                self.a2a_client.set_auth_token(self.access_token)
                
            except Exception as e:
                # Re-authenticate if refresh fails
                await self.authenticate()
```

### Implementing Message Signing

```python
from tekton.a2a.security import MessageSigner
import hmac
import hashlib
import json

class SecureMessaging:
    def __init__(self, secret_key: str):
        self.signer = MessageSigner(secret_key)
    
    async def send_signed_request(self, method: str, params: dict):
        """Send a signed request"""
        # Create request
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": generate_id()
        }
        
        # Sign the request
        signature = self.signer.sign_message(
            request, self.agent_id
        )
        
        # Send with signature header
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-A2A-Signature": signature
        }
        
        response = await self.http_client.post(
            self.hermes_url,
            json=request,
            headers=headers
        )
        
        return response.json()
```

### Role-Based Method Implementation

```python
from tekton.a2a.security import require_permission, Permission

class AdminAgent:
    """Agent with administrative capabilities"""
    
    @require_permission(Permission.SYSTEM_ADMIN)
    async def shutdown_system(self, security_context=None):
        """Shutdown the entire system (admin only)"""
        # Implementation
        pass
    
    @require_permission(Permission.TASK_DELETE)
    async def delete_task(self, task_id: str, security_context=None):
        """Delete a task (requires permission)"""
        # Implementation
        pass
    
    @require_permission(Permission.AGENT_UPDATE, resource_type="agent")
    async def update_agent_status(
        self, agent_id: str, status: str, 
        security_context=None
    ):
        """Update another agent's status"""
        # Implementation
        pass
```

## Testing A2A Features

### Unit Testing

```python
import pytest
from unittest.mock import Mock, AsyncMock
from tekton.a2a.agent import Agent, AgentCard
from tekton.a2a.task import Task, TaskState

class TestAgent:
    @pytest.fixture
    def agent(self):
        card = AgentCard(
            name="TestAgent",
            description="Test agent",
            version="1.0.0",
            capabilities=["testing"],
            supported_methods=["test.method"],
            endpoint="http://localhost:9999/"
        )
        return Agent(card)
    
    @pytest.mark.asyncio
    async def test_agent_registration(self, agent):
        """Test agent can register"""
        # Mock the client
        agent.a2a_client = AsyncMock()
        agent.a2a_client.request.return_value = {
            "agent_id": "test-123"
        }
        
        # Register
        agent_id = await agent.register()
        
        # Verify
        assert agent_id == "test-123"
        agent.a2a_client.request.assert_called_once_with(
            "agent.register",
            agent_card=agent.agent_card.dict()
        )
```

### Integration Testing

```python
import asyncio
from tekton.a2a.client import A2AClient

class TestA2AIntegration:
    @pytest.mark.integration
    async def test_task_lifecycle(self):
        """Test complete task lifecycle"""
        # Create two agents
        processor = A2AClient(
            hermes_url="http://localhost:8001",
            agent_card=create_processor_card()
        )
        
        coordinator = A2AClient(
            hermes_url="http://localhost:8001",
            agent_card=create_coordinator_card()
        )
        
        # Register both
        processor_id = await processor.register()
        coordinator_id = await coordinator.register()
        
        # Coordinator creates task
        task_id = await coordinator.create_task(
            name="Process Data",
            priority="high"
        )
        
        # Coordinator assigns to processor
        await coordinator.assign_task(task_id, processor_id)
        
        # Processor receives assignment via SSE
        events = []
        async for event in processor.stream_events(
            agent_id=processor_id,
            timeout=5
        ):
            events.append(event)
            if event.type == "task.assigned":
                break
        
        assert any(e.type == "task.assigned" for e in events)
        
        # Processor completes task
        await processor.complete_task(
            task_id, 
            result={"processed": 100}
        )
        
        # Verify task is completed
        task = await coordinator.get_task(task_id)
        assert task.state == "completed"
        assert task.result["processed"] == 100
```

## Best Practices

### 1. Error Handling

Always implement comprehensive error handling:

```python
from tekton.a2a.errors import (
    TaskNotFoundError, UnauthorizedError, RateLimitError
)

async def safe_task_update(self, task_id: str, state: str):
    """Safely update task state with retries"""
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            await self.a2a_client.update_task_state(task_id, state)
            return
            
        except TaskNotFoundError:
            # Task doesn't exist, can't retry
            raise
            
        except UnauthorizedError:
            # Re-authenticate and retry
            await self.authenticate()
            
        except RateLimitError as e:
            # Wait and retry
            wait_time = e.data.get("retry_after", retry_delay)
            await asyncio.sleep(wait_time)
            retry_delay *= 2
            
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(retry_delay)
```

### 2. Connection Management

Maintain persistent connections efficiently:

```python
class ConnectionManager:
    def __init__(self):
        self.connections = {}
        self.reconnect_tasks = {}
    
    async def get_connection(self, agent_id: str):
        """Get or create connection to agent"""
        if agent_id not in self.connections:
            self.connections[agent_id] = await self.create_connection(
                agent_id
            )
        
        conn = self.connections[agent_id]
        if not conn.is_alive():
            # Reconnect if needed
            await self.reconnect(agent_id)
        
        return conn
    
    async def reconnect(self, agent_id: str):
        """Reconnect with exponential backoff"""
        if agent_id in self.reconnect_tasks:
            return  # Already reconnecting
        
        self.reconnect_tasks[agent_id] = asyncio.create_task(
            self._reconnect_with_backoff(agent_id)
        )
```

### 3. Resource Cleanup

Always clean up resources properly:

```python
class CleanupMixin:
    async def __aenter__(self):
        await self.startup()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.shutdown()
    
    async def shutdown(self):
        """Clean shutdown"""
        # Cancel running tasks
        for task in self.running_tasks.values():
            task.cancel()
        
        # Close connections
        for conn in self.connections.values():
            await conn.close()
        
        # Unregister from Hermes
        if self.agent_id:
            await self.a2a_client.unregister()
```

### 4. Monitoring and Logging

Implement comprehensive monitoring:

```python
import structlog

logger = structlog.get_logger()

class MonitoredAgent:
    async def process_task(self, task_id: str):
        """Process task with monitoring"""
        start_time = time.time()
        
        logger.info(
            "task_processing_started",
            task_id=task_id,
            agent_id=self.agent_id
        )
        
        try:
            result = await self._do_processing(task_id)
            
            duration = time.time() - start_time
            logger.info(
                "task_processing_completed",
                task_id=task_id,
                duration=duration,
                result=result
            )
            
            # Report metrics
            await self.metrics_client.record(
                "task_processing_time",
                duration,
                tags={"agent": self.agent_id}
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "task_processing_failed",
                task_id=task_id,
                error=str(e),
                exc_info=True
            )
            raise
```

## Conclusion

The A2A Protocol provides a powerful framework for building collaborative agent systems. By following these patterns and best practices, you can create robust, scalable agents that work together effectively within the Tekton ecosystem.

For more examples and advanced patterns, see the test suites in `/tests/unit/a2a/` and `/tests/integration/`.