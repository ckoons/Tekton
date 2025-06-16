# Harmonia LLM Integration

## Overview

Harmonia integrates with Large Language Models (LLMs) through the standardized `tekton-llm-client` library to enhance its workflow engine capabilities. This integration enables AI-powered workflow creation, expression evaluation, state transitions, template expansion, and troubleshooting.

## Architecture

The LLM integration consists of these key components:

1. **LLM Adapter** (`harmonia/core/llm/adapter.py`) - Provides a unified interface for interacting with LLMs:
   - Template-based prompt management
   - Structured output generation
   - Specialized workflow functions
   - Streaming support

2. **Prompt Templates** (`harmonia/prompt_templates/`) - JSON templates for workflow operations:
   - `workflow_creation.json` - For creating workflow definitions
   - `expression_evaluation.json` - For evaluating expressions in state context
   - `state_transition.json` - For determining workflow state transitions
   - `template_expansion.json` - For expanding templates with variables
   - `workflow_troubleshooting.json` - For analyzing workflow issues
   - `system_prompts.json` - System prompts for different functions

## Usage

### Basic Text Generation

```python
from harmonia.core.llm.adapter import LLMAdapter

# Initialize adapter
adapter = LLMAdapter()

# Generate text
response = await adapter.generate(
    prompt="Design a workflow for document approval",
    system_prompt="You are a workflow design expert",
    temperature=0.7
)
print(response)
```

### Template-Based Generation

```python
# Generate using a template
response = await adapter.generate_with_template(
    template_name="workflow_creation",
    variables={
        "goal": "Create a content publishing workflow",
        "components": "List of available components...",
        "constraints": "Must include compliance review"
    },
    system_template_name="system_workflow_creation"
)
print(response)
```

### Specialized Workflow Functions

```python
# Create a workflow
workflow = await adapter.create_workflow(
    goal="Create an employee onboarding workflow",
    components="List of available components...",
    constraints="Must comply with HR policies"
)

# Evaluate an expression
result = await adapter.evaluate_expression(
    expression="${user.department == 'finance' && document.value > 5000}",
    state="Current state as JSON or text..."
)

# Determine state transition
transition = await adapter.determine_state_transition(
    current_state="Current workflow state...",
    completed_step="Step that just completed...",
    step_output="Output from completed step..."
)

# Expand a template
expanded = await adapter.expand_template(
    template="Template with ${variables}",
    state="Current state with variable values..."
)

# Troubleshoot a workflow
analysis = await adapter.troubleshoot_workflow(
    workflow="Workflow definition...",
    state="Current state...",
    error="Error details..."
)
```

### Structured Output

```python
# Generate a workflow in JSON format
workflow_json = await adapter.generate_json_workflow(
    goal="Create a document approval workflow",
    components="List of available components..."
)

# Parse structured output with custom schema
schema = {
    "type": "object",
    "properties": {
        "steps": {
            "type": "array",
            "items": {"type": "object"}
        }
    }
}

parsed_output = await adapter.parse_structured_output(
    prompt="Generate a workflow with steps for content approval",
    output_format=schema
)
```

## Configuration

The LLM adapter can be configured through environment variables:

- `RHETOR_PORT` - Port for the Rhetor LLM service (default: 8003)
- `LLM_ADAPTER_URL` - URL for the LLM adapter (default: http://localhost:<RHETOR_PORT>)
- `LLM_PROVIDER` - Default LLM provider (default: anthropic)
- `LLM_MODEL` - Default model to use (default: claude-3-haiku-20240307)

## Adding Custom Templates

To create new prompt templates:

1. Create a JSON file in the `harmonia/prompt_templates/` directory
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

- Workflow creation
- Expression evaluation
- State transitions
- Template expansion 
- Workflow troubleshooting
- JSON workflow generation

## Best Practices

1. **Template Design** - Design templates with clear instructions and consistent variable patterns
2. **Temperature Control** - Use lower temperatures (0.2-0.4) for precise tasks like expression evaluation, higher temperatures (0.6-0.8) for creative workflow design
3. **Structured Output** - Use `generate_json_workflow()` or `parse_structured_output()` when you need machine-processable output
4. **Error Handling** - Always implement proper error handling for LLM calls
5. **Context Management** - Provide sufficient context in prompts for the LLM to understand the workflow domain

## Integration with Workflow Engine

The LLM adapter can be integrated into Harmonia's workflow engine in several ways:

1. **Workflow Creation** - Using LLMs to generate workflow templates from natural language descriptions
2. **Dynamic Expression Evaluation** - Using LLMs to evaluate complex expressions that go beyond simple logic
3. **Adaptive State Transitions** - Using LLMs to determine optimal state transitions based on context and history
4. **Natural Language Templates** - Expanding templates with more sophisticated natural language processing
5. **Intelligent Troubleshooting** - Analyzing workflow errors and suggesting fixes