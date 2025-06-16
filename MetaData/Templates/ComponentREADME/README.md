# Component README Template

This template provides a standardized structure for Tekton component README files.

## Usage

1. Copy this template to your component's README.md
2. Replace placeholders (indicated by `{placeholders}`) with your component's information
3. Remove any sections that don't apply to your component
4. Add any additional sections specific to your component

## Template

```markdown
# {Component Name}

![Component Icon](./images/icon.jpg)

## Overview

{Brief description of the component, its purpose, and role within Tekton}

## Features

- {Feature 1}: {Brief description}
- {Feature 2}: {Brief description}
- {Feature 3}: {Brief description}

## Architecture

{Brief description of the component's internal architecture and integration points}

### Key Concepts

- **{Concept 1}**: {Brief explanation}
- **{Concept 2}**: {Brief explanation}
- **{Concept 3}**: {Brief explanation}

## Integration

### Dependencies

- {Dependency 1}: {Purpose and integration type}
- {Dependency 2}: {Purpose and integration type}

### API

{Brief overview of the component's API - refer to detailed API documentation}

## Setup and Installation

### Prerequisites

- {Prerequisite 1}
- {Prerequisite 2}

### Installation

```bash
# Installation commands
./setup.sh
```

## Usage

### Basic Usage

```python
# Example code showing basic usage
from {component} import Client

client = Client()
result = client.some_function()
```

### Advanced Scenarios

{Description of advanced usage scenarios with examples}

## Development

### Getting Started

{Instructions for developers who want to work on this component}

### Testing

{Instructions for running tests}

## Documentation

- [User Guide](./docs/user_guide.md)
- [API Reference](./docs/api_reference.md)
- [Developer Guide](./docs/developer_guide.md)

## License

{License information}
```