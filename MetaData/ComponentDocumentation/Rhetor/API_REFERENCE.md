# Rhetor API Reference

## Base URL

```
http://localhost:8005/api/rhetor
```

## Authentication

All API requests require authentication via one of the following methods:

- **API Key**: Passed via the `X-API-Key` header
- **Bearer Token**: Passed via the `Authorization` header

## Completions API

### Generate Completion

Generate text from a prompt.

```
POST /completions
```

#### Request Body

```json
{
  "prompt": "Explain quantum computing in simple terms",
  "model": "claude-3-sonnet-20240229",
  "provider": "anthropic",
  "max_tokens": 500,
  "temperature": 0.7,
  "top_p": 0.95,
  "frequency_penalty": 0.0,
  "presence_penalty": 0.0,
  "stop_sequences": ["User:", "\n\n"],
  "system_prompt": "You are a helpful assistant with expertise in quantum physics.",
  "metadata": {
    "user_id": "u-123",
    "session_id": "sess-456",
    "request_id": "req-789"
  }
}
```

#### Response

```json
{
  "text": "Quantum computing is like traditional computing but using some special properties of very tiny particles. In regular computers, we use bits (0s and 1s) to process information. In quantum computers, we use 'qubits' which can be 0, 1, or both at the same time - a state called 'superposition'...",
  "model": "claude-3-sonnet-20240229",
  "provider": "anthropic",
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 487,
    "total_tokens": 512,
    "cost": 0.02354
  },
  "finish_reason": "stop",
  "request_id": "req-789",
  "created_at": "2025-01-15T12:00:00Z"
}
```

### Generate Completion with Auto-routing

Let Rhetor select the appropriate model based on the task.

```
POST /completions/auto
```

#### Request Body

```json
{
  "prompt": "Write a detailed analysis of Shakespeare's use of metaphor in Hamlet",
  "max_tokens": 1000,
  "temperature": 0.7,
  "routing_parameters": {
    "task_type": "literary_analysis",
    "complexity": "high",
    "required_capabilities": ["literary_knowledge", "critical_analysis"],
    "max_cost": 0.10,
    "priority": "quality"
  },
  "metadata": {
    "user_id": "u-123",
    "session_id": "sess-456"
  }
}
```

#### Response

```json
{
  "text": "Shakespeare's use of metaphor in Hamlet is extensive and multifaceted, serving to illuminate the play's central themes of corruption, decay, madness, and moral ambiguity...",
  "model": "claude-3-opus-20240229",
  "provider": "anthropic",
  "routing_explanation": "Selected claude-3-opus for this literary analysis task due to its strong performance on complex analytical tasks requiring deep literary knowledge.",
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 968,
    "total_tokens": 988,
    "cost": 0.08902
  },
  "finish_reason": "stop",
  "request_id": "req-abcde",
  "created_at": "2025-01-15T12:30:00Z"
}
```

### Stream Completion

Stream a text completion in real-time.

```
POST /completions/stream
```

#### Request Body

Same as `/completions` endpoint.

#### Response

A stream of server-sent events (SSE):

```
event: content
data: {"text": "Quantum ", "index": 0}

event: content
data: {"text": "computing ", "index": 1}

event: content
data: {"text": "is ", "index": 2}

... (more content events) ...

event: done
data: {"usage": {"prompt_tokens": 25, "completion_tokens": 487, "total_tokens": 512, "cost": 0.02354}, "finish_reason": "stop"}
```

## Chat API

### Create Chat Completion

Generate a response in a conversation.

```
POST /chat/completions
```

#### Request Body

```json
{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello, who are you?"},
    {"role": "assistant", "content": "I'm an AI assistant created to help answer questions and provide information."},
    {"role": "user", "content": "Can you explain how AI works?"}
  ],
  "model": "gpt-4",
  "provider": "openai",
  "max_tokens": 800,
  "temperature": 0.7,
  "top_p": 0.95,
  "metadata": {
    "user_id": "u-123",
    "session_id": "sess-456"
  }
}
```

#### Response

```json
{
  "message": {
    "role": "assistant",
    "content": "AI, or artificial intelligence, works through a combination of algorithms, data, and computing power..."
  },
  "model": "gpt-4",
  "provider": "openai",
  "usage": {
    "prompt_tokens": 103,
    "completion_tokens": 785,
    "total_tokens": 888,
    "cost": 0.04976
  },
  "finish_reason": "stop",
  "request_id": "req-xyz123",
  "created_at": "2025-01-15T13:00:00Z"
}
```

### Stream Chat Completion

Stream a chat completion in real-time.

```
POST /chat/completions/stream
```

#### Request Body

Same as `/chat/completions` endpoint.

#### Response

A stream of server-sent events (SSE):

```
event: content
data: {"text": "AI, ", "index": 0}

event: content
data: {"text": "or ", "index": 1}

event: content
data: {"text": "artificial ", "index": 2}

... (more content events) ...

event: done
data: {"usage": {"prompt_tokens": 103, "completion_tokens": 785, "total_tokens": 888, "cost": 0.04976}, "finish_reason": "stop"}
```

## Templates API

### Create Template

Create a new prompt template.

```
POST /templates
```

#### Request Body

```json
{
  "name": "code_explanation",
  "content": "Explain the following {language} code step by step:\n\n```{language}\n{code}\n```\n\nProvide a detailed explanation focusing on:\n1. What the code does\n2. How it works\n3. Any important patterns or techniques used\n4. Potential improvements",
  "metadata": {
    "description": "Template for explaining code snippets",
    "required_parameters": ["language", "code"],
    "optional_parameters": [],
    "recommended_models": ["claude-3-sonnet-20240229", "gpt-4"],
    "example_parameters": {
      "language": "python",
      "code": "def factorial(n):\n    if n == 0:\n        return 1\n    return n * factorial(n-1)"
    }
  },
  "tags": ["code", "explanation", "tutorial"]
}
```

#### Response

```json
{
  "template_id": "tmpl-123e4567-e89b-12d3-a456-426614174000",
  "name": "code_explanation",
  "content": "Explain the following {language} code step by step:\n\n```{language}\n{code}\n```\n\nProvide a detailed explanation focusing on:\n1. What the code does\n2. How it works\n3. Any important patterns or techniques used\n4. Potential improvements",
  "metadata": {
    "description": "Template for explaining code snippets",
    "required_parameters": ["language", "code"],
    "optional_parameters": [],
    "recommended_models": ["claude-3-sonnet-20240229", "gpt-4"],
    "example_parameters": {
      "language": "python",
      "code": "def factorial(n):\n    if n == 0:\n        return 1\n    return n * factorial(n-1)"
    }
  },
  "tags": ["code", "explanation", "tutorial"],
  "created_at": "2025-01-15T14:00:00Z",
  "updated_at": "2025-01-15T14:00:00Z",
  "created_by": "u-123"
}
```

### Get Template

Retrieve a template by ID.

```
GET /templates/{template_id}
```

#### Parameters

| Name | Type | In | Description |
|------|------|----|------------|
| `template_id` | string | path | The unique identifier of the template |

#### Response

```json
{
  "template_id": "tmpl-123e4567-e89b-12d3-a456-426614174000",
  "name": "code_explanation",
  "content": "Explain the following {language} code step by step:\n\n```{language}\n{code}\n```\n\nProvide a detailed explanation focusing on:\n1. What the code does\n2. How it works\n3. Any important patterns or techniques used\n4. Potential improvements",
  "metadata": {
    "description": "Template for explaining code snippets",
    "required_parameters": ["language", "code"],
    "optional_parameters": [],
    "recommended_models": ["claude-3-sonnet-20240229", "gpt-4"],
    "example_parameters": {
      "language": "python",
      "code": "def factorial(n):\n    if n == 0:\n        return 1\n    return n * factorial(n-1)"
    }
  },
  "tags": ["code", "explanation", "tutorial"],
  "created_at": "2025-01-15T14:00:00Z",
  "updated_at": "2025-01-15T14:00:00Z",
  "created_by": "u-123",
  "usage_count": 157
}
```

### List Templates

Retrieve a list of available templates.

```
GET /templates
```

#### Query Parameters

| Name | Type | Description |
|------|------|------------|
| `tags` | string | Filter by tags (comma-separated) |
| `search` | string | Search term for template name or description |
| `page` | integer | Page number for pagination (default: 1) |
| `limit` | integer | Number of items per page (default: 20) |

#### Response

```json
{
  "items": [
    {
      "template_id": "tmpl-123e4567-e89b-12d3-a456-426614174000",
      "name": "code_explanation",
      "description": "Template for explaining code snippets",
      "tags": ["code", "explanation", "tutorial"],
      "created_at": "2025-01-15T14:00:00Z",
      "usage_count": 157
    },
    {
      "template_id": "tmpl-abcde123-f456-789d-e012-3456789abcde",
      "name": "concept_explanation",
      "description": "Template for explaining concepts to different audiences",
      "tags": ["explanation", "education"],
      "created_at": "2025-01-10T09:15:00Z",
      "usage_count": 284
    },
    {
      "template_id": "tmpl-fedcba98-7654-3210-abcd-123456789012",
      "name": "pros_cons_analysis",
      "description": "Template for analyzing pros and cons of a topic",
      "tags": ["analysis", "decision-making"],
      "created_at": "2025-01-05T16:30:00Z",
      "usage_count": 92
    }
  ],
  "total": 45,
  "page": 1,
  "limit": 20
}
```

### Update Template

Update an existing template.

```
PUT /templates/{template_id}
```

#### Parameters

| Name | Type | In | Description |
|------|------|----|------------|
| `template_id` | string | path | The unique identifier of the template |

#### Request Body

```json
{
  "name": "code_explanation_detailed",
  "content": "Explain the following {language} code step by step:\n\n```{language}\n{code}\n```\n\nProvide a detailed explanation focusing on:\n1. What the code does\n2. How it works\n3. Any important patterns or techniques used\n4. Potential improvements\n5. Performance considerations\n6. Security implications",
  "metadata": {
    "description": "Template for detailed explanation of code snippets",
    "required_parameters": ["language", "code"],
    "optional_parameters": ["focus_area"],
    "recommended_models": ["claude-3-opus-20240229", "gpt-4"]
  },
  "tags": ["code", "explanation", "tutorial", "detailed", "security"]
}
```

#### Response

```json
{
  "template_id": "tmpl-123e4567-e89b-12d3-a456-426614174000",
  "name": "code_explanation_detailed",
  "content": "Explain the following {language} code step by step:\n\n```{language}\n{code}\n```\n\nProvide a detailed explanation focusing on:\n1. What the code does\n2. How it works\n3. Any important patterns or techniques used\n4. Potential improvements\n5. Performance considerations\n6. Security implications",
  "metadata": {
    "description": "Template for detailed explanation of code snippets",
    "required_parameters": ["language", "code"],
    "optional_parameters": ["focus_area"],
    "recommended_models": ["claude-3-opus-20240229", "gpt-4"]
  },
  "tags": ["code", "explanation", "tutorial", "detailed", "security"],
  "created_at": "2025-01-15T14:00:00Z",
  "updated_at": "2025-01-15T15:00:00Z",
  "created_by": "u-123",
  "usage_count": 157
}
```

### Delete Template

Delete a template.

```
DELETE /templates/{template_id}
```

#### Parameters

| Name | Type | In | Description |
|------|------|----|------------|
| `template_id` | string | path | The unique identifier of the template |

#### Response

```json
{
  "success": true,
  "message": "Template deleted successfully",
  "template_id": "tmpl-123e4567-e89b-12d3-a456-426614174000"
}
```

### Render Template

Render a template with parameters.

```
POST /templates/{template_id}/render
```

#### Parameters

| Name | Type | In | Description |
|------|------|----|------------|
| `template_id` | string | path | The unique identifier of the template |

#### Request Body

```json
{
  "parameters": {
    "language": "python",
    "code": "def factorial(n):\n    if n == 0:\n        return 1\n    return n * factorial(n-1)"
  }
}
```

#### Response

```json
{
  "rendered_template": "Explain the following python code step by step:\n\n```python\ndef factorial(n):\n    if n == 0:\n        return 1\n    return n * factorial(n-1)\n```\n\nProvide a detailed explanation focusing on:\n1. What the code does\n2. How it works\n3. Any important patterns or techniques used\n4. Potential improvements",
  "template_id": "tmpl-123e4567-e89b-12d3-a456-426614174000",
  "parameters": {
    "language": "python",
    "code": "def factorial(n):\n    if n == 0:\n        return 1\n    return n * factorial(n-1)"
  }
}
```

### Generate from Template

Generate text using a template.

```
POST /templates/{template_id}/generate
```

#### Parameters

| Name | Type | In | Description |
|------|------|----|------------|
| `template_id` | string | path | The unique identifier of the template |

#### Request Body

```json
{
  "parameters": {
    "language": "python",
    "code": "def factorial(n):\n    if n == 0:\n        return 1\n    return n * factorial(n-1)"
  },
  "model": "claude-3-sonnet-20240229",
  "provider": "anthropic",
  "max_tokens": 1000,
  "temperature": 0.7,
  "metadata": {
    "user_id": "u-123",
    "session_id": "sess-456"
  }
}
```

#### Response

```json
{
  "text": "Here's a step-by-step explanation of the provided Python code:\n\n1. What the code does:\nThis function calculates the factorial of a number 'n'. In mathematics, the factorial of a non-negative integer n (written as n!) is the product of all positive integers less than or equal to n...",
  "template_id": "tmpl-123e4567-e89b-12d3-a456-426614174000",
  "model": "claude-3-sonnet-20240229",
  "provider": "anthropic",
  "usage": {
    "prompt_tokens": 86,
    "completion_tokens": 952,
    "total_tokens": 1038,
    "cost": 0.04772
  },
  "finish_reason": "stop",
  "request_id": "req-12345",
  "created_at": "2025-01-15T15:30:00Z"
}
```

## Models API

### List Models

Retrieve a list of available models.

```
GET /models
```

#### Query Parameters

| Name | Type | Description |
|------|------|------------|
| `provider` | string | Filter by provider (e.g., "openai", "anthropic") |
| `capability` | string | Filter by capability (e.g., "coding", "reasoning") |

#### Response

```json
{
  "models": [
    {
      "id": "gpt-4",
      "provider": "openai",
      "version": "gpt-4-0613",
      "description": "OpenAI's most capable model for complex tasks",
      "capabilities": ["reasoning", "coding", "creative", "instruction-following"],
      "context_window": 8192,
      "cost_per_1k_tokens": {
        "input": 0.03,
        "output": 0.06
      },
      "status": "available"
    },
    {
      "id": "claude-3-sonnet-20240229",
      "provider": "anthropic",
      "version": "claude-3-sonnet-20240229",
      "description": "Anthropic's balanced model for various tasks",
      "capabilities": ["reasoning", "coding", "creative", "instruction-following", "visual-understanding"],
      "context_window": 200000,
      "cost_per_1k_tokens": {
        "input": 0.003,
        "output": 0.015
      },
      "status": "available"
    },
    {
      "id": "claude-3-opus-20240229",
      "provider": "anthropic",
      "version": "claude-3-opus-20240229",
      "description": "Anthropic's most capable model",
      "capabilities": ["reasoning", "coding", "creative", "instruction-following", "visual-understanding"],
      "context_window": 200000,
      "cost_per_1k_tokens": {
        "input": 0.015,
        "output": 0.075
      },
      "status": "available"
    }
  ]
}
```

### Get Model Details

Retrieve details about a specific model.

```
GET /models/{model_id}
```

#### Parameters

| Name | Type | In | Description |
|------|------|----|------------|
| `model_id` | string | path | The model identifier |

#### Response

```json
{
  "id": "claude-3-sonnet-20240229",
  "provider": "anthropic",
  "version": "claude-3-sonnet-20240229",
  "description": "Anthropic's balanced model for various tasks",
  "capabilities": ["reasoning", "coding", "creative", "instruction-following", "visual-understanding"],
  "context_window": 200000,
  "cost_per_1k_tokens": {
    "input": 0.003,
    "output": 0.015
  },
  "status": "available",
  "performance_metrics": {
    "average_response_time": 2.4,
    "success_rate": 0.998,
    "average_tokens_per_second": 30
  },
  "usage_stats": {
    "total_requests": 15782,
    "total_tokens": 24563912,
    "total_cost": 312.85
  },
  "recommended_for": [
    "code generation",
    "content creation",
    "summarization",
    "question answering"
  ],
  "limitations": [
    "May occasionally produce incorrect information",
    "Limited knowledge cutoff date"
  ]
}
```

## Budget API

### Get Usage Statistics

Retrieve usage statistics.

```
GET /budget/usage
```

#### Query Parameters

| Name | Type | Description |
|------|------|------------|
| `start_date` | string | Start date for statistics (ISO 8601) |
| `end_date` | string | End date for statistics (ISO 8601) |
| `group_by` | string | Group by field (model, provider, day, user) |

#### Response

```json
{
  "summary": {
    "total_cost": 542.67,
    "total_tokens": 85792345,
    "total_requests": 24563
  },
  "breakdown": [
    {
      "model": "gpt-4",
      "provider": "openai",
      "cost": 245.32,
      "tokens": 3456789,
      "requests": 8723
    },
    {
      "model": "claude-3-sonnet-20240229",
      "provider": "anthropic",
      "cost": 201.45,
      "tokens": 32456789,
      "requests": 12845
    },
    {
      "model": "claude-3-opus-20240229",
      "provider": "anthropic",
      "cost": 95.90,
      "tokens": 1234567,
      "requests": 2995
    }
  ],
  "time_series": [
    {
      "date": "2025-01-01",
      "cost": 18.45,
      "tokens": 3245678,
      "requests": 845
    },
    {
      "date": "2025-01-02",
      "cost": 24.36,
      "tokens": 4123456,
      "requests": 956
    },
    {
      "date": "2025-01-03",
      "cost": 19.78,
      "tokens": 3567890,
      "requests": 789
    }
  ],
  "budget_status": {
    "daily_limit": 50.00,
    "monthly_limit": 1000.00,
    "daily_usage": 24.36,
    "monthly_usage": 542.67,
    "daily_remaining": 25.64,
    "monthly_remaining": 457.33
  }
}
```

### Set Budget Limits

Set budget limits for LLM usage.

```
POST /budget/limits
```

#### Request Body

```json
{
  "daily_limit": 50.00,
  "monthly_limit": 1000.00,
  "per_request_limit": 0.50,
  "per_model_limits": {
    "gpt-4": 20.00,
    "claude-3-opus-20240229": 30.00
  },
  "actions_on_limit": {
    "daily_limit_reached": "fallback_to_cheaper",
    "monthly_limit_reached": "block_requests",
    "per_request_limit_reached": "fallback_to_cheaper"
  }
}
```

#### Response

```json
{
  "success": true,
  "message": "Budget limits updated successfully",
  "limits": {
    "daily_limit": 50.00,
    "monthly_limit": 1000.00,
    "per_request_limit": 0.50,
    "per_model_limits": {
      "gpt-4": 20.00,
      "claude-3-opus-20240229": 30.00
    },
    "actions_on_limit": {
      "daily_limit_reached": "fallback_to_cheaper",
      "monthly_limit_reached": "block_requests",
      "per_request_limit_reached": "fallback_to_cheaper"
    }
  }
}
```

### Estimate Cost

Estimate the cost of a request before sending it.

```
POST /budget/estimate
```

#### Request Body

```json
{
  "prompt": "Explain the theory of relativity in detail",
  "model": "gpt-4",
  "provider": "openai",
  "max_tokens": 2000,
  "include_breakdown": true
}
```

#### Response

```json
{
  "estimated_cost": 0.1542,
  "estimated_tokens": {
    "prompt_tokens": 12,
    "estimated_completion_tokens": 2000,
    "total_tokens": 2012
  },
  "breakdown": {
    "prompt_cost": 0.00036,  // 12 tokens * $0.03/1k
    "completion_cost": 0.1538  // 2000 tokens * $0.06/1k (gpt-4 output)
  },
  "model": "gpt-4",
  "provider": "openai",
  "under_budget": true,
  "budget_status": {
    "remaining_daily": 25.64,
    "remaining_monthly": 457.33
  }
}
```

## Evaluation API

### Evaluate Response

Evaluate the quality of an LLM response.

```
POST /evaluate
```

#### Request Body

```json
{
  "prompt": "Explain quantum computing to a high school student",
  "response": "Quantum computing is like traditional computing but using some special properties of very tiny particles...",
  "criteria": ["accuracy", "clarity", "completeness"],
  "reference_text": "Quantum computing uses quantum bits or qubits which can exist in multiple states simultaneously...",
  "evaluator_model": "claude-3-sonnet-20240229"
}
```

#### Response

```json
{
  "evaluation": {
    "overall_score": 8.7,
    "criteria_scores": {
      "accuracy": 9.2,
      "clarity": 9.5,
      "completeness": 7.4
    },
    "feedback": "The response does an excellent job of explaining quantum computing in accessible terms suitable for high school students. The accuracy of the explanation is high, covering key concepts like superposition. The clarity is outstanding, using effective analogies and simple language. However, the completeness could be improved by mentioning quantum entanglement and providing more examples of potential applications."
  },
  "evaluator_model": "claude-3-sonnet-20240229",
  "evaluation_id": "eval-123e4567-e89b-12d3-a456-426614174000",
  "created_at": "2025-01-15T16:30:00Z"
}
```

### Batch Evaluate Responses

Evaluate multiple responses in a single request.

```
POST /evaluate/batch
```

#### Request Body

```json
{
  "evaluations": [
    {
      "id": "eval-1",
      "prompt": "Explain quantum computing to a high school student",
      "response": "Quantum computing is like traditional computing but using some special properties of very tiny particles...",
      "criteria": ["accuracy", "clarity", "completeness"]
    },
    {
      "id": "eval-2",
      "prompt": "Describe the water cycle",
      "response": "The water cycle is the continuous movement of water within the Earth and atmosphere...",
      "criteria": ["accuracy", "clarity", "completeness"]
    }
  ],
  "evaluator_model": "claude-3-sonnet-20240229"
}
```

#### Response

```json
{
  "evaluations": [
    {
      "id": "eval-1",
      "evaluation": {
        "overall_score": 8.7,
        "criteria_scores": {
          "accuracy": 9.2,
          "clarity": 9.5,
          "completeness": 7.4
        },
        "feedback": "The response does an excellent job of explaining quantum computing in accessible terms..."
      }
    },
    {
      "id": "eval-2",
      "evaluation": {
        "overall_score": 9.3,
        "criteria_scores": {
          "accuracy": 9.5,
          "clarity": 9.4,
          "completeness": 9.0
        },
        "feedback": "This explanation of the water cycle is comprehensive and easy to understand..."
      }
    }
  ],
  "evaluator_model": "claude-3-sonnet-20240229",
  "batch_id": "batch-123e4567-e89b-12d3-a456-426614174000",
  "created_at": "2025-01-15T17:00:00Z"
}
```

## WebSocket API

### Streaming Completions

Connect to the streaming completions WebSocket endpoint to receive real-time LLM responses.

```
ws://localhost:8005/ws/rhetor/streaming
```

#### Connection Parameters

| Name | Type | Description |
|------|------|------------|
| `api_key` | string | API key for authentication |

#### Message Format

Client -> Server:

```json
{
  "prompt": "Tell me a story about a robot learning to paint",
  "model": "gpt-4",
  "provider": "openai",
  "max_tokens": 1000,
  "temperature": 0.8,
  "stream": true,
  "system_prompt": "You are a creative storyteller."
}
```

Server -> Client (multiple messages):

```json
{
  "type": "content_chunk",
  "text": "Once upon a time",
  "index": 0
}
```

```json
{
  "type": "content_chunk",
  "text": ", there was a robot named Pixel",
  "index": 1
}
```

```json
{
  "type": "content_complete",
  "usage": {
    "prompt_tokens": 17,
    "completion_tokens": 856,
    "total_tokens": 873,
    "cost": 0.05238
  },
  "finish_reason": "stop"
}
```

### Chat Sessions

Connect to the chat WebSocket endpoint for interactive chat sessions.

```
ws://localhost:8005/ws/rhetor/chat
```

#### Connection Parameters

| Name | Type | Description |
|------|------|------------|
| `api_key` | string | API key for authentication |
| `session_id` | string | Session identifier |

#### Message Format

Client -> Server (Initialize session):

```json
{
  "type": "initialize",
  "system_prompt": "You are a helpful assistant.",
  "model": "claude-3-sonnet-20240229",
  "provider": "anthropic",
  "temperature": 0.7
}
```

Server -> Client (Initialization response):

```json
{
  "type": "initialized",
  "session_id": "sess-123e4567-e89b-12d3-a456-426614174000",
  "model": "claude-3-sonnet-20240229",
  "provider": "anthropic"
}
```

Client -> Server (Send message):

```json
{
  "type": "message",
  "content": "Hello, who are you?",
  "stream": true
}
```

Server -> Client (Stream response):

```json
{
  "type": "content_chunk",
  "text": "I'm Claude",
  "index": 0
}
```

```json
{
  "type": "content_chunk",
  "text": ", an AI assistant created by Anthropic",
  "index": 1
}
```

```json
{
  "type": "content_complete",
  "usage": {
    "prompt_tokens": 23,
    "completion_tokens": 11,
    "total_tokens": 34,
    "cost": 0.000312
  }
}
```

Client -> Server (Continue conversation):

```json
{
  "type": "message",
  "content": "What can you help me with?",
  "stream": true
}
```

Server -> Client (Stream response):

```json
{
  "type": "content_chunk",
  "text": "I can help with",
  "index": 0
}
```

```json
{
  "type": "content_chunk",
  "text": " a wide variety of tasks",
  "index": 1
}
```

```json
{
  "type": "content_complete",
  "usage": {
    "prompt_tokens": 48,
    "completion_tokens": 103,
    "total_tokens": 151,
    "cost": 0.001242
  }
}
```

## Error Responses

All endpoints follow a standard error response format:

```json
{
  "error": {
    "code": "invalid_model",
    "message": "The specified model 'gpt-5' is not available",
    "details": {
      "available_models": ["gpt-4", "gpt-3.5-turbo", "claude-3-sonnet-20240229"]
    }
  }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|------------|
| `invalid_request` | 400 | The request was malformed or invalid |
| `authentication_failed` | 401 | Authentication credentials were missing or invalid |
| `permission_denied` | 403 | The authenticated user lacks permission for the requested operation |
| `invalid_model` | 400 | The specified model is not available |
| `invalid_provider` | 400 | The specified provider is not available |
| `context_too_long` | 400 | The input context is too long for the model |
| `content_filtered` | 400 | The content was filtered due to safety concerns |
| `template_not_found` | 404 | The requested template was not found |
| `template_rendering_error` | 400 | Error rendering the template |
| `parameter_missing` | 400 | Required parameter is missing |
| `rate_limit_exceeded` | 429 | The rate limit for API requests has been exceeded |
| `budget_exceeded` | 429 | The budget limit has been exceeded |
| `provider_error` | 502 | Error from the LLM provider |
| `internal_error` | 500 | An internal server error occurred |