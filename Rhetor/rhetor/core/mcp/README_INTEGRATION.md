# MCP Tools Integration - Phase 3 Implementation

## Overview

This implementation connects the MCP (Model Context Protocol) tools to live Rhetor components, enabling real AI orchestration functionality instead of using mock data.

## Key Components

### 1. **tools_integration.py**
- `MCPToolsIntegration` class that provides real implementations for MCP tools
- Connects to `AISpecialistManager` for specialist lifecycle management
- Integrates with `AIMessagingIntegration` for cross-component communication
- Initializes Hermes message bus connection for inter-component messaging

### 2. **Updated MCP Tools** (tools.py)
All AI orchestration tools now check for live integration:
- `ListAISpecialists` - Queries actual specialist registry
- `ActivateAISpecialist` - Activates real AI specialists
- `SendMessageToSpecialist` - Routes through live messaging system
- `OrchestrateTeamChat` - Uses actual AI responses
- `GetSpecialistConversationHistory` - Retrieves real conversation data
- `ConfigureAIOrchestration` - Applies actual configuration changes

### 3. **init_integration.py**
Initialization module that:
- Creates and configures the integration layer
- Sets up Hermes message bus subscriptions
- Provides testing functions for verification

### 4. **Enhanced AISpecialistManager**
Added methods to support MCP tools:
- `activate_specialist()` - Enhanced activation with detailed status
- `get_conversation_history()` - Retrieve specialist conversation history
- `get_orchestration_settings()` - Get current orchestration configuration
- `update_orchestration_settings()` - Apply new orchestration settings

## Message Flow

### Internal Rhetor Communication
```
MCP Tool → MCPToolsIntegration → AISpecialistManager → Internal Specialist
```

### Cross-Component Communication
```
MCP Tool → MCPToolsIntegration → AIMessagingIntegration → Hermes Message Bus → Other Component
```

## Topic Structure

- `ai.specialist.<component_id>.<specialist_id>` - Specialist-specific messages
- `ai.orchestration.<conversation_id>` - Orchestration control messages
- `ai.team_chat.<topic>` - Team chat coordination

## Testing

Run the integration test script:
```bash
python /Users/cskoons/projects/github/Tekton/Rhetor/tests/test_mcp_integration.py
```

This tests:
1. Listing AI specialists
2. Activating specialists
3. Sending messages to specialists
4. Orchestrating team chats
5. Configuring orchestration settings

## Usage Example

When using MCP tools via the API:

```python
# List available AI specialists
POST /api/mcp/v2/process
{
    "tool": "ListAISpecialists",
    "arguments": {
        "filter_by_status": "active"
    }
}

# Orchestrate a team chat
POST /api/mcp/v2/process
{
    "tool": "OrchestrateTeamChat",
    "arguments": {
        "topic": "System optimization",
        "specialists": ["rhetor-orchestrator", "engram-memory"],
        "initial_prompt": "How can we improve system performance?",
        "max_rounds": 3
    }
}
```

## Next Steps

1. **Streaming Support**: Implement real-time streaming for AI responses
2. **Enhanced Error Handling**: Add retry logic and graceful degradation
3. **Performance Monitoring**: Add metrics for AI response times
4. **Dynamic Specialist Creation**: Allow creation of new specialists on demand
5. **Advanced Orchestration**: Implement voting and consensus mechanisms