# Harmonia Technical Documentation

## Architecture Overview

Harmonia is built around a workflow orchestration engine that enables the definition, execution, and monitoring of complex workflows. The architecture consists of several key components:

### Core Components

1. **Workflow Engine**
   - Central execution environment for workflows
   - Manages workflow state transitions
   - Handles event processing and routing
   - Controls execution flow based on workflow definitions

2. **Component System**
   - Pluggable components that implement specific workflow activities
   - Standard interface for component integration
   - Component lifecycle management
   - Component discovery and registration

3. **Expression Evaluator**
   - Evaluates conditional expressions within workflows
   - Supports complex logic for transition decisions
   - Provides access to workflow state and context
   - Handles variable substitution and template expressions

4. **State Management**
   - Persists workflow state between execution steps
   - Manages state transitions and history
   - Provides state inspection capabilities
   - Implements state scoping (global, workflow, and step levels)

5. **Template Engine**
   - Defines reusable workflow templates
   - Handles template instantiation with parameters
   - Supports template inheritance and composition
   - Manages template versioning

## Internal System Design

### Workflow Execution Pipeline

The workflow execution pipeline follows these stages:

1. **Definition Loading**: Parse and validate workflow definition
2. **Initialization**: Set up initial state and prepare execution context
3. **Step Execution**: Process individual workflow steps
4. **Transition Determination**: Evaluate conditions to select next steps
5. **State Update**: Update workflow state based on execution results
6. **Event Propagation**: Generate and handle events during execution
7. **Completion/Continuation**: Determine if workflow is complete or continues

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Definition     │    │     Step        │    │   Transition    │
│    Loading      ├───►│   Execution     ├───►│  Determination  │
└─────────────────┘    └─────────────────┘    └────────┬────────┘
                                                       │
┌─────────────────┐    ┌─────────────────┐    ┌────────▼────────┐
│  Completion     │    │     Event       │    │     State       │
│  Continuation   │◄───┤   Propagation   │◄───┤     Update      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Component Lifecycle

Components in Harmonia go through a defined lifecycle:

1. **Registration**: Component registers capabilities and metadata
2. **Initialization**: Component initializes with configuration
3. **Activation**: Component becomes available for workflow execution
4. **Execution**: Component processes workflow steps
5. **Deactivation**: Component gracefully shuts down
6. **Unregistration**: Component removes itself from the system

### State Management Implementation

Workflow state is managed through a hierarchical structure:

```python
class WorkflowState:
    def __init__(self, workflow_id):
        self.workflow_id = workflow_id
        self.global_state = {}  # Global state accessible to all steps
        self.step_states = {}   # Per-step state
        self.history = []       # Execution history
        self.metadata = {}      # Workflow metadata
        self.status = "PENDING" # Current workflow status

    def update_step_state(self, step_id, state_update):
        if step_id not in self.step_states:
            self.step_states[step_id] = {}
        self.step_states[step_id].update(state_update)
        
    def get_step_state(self, step_id):
        return self.step_states.get(step_id, {})
        
    def add_history_entry(self, entry):
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            **entry
        })
```

## Expression Evaluation System

Harmonia uses a powerful expression evaluation system to determine workflow transitions and calculate dynamic values:

### Expression Types

1. **Condition Expressions**: Boolean expressions that control transitions
   ```
   state.approval_status == "APPROVED" && state.user.role == "ADMIN"
   ```

2. **Value Expressions**: Expressions that produce values for use in workflow steps
   ```
   "Hello, ${state.user.name}! Your order #${state.order_id} is ${state.status}."
   ```

3. **Function Expressions**: Calls to built-in or custom functions
   ```
   formatDate(state.timestamp, "YYYY-MM-DD")
   ```

### Expression Evaluation Process

1. Parse expression string into abstract syntax tree
2. Resolve variables from workflow state
3. Execute operations according to expression semantics
4. Return resulting value for use in workflow

```python
class ExpressionEvaluator:
    def __init__(self, state_provider):
        self.state_provider = state_provider
        self.functions = self._register_standard_functions()
        
    def evaluate(self, expression, context=None):
        context = context or {}
        parsed_expr = self._parse(expression)
        return self._evaluate_node(parsed_expr, context)
        
    def _evaluate_node(self, node, context):
        # Implementation handles different node types:
        # - Literal values
        # - Variable references
        # - Function calls
        # - Operators
        # ...
```

## Template System

The template system allows for reusable workflow definitions:

### Template Structure

```json
{
  "id": "approval_process",
  "version": "1.0",
  "parameters": [
    {"name": "approver_email", "type": "string", "required": true},
    {"name": "item_name", "type": "string", "required": true},
    {"name": "expiration_hours", "type": "number", "default": 24}
  ],
  "steps": [
    {
      "id": "submit_request",
      "type": "notification",
      "config": {
        "recipient": "${parameters.approver_email}",
        "subject": "Approval needed for ${parameters.item_name}",
        "message": "Please approve this request within ${parameters.expiration_hours} hours."
      },
      "transitions": [
        {"to": "check_approval", "automatic": true}
      ]
    },
    // Additional steps...
  ]
}
```

### Template Instantiation

When instantiating a template, parameters are provided and resolved:

```json
{
  "template_id": "approval_process",
  "template_version": "1.0",
  "parameters": {
    "approver_email": "manager@example.com",
    "item_name": "Server upgrade",
    "expiration_hours": 48
  }
}
```

## Integration Patterns

### LLM Integration

Harmonia integrates with language models through a specialized adapter:

```python
class LLMAdapter:
    def __init__(self, model_provider, config=None):
        self.model_provider = model_provider
        self.config = config or {}
        
    async def process_step(self, step_config, workflow_state):
        prompt = self._build_prompt(step_config, workflow_state)
        response = await self._send_to_llm(prompt)
        return self._process_response(response, step_config)
        
    def _build_prompt(self, step_config, workflow_state):
        # Construct prompt template with state variables
        template = step_config.get("prompt_template")
        return self._substitute_variables(template, workflow_state)
```

### External System Integration

Components can integrate with external systems through standardized connectors:

```python
class APIConnector:
    def __init__(self, base_url, auth_config=None):
        self.base_url = base_url
        self.auth_config = auth_config or {}
        self.session = None
        
    async def initialize(self):
        self.session = aiohttp.ClientSession()
        if self.auth_config.get("type") == "oauth":
            await self._perform_oauth_flow()
            
    async def execute_request(self, method, path, params=None, data=None):
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        async with self.session.request(method, url, params=params, json=data) as response:
            return {
                "status_code": response.status,
                "headers": dict(response.headers),
                "data": await response.json()
            }
```

## Error Handling and Recovery

Harmonia implements robust error handling and recovery mechanisms:

1. **Step-Level Retry**: Individual steps can be configured with retry policies
   ```json
   {
     "id": "api_call",
     "type": "http_request",
     "retry": {
       "max_attempts": 3,
       "initial_delay_ms": 1000,
       "backoff_factor": 2,
       "retriable_errors": ["CONNECTION_ERROR", "TIMEOUT", "SERVER_ERROR"]
     }
   }
   ```

2. **Error Transitions**: Workflows can define specific transitions for error cases
   ```json
   {
     "transitions": [
       {"to": "success_step", "condition": "state.status == 'SUCCESS'"},
       {"to": "error_handling", "condition": "state.status == 'ERROR'"}
     ]
   }
   ```

3. **Global Error Handlers**: Define global error handlers for specific error types
   ```json
   {
     "error_handlers": [
       {
         "error_type": "VALIDATION_ERROR",
         "handler_step": "validation_error_handler"
       },
       {
         "error_type": "TIMEOUT",
         "handler_step": "timeout_handler"
       }
     ]
   }
   ```

## Workflow Data Model

The core data model consists of these primary entities:

### Workflow Definition

```python
class WorkflowDefinition:
    id: str                     # Unique workflow identifier
    version: str                # Workflow version
    steps: List[StepDefinition] # Steps in the workflow
    inputs: Dict[str, Any]      # Input schema definition
    outputs: Dict[str, Any]     # Output schema definition
    error_handlers: List[ErrorHandler] # Global error handlers
    metadata: Dict[str, Any]    # Workflow metadata
```

### Step Definition

```python
class StepDefinition:
    id: str                     # Unique step identifier
    type: str                   # Step type (determines execution behavior)
    config: Dict[str, Any]      # Step-specific configuration
    transitions: List[Transition] # Possible transitions from this step
    retry: Optional[RetryPolicy] # Retry configuration
    timeout_ms: Optional[int]   # Step execution timeout
```

### Transition

```python
class Transition:
    to: str                     # Target step ID
    condition: Optional[str]    # Condition expression for this transition
    automatic: bool = False     # Whether transition is automatic
```

### Execution Instance

```python
class WorkflowExecution:
    id: str                     # Unique execution identifier
    workflow_id: str            # Reference to workflow definition
    workflow_version: str       # Workflow version being executed
    current_step_id: Optional[str] # Currently executing step
    state: WorkflowState        # Current execution state
    status: str                 # Execution status (RUNNING, COMPLETED, etc.)
    start_time: datetime        # When execution started
    end_time: Optional[datetime] # When execution completed (if done)
```

## Performance Considerations

Harmonia is designed for high performance in workflow orchestration:

1. **Asynchronous Execution**: All operations use asynchronous patterns to maximize throughput
2. **State Minimization**: Only essential state is persisted to reduce storage requirements
3. **Caching**: Frequently accessed definitions and configurations are cached
4. **Parallelism**: Where possible, independent workflow steps execute in parallel
5. **Resource Limiting**: Configurable limits on concurrent executions protect system resources

## Security Considerations

Harmonia implements several security measures:

1. **Expression Sandboxing**: Expressions are evaluated in a sandboxed environment
2. **Input Validation**: All workflow inputs are validated against schemas
3. **Permission Checking**: Workflow operations check against permission policies
4. **Secret Handling**: Sensitive data is encrypted and never logged
5. **Audit Logging**: All significant operations are logged for auditing

## Deployment Considerations

When deploying Harmonia, consider these recommendations:

1. **Scalability**: Deploy multiple instances behind a load balancer for horizontal scaling
2. **State Storage**: Use a reliable database for workflow state persistence
3. **Monitoring**: Implement metrics collection for workflow execution statistics
4. **Logging**: Configure comprehensive logging for troubleshooting
5. **Backup**: Regularly backup workflow definitions and templates

## API Implementation Details

The API implementation follows RESTful principles with these key endpoints:

### Workflow Management API

- `POST /api/workflows`: Create a new workflow definition
- `GET /api/workflows/{id}`: Retrieve a workflow definition
- `PUT /api/workflows/{id}`: Update a workflow definition
- `DELETE /api/workflows/{id}`: Delete a workflow definition

### Execution API

- `POST /api/executions`: Start a new workflow execution
- `GET /api/executions/{id}`: Get execution status
- `POST /api/executions/{id}/suspend`: Suspend execution
- `POST /api/executions/{id}/resume`: Resume execution
- `POST /api/executions/{id}/terminate`: Terminate execution

### Template API

- `POST /api/templates`: Create a workflow template
- `GET /api/templates/{id}`: Get template definition
- `POST /api/templates/{id}/instantiate`: Create workflow from template

## Extension Points

Harmonia provides several extension points for customization:

1. **Custom Step Types**: Define new step types for specialized behavior
2. **Custom Expressions**: Add custom functions to the expression engine
3. **Storage Adapters**: Implement custom persistence mechanisms
4. **Integration Connectors**: Build connectors for external systems
5. **Event Handlers**: Create custom event processing logic

## Conclusion

This technical documentation provides a comprehensive overview of Harmonia's architecture, implementation details, and design considerations. Developers working with Harmonia should reference this document for a deep understanding of the system's internal operation and extension points.

For practical usage guidance, please refer to the [User Guide](./USER_GUIDE.md) document, which focuses on how to use Harmonia rather than its internal implementation.