# Rhetor User Guide

## Introduction

Rhetor is a prompt engineering and LLM interaction system designed for the Tekton ecosystem. It provides tools for creating, managing, and using prompt templates, handling conversation contexts, and interacting with various LLM providers. This guide will help you get started with Rhetor and explore its capabilities.

## Getting Started

### Installation

1. Ensure you have Python 3.9+ installed
2. Clone the Rhetor repository:
   ```bash
   git clone git@github.com:yourusername/Tekton.git
   cd Tekton/Rhetor
   ```

3. Install dependencies:
   ```bash
   pip install -e .
   ```
   or use the setup script:
   ```bash
   ./setup.sh
   ```

4. Start the Rhetor server:
   ```bash
   python -m rhetor.api.app
   ```

By default, Rhetor runs on port 8007. You can change this by setting the `RHETOR_PORT` environment variable.

### Configuration

Create a configuration file `config.json` in the Rhetor directory:

```json
{
  "api": {
    "host": "localhost",
    "port": 8007
  },
  "llm": {
    "default_provider": "openai",
    "default_model": "gpt-3.5-turbo",
    "providers": {
      "openai": {
        "api_key": "your-openai-api-key",
        "models": ["gpt-4", "gpt-3.5-turbo"]
      },
      "anthropic": {
        "api_key": "your-anthropic-api-key",
        "models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
      }
    }
  },
  "budget": {
    "limits": {
      "gpt-4": 10.0,
      "claude-3-opus": 5.0
    }
  }
}
```

Alternatively, you can use environment variables:
- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key
- `RHETOR_DEFAULT_PROVIDER`: Default LLM provider
- `RHETOR_DEFAULT_MODEL`: Default model for the provider

## Using the Client Library

Rhetor provides a Python client library for easy integration:

```python
from rhetor.client import RhetorClient

# Initialize client
client = RhetorClient("http://localhost:8007")

# Create a new context
context = client.create_context()
context_id = context["id"]

# Send a message and get a response
response = client.send_message(
    context_id=context_id,
    message="What is prompt engineering?",
    model="gpt-4"  # Optional, uses default if not specified
)

print(f"Response: {response}")

# Continue the conversation
response = client.send_message(
    context_id=context_id,
    message="Give me some examples of good prompts."
)

print(f"Response: {response}")
```

## Working with Templates

Templates are reusable prompt patterns with variables.

### Creating a Template

Using the client library:

```python
from rhetor.client import RhetorClient

client = RhetorClient("http://localhost:8007")

# Create a simple template
template = client.create_template(
    name="code_review",
    content="Review the following {{language}} code and suggest improvements:\n\n```{{language}}\n{{code}}\n```",
    variables=[
        {"name": "language", "type": "string", "required": True},
        {"name": "code", "type": "string", "required": True}
    ],
    metadata={
        "description": "Template for code review requests",
        "version": "1.0",
        "use_case": "programming"
    }
)

print(f"Created template: {template['name']}")
```

Using the REST API:

```bash
curl -X POST http://localhost:8007/api/templates \
  -H "Content-Type: application/json" \
  -d '{
    "name": "code_review",
    "content": "Review the following {{language}} code and suggest improvements:\n\n```{{language}}\n{{code}}\n```",
    "variables": [
      {"name": "language", "type": "string", "required": true},
      {"name": "code", "type": "string", "required": true}
    ],
    "metadata": {
      "description": "Template for code review requests",
      "version": "1.0",
      "use_case": "programming"
    }
  }'
```

### Using a Template

```python
# Render a template with variables
rendered_prompt = client.render_template(
    name="code_review",
    variables={
        "language": "python",
        "code": "def factorial(n):\n    if n == 0:\n        return 1\n    else:\n        return n * factorial(n-1)"
    }
)

print(f"Rendered prompt: {rendered_prompt}")

# Use template in a message
response = client.send_message_with_template(
    context_id=context_id,
    template_name="code_review",
    variables={
        "language": "python",
        "code": "def factorial(n):\n    if n == 0:\n        return 1\n    else:\n        return n * factorial(n-1)"
    }
)

print(f"Response: {response}")
```

### Template Inheritance

You can create template hierarchies:

```python
# Create a base template
base_template = client.create_template(
    name="base_feedback",
    content="Please provide feedback on the following {{content_type}}:\n\n{{content}}\n\nFocus on: {{focus_areas}}",
    variables=[
        {"name": "content_type", "type": "string", "required": True},
        {"name": "content", "type": "string", "required": True},
        {"name": "focus_areas", "type": "string", "required": True}
    ]
)

# Create a child template
code_feedback_template = client.create_template(
    name="code_feedback",
    content="```{{language}}\n{{content}}\n```",
    variables=[
        {"name": "language", "type": "string", "required": True}
    ],
    parent="base_feedback"  # Inherits from base_feedback
)

# Using the child template
response = client.send_message_with_template(
    context_id=context_id,
    template_name="code_feedback",
    variables={
        "content_type": "code",
        "language": "javascript",
        "content": "function sum(a, b) { return a + b; }",
        "focus_areas": "readability, performance, and best practices"
    }
)
```

## Managing Contexts

Contexts maintain conversation history for coherent LLM interactions.

### Creating a Context

```python
# Create a new context
context = client.create_context(
    max_tokens=4000,  # Maximum tokens to preserve in history
    metadata={        # Optional metadata
        "user_id": "user123",
        "session_type": "code_assistance"
    }
)

context_id = context["id"]
print(f"Created context: {context_id}")
```

### Using a Context for Conversation

```python
# Start a conversation
response = client.send_message(
    context_id=context_id,
    message="I'm working on a Python function to calculate Fibonacci numbers. Any suggestions?"
)

print(f"Response: {response}")

# Continue the conversation
response = client.send_message(
    context_id=context_id,
    message="How can I optimize it for large numbers?"
)

print(f"Response: {response}")

# Add a system message to guide the conversation
client.add_system_message(
    context_id=context_id,
    content="You are a Python expert focused on performance optimization."
)

# Continue with more focused assistance
response = client.send_message(
    context_id=context_id,
    message="Can you help me implement memoization?"
)
```

### Retrieving Context History

```python
# Get conversation history
history = client.get_context(context_id)

for message in history["messages"]:
    print(f"[{message['role']}] {message['content'][:50]}...")
```

## LLM Model Management

Rhetor supports multiple LLM providers and models.

### Listing Available Models

```python
# Get all available models
models = client.list_models()

for model in models:
    print(f"{model['id']} ({model['provider']})")
```

### Model Selection

```python
# Send message with specific model
response = client.send_message(
    context_id=context_id,
    message="Explain quantum computing in simple terms.",
    model="claude-3-opus"  # Specify model
)

print(f"Response from Claude Opus: {response}")

# Change default model for a context
client.set_context_model(
    context_id=context_id,
    model="gpt-4"
)

# Future messages will use gpt-4 by default
response = client.send_message(
    context_id=context_id,
    message="Continue explaining quantum bits."
)
```

### Model Parameters

```python
# Use custom parameters
response = client.send_message(
    context_id=context_id,
    message="Generate five creative ideas for a science fiction story.",
    params={
        "temperature": 0.9,  # Higher creativity
        "max_tokens": 500,   # Longer response
        "top_p": 0.95        # Slightly more diverse sampling
    }
)

print(f"Creative response: {response}")
```

## Budget Management

Rhetor helps track and manage LLM usage costs.

### Viewing Usage

```python
# Get usage report
usage = client.get_usage_report()

print(f"Total cost: ${usage['total_cost']:.2f}")
print(f"Total tokens: {usage['total_tokens']}")

for model, data in usage['models'].items():
    print(f"{model}: ${data['cost']:.2f} ({data['tokens']} tokens)")
```

### Setting Budget Limits

```python
# Set budget limits
client.set_budget_limits({
    "gpt-4": 10.0,         # $10 limit for GPT-4
    "claude-3-opus": 5.0    # $5 limit for Claude Opus
})

# Get remaining budget
budget = client.get_budget_status()

for model, data in budget['models'].items():
    if data['limit']:
        print(f"{model}: ${data['used']:.2f} / ${data['limit']:.2f} ({data['remaining_percentage']:.1f}% remaining)")
```

## Command Line Interface

Rhetor includes a command-line interface for common operations:

### Template Management

Create a template:

```bash
python -m rhetor.cli.main template create \
  --name "summarize" \
  --content "Summarize the following text: {{text}}" \
  --variables '[{"name":"text","type":"string","required":true}]'
```

List templates:

```bash
python -m rhetor.cli.main template list
```

### LLM Interaction

Send a single query:

```bash
python -m rhetor.cli.main llm query "What is prompt engineering?" --model "gpt-3.5-turbo"
```

Start an interactive session:

```bash
python -m rhetor.cli.main llm chat
```

### Budget Management

Get usage report:

```bash
python -m rhetor.cli.main budget usage
```

Set budget limits:

```bash
python -m rhetor.cli.main budget set-limits \
  --model "gpt-4" --limit 10.0 \
  --model "claude-3-opus" --limit 5.0
```

## Integration with Other Tekton Components

### Hermes Integration

Rhetor can register with Hermes for service discovery:

```python
from rhetor.utils.hermes_helper import register_with_hermes

# Register Rhetor with Hermes
success, api_key = register_with_hermes(
    hermes_url="http://localhost:8002",
    component_info={
        "name": "Rhetor",
        "version": "1.0.0",
        "http_endpoint": "http://localhost:8007/api",
        "ws_endpoint": "ws://localhost:8007/ws",
        "capabilities": ["prompt-engineering", "llm-interaction"]
    }
)

if success:
    print(f"Registered with Hermes: {api_key}")
else:
    print("Failed to register with Hermes")
```

### Engram Integration

Use Engram for enhanced memory capabilities:

```python
from rhetor.utils.engram_helper import EngramHelper

# Initialize Engram helper
engram = EngramHelper("http://localhost:8001")

# Store important information in Engram
memory_id = engram.store_memory(
    text="The user prefers detailed explanations with code examples.",
    metadata={"user_id": "user123", "preference_type": "communication_style"}
)

# Search for relevant memories
memories = engram.search_memory(
    query="user communication preferences",
    limit=5
)

for memory in memories:
    print(f"Memory: {memory['text']}")
```

## Advanced Use Cases

### Multi-Step Prompting

Break complex tasks into steps:

```python
# 1. First, analyze the problem
analysis = client.send_message_with_template(
    context_id=context_id,
    template_name="analyze_problem",
    variables={"problem_statement": problem_statement}
)

# 2. Generate a solution approach
approach = client.send_message(
    context_id=context_id,
    message=f"Based on this analysis, propose a solution approach: {analysis}"
)

# 3. Implement the solution
implementation = client.send_message_with_template(
    context_id=context_id,
    template_name="implement_solution",
    variables={
        "problem_statement": problem_statement,
        "analysis": analysis,
        "approach": approach
    }
)

# 4. Test and refine
test_results = client.send_message(
    context_id=context_id,
    message=f"Test this implementation for edge cases: {implementation}"
)
```

### Specialized Prompting Techniques

#### Chain-of-Thought

```python
response = client.send_message_with_template(
    context_id=context_id,
    template_name="chain_of_thought",
    variables={
        "question": "If John has 5 apples and gives 2 to Mary, then buys 3 more but eats 1, how many apples does John have?",
        "step_instructions": "Think step by step to solve this problem."
    }
)
```

#### Few-Shot Learning

```python
response = client.send_message_with_template(
    context_id=context_id,
    template_name="few_shot",
    variables={
        "task_description": "Classify the sentiment of the given text as positive, negative, or neutral.",
        "examples": [
            {"input": "I love this product!", "output": "positive"},
            {"input": "This doesn't work at all.", "output": "negative"},
            {"input": "It arrived on schedule.", "output": "neutral"}
        ],
        "input": "While not perfect, it does the job adequately."
    }
)
```

## Troubleshooting

### Common Issues

1. **Connection Error**
   - Check that the Rhetor server is running
   - Verify the server URL in your client configuration
   - Ensure network connectivity between client and server

2. **Authentication Errors**
   - Check that your API keys are correctly set in configuration
   - Verify the keys have the necessary permissions
   - Check for typos in API keys

3. **Template Errors**
   - Ensure all required variables are provided
   - Check variable types match the template definition
   - Verify the template name exists in the registry

4. **Budget Exceeded**
   - Check your usage report to see which models exceeded limits
   - Increase the budget limit or switch to a more cost-effective model
   - Implement cost optimization strategies

### Logging

Adjust logging level for better debugging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or configure logging in your application:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("rhetor.log"),
        logging.StreamHandler()
    ]
)

# Get logger
logger = logging.getLogger("rhetor")
```

## Best Practices

### Prompt Engineering Tips

1. **Be Specific**: Clearly define what you want the LLM to do
2. **Provide Context**: Include relevant information for better responses
3. **Use Examples**: Demonstrate desired output format with examples
4. **Break Down Complex Tasks**: Split complex requests into simpler steps
5. **Iterate and Refine**: Test prompts and refine based on results

### Cost Optimization

1. **Use Smaller Models**: Use the smallest model suitable for your task
2. **Optimize Context Size**: Keep conversation contexts concise
3. **Cache Responses**: Store and reuse responses for similar queries
4. **Set Budget Alerts**: Configure alerts for budget thresholds
5. **Monitor Usage**: Regularly review usage reports

### Security Considerations

1. **Secure API Keys**: Never hardcode API keys in source code
2. **Validate Input**: Always validate user input before sending to LLMs
3. **Review Outputs**: Monitor LLM outputs for potentially harmful content
4. **Limit Access**: Restrict access to sensitive LLM capabilities
5. **Use Encryption**: Encrypt sensitive data in transit and at rest

## Conclusion

This guide covers the basics of using Rhetor for prompt engineering and LLM interactions. For more detailed information, check the [API Reference](./API_REFERENCE.md) and [Technical Documentation](./TECHNICAL_DOCUMENTATION.md).

If you encounter issues or need assistance, please refer to the [Tekton Documentation](../../README.md) for community support options.