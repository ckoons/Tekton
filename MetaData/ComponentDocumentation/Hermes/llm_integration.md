# Hermes LLM Integration

## Overview

Hermes integrates with Large Language Models (LLMs) through the standardized `tekton-llm-client` library to enhance message bus and service discovery capabilities. This integration enables AI-powered message analysis, service analysis, and interactive assistance with Hermes functionality.

## Architecture

The LLM integration consists of two primary components:

1. **Enhanced LLM Client** (`hermes/core/llm_client.py`) - Provides a unified interface using tekton-llm-client:
   - Prompt template management
   - Message and service analysis
   - Chat with history management
   - Streaming support
   - Structured output parsing

2. **Legacy LLM Adapter** (`hermes/core/llm_adapter.py`) - Maintains backward compatibility:
   - Delegates to the enhanced LLM client
   - Preserves existing API surface
   - Provides seamless migration path

3. **Prompt Templates** (`hermes/prompt_templates/`) - JSON templates for common operations:
   - `message_analysis.json` - For analyzing messages flowing through Hermes
   - `service_analysis.json` - For analyzing service registrations
   - `system_prompts.json` - System prompts for different roles

## Usage

### Enhanced LLM Client

```python
from hermes.core.llm_client import LLMClient

# Initialize client
client = LLMClient()

# Analyze a message
analysis = await client.analyze_message(
    message_content="JSON message content...",
    message_type="registration"
)

# Analyze a service registration
service_analysis = await client.analyze_service(
    service_data=service_registration_dict
)

# Chat with the LLM
response = await client.chat(
    message="How does Hermes handle service discovery?",
    chat_history=previous_messages
)

# Stream a chat response
await client.streaming_chat(
    message="Explain message routing in Hermes",
    callback=handle_chunk
)

# Generate with a template
result = await client.generate_with_template(
    template_name="message_analysis",
    variables={"message_content": message}
)
```

### Legacy LLM Adapter (Backward Compatibility)

```python
from hermes.core.llm_adapter import LLMAdapter

# Initialize adapter
adapter = LLMAdapter()

# Analyze a message
analysis = await adapter.analyze_message(
    message_content="JSON message content...",
    message_type="registration"
)

# Analyze a service registration
service_analysis = await adapter.analyze_service(
    service_data=service_registration_dict
)

# Chat with the LLM
response = await adapter.chat(
    message="How does Hermes handle service discovery?",
    chat_history=previous_messages
)
```

## Configuration

The LLM integration can be configured through environment variables:

- `RHETOR_PORT` - Port for the Rhetor LLM service (default: 8003)
- `LLM_ADAPTER_URL` - URL for the LLM adapter (default: http://localhost:<RHETOR_PORT>)
- `LLM_PROVIDER` - Default LLM provider (default: anthropic)
- `LLM_MODEL` - Default model to use (default: claude-3-haiku-20240307)

## Prompt Templates

The system uses JSON templates for structured prompting:

### Message Analysis Template

```json
{
  "name": "message_analysis",
  "template": "Analyze the following message that was sent through the Hermes message bus.\nExtract key information such as:\n1. Message purpose...",
  "description": "Template for analyzing messages sent through the Hermes bus"
}
```

### Service Analysis Template

```json
{
  "name": "service_analysis",
  "template": "Analyze the following service registration in the Tekton platform.\nExtract key information such as:\n1. Service capabilities...",
  "description": "Template for analyzing service registrations"
}
```

## Analysis Output

Analysis functions return structured data:

### Message Analysis

```python
{
    "purpose": "Memory retrieval response for project status meeting notes",
    "components": ["engram.memory", "ergon.agent"],
    "data_summary": "Query results for project status meeting notes",
    "priority": "normal",
    "summary": "This message provides query results from Engram memory to Ergon agent...",
    "full_analysis": "Full text of the analysis..."
}
```

### Service Analysis

```python
{
    "capabilities": ["Analyze performance metrics", "Assess intelligence capabilities", ...],
    "dependencies": ["hermes.core", "engram.memory", ...],
    "integration_points": ["HTTP API", "WebSocket endpoint", ...],
    "use_cases": ["Performance monitoring", "Intelligence assessment", ...],
    "summary": "Sophia Analytics provides advanced analytics and intelligence measurement...",
    "full_analysis": "Full text of the analysis..."
}
```

## Examples

See `examples/llm_client_example.py` for complete working examples of:

- Message analysis
- Service analysis
- Chat interaction
- Streaming chat
- Custom template usage

## Moving to Enhanced Client

If you're currently using the legacy `LLMAdapter`, migrating to the enhanced `LLMClient` is simple:

1. Update imports:
   ```python
   # Old
   from hermes.core.llm_adapter import LLMAdapter
   
   # New
   from hermes.core.llm_client import LLMClient
   ```

2. Update initialization:
   ```python
   # Old
   adapter = LLMAdapter()
   
   # New
   client = LLMClient()
   ```

The method signatures are compatible, with the enhanced client providing additional options and capabilities.