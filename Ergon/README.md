# Ergon

## Overview

Ergon is the container management and solution registry platform for the Tekton ecosystem. It provides a comprehensive system for storing, testing, and composing deployable solutions with automated standards compliance and sandbox testing capabilities.

## Key Features

### Registry System
- JSON-based universal storage for deployable units
- Automatic import from TektonCore completed projects
- Standards compliance checking and scoring
- Solution lineage tracking and versioning
- Type-based organization (containers, solutions, tools, configs)

### Sandbox Testing
- Isolated testing environments for Registry solutions
- Multiple provider support (sandbox-exec for macOS, Docker for full isolation)
- Real-time output streaming
- Resource limits and monitoring
- One-click testing from Registry UI

### Additional Capabilities
- Agent creation and configuration
- Tool registration and discovery
- Workflow definition and execution
- MCP (Model Control Protocol) implementation
- Multi-agent collaboration

## Quick Start

```bash
# Start Ergon
./run_tekton_ui.sh

# Start Ergon UI without authentication
./run_ui_no_auth.sh

# Run the chatbot interface
./run_chatbot
```

## Documentation

For detailed documentation, see the following resources in the MetaData directory:

- [Component Summaries](../MetaData/ComponentSummaries.md) - Overview of all Tekton components
- [Tekton Architecture](../MetaData/TektonArchitecture.md) - Overall system architecture
- [Component Integration](../MetaData/ComponentIntegration.md) - How components interact
- [CLI Operations](../MetaData/CLI_Operations.md) - Command-line operations
- [GUI Operations](../MetaData/GUI_Operations.md) - UI operations
- [Prebuilt Agents](../MetaData/Ergon_PREBUILT_AGENTS.md) - Available agent templates