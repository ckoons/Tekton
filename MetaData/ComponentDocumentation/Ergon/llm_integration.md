# Ergon LLM Integration

## Overview

Ergon integrates with Large Language Models (LLMs) through the standardized `tekton-llm-client` library, providing a unified interface for AI capabilities across agent orchestration, workflow planning, memory operations, and coordination tasks.

## Architecture

The LLM integration consists of these key components:

1. **Enhanced LLM Adapter** (`ergon/core/llm/adapter.py`) - Provides a unified interface for LLM operations with:
   - Prompt template management
   - Streaming support
   - Structured output parsing
   - High-level task functions

2. **Prompt Templates** (`ergon/prompt_templates/`) - JSON templates for agent operations:
   - `agent_task_execution.json` - For autonomous task execution
   - `workflow_planning.json` - For creating agent workflows
   - `memory_query.json` - For memory retrieval and synthesis
   - `agent_coordination.json` - For coordinating multiple agents
   - `system_prompts.json` - System prompts for different roles

3. **Legacy Integration** (`ergon/core/llm/rhetor_adapter.py`) - For backward compatibility with existing code

## Usage

### Basic Text Generation

```python
from ergon.core.llm.adapter import LLMAdapter

# Initialize adapter
adapter = LLMAdapter()

# Generate text
response = await adapter.generate(
    prompt="Explain how agents can collaborate effectively",
    system_prompt="You are an agent coordination expert",
    temperature=0.7
)
print(response)
```

### Template-Based Generation

```python
# Generate using a template
response = await adapter.generate_with_template(
    template_name="agent_task_execution",
    variables={
        "task_description": "Create a summary of quarterly financial data",
        "context": "The data is from Q1 2025 and shows revenue growth",
        "constraints": "Focus only on key performance indicators"
    },
    system_template_name="system_agent_execution"
)
print(response)
```

### Specialized Agent Functions

```python
# Execute an agent task
task_result = await adapter.execute_agent_task(
    task_description="Analyze customer feedback data",
    context="We have 500 customer reviews to analyze",
    constraints="Identify the top 3 issues customers mention"
)

# Plan a workflow
workflow_plan = await adapter.plan_workflow(
    goal="Build an automated data pipeline",
    available_agents="1. Data Collection Agent\n2. Analysis Agent\n3. Reporting Agent",
    constraints="Must complete within 24 hours"
)

# Query memory
memory_result = await adapter.query_memory(
    query="What happened in the last client meeting?",
    retrieved_memories="Notes from meeting on April 15...",
    context="We're preparing for follow-up"
)

# Coordinate agents
coordination = await adapter.coordinate_agents(
    task_description="Build a recommendation system",
    agents="1. Data Agent\n2. Model Agent\n3. UI Agent",
    previous_steps="Data processing is complete",
    current_state="Ready to train the model"
)
```

### Structured Output

```python
# Get structured JSON output
schema = {
    "type": "object",
    "properties": {
        "task_breakdown": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "step": {"type": "string"},
                    "agent": {"type": "string"},
                    "expected_output": {"type": "string"}
                }
            }
        },
        "estimated_completion_time": {"type": "string"}
    }
}

structured_output = await adapter.parse_structured_output(
    prompt="Break down the task of creating a dashboard into steps",
    output_format=schema
)
print(structured_output)
```

## Configuration

The LLM adapter can be configured through environment variables:

- `RHETOR_PORT` - Port for the Rhetor LLM service (default: 8003)
- `LLM_ADAPTER_URL` - URL for the LLM adapter (default: http://localhost:<RHETOR_PORT>)
- `LLM_PROVIDER` - Default LLM provider (default: anthropic)
- `LLM_MODEL` - Default model to use (default: claude-3-haiku-20240307)

## Adding Custom Templates

To create new prompt templates:

1. Create a JSON file in the `ergon/prompt_templates/` directory
2. Use the following structure:

```json
{
  "name": "template_name",
  "template": "Your prompt template with {{ variables }} using Jinja2 syntax",
  "description": "What this template does"
}
```

## Examples

See `examples/llm_adapter_example.py` for complete working examples of:

- Agent task execution
- Workflow planning
- Memory queries
- Agent coordination

## Best Practices

1. **Template Management** - Maintain templates as separate files for reusability
2. **Temperature Control** - Use lower temperatures (0.3-0.5) for planning and analysis, higher (0.7-0.9) for creative tasks
3. **Model Selection** - Use smaller models for simple tasks, larger models for complex reasoning
4. **Structured Output** - Use structured output parsing for data that needs further processing
5. **Error Handling** - Always handle potential LLM service errors gracefully

## Migration from Legacy Integration

If you're using the older `client.py` or `rhetor_adapter.py` implementation:

1. Replace imports:
   ```python
   # Old
   from ergon.core.llm.client import LLMClient
   
   # New
   from ergon.core.llm.adapter import LLMAdapter
   ```

2. Update initialization:
   ```python
   # Old
   client = LLMClient(model_name="claude-3-sonnet-20240229")
   
   # New
   adapter = LLMAdapter(model="claude-3-sonnet-20240229")
   ```

3. Update method calls:
   ```python
   # Old
   response = await client.acomplete([{"role": "user", "content": prompt}])
   
   # New
   response = await adapter.generate(prompt=prompt)
   ```