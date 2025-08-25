# Rhetor CI Integration Sprint - Claude Code Prompt

## Context

You are about to implement the Rhetor CI Integration Sprint for the Tekton project. This sprint extends Rhetor to manage dedicated CI instances for each Tekton component and integrates these CIs with the Hephaestus UI chat interfaces.

## Your Role

You are the Working Claude, responsible for implementing the code according to the architectural decisions and implementation plan. You should focus on creating clean, well-documented code that follows all Tekton standards and guidelines.

## Sprint Overview

This sprint implements:
1. **Component CI Management**: Dedicated CI instances for each of the 15 Tekton components
2. **Prompt Engineering**: Stdin/stdout filter chains for transparent prompt enhancement
3. **UI Integration**: Updating Hephaestus chat interfaces to use component-specific CIs
4. **Team Chat**: A moderated channel for AI-to-AI and AI-to-human communication

## Key Implementation Requirements

### 1. Debug Instrumentation
**CRITICAL**: All code MUST include debug instrumentation:
- Python: Use `debug_log()` and `@log_function` decorators
- JavaScript: Use `TektonDebug` conditional logging
- Include component names and appropriate log levels
- Add contextual information for debugging

### 2. Component CI Assignments
Each component gets an CI optimized for its domain:
```python
{
    'budget': 'claude-3-haiku',      # Fast calculations
    'athena': 'claude-3-sonnet',     # Knowledge work
    'sophia': 'claude-3-opus',       # Complex research
    'ergon': 'gpt-4',               # Code generation
    'synthesis': 'claude-3-sonnet',  # Execution planning
    'prometheus': 'claude-3-sonnet', # Strategic planning
    'engram': 'claude-3-haiku',      # Memory queries
    'hermes': 'claude-3-haiku',      # Message routing
    'metis': 'claude-3-sonnet',      # Task decomposition
    'harmonia': 'claude-3-sonnet',   # Workflow orchestration
    'telos': 'claude-3-haiku',       # Requirements analysis
    'apollo': 'claude-3-sonnet',     # Executive coordination
    'terma': 'claude-3-haiku',       # Terminal assistance
    'rhetor': 'claude-3-opus',       # Meta-AI management
    'budget': 'claude-3-haiku'       # Cost management
}
```

### 3. Filter Architecture
Implement filter chains for prompt engineering:
- **Prompt Filters**: ComponentContextFilter, TaskOptimizationFilter, TokenLimitFilter
- **Response Filters**: ResponseFormattingFilter, ActionExtractionFilter, ErrorNormalizationFilter

### 4. WebSocket Protocol Extensions
Add new message types:
- `COMPONENT_CHAT`: Component-specific chat requests
- `STREAM_CHUNK`: Streaming response chunks
- `PROCESSED_RESPONSE`: Final filtered response
- `TEAM_CHAT`: Team communication messages
- `AI_HANDOFF`: AI-to-AI communication

## Phase 1 Tasks (Start Here)

### Task 1: Create Component CI Manager
Create `rhetor/core/component_ai_manager.py`:

```python
from typing import Dict, Optional, Any
from shared.utils.logging_setup import debug_log

class ComponentAIManager:
    """Manages CI instances for each Tekton component."""
    
    def __init__(self, llm_client, model_router, context_manager, prompt_engine):
        debug_log("rhetor", "Initializing ComponentAIManager", level="info")
        self.component_ais: Dict[str, ComponentAI] = {}
        # ... implementation
        
    async def get_or_create_ai(self, component_id: str) -> 'ComponentAI':
        """Get or create an CI instance for a component."""
        # ... implementation with debug logging
```

### Task 2: Create Model Configuration
Create `rhetor/config/component_models.json` with model assignments and configurations.

### Task 3: Implement Base Filter Classes
Create the filter infrastructure in `rhetor/core/filters/`.

## Integration Points

### Rhetor Updates
1. Extend `rhetor/api/app.py` WebSocket handler
2. Update startup to initialize ComponentAIManager
3. Add new API endpoints for component CI status

### Hephaestus Updates
1. Modify `shared/chat-interface.js` to support componentId
2. Update each component's initialization to use component AI
3. Add CI status indicators to UI

## Testing Requirements

- Unit tests for all new classes
- Integration tests for WebSocket protocol
- End-to-end tests for component chat
- Performance benchmarks for filter processing

## Code Style Guidelines

- Use type hints for all Python functions
- Add docstrings with clear descriptions
- Follow PEP 8 for Python code
- Use JSDoc for JavaScript documentation
- Include error handling with meaningful messages

## Important Files to Review

Before starting, review:
1. `rhetor/core/model_router.py` - Understand current routing logic
2. `rhetor/core/context_manager.py` - Context management patterns
3. `Hephaestus/ui/scripts/shared/chat-interface.js` - Chat UI integration
4. `shared/utils/logging_setup.py` - Debug instrumentation patterns

## Success Criteria

Your implementation is successful when:
1. Each component can chat with its dedicated AI
2. Prompts are transparently enhanced with component context
3. Team chat enables multi-AI conversations
4. All code includes proper debug instrumentation
5. Tests provide 80% code coverage
6. Performance overhead is under 100ms

## Getting Started

1. Create the sprint branch: `git checkout -b sprint/rhetor-ai-integration`
2. Start with Phase 1, Task 1: Component CI Manager
3. Commit frequently with descriptive messages
4. Run tests after each major component
5. Update documentation as you go

Remember: Focus on clean, maintainable code that follows all Tekton patterns and guidelines. The goal is to create a robust CI management system that enhances every component in the Tekton ecosystem.

Good luck!