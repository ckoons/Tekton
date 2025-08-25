# Rhetor Technical Documentation

## Architecture Overview

Rhetor is designed as a prompt engineering and LLM interaction management system within the Tekton ecosystem. Its architecture focuses on standardizing prompt templates, managing contexts, and providing consistent LLM interactions.

### Core Components

1. **Prompt Engine**
   - Central hub for prompt template management
   - Handles prompt resolution with variables
   - Manages prompt versioning and variants
   - Provides prompt optimization features

2. **Context Manager**
   - Maintains conversation contexts and history
   - Manages context windows efficiently
   - Provides context persistence
   - Handles context pruning and relevance

3. **LLM Client**
   - Abstracts communication with various LLM providers
   - Manages authentication and API keys
   - Handles request formatting and response parsing
   - Implements retry and fallback mechanisms

4. **Budget Manager**
   - Tracks token usage and costs
   - Enforces budget limits and quotas
   - Provides cost optimization strategies
   - Generates usage reports

5. **Template Manager**
   - Stores and retrieves prompt templates
   - Manages template categories and metadata
   - Provides template inheritance and composition
   - Handles template validation

6. **AI Socket Registry**
   - Manages CI communication sockets following Unix philosophy
   - Provides team chat broadcast capabilities
   - Handles transparent message routing with headers
   - Maintains socket persistence via Engram
   - Monitors socket health and responsiveness

## Internal System Design

### Prompt Management Architecture

The prompt management system follows these components:

1. **Template Registry**: Stores prompt templates with metadata
2. **Template Resolver**: Processes templates with variable substitution
3. **Template Validator**: Ensures templates meet structure requirements
4. **Template Renderer**: Produces final prompt text for LLM submission

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Template     │     │    Template     │     │    Template     │     │    Template     │
│    Registry     ├────►│    Resolver     ├────►│    Validator    ├────►│    Renderer     │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Template Structure

Templates are stored in a hierarchical structure:

```python
class PromptTemplate:
    def __init__(self, name, content, metadata=None, variables=None, parent=None):
        self.name = name
        self.content = content
        self.metadata = metadata or {}
        self.variables = variables or []
        self.parent = parent
        self.version = metadata.get('version', '1.0')
        self.created_at = datetime.now().isoformat()
        
    def to_dict(self):
        """Convert template to dictionary representation"""
        return {
            "name": self.name,
            "content": self.content,
            "metadata": self.metadata,
            "variables": self.variables,
            "parent": self.parent,
            "version": self.version,
            "created_at": self.created_at
        }
        
    @classmethod
    def from_dict(cls, data):
        """Create template from dictionary representation"""
        return cls(
            name=data["name"],
            content=data["content"],
            metadata=data.get("metadata", {}),
            variables=data.get("variables", []),
            parent=data.get("parent")
        )
```

A template example:

```json
{
  "name": "code_review",
  "content": "Review the following code for {{language}} and identify any issues:\n\n```{{language}}\n{{code}}\n```\n\nFocus on: {{focus_areas}}",
  "metadata": {
    "description": "Template for code review requests",
    "version": "1.2",
    "use_case": "programming",
    "models": ["claude-3-opus", "gpt-4"]
  },
  "variables": [
    {"name": "language", "type": "string", "required": true},
    {"name": "code", "type": "string", "required": true},
    {"name": "focus_areas", "type": "string", "default": "bugs, performance issues, security vulnerabilities"}
  ],
  "parent": "base_review"
}
```

### LLM Integration Architecture

The LLM client abstracts away provider-specific details:

```python
class LLMClient:
    def __init__(self, provider, api_key=None, default_params=None):
        self.provider = provider
        self.api_key = api_key or self._get_api_key_from_env(provider)
        self.default_params = default_params or {}
        self.client = self._initialize_client()
        
    def _initialize_client(self):
        """Initialize provider-specific client"""
        if self.provider == "openai":
            import openai
            openai.api_key = self.api_key
            return openai
        elif self.provider == "anthropic":
            from anthropic import Anthropic
            return Anthropic(api_key=self.api_key)
        # Add other providers as needed
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
            
    async def generate_text(self, prompt, params=None):
        """Generate text from prompt with provider-specific formatting"""
        params = {**self.default_params, **(params or {})}
        
        try:
            if self.provider == "openai":
                response = await self.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    **params
                )
                return response.choices[0].message.content
            elif self.provider == "anthropic":
                response = await self.client.messages.create(
                    content=prompt,
                    **params
                )
                return response.content[0].text
            # Add other providers as needed
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise
```

### Model Router Implementation

The model router selects the appropriate model based on task requirements:

```python
class ModelRouter:
    def __init__(self, models_config, default_model=None):
        self.models_config = models_config
        self.default_model = default_model or self._get_first_available_model()
        self.usage_stats = {}
        
    def _get_first_available_model(self):
        """Get first available model from config"""
        for model_id, config in self.models_config.items():
            if config.get("available", True):
                return model_id
        raise ValueError("No available models configured")
        
    def select_model(self, task_requirements=None, context=None):
        """Select appropriate model based on requirements"""
        if not task_requirements:
            return self.default_model
            
        # Extract requirements
        complexity = task_requirements.get("complexity", "medium")
        token_limit = task_requirements.get("token_limit", 0)
        capabilities = task_requirements.get("capabilities", [])
        priority = task_requirements.get("priority", "standard")
        
        # Filter eligible models
        eligible_models = []
        for model_id, config in self.models_config.items():
            # Skip unavailable models
            if not config.get("available", True):
                continue
                
            # Check token limit
            if token_limit > config.get("max_tokens", 0):
                continue
                
            # Check capabilities
            model_capabilities = config.get("capabilities", [])
            if not all(cap in model_capabilities for cap in capabilities):
                continue
                
            # Add to eligible models
            eligible_models.append((model_id, config))
            
        if not eligible_models:
            logger.warning(f"No models match requirements: {task_requirements}")
            return self.default_model
            
        # Sort by priority and select
        if priority == "cost":
            return min(eligible_models, key=lambda x: x[1].get("cost_per_1k", float("inf")))[0]
        elif priority == "performance":
            return max(eligible_models, key=lambda x: x[1].get("performance_score", 0))[0]
        elif priority == "speed":
            return min(eligible_models, key=lambda x: x[1].get("avg_response_time", float("inf")))[0]
        else:  # standard priority
            # Balance between cost and performance
            return sorted(
                eligible_models,
                key=lambda x: (
                    x[1].get("performance_score", 0) / 
                    max(x[1].get("cost_per_1k", 0.01), 0.01)
                ),
                reverse=True
            )[0][0]
```

## Budget Management System

The budget management system tracks and controls LLM usage costs:

### Cost Tracking

```python
class BudgetManager:
    def __init__(self, config=None):
        self.config = config or self._load_default_config()
        self.usage = defaultdict(int)  # model -> token count
        self.costs = defaultdict(float)  # model -> cost
        self.limits = {}  # model -> limit
        
    def _load_default_config(self):
        """Load default cost configuration"""
        return {
            "models": {
                "gpt-4": {"input_cost_per_1k": 0.03, "output_cost_per_1k": 0.06},
                "gpt-3.5-turbo": {"input_cost_per_1k": 0.0015, "output_cost_per_1k": 0.002},
                "claude-3-opus": {"input_cost_per_1k": 0.015, "output_cost_per_1k": 0.075},
                "claude-3-sonnet": {"input_cost_per_1k": 0.003, "output_cost_per_1k": 0.015}
            }
        }
        
    def record_usage(self, model, input_tokens, output_tokens):
        """Record token usage and calculate cost"""
        self.usage[model] += input_tokens + output_tokens
        
        model_config = self.config["models"].get(
            model, 
            {"input_cost_per_1k": 0.01, "output_cost_per_1k": 0.01}
        )
        
        input_cost = (input_tokens / 1000) * model_config["input_cost_per_1k"]
        output_cost = (output_tokens / 1000) * model_config["output_cost_per_1k"]
        total_cost = input_cost + output_cost
        
        self.costs[model] += total_cost
        
        # Check if this exceeds budget limit
        if model in self.limits and self.costs[model] > self.limits[model]:
            logger.warning(f"Budget limit exceeded for {model}: {self.costs[model]} > {self.limits[model]}")
            return False
            
        return True
        
    def set_budget_limit(self, model, limit):
        """Set budget limit for a model"""
        self.limits[model] = limit
        
    def get_usage_report(self):
        """Get usage and cost report"""
        total_cost = sum(self.costs.values())
        total_tokens = sum(self.usage.values())
        
        return {
            "total_cost": total_cost,
            "total_tokens": total_tokens,
            "models": {
                model: {
                    "tokens": self.usage[model],
                    "cost": self.costs[model],
                    "limit": self.limits.get(model, None),
                    "limit_remaining": self.limits.get(model, float("inf")) - self.costs[model] 
                        if model in self.limits else None
                }
                for model in self.usage
            }
        }
```

### Budget Optimization Strategies

The system implements several strategies to optimize budget usage:

1. **Model Downgrading**: Automatically downgrade to cheaper models when budget is tight
2. **Context Pruning**: Reduce context size to lower token costs
3. **Response Length Control**: Limit output tokens for cost control
4. **Caching**: Cache responses to avoid redundant API calls

```python
class BudgetOptimizer:
    def __init__(self, budget_manager, model_router):
        self.budget_manager = budget_manager
        self.model_router = model_router
        self.strategy = "balanced"  # balanced, aggressive, conservative
        
    def optimize_request(self, model, prompt, params):
        """Optimize request for budget efficiency"""
        # Check remaining budget
        model_data = self.budget_manager.get_usage_report()["models"].get(model, {})
        remaining = model_data.get("limit_remaining")
        
        if remaining is not None and remaining < 1.0:
            # Budget is very low, apply aggressive optimization
            optimized_model, optimized_params = self._apply_aggressive_optimization(model, params)
            return optimized_model, prompt, optimized_params
            
        if self.strategy == "aggressive":
            # Always optimize aggressively
            optimized_model, optimized_params = self._apply_aggressive_optimization(model, params)
            return optimized_model, prompt, optimized_params
            
        elif self.strategy == "balanced":
            # Balance between cost and quality
            if remaining is not None and remaining < 10.0:
                # Budget is getting low
                optimized_model, optimized_params = self._apply_moderate_optimization(model, params)
                return optimized_model, prompt, optimized_params
            return model, prompt, params
            
        elif self.strategy == "conservative":
            # Optimize only when necessary
            if remaining is not None and remaining < 5.0:
                # Budget is critically low
                optimized_model, optimized_params = self._apply_moderate_optimization(model, params)
                return optimized_model, prompt, optimized_params
            return model, prompt, params
            
        return model, prompt, params
        
    def _apply_aggressive_optimization(self, model, params):
        """Apply aggressive budget optimization"""
        # 1. Downgrade to cheapest model that can handle the task
        cheaper_model = self._find_cheaper_alternative(model)
        
        # 2. Reduce max tokens significantly
        optimized_params = dict(params)
        if "max_tokens" in optimized_params:
            optimized_params["max_tokens"] = min(optimized_params["max_tokens"], 256)
            
        # 3. Disable other costly parameters
        if "top_k" in optimized_params:
            optimized_params["top_k"] = 40  # Less diverse but cheaper
            
        return cheaper_model, optimized_params
        
    def _apply_moderate_optimization(self, model, params):
        """Apply moderate budget optimization"""
        # 1. Consider downgrading model if significantly cheaper
        model_config = self.model_router.models_config.get(model, {})
        model_cost = model_config.get("cost_per_1k", 0.01)
        
        alternatives = []
        for m_id, m_config in self.model_router.models_config.items():
            if m_config.get("available", True) and m_config.get("cost_per_1k", 0.01) < model_cost * 0.7:
                alternatives.append((m_id, m_config))
                
        cheaper_model = model
        if alternatives:
            cheaper_model = max(alternatives, key=lambda x: x[1].get("performance_score", 0))[0]
            
        # 2. Apply moderate parameter optimizations
        optimized_params = dict(params)
        if "max_tokens" in optimized_params:
            optimized_params["max_tokens"] = min(optimized_params["max_tokens"], 512)
            
        return cheaper_model, optimized_params
        
    def _find_cheaper_alternative(self, model):
        """Find cheapest adequate alternative to current model"""
        model_config = self.model_router.models_config.get(model, {})
        required_capabilities = model_config.get("capabilities", [])
        
        candidates = []
        for m_id, m_config in self.model_router.models_config.items():
            if not m_config.get("available", True):
                continue
                
            # Check capabilities
            model_capabilities = m_config.get("capabilities", [])
            if not all(cap in model_capabilities for cap in required_capabilities):
                continue
                
            candidates.append((m_id, m_config))
            
        if not candidates:
            return model
            
        # Return cheapest option
        return min(candidates, key=lambda x: x[1].get("cost_per_1k", float("inf")))[0]
```

## Context Management

The context management system efficiently handles conversation history:

### Context Structure

```python
class Context:
    def __init__(self, id=None, max_tokens=4000):
        self.id = id or str(uuid.uuid4())
        self.max_tokens = max_tokens
        self.messages = []
        self.metadata = {}
        self.token_count = 0
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        
    def add_message(self, role, content, token_count=None):
        """Add message to context"""
        message = {
            "id": str(uuid.uuid4()),
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        # Calculate tokens if not provided
        if token_count is None:
            token_count = self._count_tokens(content)
            
        # Update token count
        self.token_count += token_count
        
        # Add message
        self.messages.append(message)
        
        # Update timestamp
        self.updated_at = datetime.now().isoformat()
        
        # Prune if necessary
        if self.token_count > self.max_tokens:
            self._prune_context()
            
        return message
        
    def _prune_context(self):
        """Prune context to stay within token limit"""
        if not self.messages:
            return
            
        # Always keep the system message if present
        system_message = None
        if self.messages and self.messages[0]["role"] == "system":
            system_message = self.messages[0]
            
        # Always keep the most recent user message and assistant response
        recent_messages = self.messages[-2:] if len(self.messages) >= 2 else self.messages
        
        # Remove older messages until within token limit
        removable_messages = self.messages[1:-2] if system_message else self.messages[:-2]
        
        self.messages = []
        self.token_count = 0
        
        # Re-add system message if present
        if system_message:
            self.messages.append(system_message)
            self.token_count += self._count_tokens(system_message["content"])
            
        # Add recent messages
        for message in recent_messages:
            self.messages.append(message)
            self.token_count += self._count_tokens(message["content"])
            
        # Add as many removable messages as possible, starting from most recent
        for message in reversed(removable_messages):
            token_count = self._count_tokens(message["content"])
            if self.token_count + token_count <= self.max_tokens:
                self.messages.insert(1 if system_message else 0, message)
                self.token_count += token_count
            else:
                break
        
    def _count_tokens(self, text):
        """Estimate token count for text"""
        # Simple estimation: ~4 characters per token
        return len(text) // 4 + 1
```

### Context Manager Implementation

```python
class ContextManager:
    def __init__(self, storage_path=None):
        self.storage_path = storage_path
        self.contexts = {}  # id -> Context
        
    def create_context(self, max_tokens=4000, metadata=None):
        """Create new context"""
        context = Context(max_tokens=max_tokens)
        
        if metadata:
            context.metadata = metadata
            
        self.contexts[context.id] = context
        
        # Persist context if storage path provided
        if self.storage_path:
            self._save_context(context)
            
        return context
        
    def get_context(self, context_id):
        """Get context by ID"""
        # Check in-memory cache
        if context_id in self.contexts:
            return self.contexts[context_id]
            
        # Try loading from storage
        if self.storage_path:
            context = self._load_context(context_id)
            if context:
                self.contexts[context_id] = context
                return context
                
        return None
        
    def add_message(self, context_id, role, content):
        """Add message to context"""
        context = self.get_context(context_id)
        if not context:
            raise ValueError(f"Context not found: {context_id}")
            
        message = context.add_message(role, content)
        
        # Persist updated context
        if self.storage_path:
            self._save_context(context)
            
        return message
        
    def _save_context(self, context):
        """Save context to storage"""
        if not self.storage_path:
            return
            
        os.makedirs(self.storage_path, exist_ok=True)
        
        context_path = os.path.join(self.storage_path, f"{context.id}.json")
        
        with open(context_path, 'w') as f:
            json.dump({
                "id": context.id,
                "max_tokens": context.max_tokens,
                "messages": context.messages,
                "metadata": context.metadata,
                "token_count": context.token_count,
                "created_at": context.created_at,
                "updated_at": context.updated_at
            }, f)
            
    def _load_context(self, context_id):
        """Load context from storage"""
        if not self.storage_path:
            return None
            
        context_path = os.path.join(self.storage_path, f"{context_id}.json")
        
        if not os.path.exists(context_path):
            return None
            
        try:
            with open(context_path, 'r') as f:
                data = json.load(f)
                
            context = Context(id=data["id"], max_tokens=data["max_tokens"])
            context.messages = data["messages"]
            context.metadata = data["metadata"]
            context.token_count = data["token_count"]
            context.created_at = data["created_at"]
            context.updated_at = data["updated_at"]
            
            return context
        except Exception as e:
            logger.error(f"Error loading context {context_id}: {e}")
            return None
```

## Template Management System

The template management system handles prompt templates:

### Template Registry

```python
class TemplateManager:
    def __init__(self, storage_path=None):
        self.storage_path = storage_path
        self.templates = {}  # name -> PromptTemplate
        
        # Load templates if storage path provided
        if self.storage_path:
            self._load_templates()
            
    def register_template(self, template):
        """Register new template"""
        # Validate template
        self._validate_template(template)
        
        # Store template
        self.templates[template.name] = template
        
        # Persist template if storage path provided
        if self.storage_path:
            self._save_template(template)
            
        return template
        
    def get_template(self, name):
        """Get template by name"""
        return self.templates.get(name)
        
    def render_template(self, name, variables=None):
        """Render template with variables"""
        template = self.get_template(name)
        if not template:
            raise ValueError(f"Template not found: {name}")
            
        # Validate variables
        self._validate_variables(template, variables)
        
        # Render template
        return self._render(template, variables or {})
        
    def _render(self, template, variables):
        """Render template content with variables"""
        content = template.content
        
        # Process parent template first if exists
        if template.parent:
            parent_template = self.get_template(template.parent)
            if parent_template:
                # Get parent content with variables
                content = self._render(parent_template, variables)
                
        # Replace variables in content
        for var_name, var_value in variables.items():
            placeholder = "{{" + var_name + "}}"
            content = content.replace(placeholder, str(var_value))
            
        return content
        
    def _validate_template(self, template):
        """Validate template structure"""
        if not template.name:
            raise ValueError("Template must have a name")
            
        if not template.content:
            raise ValueError("Template must have content")
            
        # Validate parent template exists if specified
        if template.parent and not self.get_template(template.parent):
            raise ValueError(f"Parent template not found: {template.parent}")
            
    def _validate_variables(self, template, variables):
        """Validate variables against template requirements"""
        variables = variables or {}
        
        # Check required variables
        for var in template.variables:
            if var.get("required", False) and var["name"] not in variables:
                # If default value exists, use it
                if "default" in var:
                    variables[var["name"]] = var["default"]
                else:
                    raise ValueError(f"Required variable missing: {var['name']}")
                    
        # Check variable types
        for var_name, var_value in variables.items():
            # Find variable definition
            var_def = next((v for v in template.variables if v["name"] == var_name), None)
            if var_def and "type" in var_def:
                expected_type = var_def["type"]
                
                # Validate type
                if expected_type == "string" and not isinstance(var_value, str):
                    raise ValueError(f"Variable {var_name} must be a string")
                elif expected_type == "number" and not isinstance(var_value, (int, float)):
                    raise ValueError(f"Variable {var_name} must be a number")
                elif expected_type == "boolean" and not isinstance(var_value, bool):
                    raise ValueError(f"Variable {var_name} must be a boolean")
                    
    def _load_templates(self):
        """Load templates from storage"""
        if not self.storage_path or not os.path.exists(self.storage_path):
            return
            
        try:
            for filename in os.listdir(self.storage_path):
                if filename.endswith(".json"):
                    template_path = os.path.join(self.storage_path, filename)
                    
                    with open(template_path, 'r') as f:
                        data = json.load(f)
                        
                    template = PromptTemplate.from_dict(data)
                    self.templates[template.name] = template
        except Exception as e:
            logger.error(f"Error loading templates: {e}")
            
    def _save_template(self, template):
        """Save template to storage"""
        if not self.storage_path:
            return
            
        os.makedirs(self.storage_path, exist_ok=True)
        
        template_path = os.path.join(self.storage_path, f"{template.name}.json")
        
        with open(template_path, 'w') as f:
            json.dump(template.to_dict(), f)
```

## CI Socket Registry Architecture

The CI Socket Registry implements the Unix philosophy where "AIs are just sockets that read and write." This architecture enables seamless multi-AI collaboration and team chat functionality.

### Design Principles

1. **Simplicity**: Sockets are just dictionaries with read/write operations
2. **Transparency**: Headers are metadata, invisible to CIs
3. **Persistence**: Socket state survives restarts via Engram
4. **Unix-like**: Everything is a stream, fail silently with logging

### Socket Structure

```python
@dataclass
class AISocket:
    socket_id: str              # Unique identifier
    model: str                  # CI model (e.g., "claude-3")
    prompt: str                 # System prompt
    context: Dict[str, Any]     # Socket context
    created_at: str             # ISO timestamp
    state: SocketState          # ACTIVE, INACTIVE, UNRESPONSIVE
    last_activity: str          # ISO timestamp
    message_queue: List[Dict]   # Message queue
```

### Registry Operations

#### Socket Lifecycle
```python
# Create: On-demand socket creation
socket_id = await registry.create(model, prompt, context)

# Read: Automatic header addition
messages = await registry.read(socket_id)  # Adds [team-chat-from-X]

# Write: Automatic header wrapping
await registry.write(socket_id, message)   # Adds [team-chat-to-Y]

# Reset: Clear context, keep alive
await registry.reset(socket_id)

# Delete: Terminate and cleanup
await registry.delete(socket_id)
```

#### Broadcasting
The special `team-chat-all` socket enables broadcasting:

```python
# Broadcast to all active sockets
await registry.write("team-chat-all", "Team question")

# Collect all responses
responses = await registry.read("team-chat-all")
```

### Message Routing

Messages are wrapped with transparent headers:

1. **Write Operation**: 
   - User writes: "Hello AI"
   - Socket receives: "[team-chat-to-apollo-123] Hello AI"
   - CI sees: "Hello AI"

2. **Read Operation**:
   - CI writes: "My response"
   - Registry adds: "[team-chat-from-apollo-123] My response"
   - User sees full message with source

### Persistence Layer

Socket state is persisted to Engram with local backup:

```python
# Persistence namespace
namespace = "rhetor_sockets"

# Socket saved on every state change
await engram_client.store_memory(
    namespace=namespace,
    key=socket_id,
    data=socket.to_dict(),
    metadata={"type": "ai_socket", "model": model}
)

# Restored on registry initialization
memories = await engram_client.list_memories(namespace)
```

### Health Monitoring

Sockets can be marked unresponsive:

```python
# Mark socket as unresponsive
await registry.mark_unresponsive(socket_id)

# Unresponsive sockets reject writes
if socket.state != SocketState.ACTIVE:
    return False  # Write rejected
```

### Team Chat Integration

The socket registry enables Rhetor's team chat moderation modes:

1. **Pass-through**: Stream all responses immediately
2. **Synthesis**: Collect and summarize responses  
3. **Consensus**: Group by agreement patterns
4. **Directed**: Call on specific CIs

### Performance Considerations

- In-memory socket storage for fast access
- Async operations throughout
- Minimal overhead on read/write operations
- Efficient broadcast using dictionary iteration
- Lazy persistence (only on state changes)

## Communication Module

The communication module handles interactions with LLMs:

### Communication Class

```python
class Communication:
    def __init__(self, llm_client, context_manager, budget_manager=None):
        self.llm_client = llm_client
        self.context_manager = context_manager
        self.budget_manager = budget_manager
        
    async def send_message(self, context_id, message, model=None, params=None):
        """Send message to LLM and get response"""
        # Get context
        context = self.context_manager.get_context(context_id)
        if not context:
            raise ValueError(f"Context not found: {context_id}")
            
        # Add user message to context
        self.context_manager.add_message(context_id, "user", message)
        
        # Prepare conversation history
        conversation = self._prepare_conversation(context)
        
        # Set default model if not provided
        model = model or "gpt-3.5-turbo"
        
        # Set default parameters
        default_params = {
            "max_tokens": 1024,
            "temperature": 0.7
        }
        params = {**default_params, **(params or {})}
        
        # Apply budget optimization if enabled
        if self.budget_manager:
            model, conversation, params = self.budget_manager.optimize_request(model, conversation, params)
            
        # Send request to LLM
        response = await self.llm_client.generate_text(conversation, model, params)
        
        # Record usage if budget manager available
        if self.budget_manager and "usage" in response:
            self.budget_manager.record_usage(
                model,
                response["usage"]["prompt_tokens"],
                response["usage"]["completion_tokens"]
            )
            
        # Add assistant response to context
        self.context_manager.add_message(context_id, "assistant", response["choices"][0]["message"]["content"])
        
        return response["choices"][0]["message"]["content"]
        
    def _prepare_conversation(self, context):
        """Prepare conversation history for LLM"""
        # Format messages for provider
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in context.messages
        ]
```

## Hermes Integration

Rhetor integrates with Hermes for service discovery and messaging:

```python
class HermesHelper:
    def __init__(self, hermes_url):
        self.hermes_url = hermes_url
        self.api_key = None
        self.component_id = None
        
    async def register_component(self):
        """Register Rhetor with Hermes"""
        component_info = {
            "name": "Rhetor",
            "version": "1.0.0",
            "description": "Prompt engineering and LLM interaction system",
            "endpoints": {
                "http": "http://localhost:8007/api",
                "websocket": "ws://localhost:8007/ws"
            },
            "capabilities": ["prompt-engineering", "llm-interaction"]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.hermes_url}/api/register",
                    json=component_info
                ) as response:
                    if response.status != 200:
                        logger.error(f"Failed to register with Hermes: {await response.text()}")
                        return False
                        
                    result = await response.json()
                    self.api_key = result["api_key"]
                    self.component_id = result["id"]
                    
            logger.info(f"Registered with Hermes, ID: {self.component_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error registering with Hermes: {e}")
            return False
            
    async def discover_llm_services(self):
        """Discover LLM services via Hermes"""
        if not self.api_key:
            logger.warning("Not registered with Hermes")
            return []
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.hermes_url}/api/services",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    params={"capability": "llm-processing"}
                ) as response:
                    if response.status != 200:
                        logger.error(f"Failed to discover services: {await response.text()}")
                        return []
                        
                    return await response.json()
                    
        except Exception as e:
            logger.error(f"Error discovering services: {e}")
            return []
            
    async def send_heartbeat(self):
        """Send heartbeat to Hermes"""
        if not self.api_key or not self.component_id:
            logger.warning("Not registered with Hermes")
            return False
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.hermes_url}/api/heartbeat",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={"component_id": self.component_id}
                ) as response:
                    return response.status == 200
                    
        except Exception as e:
            logger.error(f"Error sending heartbeat: {e}")
            return False
```

## Engram Integration

Rhetor can use Engram for enhanced memory capabilities:

```python
class EngramHelper:
    def __init__(self, engram_url):
        self.engram_url = engram_url
        
    async def store_memory(self, text, metadata=None):
        """Store text in Engram memory"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.engram_url}/api/memory",
                    json={
                        "text": text,
                        "metadata": metadata or {}
                    }
                ) as response:
                    if response.status != 200:
                        logger.error(f"Failed to store memory: {await response.text()}")
                        return None
                        
                    return await response.json()
                    
        except Exception as e:
            logger.error(f"Error storing memory: {e}")
            return None
            
    async def search_memory(self, query, limit=5):
        """Search Engram memory"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.engram_url}/api/memory/search",
                    params={
                        "query": query,
                        "limit": limit
                    }
                ) as response:
                    if response.status != 200:
                        logger.error(f"Failed to search memory: {await response.text()}")
                        return []
                        
                    return await response.json()
                    
        except Exception as e:
            logger.error(f"Error searching memory: {e}")
            return []
```

## API Implementation Details

The API implementation follows RESTful principles with these key endpoints:

### Template API

- `POST /api/templates`: Create a new template
- `GET /api/templates`: List all templates
- `GET /api/templates/{name}`: Get template by name
- `PUT /api/templates/{name}`: Update template
- `DELETE /api/templates/{name}`: Delete template
- `POST /api/templates/{name}/render`: Render template with variables

### Context API

- `POST /api/contexts`: Create a new context
- `GET /api/contexts/{id}`: Get context by ID
- `POST /api/contexts/{id}/messages`: Add message to context
- `GET /api/contexts/{id}/messages`: Get context messages

### LLM API

- `POST /api/llm/completions`: Generate completion from an LLM
- `GET /api/llm/models`: List available LLM models
- `GET /api/llm/usage`: Get usage statistics

### Budget API

- `GET /api/budget/usage`: Get budget usage report
- `POST /api/budget/limits`: Set budget limits

## CLI Implementation

Rhetor includes a command-line interface for common operations:

```python
def main():
    parser = argparse.ArgumentParser(description="Rhetor CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Template commands
    template_parser = subparsers.add_parser("template", help="Template operations")
    template_subparsers = template_parser.add_subparsers(dest="template_command")
    
    # Create template
    create_template_parser = template_subparsers.add_parser("create", help="Create template")
    create_template_parser.add_argument("name", help="Template name")
    create_template_parser.add_argument("content", help="Template content")
    create_template_parser.add_argument("--metadata", help="Template metadata (JSON)")
    create_template_parser.add_argument("--variables", help="Template variables (JSON)")
    create_template_parser.add_argument("--parent", help="Parent template name")
    
    # List templates
    list_templates_parser = template_subparsers.add_parser("list", help="List templates")
    
    # LLM commands
    llm_parser = subparsers.add_parser("llm", help="LLM operations")
    llm_subparsers = llm_parser.add_subparsers(dest="llm_command")
    
    # Query LLM
    query_llm_parser = llm_subparsers.add_parser("query", help="Query LLM")
    query_llm_parser.add_argument("prompt", help="Prompt text")
    query_llm_parser.add_argument("--model", help="Model to use")
    query_llm_parser.add_argument("--params", help="Parameters (JSON)")
    
    # List models
    list_models_parser = llm_subparsers.add_parser("models", help="List models")
    
    # Budget commands
    budget_parser = subparsers.add_parser("budget", help="Budget operations")
    budget_subparsers = budget_parser.add_subparsers(dest="budget_command")
    
    # Get usage
    usage_parser = budget_subparsers.add_parser("usage", help="Get usage report")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute command
    if args.command == "template":
        if args.template_command == "create":
            metadata = json.loads(args.metadata) if args.metadata else None
            variables = json.loads(args.variables) if args.variables else None
            template = create_template(args.name, args.content, metadata, variables, args.parent)
            print(f"Created template: {template.name}")
        elif args.template_command == "list":
            templates = list_templates()
            for template in templates:
                print(f"{template.name} (v{template.version})")
    elif args.command == "llm":
        if args.llm_command == "query":
            params = json.loads(args.params) if args.params else None
            response = query_llm(args.prompt, args.model, params)
            print(response)
        elif args.llm_command == "models":
            models = list_models()
            for model in models:
                print(f"{model['id']} - {model['provider']}")
    elif args.command == "budget":
        if args.budget_command == "usage":
            usage = get_budget_usage()
            print(f"Total cost: ${usage['total_cost']:.2f}")
            print(f"Total tokens: {usage['total_tokens']}")
            for model, data in usage['models'].items():
                print(f"  {model}: ${data['cost']:.2f} ({data['tokens']} tokens)")
    else:
        parser.print_help()
```

## Conclusion

This technical documentation provides a comprehensive overview of Rhetor's architecture, implementation details, and design considerations. Developers working with Rhetor should reference this document for a deep understanding of the system's internal operation.

For practical usage guidance, please refer to the [User Guide](./USER_GUIDE.md) document, which focuses on how to use Rhetor rather than its internal implementation.