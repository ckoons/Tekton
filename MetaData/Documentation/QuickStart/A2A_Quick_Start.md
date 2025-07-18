# A2A Protocol Quick Start Tutorial

## Introduction

This tutorial will help you get started with the A2A (Agent-to-Agent) Protocol in Tekton. By the end of this tutorial, you'll have created a simple agent that can communicate with other agents, process tasks, and participate in conversations.

## Prerequisites

- Python 3.9 or higher
- Tekton environment set up
- Hermes running on localhost:8001

## Step 1: Create Your First Agent

Let's create a simple calculator agent that can perform basic math operations.

### 1.1 Create the Agent File

Create a file called `calculator_agent.py`:

```python
import asyncio
from tekton.a2a.agent import Agent, AgentCard
from tekton.a2a.client import A2AClient
from tekton.a2a.methods import MethodDispatcher
from tekton.a2a.jsonrpc import JSONRPCRequest, create_success_response

class CalculatorAgent(Agent):
    def __init__(self):
        # Create agent card describing our capabilities
        card = AgentCard(
            name="Calculator",
            description="Simple calculator agent for basic math",
            version="1.0.0",
            capabilities=["arithmetic", "calculation"],
            supported_methods=[
                "calc.add",
                "calc.subtract", 
                "calc.multiply",
                "calc.divide"
            ],
            endpoint="http://localhost:8100/"
        )
        
        super().__init__(card)
        
        # Initialize method dispatcher
        self.dispatcher = MethodDispatcher()
        self._register_methods()
    
    def _register_methods(self):
        """Register our calculation methods"""
        self.dispatcher.register("calc.add", self.add)
        self.dispatcher.register("calc.subtract", self.subtract)
        self.dispatcher.register("calc.multiply", self.multiply)
        self.dispatcher.register("calc.divide", self.divide)
    
    async def add(self, a: float, b: float, **kwargs) -> float:
        """Add two numbers"""
        return a + b
    
    async def subtract(self, a: float, b: float, **kwargs) -> float:
        """Subtract b from a"""
        return a - b
    
    async def multiply(self, a: float, b: float, **kwargs) -> float:
        """Multiply two numbers"""
        return a * b
    
    async def divide(self, a: float, b: float, **kwargs) -> float:
        """Divide a by b"""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b

async def main():
    # Create and start the agent
    agent = CalculatorAgent()
    
    # Create A2A client for communication with Hermes
    agent.a2a_client = A2AClient(
        hermes_url="http://localhost:8001",
        agent_card=agent.agent_card
    )
    
    # Register with Hermes
    print("Registering with Hermes...")
    agent_id = await agent.register()
    print(f"Registered with ID: {agent_id}")
    
    # Start heartbeat to stay registered
    asyncio.create_task(agent.heartbeat_loop())
    
    print("Calculator agent is ready!")
    print("Supported methods:", agent.agent_card.supported_methods)
    
    # Keep running
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
        await agent.unregister()

if __name__ == "__main__":
    asyncio.run(main())
```

### 1.2 Run Your Agent

```bash
python calculator_agent.py
```

You should see:
```
Registering with Hermes...
Registered with ID: agent-calc-123
Calculator agent is ready!
Supported methods: ['calc.add', 'calc.subtract', 'calc.multiply', 'calc.divide']
```

## Step 2: Create a Client Agent

Now let's create another agent that uses the calculator.

### 2.1 Create the Client

Create `math_student_agent.py`:

```python
import asyncio
from tekton.a2a.agent import Agent, AgentCard
from tekton.a2a.client import A2AClient

class MathStudentAgent(Agent):
    def __init__(self):
        card = AgentCard(
            name="MathStudent",
            description="Agent that needs help with math",
            version="1.0.0",
            capabilities=["learning"],
            supported_methods=[],
            endpoint="http://localhost:8101/"
        )
        super().__init__(card)
    
    async def do_homework(self):
        """Use the calculator to solve math problems"""
        # Find calculator agents
        print("Looking for a calculator...")
        calc_agents = await self.a2a_client.find_agents_by_capability(
            "arithmetic"
        )
        
        if not calc_agents:
            print("No calculator found!")
            return
        
        calc_id = calc_agents[0]
        print(f"Found calculator: {calc_id}")
        
        # Solve some problems
        problems = [
            ("calc.add", {"a": 15, "b": 27}),
            ("calc.multiply", {"a": 6, "b": 7}),
            ("calc.divide", {"a": 100, "b": 4}),
            ("calc.subtract", {"a": 50, "b": 13})
        ]
        
        for method, params in problems:
            result = await self.a2a_client.request(
                method, 
                **params,
                target_agent=calc_id
            )
            
            if method == "calc.add":
                print(f"{params['a']} + {params['b']} = {result}")
            elif method == "calc.multiply":
                print(f"{params['a']} × {params['b']} = {result}")
            elif method == "calc.divide":
                print(f"{params['a']} ÷ {params['b']} = {result}")
            elif method == "calc.subtract":
                print(f"{params['a']} - {params['b']} = {result}")

async def main():
    # Create student agent
    student = MathStudentAgent()
    student.a2a_client = A2AClient(
        hermes_url="http://localhost:8001",
        agent_card=student.agent_card
    )
    
    # Register
    print("Math student registering...")
    await student.register()
    
    # Wait a moment for calculator to be ready
    await asyncio.sleep(2)
    
    # Do homework
    print("\nDoing math homework:")
    await student.do_homework()
    
    # Cleanup
    await student.unregister()

if __name__ == "__main__":
    asyncio.run(main())
```

### 2.2 Run Both Agents

In one terminal:
```bash
python calculator_agent.py
```

In another terminal:
```bash
python math_student_agent.py
```

You should see the math problems being solved!

## Step 3: Working with Tasks

Let's enhance our calculator to process tasks asynchronously.

### 3.1 Task-Aware Calculator

Update `calculator_agent.py` to handle tasks:

```python
class TaskCalculatorAgent(CalculatorAgent):
    def __init__(self):
        super().__init__()
        # Update capabilities
        self.agent_card.capabilities.append("task_processing")
    
    async def start_task_processor(self):
        """Process assigned calculation tasks"""
        print("Starting task processor...")
        
        # Subscribe to task assignments
        async for event in self.a2a_client.stream_events(
            event_type="task.assigned",
            agent_id=self.agent_id
        ):
            task_id = event.data["task_id"]
            asyncio.create_task(self.process_task(task_id))
    
    async def process_task(self, task_id: str):
        """Process a calculation task"""
        try:
            # Get task details
            task = await self.a2a_client.get_task(task_id)
            print(f"Processing task: {task.name}")
            
            # Update state
            await self.a2a_client.update_task_state(
                task_id, "in_progress"
            )
            
            # Extract calculation from metadata
            operation = task.metadata.get("operation")
            a = task.metadata.get("a", 0)
            b = task.metadata.get("b", 0)
            
            # Perform calculation
            if operation == "add":
                result = await self.add(a, b)
            elif operation == "multiply":
                result = await self.multiply(a, b)
            else:
                raise ValueError(f"Unknown operation: {operation}")
            
            # Complete task
            await self.a2a_client.complete_task(
                task_id,
                result={"answer": result}
            )
            print(f"Task {task_id} completed: {result}")
            
        except Exception as e:
            await self.a2a_client.fail_task(
                task_id,
                error=str(e)
            )
```

### 3.2 Create Tasks

Create `task_creator.py`:

```python
import asyncio
from tekton.a2a.client import A2AClient
from tekton.a2a.agent import AgentCard

async def create_calculation_tasks():
    # Create a simple client
    client = A2AClient(
        hermes_url="http://localhost:8001",
        agent_card=AgentCard(
            name="TaskCreator",
            description="Creates calculation tasks",
            version="1.0.0",
            capabilities=["task_creation"],
            supported_methods=[],
            endpoint="http://localhost:8102/"
        )
    )
    
    # Register
    await client.register()
    
    # Create some calculation tasks
    tasks = [
        ("Calculate Sum", "add", 100, 200),
        ("Calculate Product", "multiply", 12, 15),
        ("Complex Calculation", "add", 3.14159, 2.71828)
    ]
    
    for name, op, a, b in tasks:
        task_id = await client.create_task(
            name=name,
            description=f"Calculate {op} of {a} and {b}",
            priority="medium",
            metadata={
                "operation": op,
                "a": a,
                "b": b
            }
        )
        print(f"Created task: {task_id} - {name}")
        
        # Find calculator and assign
        calculators = await client.find_agents_by_capability(
            "task_processing"
        )
        
        if calculators:
            await client.assign_task(task_id, calculators[0])
            print(f"Assigned to: {calculators[0]}")
    
    # Wait for results
    await asyncio.sleep(5)
    
    # Cleanup
    await client.unregister()

if __name__ == "__main__":
    asyncio.run(create_calculation_tasks())
```

## Step 4: Multi-Agent Conversations

Let's create agents that can discuss math problems together.

### 4.1 Conversational Math Tutor

Create `math_tutor_agent.py`:

```python
import asyncio
from tekton.a2a.agent import Agent, AgentCard
from tekton.a2a.client import A2AClient

class MathTutorAgent(Agent):
    def __init__(self):
        card = AgentCard(
            name="MathTutor",
            description="Helps students learn math",
            version="1.0.0",
            capabilities=["teaching", "math_expertise"],
            supported_methods=["tutor.explain"],
            endpoint="http://localhost:8103/"
        )
        super().__init__(card)
    
    async def start_tutoring_session(self):
        """Start a tutoring conversation"""
        # Create a conversation
        conv_id = await self.a2a_client.create_conversation(
            topic="Math Problem Solving",
            description="Interactive math tutoring session",
            turn_taking_mode="free_form"
        )
        
        print(f"Started tutoring session: {conv_id}")
        
        # Wait for students to join
        await asyncio.sleep(2)
        
        # Send welcome message
        await self.a2a_client.send_conversation_message(
            conv_id,
            "Welcome to the math tutoring session! What would you like to learn today?"
        )
        
        # Listen for questions
        async for event in self.a2a_client.stream_conversation_events(conv_id):
            if event.type == "conversation.message":
                await self.handle_student_message(
                    conv_id, 
                    event.data
                )
    
    async def handle_student_message(self, conv_id: str, message: dict):
        """Respond to student questions"""
        content = message["content"].lower()
        sender = message["sender_id"]
        
        if sender == self.agent_id:
            return  # Don't respond to ourselves
        
        # Simple keyword-based responses
        if "add" in content or "addition" in content:
            response = "Addition is combining two or more numbers to get their sum. For example, 3 + 4 = 7."
        elif "multiply" in content:
            response = "Multiplication is repeated addition. For example, 3 × 4 means adding 3 four times: 3 + 3 + 3 + 3 = 12."
        elif "divide" in content:
            response = "Division splits a number into equal parts. For example, 12 ÷ 3 = 4 means 12 split into 3 equal groups gives 4 in each group."
        else:
            response = "That's an interesting question! Can you be more specific about what you'd like to know?"
        
        # Send response
        await self.a2a_client.send_conversation_message(
            conv_id,
            response,
            reply_to=message.get("message_id")
        )
```

### 4.2 Student Participating in Conversation

Update the student agent to join conversations:

```python
async def join_tutoring_session(self):
    """Join a tutoring conversation"""
    # Find active conversations
    conversations = await self.a2a_client.list_conversations(
        state="active"
    )
    
    for conv in conversations:
        if "tutoring" in conv.topic.lower():
            # Join the conversation
            await self.a2a_client.join_conversation(
                conv.id,
                role="participant"
            )
            
            print(f"Joined tutoring session: {conv.topic}")
            
            # Ask a question
            await self.a2a_client.send_conversation_message(
                conv.id,
                "How does multiplication work?"
            )
            
            # Listen for responses
            async for event in self.a2a_client.stream_conversation_events(
                conv.id,
                timeout=30
            ):
                if event.type == "conversation.message":
                    msg = event.data
                    if msg["sender_id"] != self.agent_id:
                        print(f"Tutor says: {msg['content']}")
```

## Step 5: Building a Simple Workflow

Let's create a workflow that solves complex math problems step by step.

### 5.1 Workflow Example

Create `math_workflow.py`:

```python
import asyncio
from tekton.a2a.client import A2AClient
from tekton.a2a.agent import AgentCard

async def solve_quadratic_equation(a: float, b: float, c: float):
    """Solve ax² + bx + c = 0 using a workflow"""
    
    client = A2AClient(
        hermes_url="http://localhost:8001",
        agent_card=AgentCard(
            name="WorkflowCoordinator",
            description="Coordinates math workflows",
            version="1.0.0",
            capabilities=["workflow_management"],
            supported_methods=[],
            endpoint="http://localhost:8104/"
        )
    )
    
    await client.register()
    
    print(f"Solving {a}x² + {b}x + {c} = 0")
    
    # Create tasks for each step
    # Step 1: Calculate discriminant (b² - 4ac)
    task1 = await client.create_task(
        name="Calculate b²",
        metadata={"operation": "multiply", "a": b, "b": b}
    )
    
    task2 = await client.create_task(
        name="Calculate 4ac",
        metadata={"operation": "multiply", "a": 4*a, "b": c}
    )
    
    task3 = await client.create_task(
        name="Calculate discriminant",
        metadata={"operation": "subtract", "depends_on": [task1, task2]}
    )
    
    # Create sequential workflow
    workflow_id = await client.create_sequential_workflow(
        name="Quadratic Equation Solver",
        task_ids=[task1, task2, task3]
    )
    
    # Start workflow
    await client.start_workflow(workflow_id)
    
    print(f"Workflow {workflow_id} started")
    
    # Monitor progress
    async for event in client.stream_workflow_events(workflow_id):
        if event.type == "workflow.task_completed":
            print(f"Completed: {event.data['task_name']}")
        elif event.type == "workflow.completed":
            print("Workflow completed!")
            break
    
    await client.unregister()

if __name__ == "__main__":
    # Solve x² + 5x + 6 = 0
    asyncio.run(solve_quadratic_equation(1, 5, 6))
```

## Step 6: Adding Security

Let's secure our agents with authentication.

### 6.1 Authenticated Agent

Create `secure_agent.py`:

```python
import os
from tekton.a2a.agent import Agent, AgentCard
from tekton.a2a.client import A2AClient

class SecureAgent(Agent):
    def __init__(self):
        card = AgentCard(
            name="SecureCalculator",
            description="Calculator with authentication",
            version="1.0.0",
            capabilities=["secure_arithmetic"],
            supported_methods=["secure.calculate"],
            endpoint="http://localhost:8105/"
        )
        super().__init__(card)
        
        # Store credentials
        self.agent_password = os.getenv(
            "AGENT_PASSWORD", 
            "default-password"
        )
    
    async def authenticate(self):
        """Login to get access token"""
        response = await self.a2a_client.request(
            "auth.login",
            agent_id=self.agent_id,
            password=self.agent_password
        )
        
        # Store tokens
        self.access_token = response["access_token"]
        self.refresh_token = response["refresh_token"]
        
        # Configure client to use token
        self.a2a_client.set_auth_token(self.access_token)
        
        print(f"Authenticated as {response['role']}")
        return response
    
    async def secure_calculate(
        self, 
        expression: str,
        security_context=None
    ):
        """Perform calculation with security context"""
        # Check who's asking
        requester = security_context.agent_id if security_context else "unknown"
        print(f"Calculation requested by: {requester}")
        
        # Simple expression evaluator (BE CAREFUL IN PRODUCTION!)
        # This is just for demonstration
        allowed_chars = "0123456789+-*/() ."
        if all(c in allowed_chars for c in expression):
            try:
                result = eval(expression)
                return {"result": result, "calculated_for": requester}
            except:
                return {"error": "Invalid expression"}
        else:
            return {"error": "Forbidden characters in expression"}

async def main():
    agent = SecureAgent()
    agent.a2a_client = A2AClient(
        hermes_url="http://localhost:8001",
        agent_card=agent.agent_card
    )
    
    # Register
    await agent.register()
    
    # Authenticate
    auth_info = await agent.authenticate()
    print(f"Permissions: {auth_info['permissions']}")
    
    # Now the agent is ready with authentication
    print("Secure agent ready!")
    
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        await agent.unregister()

if __name__ == "__main__":
    asyncio.run(main())
```

## Next Steps

Congratulations! You've learned the basics of the A2A Protocol. Here are some next steps:

1. **Explore Advanced Features**
   - Implement more complex workflows with conditional logic
   - Create agents that learn from interactions
   - Build fault-tolerant agents with retry logic

2. **Integration with Tekton Components**
   - Connect your agents to Athena for knowledge management
   - Use Engram for memory persistence
   - Integrate with Rhetor for natural language processing

3. **Performance Optimization**
   - Implement connection pooling
   - Add caching for frequently accessed data
   - Use batch operations for efficiency

4. **Security Hardening**
   - Implement message signing
   - Add rate limiting
   - Create custom permission schemes

## Troubleshooting

### Common Issues

1. **"Connection refused" errors**
   - Make sure Hermes is running on port 8001
   - Check firewall settings

2. **"Agent not found" errors**
   - Ensure agents are registered before making requests
   - Check that heartbeats are being sent

3. **"Unauthorized" errors**
   - Verify authentication tokens are valid
   - Check token expiration
   - Ensure proper permissions for methods

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Getting Help

- Check the [A2A API Reference](/MetaData/TektonDocumentation/API_Standards/A2A_Protocol_API_Reference.md)
- Read the [Implementation Guide](/MetaData/TektonDocumentation/DeveloperGuides/A2A_Implementation_Guide.md)
- Look at test examples in `/tests/unit/a2a/`

Happy coding with A2A!