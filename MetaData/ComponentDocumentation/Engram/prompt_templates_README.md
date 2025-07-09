# Engram Prompt Templates

This directory contains prompt templates for the Engram memory system. These templates are used by the LLM adapter to format prompts for memory analysis, categorization, and summarization tasks.

## Template Usage

Templates are loaded and registered by the `PromptTemplateRegistry` in the LLM adapter. While some templates are defined inline, more complex templates can be stored in this directory as JSON or YAML files.

## Available Templates

The Engram system uses the following prompt templates:

1. **memory_analysis**: Templates for analyzing memory content
2. **memory_categorization**: Templates for categorizing memory into predefined categories 
3. **memory_summarization**: Templates for summarizing related memories

Additionally, corresponding system prompts are available for each template type.

## Format

Templates can be defined in JSON format:

```json
{
  "template": "Please analyze the following content:\n\n{content}\n\n{context_prompt}",
  "output_format": "text",
  "description": "Analysis of memory content"
}
```

Or in YAML format:

```yaml
template: |-
  Please analyze the following content:

  {content}

  {context_prompt}
output_format: text
description: Analysis of memory content
```

## Adding New Templates

To add new templates, create a JSON or YAML file in this directory with the appropriate structure, and modify the `_load_templates` method in the LLM adapter to load it.