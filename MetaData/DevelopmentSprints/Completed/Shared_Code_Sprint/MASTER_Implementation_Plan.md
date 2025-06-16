# Tekton Shared Code - Master Implementation Plan

## Overview

This master plan consolidates all shared code implementations for Tekton, creating standardized, reusable utilities to replace duplicated code across components. The implementation will create shared bash utilities, a standardized component registration system, enhanced LLM utilities, and other core shared functionality.

## Implementation Phases

### Phase 1: Core Shell Utilities (Week 1)

#### 1. Create Bash Utility Libraries

1. Create directory structure:
```
scripts/
└── lib/
    ├── tekton-utils.sh       # Core shared utilities
    ├── tekton-ports.sh       # Port management
    ├── tekton-process.sh     # Process handling
    └── tekton-config.sh      # Configuration utilities
```

2. Implement core utility functions:
   - Color output and formatting
   - Directory detection
   - Logging functions
   - Common utility functions
   - Process management
   - Port handling

3. Create Python configuration bridge:
   - Implement `scripts/bin/tekton-config-cli.py`
   - Support environment variables and configuration files
   - Provide port management functions

4. Update core scripts:
   - Refactor `tekton-launch` to use shared libraries
   - Refactor `tekton-status` to use shared libraries
   - Refactor `tekton-kill` to use shared libraries

### Phase 2: Unified Component Registration (Week 2)

#### 1. Create `tekton-register` Utility

1. Create core registration library:
```
tekton-core/tekton/utils/registration/
├── __init__.py
├── cli.py               # Command-line interface
├── config.py            # Configuration loading
├── models.py            # Data models
├── registry.py          # Registration logic
└── heartbeat.py         # Heartbeat handling
```

2. Implement YAML configuration format:
```yaml
component:
  id: "component_id"
  name: "Component Name"
  version: "0.1.0"
  description: "Component description"
  port: 8000

capabilities:
  - id: "capability_id"
    name: "Capability Name"
    description: "Capability description"
    methods:
      - id: "method_id"
        name: "Method Name"
        description: "Method description"
        parameters:
          - name: "param_name"
            type: "string"
            required: true
        returns:
          type: "object"
```

3. Create command-line interface:
```
tekton-register register --component COMPONENT_ID [--config CONFIG_FILE] [--hermes-url URL]
tekton-register unregister --component COMPONENT_ID [--hermes-url URL]
tekton-register status --component COMPONENT_ID [--hermes-url URL]
tekton-register generate --component COMPONENT_ID [--output OUTPUT_FILE]
```

4. Implement initial component migration:
   - Create YAML configurations for Telos and Rhetor
   - Update their launch scripts to use `tekton-register`
   - Test registration functionality

### Phase 3: Enhanced LLM Integration (Week 3)

1. Create enhanced tekton-llm-client:
```
tekton-llm-client/
├── tekton_llm_client/
│   ├── prompt_templates/       # NEW: Shared prompt templates
│   │   ├── __init__.py
│   │   ├── registry.py
│   │   └── templates/
│   ├── response_handlers/      # NEW: Response parsers
│   │   ├── __init__.py
│   │   ├── json_parser.py
│   │   └── stream_handler.py
│   └── config/                 # NEW: Configuration
│       ├── __init__.py
│       └── environment.py
```

2. Implement shared prompt templates:
   - Create a registry for common system prompts
   - Implement template rendering with variables
   - Add context management utilities

3. Create response handlers:
   - Implement structured output parsing
   - Create streaming response utilities
   - Add error handling mechanisms

4. Update one initial component:
   - Migrate one component to use the enhanced LLM client
   - Create example implementation for others to follow

### Phase 4: Complete Component Migration and Cleanup (Week 4)

1. Complete component registration migration:
   - Create YAML configurations for all remaining components
   - Update all launch scripts to use `tekton-register`
   - Remove all individual `register_with_hermes.py` scripts
   - Test all components with the new registration system

2. Expand LLM client adoption:
   - Migrate remaining components to use enhanced LLM utilities
   - Convert existing prompt templates to the shared system
   - Standardize response handling across components

3. Apply shell utilities:
   - Update all component setup scripts to use shared utilities
   - Standardize launch processes across components
   - Create consistent configuration handling

4. Update documentation:
   - Update `docs/COMPONENT_LIFECYCLE.md`
   - Update `docs/SHARED_COMPONENT_UTILITIES.md`
   - Create a comprehensive shared code reference
   - Document migration paths for future components

## Core Implementation Details

### Bash Utility Library

```bash
#!/bin/bash
# tekton-utils.sh - Core shared utilities

# ANSI color codes
export TEKTON_COLOR_BLUE="\033[94m"
export TEKTON_COLOR_GREEN="\033[92m"
export TEKTON_COLOR_YELLOW="\033[93m"
export TEKTON_COLOR_RED="\033[91m"
export TEKTON_COLOR_BOLD="\033[1m"
export TEKTON_COLOR_RESET="\033[0m"

# Tekton directory detection
tekton_find_root() {
  local script_dir="$1"
  # Detection logic here
}

# Logging functions
tekton_log_info() {
  echo -e "${TEKTON_COLOR_BLUE}[INFO]${TEKTON_COLOR_RESET} $*"
}

# Additional utility functions
# ...
```

### Component Registration Library

```python
#!/usr/bin/env python3
"""
Tekton Component Registration Tool

Registers Tekton components with Hermes service registry.
"""

import sys
import os
import argparse
import asyncio
import signal
import yaml
import logging
from typing import Dict, List, Any, Optional

# Core registration functionality
class HermesRegistrationClient:
    """Client for Hermes registration service."""
    
    def __init__(self, component_id: str, hermes_url: str):
        self.component_id = component_id
        self.hermes_url = hermes_url
        # Initialize client
    
    async def register(self, capabilities: List[Dict[str, Any]]) -> bool:
        """Register component with Hermes."""
        # Registration implementation
        
    async def start_heartbeat(self) -> None:
        """Start heartbeat process."""
        # Heartbeat implementation
        
    async def close(self) -> None:
        """Unregister and close client."""
        # Cleanup implementation

# Main command functions
async def register_command(args):
    """Register a component with Hermes."""
    # Implementation
    
async def unregister_command(args):
    """Unregister a component from Hermes."""
    # Implementation
    
def generate_command(args):
    """Generate a component configuration template."""
    # Implementation

# Main entry point
async def main():
    """Main entry point."""
    # Parse arguments and dispatch to appropriate command
    
if __name__ == "__main__":
    asyncio.run(main())
```

### LLM Integration Utilities

```python
# Enhanced LLM client with prompt templates and response handlers

class PromptTemplate:
    """Template for LLM prompts with variable substitution."""
    
    def __init__(self, template_string: str):
        self.template = template_string
        
    def render(self, **kwargs) -> str:
        """Render template with variables."""
        return self.template.format(**kwargs)

class PromptRegistry:
    """Registry for common prompt templates."""
    
    def __init__(self):
        self.templates = {}
        
    def register(self, name: str, template: str) -> None:
        """Register a new template."""
        self.templates[name] = PromptTemplate(template)
        
    def get(self, name: str) -> PromptTemplate:
        """Get a template by name."""
        return self.templates.get(name)

# Additional LLM utilities
# ...
```

## Migration Strategy

For each component, follow this migration process:

1. Update to use shared bash utilities:
   - Replace custom bash functions with shared utilities
   - Use standardized logging and configuration

2. Migrate to tekton-register:
   - Create YAML configuration file
   - Update launch script to use tekton-register
   - Remove component-specific register_with_hermes.py

3. Enhance LLM integration:
   - Update LLM adapters to use shared client
   - Convert prompt templates to shared registry
   - Use standardized response handlers

4. Test and validate:
   - Verify all functionality works with shared code
   - Ensure registration with Hermes works correctly
   - Validate component startup and shutdown

## Cleanup Strategy

After migration, remove all replaced code:

1. Delete all individual register_with_hermes.py scripts
2. Remove duplicated bash utility functions
3. Clean up redundant configuration loading
4. Consolidate error handling and logging

## Documentation Updates

Update the following documentation:

1. `docs/COMPONENT_LIFECYCLE.md` - Update with standardized registration process
2. `docs/SHARED_COMPONENT_UTILITIES.md` - Document all shared utilities
3. `docs/STANDARDIZED_ERROR_HANDLING.md` - Update with shared error handling
4. Component-specific documentation - Update to reference shared utilities

## Success Criteria

The implementation is successful when:

1. All components use shared bash utilities
2. All components register with Hermes using tekton-register
3. Components use enhanced LLM client where appropriate
4. No duplicated utility code remains across components
5. Documentation is updated to reflect the new approach
6. All tests pass successfully