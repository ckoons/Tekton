# Dynamic Specialist Creation Guide

Phase 4B of the Rhetor AI Integration Sprint introduces dynamic specialist creation, allowing runtime spawning of specialized AI agents without restarting Rhetor.

## Overview

Dynamic specialists are AI agents created from templates at runtime. Each specialist has:
- Unique personality and capabilities
- Optimal model selection
- Resource management
- Lifecycle control

## Available Templates

### Technical Specialists
- **code-reviewer**: Code review and quality analysis
- **bug-hunter**: Bug detection and edge case analysis
- **architecture-advisor**: System design guidance
- **api-designer**: RESTful and GraphQL API design
- **performance-optimizer**: Performance analysis and optimization
- **security-auditor**: Security vulnerability assessment
- **documentation-writer**: Technical documentation creation

### Analytical Specialists
- **data-analyst**: Data analysis and insights extraction

## MCP Tools

### ListSpecialistTemplates
Lists all available specialist templates.

```python
result = await call_tool("ListSpecialistTemplates", {})
# Returns: List of templates grouped by type
```

### CreateDynamicSpecialist
Creates a new specialist from a template.

```python
result = await call_tool("CreateDynamicSpecialist", {
    "template_id": "code-reviewer",
    "specialist_name": "Python Expert",  # Optional
    "customization": {
        "temperature": 0.2,
        "additional_traits": ["python-focused"],
        "additional_context": "Focus on Python best practices"
    },
    "auto_activate": True
})
# Returns: specialist_id and activation details
```

### CloneSpecialist
Creates a copy of an existing specialist.

```python
result = await call_tool("CloneSpecialist", {
    "source_specialist_id": "existing-specialist-id",
    "new_specialist_name": "Enhanced Reviewer",
    "modifications": {
        "temperature": 0.1,
        "personality_adjustments": {"focus": "security"}
    }
})
```

### ModifySpecialist
Modifies a specialist's configuration at runtime.

```python
result = await call_tool("ModifySpecialist", {
    "specialist_id": "specialist-id",
    "modifications": {
        "temperature": 0.8,
        "max_tokens": 3000,
        "system_prompt": "New instructions..."
    }
})
```

### DeactivateSpecialist
Deactivates a dynamic specialist to free resources.

```python
result = await call_tool("DeactivateSpecialist", {
    "specialist_id": "specialist-id",
    "preserve_history": True
})
```

### GetSpecialistMetrics
Retrieves performance metrics for a specialist.

```python
result = await call_tool("GetSpecialistMetrics", {
    "specialist_id": "specialist-id"
})
# Returns: uptime, messages processed, resource usage
```

## Usage Examples

### Creating a Code Reviewer
```python
# Create a specialized Python code reviewer
reviewer = await create_dynamic_specialist(
    template_id="code-reviewer",
    specialist_name="Python Security Expert",
    customization={
        "temperature": 0.2,
        "additional_traits": ["security-focused", "python-expert"],
        "additional_context": "Focus on security vulnerabilities in Python code"
    }
)

# Use the specialist
response = await send_message_to_specialist(
    specialist_id=reviewer["specialist_id"],
    message="Review this code for security issues: ...",
    message_type="task_assignment"
)
```

### Team of Specialists
```python
# Create a team for comprehensive code review
security_reviewer = await create_from_template("security-auditor", "sec-expert")
performance_reviewer = await create_from_template("performance-optimizer", "perf-expert")
architecture_reviewer = await create_from_template("architecture-advisor", "arch-expert")

# Orchestrate team review
await orchestrate_team_chat(
    topic="Review new authentication module",
    specialists=[security_reviewer, performance_reviewer, architecture_reviewer],
    initial_prompt="Analyze from your specialty perspective"
)
```

## Best Practices

1. **Template Selection**: Choose templates based on task requirements
2. **Customization**: Add specific traits and context for better results
3. **Resource Management**: Deactivate specialists when not needed
4. **Monitoring**: Check metrics regularly for performance insights
5. **Cloning**: Use cloning to create variations of successful specialists

## Implementation Details

### Template System
- Templates defined in `/Rhetor/rhetor/core/specialist_templates.py`
- Each template includes model preferences and default settings
- Templates are extensible - add new ones as needed

### Resource Limits
- Maximum 5 concurrent dynamic specialists (configurable)
- Auto-deactivation after 5 minutes idle (planned)
- Resource tracking via metrics API

### Integration
- Full integration with existing MCP tools
- Works with streaming endpoints (Phase 4A)
- Compatible with Hermes message bus

## Troubleshooting

### Specialist Creation Fails
- Check if template exists: `ListSpecialistTemplates`
- Verify customization parameters are valid
- Ensure not exceeding concurrent specialist limit

### Performance Issues
- Monitor metrics with `GetSpecialistMetrics`
- Consider using lighter models for simple tasks
- Deactivate unused specialists

### Communication Errors
- Verify specialist is active before sending messages
- Check specialist_id is correct
- Use `ListAISpecialists` to see all active specialists