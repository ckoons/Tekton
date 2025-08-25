# CI Orchestration Tools Quick Reference

## Overview

This quick reference provides a concise guide to the CI orchestration tools available in Tekton. The primary interface for CI interaction is now **aish** (AI Shell), which provides a simple, Unix-like command interface to all CI capabilities.

**Important Update (July 2025)**: aish is now the standard way to interact with CIs in Tekton. Individual CI commands (apollo, athena, etc.) are deprecated in favor of the unified `aish` command.

## Primary Tool: aish

### Basic Usage

```bash
# Direct CI interaction
aish <ai-name> "message"

# Piped input
echo "data" | aish <ai-name>

# List available CIs
aish -l

# Team chat
aish team-chat "message"
```

### Integration with MCP Tools

While aish is the primary user interface, the MCP tools below are still available for programmatic access through Rhetor. These tools enable sophisticated AI-powered workflows, live component interaction, and dynamic specialist management.

## Tool Categories

### 🤖 Model Management (6 tools)

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `GetAvailableModels` | List all available LLM models | None |
| `SetDefaultModel` | Set the default model for operations | `model_name` |
| `GetModelCapabilities` | Get detailed model capabilities | `model_name` |
| `TestModelConnection` | Test connectivity to model providers | `provider` |
| `GetModelPerformance` | Get performance metrics for models | `model_name`, `time_range` |
| `ManageModelRotation` | Configure model rotation strategies | `strategy`, `models` |

### 📝 Prompt Engineering (6 tools)

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `CreatePromptTemplate` | Create reusable prompt templates | `name`, `content`, `parameters` |
| `OptimizePrompt` | Optimize prompts for better performance | `prompt`, `optimization_goal` |
| `ValidatePromptSyntax` | Validate prompt syntax and structure | `prompt` |
| `GetPromptHistory` | Retrieve prompt usage history | `template_id`, `limit` |
| `AnalyzePromptPerformance` | Analyze prompt effectiveness | `template_id`, `metrics` |
| `ManagePromptLibrary` | Manage prompt template library | `action`, `template_id` |

### 🧠 Context Management (4 tools)

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `AnalyzeContextUsage` | Analyze context window usage | `conversation_id` |
| `OptimizeContextWindow` | Optimize context for token efficiency | `context`, `target_tokens` |
| `TrackContextHistory` | Track context changes over time | `conversation_id` |
| `CompressContext` | Compress context to save tokens | `context`, `compression_level` |

### 👥 CI Specialist Tools (6 tools)

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `ListAISpecialists` | List all available CI specialists | `filter_active` |
| `ActivateAISpecialist` | Activate a specialist for use | `specialist_id` |
| `SendMessageToSpecialist` | Send messages to specialists | `specialist_id`, `message`, `message_type` |
| `OrchestrateTeamChat` | Orchestrate multi-specialist conversations | `specialist_ids`, `topic`, `max_rounds` |
| `GetSpecialistConversationHistory` | Get conversation history | `specialist_id`, `context_id` |
| `ConfigureAIOrchestration` | Configure orchestration settings | `settings` |

### 🔧 Dynamic Specialist Tools (6 tools)

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `ListSpecialistTemplates` | List available specialist templates | None |
| `CreateDynamicSpecialist` | Create specialists from templates | `template_id`, `specialist_name`, `customization` |
| `CloneSpecialist` | Clone existing specialists | `source_id`, `new_name`, `modifications` |
| `ModifySpecialist` | Modify specialist configurations | `specialist_id`, `modifications` |
| `DeactivateSpecialist` | Deactivate specialists | `specialist_id` |
| `GetSpecialistMetrics` | Get specialist performance metrics | `specialist_id`, `time_range` |

### 📡 Streaming Tools (2 tools)

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `SendMessageToSpecialistStream` | Stream specialist responses | `specialist_id`, `message`, `stream_options` |
| `OrchestrateTeamChatStream` | Stream team chat conversations | `specialist_ids`, `topic`, `stream_options` |

## Common Usage Patterns

### Basic Tool Execution

```bash
# Via HTTP API
curl -X POST http://localhost:8003/api/mcp/v2/process \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "ListAISpecialists",
    "arguments": {"filter_active": true}
  }'
```

### Send Message to Specialist

```python
# Python example
response = await client.post(
    "http://localhost:8003/api/mcp/v2/process",
    json={
        "tool_name": "SendMessageToSpecialist",
        "arguments": {
            "specialist_id": "code-reviewer",
            "message": "Review this Python function",
            "message_type": "review_request",
            "context_id": "session_123"
        }
    }
)
```

### Orchestrate Team Chat

```python
# Multi-specialist collaboration
response = await client.post(
    "http://localhost:8003/api/mcp/v2/process",
    json={
        "tool_name": "OrchestrateTeamChat",
        "arguments": {
            "specialist_ids": ["architect", "security-auditor", "performance-optimizer"],
            "topic": "Design secure API endpoint",
            "max_rounds": 5,
            "conversation_style": "collaborative"
        }
    }
)
```

### Create Dynamic Specialist

```python
# Create custom specialist at runtime
response = await client.post(
    "http://localhost:8003/api/mcp/v2/process",
    json={
        "tool_name": "CreateDynamicSpecialist",
        "arguments": {
            "template_id": "code-reviewer",
            "specialist_name": "Python Security Expert",
            "customization": {
                "temperature": 0.2,
                "focus": "security vulnerabilities",
                "language": "python"
            },
            "auto_activate": true
        }
    }
)
```

## Tool Response Formats

### Success Response
```json
{
    "success": true,
    "result": {
        // Tool-specific result data
    },
    "metadata": {
        "execution_time": 0.123,
        "tokens_used": 150
    }
}
```

### Error Response
```json
{
    "success": false,
    "error": "Error message",
    "error_type": "validation_error",
    "details": {
        // Additional error context
    }
}
```

## Best Practices

1. **Tool Selection**
   - Choose the most specific tool for your task
   - Use streaming tools for long-running operations
   - Batch operations when possible

2. **Specialist Management**
   - Activate specialists before use
   - Deactivate when not needed to save resources
   - Use templates for consistent specialist creation

3. **Context Optimization**
   - Monitor context usage with `AnalyzeContextUsage`
   - Compress large contexts before sending
   - Track conversation history for continuity

4. **Error Handling**
   - Always check `success` field in responses
   - Handle rate limiting gracefully
   - Implement retry logic for transient failures

5. **Performance**
   - Use `GetModelPerformance` to monitor costs
   - Cache prompt templates
   - Stream responses for better UX

## Integration Tips

### Direct Access (Within Rhetor)
```python
from rhetor.core.mcp.tools_integration import MCPToolsIntegrationUnified

# Uses the new unified CI system
integration = MCPToolsIntegrationUnified()
result = await integration.list_ai_specialists(filter_active=True)
```

### Via Hermes (From Any Component)
```python
import httpx

async with httpx.AsyncClient() as client:
    # All tools accessible via Hermes aggregation
    response = await client.post(
        "http://localhost:8001/api/mcp/v2/tools/rhetor.SendMessageToSpecialist/execute",
        json={"parameters": {...}}
    )
```

### WebSocket Streaming
```javascript
// JavaScript client for streaming
const ws = new WebSocket('ws://localhost:8003/ws/stream');
ws.send(JSON.stringify({
    tool: 'SendMessageToSpecialistStream',
    arguments: {...}
}));
```

## Common Workflows

### Code Review Workflow
1. `ActivateAISpecialist` - Activate code-reviewer
2. `SendMessageToSpecialist` - Submit code for review
3. `GetSpecialistConversationHistory` - Retrieve feedback
4. `DeactivateSpecialist` - Clean up when done

### Prompt Optimization Workflow
1. `CreatePromptTemplate` - Define initial template
2. `AnalyzePromptPerformance` - Measure effectiveness
3. `OptimizePrompt` - Improve based on metrics
4. `ValidatePromptSyntax` - Ensure correctness

### Team Collaboration Workflow
1. `ListAISpecialists` - See available specialists
2. `ActivateAISpecialist` - Activate needed specialists
3. `OrchestrateTeamChat` - Run collaborative session
4. `GetSpecialistMetrics` - Analyze performance

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Tool not found | Check tool name spelling and prefix |
| Specialist not responding | Verify specialist is activated |
| Streaming timeout | Increase client timeout settings |
| Token limit exceeded | Use `CompressContext` or reduce message size |
| Invalid parameters | Check tool schema with MCP discovery |

## Additional Resources

- [AI Orchestration Architecture](../Architecture/AI_Orchestration_Architecture.md)
- [MCP Implementation Guide](../DeveloperGuides/MCP_IMPLEMENTATION_GUIDE.md)
- [Rhetor Technical Documentation](../../ComponentDocumentation/Rhetor/TECHNICAL_DOCUMENTATION.md)
- [Building New Components Tutorial](../Building_New_Tekton_Components/Step_By_Step_Tutorial.md)

---

*Last updated: Phase 4B completion*