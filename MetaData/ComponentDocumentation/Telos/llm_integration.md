# Telos LLM Integration

## Overview

Telos integrates with Large Language Models (LLMs) to enhance requirements management workflows through the Tekton LLM Client. 
This integration allows Telos to leverage AI capabilities for requirements analysis, refinement, validation, 
traceability, and more.

## Features

- **Requirement Analysis**: Evaluate requirements against quality criteria including clarity, completeness, testability, feasibility, and consistency
- **Requirement Refinement**: Improve requirements based on feedback and best practices
- **Validation**: Systematically validate requirements against defined criteria
- **Conflict Detection**: Identify conflicts, inconsistencies, and dependencies between requirements
- **Acceptance Criteria Generation**: Generate comprehensive acceptance criteria for requirements
- **Traceability**: Generate links between requirements and implementation artifacts
- **Project Initialization**: Initialize new projects with recommended structure and initial requirements

## Architecture

The LLM integration consists of the following components:

1. **LLM Adapter** (`telos/core/llm_adapter.py`): Core integration with the Tekton LLM Client
2. **Prompt Templates** (`telos/prompt_templates/`): JSON templates for different LLM operations
3. **Configuration** (`telos/config/`): LLM configuration settings

## Usage

### Client API

The Telos client provides methods for accessing LLM capabilities:

```python
from telos.client import get_telos_client

# Create client
client = await get_telos_client()

# Analyze a requirement
result = await client.llm_analyze_requirement(
    requirement_text="The system shall authenticate users with strong passwords",
    context="This is a financial application with strict security requirements"
)

# Generate traceability
traces = await client.llm_generate_traces(
    requirements="List of requirements...",
    artifacts="List of implementation artifacts..."
)

# Initialize a project
recommendations = await client.llm_initialize_project(
    project_name="New Project",
    project_description="Project description...",
    project_domain="Healthcare",
    stakeholders="List of stakeholders...",
    constraints="Project constraints..."
)
```

### Adding Custom Templates

To create new prompt templates:

1. Create a JSON file in the `telos/prompt_templates/` directory
2. Use the following structure:

```json
{
  "name": "template_name",
  "template": "Your prompt template here with {{ variables }} using Jinja2 syntax",
  "description": "Description of what this template does"
}
```

## Configuration

LLM settings are stored in `telos/config/llm_config.json`:

```json
{
  "default_model": "claude-3-sonnet-20240229",
  "models": {
    "claude-3-sonnet-20240229": {
      "description": "Claude 3 Sonnet",
      "temperature": 0.7,
      "max_tokens": 4000
    }
  },
  "fallback_sequence": [
    "claude-3-sonnet-20240229",
    "claude-3-haiku-20240307"
  ],
  "request_timeout": 60,
  "retry_attempts": 3
}
```

## Examples

See `examples/llm_integration_example.py` for a complete working example.

## Dependencies

- `tekton-llm-client`: Core LLM client library for Tekton
- `jinja2`: Template rendering library for prompt templates

## Best Practices

1. **Model Selection**: Use less capable models for simple tasks and more capable models for complex analysis
2. **Prompt Templates**: Keep templates well-structured with clear instructions
3. **Validation**: Always validate LLM outputs when using for critical requirements
4. **Error Handling**: Implement robust error handling for LLM service unavailability

## Future Enhancements

- Structured output parsing for more consistent results
- Fine-tuning capabilities for domain-specific requirements
- Batch processing for large sets of requirements
- Feedback loop for continuous improvement of LLM responses