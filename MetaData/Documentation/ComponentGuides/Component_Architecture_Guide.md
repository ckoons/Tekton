# Component Architecture Guide

## Overview

Tekton components follow a unified architecture pattern that ensures consistency, interoperability, and maintainability. This guide explains the architectural principles and patterns that all components must follow.

## Architectural Layers

### 1. API Layer (FastAPI)
- Single port for all services (HTTP, WebSocket, MCP)
- RESTful endpoints for standard operations
- WebSocket support for real-time communication
- MCP v2 endpoints for inter-component communication
- **API Consistency Standards (Required as of API Consistency Sprint):**
  - All components use version "0.1.0"
  - Infrastructure endpoints at root: `/health`, `/ready`, `/status`, `/shutdown`
  - Business logic under `/api/v1/` prefix
  - Service discovery at `/api/v1/discovery`
  - OpenAPI docs at `/api/v1/docs`
  - Use shared API utilities: `create_standard_routers()`, `mount_standard_routers()`
  - MCP endpoints remain at `/api/mcp/v2` (unchanged)

### 2. Business Logic Layer
- Core functionality isolated from API concerns
- Domain models separate from API models
- Stateless operations where possible
- Clear separation of concerns

### 3. Integration Layer
- Hermes registration and heartbeat
- Inter-component communication via MCP
- Environment-based configuration
- Health monitoring and diagnostics

### 4. UI Layer
- Hephaestus-integrated components
- Simple visibility and control interface
- LLM chat integration for complex interactions
- Real-time updates via WebSocket

## Component Communication Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Hephaestus    │────▶│   Component     │────▶│     Hermes      │
│      (UI)       │◀────│     (API)       │◀────│   (Registry)    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         │                       │                         │
         │                       │                         │
         ▼                       ▼                         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   LLM Client    │     │  Other Tekton   │     │    Component    │
│  (Chat/Tools)   │     │   Components    │     │   Discovery     │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Single Port Architecture

Each component operates on a single port that handles:
- HTTP REST API endpoints
- WebSocket connections
- MCP protocol messages
- Health check endpoints

Example port configuration:
```python
# Port assignments (from config/port_assignments.md)
COMPONENT_PORTS = {
    'engram': 8000,
    'hermes': 8001,
    'ergon': 8002,
    'rhetor': 8003,
    # ... etc
}
```

## Service Registration Pattern

Components MUST use the lifespan pattern with shared utilities:

```python
# REQUIRED: Use lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup with shared utilities
    async def component_startup():
        # Get configuration - NEVER hardcode ports
        config = get_component_config()
        port = config.mycomponent.port if hasattr(config, 'mycomponent') else int(os.environ.get("MYCOMPONENT_PORT", 8015))
        
        # Register with Hermes
        hermes_registration = HermesRegistration()
        await hermes_registration.register_component(
            component_name="mycomponent",
            port=port,  # From config, never hardcoded
            version="0.1.0",
            capabilities=["capability1", "capability2"],
            metadata={"description": "My component description"}
        )
        
        # Start heartbeat with interval
        asyncio.create_task(heartbeat_loop(hermes_registration, "mycomponent", interval=30))
    
    # Execute startup with metrics
    metrics = await component_startup("mycomponent", component_startup, timeout=30)
    logger.info(f"Started in {metrics.total_time:.2f}s")
    
    yield
    
    # Shutdown with GracefulShutdown
    shutdown = GracefulShutdown("mycomponent")
    await shutdown.shutdown_sequence(timeout=10)
    await asyncio.sleep(0.5)  # CRITICAL: Socket release delay

app = FastAPI(lifespan=lifespan)  # REQUIRED
```

## MCP Integration

All components expose capabilities through MCP v2:

```python
# Standard MCP endpoint structure
@router.post("/mcp/v2/tools/list")
async def list_tools() -> MCPToolList:
    """List available MCP tools"""

@router.post("/mcp/v2/tools/call")
async def call_tool(request: MCPToolCall) -> MCPToolResponse:
    """Execute an MCP tool"""
```

## Environment Configuration

Components use Tekton's three-tier environment system through shared utilities:
1. System environment variables
2. User-level `.env.tekton`
3. Component-level `.env`

```python
# REQUIRED: Use shared utilities for all configuration
from shared.utils.env_config import get_component_config
from shared.utils.logging_setup import setup_component_logging

# Get configuration
config = get_component_config()
logger = setup_component_logging("mycomponent")

# NEVER hardcode values
port = config.mycomponent.port if hasattr(config, 'mycomponent') else int(os.environ.get("MYCOMPONENT_PORT", 8015))
```

## Health Check Pattern

All components implement standard health endpoints:

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "component": "mycomponent",
        "version": "0.1.0",
        "uptime": get_uptime(),
        "dependencies": check_dependencies()
    }
```

## UI Integration Pattern

UI components follow these principles:
- Direct HTML injection (no Shadow DOM)
- BEM CSS naming convention
- Self-contained functionality
- LLM chat integration on every panel

```html
<!-- Standard UI structure -->
<div id="mycomponent-component">
    <div class="mycomponent">
        <div class="mycomponent__header">
            <!-- Header content -->
        </div>
        <div class="mycomponent__tabs">
            <!-- Tab navigation -->
        </div>
        <div class="mycomponent__content">
            <!-- Main content panels -->
        </div>
    </div>
</div>
```

## CI Interface Implementation

### Overview
Every Tekton component integrates CI capabilities through two primary interfaces:
1. **Chat Interface** - Natural language interaction via Hephaestus UI
2. **MCP Tools** - Programmatic CI access for component operations

### Chat Interface Integration

The chat interface is automatically provided by `tekton-llm-client.js` and integrates with your component panels:

```javascript
// Initialize chat in your component
initializeChat() {
    const chatContainer = document.getElementById('mycomponent-chat-container');
    if (chatContainer && window.TektonLLMClient) {
        window.TektonLLMClient.initializeChat('mycomponent', chatContainer);
    }
}
```

#### Chat Context Switching
Components can provide multiple chat contexts for different operational modes:

```html
<!-- Chat options bar in your component HTML -->
<div class="mycomponent__menu-bar">
    <div class="mycomponent__chat-options">
        <div class="mycomponent__chat-option mycomponent__chat-option--active" 
             onclick="mycomponent_switchChat('main')">Main Chat</div>
        <div class="mycomponent__chat-option" 
             onclick="mycomponent_switchChat('help')">Help Chat</div>
        <div class="mycomponent__chat-option" 
             onclick="mycomponent_switchChat('debug')">Debug Chat</div>
    </div>
</div>
```

```javascript
// Handle chat context switching
function mycomponent_switchChat(chatType) {
    // Update UI
    document.querySelectorAll('.mycomponent__chat-option').forEach(option => {
        option.classList.remove('mycomponent__chat-option--active');
    });
    event.target.classList.add('mycomponent__chat-option--active');
    
    // Notify chat system of context switch
    if (window.TektonLLMClient) {
        window.TektonLLMClient.switchContext('mycomponent', chatType);
    }
}
```

### MCP Tool Integration for AI

Components expose their functionality as MCP tools that CI agents can discover and use:

```python
# mycomponent/api/mcp_endpoints.py
from fastmcp import FastMCP
from typing import List, Dict, Any

# Initialize FastMCP
mcp = FastMCP("mycomponent", dependencies=["engram", "rhetor"])

@mcp.tool()
async def analyze_data(data: str, analysis_type: str = "summary") -> Dict[str, Any]:
    """
    Analyze data using CI capabilities.
    
    Args:
        data: The data to analyze
        analysis_type: Type of analysis (summary, insights, patterns)
    
    Returns:
        Analysis results including insights and recommendations
    """
    # Use Rhetor for CI analysis
    rhetor_client = mcp.get_dependency("rhetor")
    
    prompt = f"Analyze the following data for {analysis_type}: {data}"
    response = await rhetor_client.call_tool(
        "generate_response",
        {"prompt": prompt, "context": "data_analysis"}
    )
    
    return {
        "analysis_type": analysis_type,
        "results": response.get("response"),
        "timestamp": datetime.utcnow().isoformat()
    }

@mcp.tool()
async def get_ai_recommendations(context: Dict[str, Any]) -> List[str]:
    """
    Get AI-powered recommendations based on component state.
    
    Args:
        context: Current component context and state
    
    Returns:
        List of actionable recommendations
    """
    # Implementation here
    pass
```

### AI-Enhanced Features

#### 1. Natural Language Commands
Allow users to control your component through natural language:

```python
@mcp.tool()
async def execute_natural_command(command: str) -> Dict[str, Any]:
    """
    Execute a natural language command.
    
    Examples:
        - "Show me the last 10 operations"
        - "Configure the component for high performance"
        - "Analyze the current error patterns"
    """
    # Parse intent using AI
    rhetor = mcp.get_dependency("rhetor")
    intent = await rhetor.call_tool(
        "analyze_intent",
        {"text": command, "context": "component_command"}
    )
    
    # Execute based on intent
    if intent["type"] == "query":
        return await handle_query(intent["parameters"])
    elif intent["type"] == "configuration":
        return await handle_configuration(intent["parameters"])
    # ... etc
```

#### 2. Intelligent Monitoring
Use CI to detect anomalies and patterns:

```python
@mcp.tool()
async def monitor_with_ai(metrics: List[Dict[str, float]]) -> Dict[str, Any]:
    """
    AI-powered monitoring and anomaly detection.
    """
    # Store metrics in Engram for pattern recognition
    engram = mcp.get_dependency("engram")
    await engram.call_tool(
        "store_memory",
        {
            "content": json.dumps(metrics),
            "memory_type": "metrics",
            "tags": ["monitoring", "mycomponent"]
        }
    )
    
    # Analyze patterns
    analysis = await engram.call_tool(
        "analyze_patterns",
        {"memory_type": "metrics", "lookback_hours": 24}
    )
    
    return {
        "anomalies": analysis.get("anomalies", []),
        "trends": analysis.get("trends", []),
        "recommendations": analysis.get("recommendations", [])
    }
```

#### 3. Conversational Configuration
Enable configuration through conversation:

```python
@mcp.tool()
async def configure_via_chat(conversation_id: str) -> Dict[str, Any]:
    """
    Configure component through a guided conversation.
    """
    # This tool would be called by the chat interface
    # to handle multi-turn configuration dialogs
    pass
```

### UI Components for CI Integration

#### 1. CI Insights Panel
Display AI-generated insights in your component:

```html
<div id="mycomponent-insights-panel" class="mycomponent__panel">
    <div class="mycomponent__panel-header">
        <h2>CI Insights</h2>
        <button class="mycomponent__btn" onclick="mycomponent_refreshInsights()">
            Refresh
        </button>
    </div>
    <div class="mycomponent__insights-container">
        <div class="mycomponent__insight-card">
            <h3>Pattern Analysis</h3>
            <div id="mycomponent-patterns"></div>
        </div>
        <div class="mycomponent__insight-card">
            <h3>Recommendations</h3>
            <div id="mycomponent-recommendations"></div>
        </div>
    </div>
</div>
```

#### 2. CI Command Bar
Add a command bar for natural language input:

```html
<div class="mycomponent__command-bar">
    <input type="text" 
           class="mycomponent__command-input" 
           placeholder="Type a command or question..."
           onkeypress="mycomponent_handleCommand(event)">
    <button class="mycomponent__btn" onclick="mycomponent_executeCommand()">
        Execute
    </button>
</div>
```

### Best Practices for CI Integration

1. **Context Awareness** - Provide rich context to CI for better responses
2. **Progressive Disclosure** - Start simple, reveal CI features as needed
3. **Feedback Loops** - Allow users to correct/improve CI responses
4. **Transparency** - Show when CI is being used and why
5. **Fallback Options** - Always provide non-CI alternatives
6. **Performance** - Cache CI responses when appropriate
7. **Privacy** - Be clear about what data is sent to CI services

### Common CI Integration Patterns

#### 1. AI-Assisted Debugging
```python
@mcp.tool()
async def debug_with_ai(error_context: Dict[str, Any]) -> Dict[str, Any]:
    """Help debug issues using CI analysis of error patterns."""
    # Analyze error patterns, suggest fixes
```

#### 2. Predictive Operations
```python
@mcp.tool()
async def predict_resource_needs(historical_data: List[Dict]) -> Dict[str, Any]:
    """Predict future resource requirements based on patterns."""
    # Use CI to forecast needs
```

#### 3. Natural Language Queries
```python
@mcp.tool()
async def query_in_natural_language(query: str) -> Any:
    """Allow querying component data using natural language."""
    # Convert NL to structured queries
```

### Integration with Other Tekton CI Components

Your component can leverage other Tekton CI components:

- **Rhetor** - LLM management and prompt optimization
- **Engram** - Memory and pattern recognition
- **Apollo** - Planning and action coordination
- **Athena** - Knowledge graph queries
- **Sophia** - Advanced CI research and optimization

Example integration:
```python
# Using multiple CI components together
@mcp.tool()
async def intelligent_optimization() -> Dict[str, Any]:
    """Optimize component using multiple CI services."""
    
    # Get historical patterns from Engram
    patterns = await mcp.get_dependency("engram").call_tool(
        "get_patterns", {"component": "mycomponent"}
    )
    
    # Plan optimization strategy with Apollo
    plan = await mcp.get_dependency("apollo").call_tool(
        "create_plan", {"goal": "optimize_performance", "context": patterns}
    )
    
    # Execute with Sophia's research capabilities
    research = await mcp.get_dependency("sophia").call_tool(
        "research_optimization", {"plan": plan}
    )
    
    return {
        "optimization_plan": plan,
        "research_insights": research,
        "recommended_actions": plan.get("actions", [])
    }
```

## Error Handling

Consistent error handling across all layers:

```python
# Standard error response
class APIError(BaseModel):
    error: str
    component: str
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None
```

## Startup and Shutdown

**IMPORTANT**: The `@app.on_event` decorators are deprecated. Components MUST use the lifespan pattern with shared utilities:

```python
from shared.utils.startup import component_startup
from shared.utils.shutdown import GracefulShutdown

# See the Service Registration Pattern section above for the complete lifespan implementation
# Key requirements:
# 1. Use asynccontextmanager with lifespan
# 2. Use component_startup for startup metrics
# 3. Use GracefulShutdown for cleanup
# 4. Include socket release delay (0.5s) after shutdown
# 5. Pass lifespan to FastAPI constructor
```

## Component Categories

While all components follow the same architecture, they typically fall into these categories:

### Service Components
- Provide specific functionality (e.g., Engram for memory)
- Focus on a single domain
- Expose capabilities via MCP

### Orchestration Components  
- Coordinate other components (e.g., Apollo, Ergon)
- Manage workflows and processes
- Heavy MCP tool usage

### Interface Components
- Primary user interaction (e.g., Rhetor for LLM management)
- Rich UI requirements
- WebSocket for real-time updates

### Utility Components
- Support functionality (e.g., Budget for token management)
- Often called by other components
- Minimal UI requirements

## Best Practices

1. **Keep It Simple** - No clever abstractions that break
2. **Fail Fast** - Clear error messages, quick failure detection
3. **Document Everything** - Code is read more than written
4. **Test First** - Let tests drive the implementation
5. **Use Shared Utilities** - MANDATORY, not optional
6. **Monitor Health** - Always know component status
7. **Log Appropriately** - Not too much, not too little

## Common Pitfalls to Avoid

1. Creating component-specific utilities instead of using shared ones
2. Complex UI logic instead of leveraging LLM capabilities
3. Tight coupling between components
4. Ignoring the three-tier environment system
5. Custom health check formats
6. Skipping Hermes registration
7. Not implementing proper shutdown handlers
8. Using deprecated @app.on_event decorators
9. Hardcoding port numbers
10. Using logging.getLogger instead of setup_component_logging
11. Forgetting the socket release delay in shutdown
12. Not using the lifespan pattern

---

*Next: [Backend Implementation Guide](./Backend_Implementation_Guide.md)*