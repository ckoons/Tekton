# CI Thinking Levels and Dynamic Model Selection

## Overview

Tekton's CI system now features intelligent, keyword-based model selection that automatically chooses the appropriate model based on the complexity and nature of your request. This system uses the gpt-oss models as the primary choice, with automatic fallback to other available models when needed.

## Default Model

The system now defaults to **gpt-oss:20b** for quick, routine tasks. This 13GB model provides fast response times while maintaining good quality for most interactions.

## Thinking Levels

### Level 1: Quick Response (Default)
- **Model**: gpt-oss:20b
- **Temperature**: 0.5
- **Max Tokens**: 1536
- **Triggers**: Default for all queries without special keywords
- **Keywords**: "quick", "simple", "list", "show", "status", "check", "what", "where", "when"
- **Use Cases**: 
  - Status checks
  - Simple queries
  - Listing information
  - Basic questions
  - Routine operations

### Level 2: Problem Solving
- **Model**: gpt-oss:120b
- **Temperature**: 0.6
- **Max Tokens**: 2048
- **Keywords**: "write code", "implement", "create function", "generate", "solve", "fix", "optimize", "refactor"
- **Use Cases**:
  - Code generation
  - Bug fixing
  - Implementation tasks
  - Optimization problems
  - Refactoring operations

### Level 3: Analytical Thinking
- **Model**: gpt-oss:120b
- **Temperature**: 0.7
- **Max Tokens**: 3072
- **Keywords**: "think about", "consider this", "analyze", "explain why", "understand", "debug", "investigate", "examine", "evaluate"
- **Use Cases**:
  - Code analysis
  - Debugging complex issues
  - Architectural decisions
  - System evaluation
  - In-depth explanations

### Level 4: Deep Reasoning
- **Model**: gpt-oss:120b
- **Temperature**: 0.9
- **Max Tokens**: 4096
- **Keywords**: "deeply think", "carefully consider", "contemplate", "reason through", "comprehensive analysis", "thorough examination", "full review", "explore all", "extensive analysis"
- **Use Cases**:
  - Complex problem-solving
  - Creative solutions
  - Comprehensive code reviews
  - Strategic planning
  - Extensive documentation analysis

## How It Works

The system automatically detects keywords in your message and selects the appropriate model and parameters. This happens transparently - you simply phrase your request naturally and the system adapts.

### Examples

1. **Quick Task**: "Show me the project status"
   - Uses: gpt-oss:20b (fast response)

2. **Code Generation**: "Write code to implement a binary search"
   - Uses: gpt-oss:120b with problem-solving parameters

3. **Analysis**: "Analyze why this function is performing slowly"
   - Uses: gpt-oss:120b with analytical parameters

4. **Deep Thinking**: "Deeply think about the architectural implications of this design"
   - Uses: gpt-oss:120b with maximum reasoning capacity

## Benefits

1. **Resource Optimization**: Only uses large models when necessary
2. **Faster Response Times**: Quick model for simple queries
3. **Better Quality**: Appropriate reasoning depth for each task
4. **Natural Interface**: No need to manually select models
5. **Transparent Operation**: Works automatically based on your language

## Technical Implementation

The model selection logic is implemented in `/shared/ai/specialist_worker.py` in the `detect_thinking_level()` method. Each CI specialist inherits this capability, allowing all Tekton CIs to dynamically adjust their thinking level.

### Response Metadata

When an CI responds, it includes metadata about the thinking level used:
- `model`: The actual model used (e.g., "gpt-oss:120b")
- `thinking_level`: Human-readable level (e.g., "Deep Reasoning")
- `temperature`: The temperature setting used
- `max_tokens`: The token limit applied

## Configuration

### Project-Level Model Selection

When creating new projects, you can still manually select a companion intelligence model. The UI now offers:
- gpt-oss:20b (Default - Fast)
- gpt-oss:120b (Smart - Deep Thinking)
- Traditional models (llama3.3:70b, etc.)

### Environment Variables

AI specialists can be configured with specific models using environment variables:
```bash
<COMPONENT>_AI_MODEL=gpt-oss:120b
```

## Model Characteristics

### gpt-oss:20b
- **Size**: 13 GB
- **Speed**: Fast loading and response
- **Best For**: Routine tasks, quick queries, standard development
- **Context Window**: 32K tokens

### gpt-oss:120b
- **Size**: 65 GB
- **Speed**: Slower loading, thoughtful responses
- **Best For**: Complex reasoning, deep analysis, creative solutions
- **Context Window**: 32K tokens

## Fallback Behavior

If a requested model is not available, the system will:
1. Fall back to the default gpt-oss:20b
2. If that's unavailable, use llama3.3:70b
3. Log the fallback for monitoring

## Future Enhancements

Planned improvements include:
- Learning from user feedback to refine keyword detection
- Per-component model preferences
- Context-aware model selection based on conversation history
- Preemptive model loading based on detected patterns