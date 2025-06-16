# Hermes

## Overview

Hermes is the central message bus and component registration system for the Tekton ecosystem. It facilitates communication between components, manages component lifecycles, and provides service discovery capabilities.

## Key Features

- Message routing between Tekton components
- Component registration and discovery
- Lifecycle management (startup, monitoring, recovery)
- Centralized logging system
- Database services coordination

## Quick Start

```bash
# Start Hermes standalone
./scripts/tekton_launch --components hermes

# Check Hermes status
curl http://localhost:8000/health

# Run the registration server
python -m hermes.scripts.run_registration_server
```

## Documentation

For detailed documentation, see the following resources in the MetaData directory:

- [Component Summaries](../MetaData/ComponentSummaries.md) - Overview of all Tekton components
- [Tekton Architecture](../MetaData/TektonArchitecture.md) - Overall system architecture
- [Component Integration](../MetaData/ComponentIntegration.md) - How components interact
- [CLI Operations](../MetaData/CLI_Operations.md) - Command-line operations