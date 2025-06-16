# Prometheus Prompt Templates

This directory contains prompt templates for the Prometheus planning system. These templates are used by the LLM adapter to format prompts for various planning and analysis tasks.

## Template Usage

Templates are loaded and registered by the `PromptTemplateRegistry` in the LLM adapter. While some templates are defined inline in the adapter, more complex templates can be stored in this directory as JSON or YAML files.

## Available Templates

The Prometheus system uses the following prompt templates:

1. **task_breakdown**: Templates for breaking down requirements into tasks
2. **retrospective_analysis**: Templates for analyzing retrospective data
3. **improvement_suggestions**: Templates for generating improvement suggestions
4. **risk_analysis**: Templates for identifying and analyzing project risks
5. **critical_path_analysis**: Templates for analyzing the critical path through a project

Additionally, corresponding system prompts are available for each template type.

## Format

Templates can be defined in JSON format:

```json
{
  "name": "task_breakdown",
  "template": "Given the following requirements, break them down into specific implementation tasks...",
  "description": "Template for breaking down requirements into tasks",
  "output_format": "json",
  "version": "1.0.0"
}
```

Or in YAML format:

```yaml
name: task_breakdown
template: |-
  Given the following requirements, break them down into specific implementation tasks...
description: Template for breaking down requirements into tasks
output_format: json
version: 1.0.0
```

## Adding New Templates

To add new templates, create a JSON or YAML file in this directory with the appropriate structure, and the LLM adapter will automatically load it at initialization time.