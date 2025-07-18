# Tekton LLM Integration Plan

## Overview

This document outlines a comprehensive plan to streamline LLM integration across all Tekton components by leveraging Rhetor as the centralized LLM service. The goal is to eliminate duplication of LLM adapter implementations, standardize communication patterns, and create a shared library that all components can use to integrate with Rhetor.

## Current State Analysis

After examining the codebase, we have identified the following:

1. **Rhetor** has a complete LLM integration implementation with:
   - Multiple provider support (Anthropic, OpenAI, Ollama, Simulated)
   - HTTP and WebSocket interfaces
   - Streaming and non-streaming capabilities
   - Context management
   - Budget tracking
   - Prompt templates and management

2. **Current Duplication** exists in several components:
   - LLMAdapter: A separate adapter component for LLM integration
   - Terma, Hermes, Engram, Telos: Each has its own LLM adapter implementation
   - Redundant WebSocket and HTTP client implementations

3. **Inconsistent Patterns**:
   - Different APIs and interfaces across components
   - Varying levels of error handling and fallback strategies
   - Inconsistent context management strategies

## Solution Plan

### 1. Create Shared Library Package: `tekton-llm-client`

Create a dedicated package that all components can use to interact with Rhetor:

```
tekton-llm-client/
├── tekton_llm_client/
│   ├── __init__.py
│   ├── client.py                # Main client interface
│   ├── ws_client.py             # WebSocket client
│   ├── http_client.py           # HTTP client
│   ├── models.py                # Shared data models
│   ├── exceptions.py            # Exception hierarchy
│   ├── auth.py                  # Authentication
│   ├── context_manager.py       # Context management
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── token_counter.py     # Token counting utilities
│   │   ├── streaming.py         # Streaming utilities
│   │   └── retries.py           # Retry logic
│   └── adapters/
│       ├── __init__.py
│       ├── base.py              # Base adapter
│       ├── rhetor.py            # Rhetor adapter (primary)
│       └── fallback.py          # Local fallback adapter
├── setup.py
└── requirements.txt
```

### 2. Core Client Interface Design

The client interface should provide a simple, intuitive API that covers all essential LLM operations:

```python
class TektonLLMClient:
    """Client for interacting with Tekton LLM services."""
    
    def __init__(
        self,
        component_id: str,
        rhetor_url: Optional[str] = None,
        provider_id: Optional[str] = None,
        model_id: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        use_fallback: bool = True,
        auth_token: Optional[str] = None
    ):
        """Initialize the Tekton LLM client."""
        pass
    
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        streaming: bool = False,
        callback: Optional[Callable] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Union[Dict[str, Any], AsyncGenerator[Dict[str, Any], None]]:
        """Generate text using the LLM."""
        pass
    
    async def generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        streaming: bool = False,
        callback: Optional[Callable] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Union[Dict[str, Any], AsyncGenerator[Dict[str, Any], None]]:
        """Generate a chat response using the LLM."""
        pass
    
    # Additional methods for specific use cases
```

### 3. WebSocket Interface Design

```python
class TektonLLMWebSocketClient:
    """WebSocket client for interacting with Tekton LLM services."""
    
    def __init__(
        self,
        component_id: str,
        rhetor_url: Optional[str] = None,
        on_message: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
        on_close: Optional[Callable] = None,
        reconnect_interval: int = 5000,
        auth_token: Optional[str] = None
    ):
        """Initialize the WebSocket client."""
        pass
    
    async def connect(self) -> None:
        """Connect to the WebSocket server."""
        pass
    
    async def generate(
        self,
        prompt: str,
        context_id: str = "default",
        system_prompt: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate a response using the LLM via WebSocket."""
        pass
    
    # Additional methods
```

### 4. Migration Strategy

1. **Phase 1: Create and Test Shared Library**
   - Develop the `tekton-llm-client` package
   - Implement comprehensive tests
   - Create migration guides and examples

2. **Phase 2: Component Refactoring**
   - Refactor each component one by one to use the shared library
   - Prioritize order:
     1. LLMAdapter (phase out in favor of direct Rhetor integration)
     2. Terma (terminal chat interface)
     3. Hermes (message bus)
     4. Engram (memory system)
     5. Telos (requirements management)
     6. Prometheus/Epimetheus (after implementation is complete)

3. **Phase 3: LLM Adapter Phase-Out**
   - Once all components are using the shared library
   - Deprecate the LLMAdapter component
   - Document Rhetor as the official LLM integration component

### 5. Component-Specific Strategies

#### LLMAdapter
- Gradually phase out by redirecting calls to Rhetor
- Keep interface compatibility during transition
- Provide deprecation notices and migration guidance

#### Terma
- Replace Terma's `llm_adapter.py` with `tekton-llm-client`
- Update WebSocket communication to use the new client
- Preserve existing terminal chat interface behavior

#### Hermes
- Replace `hermes/core/llm_adapter.py` with `tekton-llm-client`
- Update service registration to use Rhetor for LLM capabilities
- Maintain existing interface for backward compatibility

#### Engram
- Replace custom LLM integration with `tekton-llm-client`
- Update memory augmentation to use Rhetor's context management
- Leverage Rhetor's budget tracking for LLM usage in memory operations

#### Telos
- Replace `telos/core/llm_adapter.py` with `tekton-llm-client`
- Update requirement analysis functions to use Rhetor
- Maintain existing interfaces for backward compatibility

#### Prometheus/Epimetheus
- Replace Prometheus/Epimetheus LLM integration code with `tekton-llm-client`
- Refactor planning and analysis functions to use Rhetor's capabilities
- Maintain existing interfaces for backward compatibility
- Update forward-looking planning and retrospective analysis functions to leverage Rhetor's prompt management

### 6. Implementation Details

#### Environment Variable Standardization
```
# Rhetor connection
RHETOR_URL=http://localhost:8003
RHETOR_WS_URL=ws://localhost:8003/ws

# Authentication (if needed)
RHETOR_AUTH_TOKEN=<token>

# Default settings
RHETOR_DEFAULT_PROVIDER=anthropic
RHETOR_DEFAULT_MODEL=claude-3-sonnet-20240229
RHETOR_TIMEOUT=30
RHETOR_MAX_RETRIES=3

# Component-specific settings
<COMPONENT>_CONTEXT_ID=<component-specific-context>
```

#### JavaScript Client for Frontend
Create a standardized JavaScript client for frontend components to use:

```javascript
class TektonLLMClient {
    constructor(options) {
        this.rhetorUrl = options.rhetorUrl || '/api/llm';
        this.rhetorWsUrl = options.rhetorWsUrl || 'ws://localhost:8003/ws';
        this.componentId = options.componentId || 'default';
        // Other initialization
    }
    
    async generateText(prompt, options = {}) {
        // Implementation
    }
    
    async streamText(prompt, callback, options = {}) {
        // Implementation
    }
    
    // Other methods
}
```

#### Documentation Updates
- Update `CLAUDE.md` to reflect that Rhetor's LLM support is complete
- Update existing integration guide to reference the new shared library
- Create migration guides for each component
- Document best practices for LLM integration in Tekton

## Components to Refactor

1. LLMAdapter
2. Terma
3. Hermes
4. Engram
5. Telos
6. Ergon
7. Tekton
8. Prometheus/Epimetheus

## Timeline and Resources

### Phase 1: Shared Library Development (1-2 weeks)
- Create `tekton-llm-client` package
- Implement core functionality
- Write tests and documentation
- Create sample applications

### Phase 2: Component Migration (2-4 weeks)
- Migrate components one by one
- Test each migration thoroughly
- Update documentation

### Phase 3: Cleanup and Finalization (1 week)
- Remove deprecated code
- Final documentation updates
- Performance tuning

## Conclusion

By implementing this plan, we will:
1. Eliminate duplication across Tekton components
2. Standardize LLM integration through Rhetor
3. Improve maintainability and reduce code complexity
4. Create a consistent user experience across all components
5. Make future enhancements easier to implement

The shared library approach will allow us to evolve the LLM integration capabilities while maintaining a stable interface for all components.

## Additional Considerations

### Handling Local Models
- Support for local models through Ollama
- Graceful degradation when Rhetor is unavailable
- Local fallback options for critical functionality

### Security Considerations
- Authentication and authorization
- Rate limiting and budget enforcement
- Sensitive data handling

### Performance Optimization
- Connection pooling
- Response caching
- Batch processing where appropriate

## See Also

- [Shared Utilities](../DeveloperGuides/SharedUtilities.md)
- [Component Integration Patterns](./ComponentIntegrationPatterns.md)
- [Single Port Architecture](./SinglePortArchitecture.md)