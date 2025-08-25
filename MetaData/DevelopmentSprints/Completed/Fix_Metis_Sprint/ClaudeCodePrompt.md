# Claude Code Prompt - Fix Metis Sprint

You are about to implement CI capabilities for the Metis component in the Tekton ecosystem. Metis is currently a basic task management system that needs to become an intelligent task decomposition engine.

## Context

Metis was designed to be the intelligent task breakdown system for Tekton, but currently only implements basic CRUD operations. Your mission is to add AI-powered capabilities while preserving all existing functionality.

## Current State

- Metis has working API endpoints for task CRUD operations
- Task models, storage, and WebSocket support are functional
- MCP tools are defined but not implemented (empty lists)
- No AI/LLM integration exists
- Complexity scoring is manual, not AI-driven

## Your Mission

Transform Metis into an intelligent task decomposition system by:

1. Adding LLM integration via Rhetor (port 8003)
2. Implementing automatic task decomposition
3. Creating AI-powered complexity analysis
4. Implementing the MCP tools
5. Adding new AI-powered API endpoints

## Implementation Guidelines

### Do:
- Keep all existing code functional
- Add new modules alongside existing ones
- Use the standard Tekton LLM adapter pattern
- Create comprehensive error handling
- Implement async operations throughout
- Add proper logging
- Create example usage scripts

### Don't:
- Modify existing CRUD operations
- Change data models
- Alter storage mechanisms
- Break backward compatibility
- Create UI components

## Key Files to Create/Modify

### New Files:
- `/metis/core/llm_adapter.py` - Connection to Rhetor
- `/metis/core/task_decomposer.py` - CI decomposition engine
- `/metis/core/complexity_analyzer.py` - CI complexity scoring
- `/metis/prompt_templates/*.json` - Prompt templates
- `/tests/ai/test_*.py` - Test suite for CI features

### Files to Update:
- `/metis/core/mcp/tools.py` - Implement the tool handlers
- `/metis/api/routes.py` - Add CI endpoints
- `/metis/core/task_manager.py` - Add convenience methods

## Technical Requirements

1. **LLM Integration**: Use `tekton-llm-client` to connect to Rhetor
2. **Prompt Templates**: Create JSON-based templates with variable substitution
3. **Task Decomposition**: Support configurable depth (default 2, max 5)
4. **Complexity Analysis**: Multi-factor scoring with explanations
5. **Error Handling**: Graceful degradation if CI fails

## API Endpoints to Add

```
POST /api/v1/tasks/{task_id}/decompose?depth=2&max_subtasks=10
POST /api/v1/tasks/{task_id}/analyze-complexity
POST /api/v1/tasks/{task_id}/suggest-order
```

## MCP Tools to Implement

1. `decompose_task` - Break down tasks into subtasks
2. `analyze_task_complexity` - CI complexity scoring
3. `suggest_task_order` - Optimal execution ordering
4. `generate_subtasks` - Create subtasks from description
5. `detect_dependencies` - Find task relationships

## Success Criteria

1. Can decompose a high-level task into meaningful subtasks
2. CI complexity scores are reasonable and explainable
3. All existing tests still pass
4. New CI features have test coverage
5. Example scripts demonstrate functionality
6. No regression in existing features

## Testing Approach

1. Mock LLM responses for unit tests
2. Integration tests with actual Rhetor connection
3. Performance benchmarks for decomposition
4. Error scenario testing

## Example Task Decomposition

Input Task:
```
Title: "Implement User Authentication System"
Description: "Build complete auth with login, registration, password reset, JWT"
```

Expected Output:
```
Subtasks:
1. "Design Authentication Schema" (2 hours)
2. "Implement User Model and Database" (3 hours)
3. "Create Registration Endpoint" (4 hours)
4. "Implement Login with JWT" (4 hours)
5. "Add Password Reset Flow" (3 hours)
6. "Write Authentication Tests" (4 hours)
```

## Important Notes

- This is an enhancement, not a rewrite
- Preserve all existing functionality
- Focus on adding intelligence to task management
- Make the CI features discoverable but not mandatory
- Ensure the system works even if Rhetor is unavailable

## Time Allocation

- Setup and Planning: 1 hour
- Core Implementation: 3 hours
- Integration and Testing: 1-2 hours

Total: 4-6 hours

Begin by reviewing the existing Metis codebase to understand the current structure, then proceed with implementing the CI capabilities according to this plan.