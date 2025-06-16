# Rhetor MCP Integration

This document describes the Model Context Protocol (MCP) integration for Rhetor, providing standardized access to LLM management, prompt engineering, and context management capabilities.

## Overview

Rhetor's MCP integration enables external systems to interact with its LLM management features through a standardized protocol. The implementation provides 16 tools organized into three main capability areas.

## MCP Capabilities

### 1. LLM Management (`llm_management`)

Manages large language models, providers, and routing decisions.

**Tools:**
- `get_available_models` - List all available LLM models and providers
- `set_default_model` - Configure the default model for operations  
- `get_model_capabilities` - Retrieve model specifications and capabilities
- `test_model_connection` - Verify connectivity to specific models
- `get_model_performance` - Analyze model performance metrics
- `manage_model_rotation` - Set up automatic model rotation strategies

### 2. Prompt Engineering (`prompt_engineering`)

Provides prompt optimization, template management, and engineering tools.

**Tools:**
- `create_prompt_template` - Create reusable prompt templates with variables
- `optimize_prompt` - Improve prompt effectiveness through optimization
- `validate_prompt_syntax` - Check prompt structure and variable usage
- `get_prompt_history` - Retrieve prompt usage history and patterns
- `analyze_prompt_performance` - Evaluate prompt effectiveness across contexts
- `manage_prompt_library` - Organize and search prompt template library

### 3. Context Management (`context_management`)

Handles conversation context optimization and memory management.

**Tools:**
- `analyze_context_usage` - Monitor context usage patterns and efficiency
- `optimize_context_window` - Optimize context for better performance
- `track_context_history` - Track conversation patterns and metrics
- `compress_context` - Reduce token usage while preserving information

## API Endpoints

### Standard MCP Endpoints

- `GET /api/mcp/v2/health` - Health check and status
- `GET /api/mcp/v2/capabilities` - List available capabilities
- `GET /api/mcp/v2/tools` - List available tools
- `POST /api/mcp/v2/process` - Execute MCP tools

### Rhetor-Specific Endpoints

- `GET /api/mcp/v2/llm-status` - LLM system status and metrics
- `POST /api/mcp/v2/execute-llm-workflow` - Execute predefined LLM workflows

## Workflows

### Model Optimization Workflow

Automatically tests and selects the optimal model for a given task type.

```json
{
  "workflow_name": "model_optimization",
  "parameters": {
    "task_type": "code_analysis",
    "performance_criteria": ["speed", "quality", "cost"]
  }
}
```

### Prompt Optimization Workflow  

Optimizes prompts for better performance and effectiveness.

```json
{
  "workflow_name": "prompt_optimization", 
  "parameters": {
    "base_prompt": "Analyze this data...",
    "task_context": {"domain": "finance"},
    "optimization_goals": ["clarity", "effectiveness"]
  }
}
```

### Context Analysis Workflow

Analyzes and optimizes conversation context usage.

```json
{
  "workflow_name": "context_analysis",
  "parameters": {
    "context_id": "conversation_123",
    "analysis_period": "last_week",
    "optimization_target": "efficiency"
  }
}
```

### Multi-Model Comparison Workflow

Compares multiple models on the same tasks to find the best fit.

```json
{
  "workflow_name": "multi_model_comparison",
  "parameters": {
    "task_description": "Code review and analysis",
    "test_prompts": ["Review this code...", "Find bugs in..."],
    "comparison_metrics": ["speed", "quality", "cost"]
  }
}
```

## Usage Examples

### Basic Tool Execution

```python
import aiohttp

async def test_model_capabilities():
    async with aiohttp.ClientSession() as session:
        request_data = {
            "tool_name": "get_model_capabilities",
            "arguments": {
                "provider_id": "anthropic",
                "model_id": "claude-3-sonnet"
            }
        }
        
        async with session.post(
            "http://localhost:8003/api/mcp/v2/process",
            json=request_data
        ) as response:
            result = await response.json()
            print(f"Model capabilities: {result}")
```

### Template Creation

```python
async def create_analysis_template():
    request_data = {
        "tool_name": "create_prompt_template",
        "arguments": {
            "name": "Data Analysis Template",
            "template": "Analyze {data_type}: {input}\n\nProvide:\n1. Key insights\n2. Recommendations", 
            "variables": ["data_type", "input"],
            "tags": ["analysis", "data"]
        }
    }
    
    # Execute request...
```

### Context Optimization

```python
async def optimize_conversation_context():
    request_data = {
        "tool_name": "optimize_context_window",
        "arguments": {
            "context_id": "long_conversation", 
            "optimization_strategy": "efficiency",
            "preserve_recent_messages": True
        }
    }
    
    # Execute request...
```

## Testing

Run the comprehensive test suite to verify MCP functionality:

```bash
# Run tests
cd Rhetor/examples
./run_fastmcp_test.sh

# Or run manually
python test_fastmcp.py
```

The test suite covers:
- Health checks and status verification
- All 16 MCP tools
- Workflow execution
- Error handling and edge cases

## Integration Guidelines

### Client Implementation

1. **Health Check**: Always start by verifying Rhetor is running
2. **Capability Discovery**: Query available capabilities and tools
3. **Error Handling**: Handle connection failures and tool errors gracefully
4. **Performance**: Use workflows for complex multi-step operations

### Best Practices

1. **Template Management**: Use descriptive names and tags for templates
2. **Context Optimization**: Monitor token usage and optimize regularly
3. **Model Selection**: Test models for your specific use cases
4. **Prompt Engineering**: Validate syntax before deployment

## Configuration

Rhetor's MCP integration uses the standard port configuration:

- **Port**: 8003 (default)
- **Host**: 0.0.0.0 (configurable)
- **Protocol**: HTTP/HTTPS with JSON

Environment variables:
- `RHETOR_PORT` - Override default port
- `RHETOR_HOST` - Override default host
- `RHETOR_LOG_LEVEL` - Set logging level

## Error Handling

All MCP tools return standardized responses:

```json
{
  "success": true,
  "result": { /* tool-specific data */ },
  "message": "Operation completed successfully"
}
```

Error responses:

```json
{
  "success": false,
  "error": "Detailed error message",
  "error_code": "OPTIONAL_ERROR_CODE"
}
```

## Performance Considerations

- **Caching**: Model capabilities and performance data are cached
- **Async**: All operations are asynchronous for better performance  
- **Batching**: Use workflows for multiple related operations
- **Resource Limits**: Context compression helps manage memory usage

## Security

- **No Authentication**: Currently no auth required (development mode)
- **CORS**: Enabled for all origins in development
- **Input Validation**: All tool parameters are validated
- **Rate Limiting**: Consider implementing for production use

## Future Enhancements

- Authentication and authorization
- Tool result caching
- Streaming responses for long operations
- Model performance benchmarking
- Advanced prompt optimization algorithms