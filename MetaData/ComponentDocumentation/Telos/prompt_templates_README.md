# Telos Prompt Templates

This directory contains prompt templates for the Telos Requirements Management System. These templates are used by the LLM adapter to format prompts for requirement analysis, refinement, validation, and other operations.

## Template Usage

Templates are loaded and registered by the `PromptTemplateRegistry` in the LLM adapter. While some templates are defined inline, more complex templates can be stored in this directory as JSON or YAML files.

## Available Templates

The Telos system uses the following prompt templates:

1. **requirement_analysis**: Templates for analyzing requirements against quality criteria
2. **requirement_refinement**: Templates for refining requirements based on feedback
3. **requirement_validation**: Templates for validating requirements against specific criteria
4. **conflict_detection**: Templates for detecting conflicts between requirements
5. **acceptance_criteria_generation**: Templates for generating acceptance criteria

Additionally, corresponding system prompts are available for each template type.

## Format

Templates can be defined in JSON format:

```json
{
  "name": "requirement_analysis",
  "template": "Please analyze this requirement:\n\n{{ requirement_text }}...",
  "description": "Template for requirement analysis"
}
```

Or in YAML format:

```yaml
name: requirement_analysis
template: |-
  Please analyze this requirement:

  {{ requirement_text }}
  ...
description: Template for requirement analysis
```

## Adding New Templates

To add new templates, create a JSON or YAML file in this directory with the appropriate structure, and the LLM adapter will automatically load it at initialization time.