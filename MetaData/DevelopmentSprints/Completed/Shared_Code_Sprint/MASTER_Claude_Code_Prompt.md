# Tekton Shared Code Implementation Sprint

## Overview

This sprint focuses on creating standardized, shared code utilities across the Tekton ecosystem, eliminating code duplication, improving maintainability, and ensuring consistent behavior across components. You will implement shared bash utilities, a unified component registration system, enhanced LLM integration utilities, and other core shared functionality.

## Sprint Objectives

1. Create shared bash utility libraries for common functions used across components
2. Implement a unified `tekton-register` utility to replace individual `register_with_hermes.py` scripts
3. Enhance the tekton-llm-client with shared prompt templates and response handlers
4. Migrate all components to use these shared utilities
5. Remove duplicated code after successful migration
6. Update documentation to reflect the standardized approaches

## Implementation Tasks

### Phase 1: Core Shell Utilities

1. **Create Bash Utility Libraries**
   - Create directory structure in `scripts/lib/`
   - Implement core utility functions (logging, directory detection, etc.)
   - Create port and process management utilities
   - Implement configuration utilities

2. **Create Python Configuration Bridge**
   - Implement `scripts/bin/tekton-config-cli.py` for bash/Python integration
   - Support environment variables and configuration files
   - Provide port management functions

3. **Update Core Scripts**
   - Refactor `tekton-launch`, `tekton-status`, and `tekton-kill` to use shared libraries
   - Test to ensure functionality is preserved

### Phase 2: Unified Component Registration

1. **Create tekton-register Utility**
   - Implement core registration library in `tekton-core/tekton/utils/registration/`
   - Create YAML configuration format for component capabilities
   - Implement command-line interface at `tekton-core/scripts/bin/tekton-register`

2. **Implement Component Migration**
   - Create YAML configurations for initial components (Telos and Rhetor)
   - Update their launch scripts to use `tekton-register`
   - Test registration functionality

3. **Continue Component Migration**
   - Create YAML configurations for all remaining components
   - Update all launch scripts to use `tekton-register`
   - Remove all individual `register_with_hermes.py` scripts

### Phase 3: Enhanced LLM Integration

1. **Enhance tekton-llm-client**
   - Create shared prompt template system
   - Implement response handlers for different output formats
   - Add configuration utilities

2. **Migrate Components to Enhanced Client**
   - Update component LLM adapters to use shared client
   - Convert prompt templates to shared registry
   - Use standardized response handlers

### Phase 4: Cleanup and Documentation

1. **Complete Component Migration**
   - Ensure all components use shared utilities
   - Remove all duplicated code
   - Test all functionality

2. **Update Documentation**
   - Update `docs/COMPONENT_LIFECYCLE.md`
   - Update `docs/SHARED_COMPONENT_UTILITIES.md`
   - Create a comprehensive shared code reference

## Implementation Guidelines

1. **Code Quality**
   - Follow Tekton's Python and Bash style guidelines
   - Include comprehensive docstrings for all functions and classes
   - Write clear and consistent error messages
   - Implement proper logging throughout

2. **Compatibility**
   - Ensure backward compatibility where needed
   - Support graceful degradation when dependencies are unavailable
   - Provide clear migration paths for components

3. **Error Handling**
   - Implement robust error handling in all utilities
   - Use consistent error patterns across all shared code
   - Provide helpful error messages for troubleshooting

4. **Documentation**
   - Document all shared utilities thoroughly
   - Include examples for common use cases
   - Create migration guides for component developers

## Specific Implementation Details

### Bash Utility Structure

```
scripts/
└── lib/
    ├── tekton-utils.sh       # Core shared utilities
    ├── tekton-ports.sh       # Port management
    ├── tekton-process.sh     # Process handling
    └── tekton-config.sh      # Configuration utilities
```

### Component Registration Library Structure

```
tekton-core/tekton/utils/registration/
├── __init__.py
├── cli.py               # Command-line interface
├── config.py            # Configuration loading
├── models.py            # Data models
├── registry.py          # Registration logic
└── heartbeat.py         # Heartbeat handling
```

### YAML Configuration Format

```yaml
# component.yaml
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

### LLM Client Enhancements

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

## Deliverables

1. **Shared Bash Utilities**
   - Complete implementation of all bash utility libraries
   - Updated core scripts using these utilities

2. **tekton-register Utility**
   - Core registration library
   - Command-line interface
   - YAML configuration format and validation
   - All components migrated to the new system
   - All individual `register_with_hermes.py` scripts removed

3. **Enhanced LLM Client**
   - Shared prompt template system
   - Response handlers for different output formats
   - Configuration utilities
   - Components migrated to use the enhanced client

4. **Updated Documentation**
   - Comprehensive shared code reference
   - Migration guides for component developers
   - Updated component lifecycle documentation

## Testing Requirements

1. Test shared bash utilities with different scenarios
2. Verify component registration for all components
3. Test LLM integration with different models
4. Ensure all error cases are handled properly

## Documentation Requirements

1. Update `docs/COMPONENT_LIFECYCLE.md` with the standardized registration process
2. Update `docs/SHARED_COMPONENT_UTILITIES.md` with all shared utilities
3. Create a comprehensive shared code reference
4. Document migration paths for future components

## Clean-up Requirements

1. After successful migration:
   - Remove all individual `register_with_hermes.py` scripts
   - Remove duplicated bash utilities in component directories
   - Clean up redundant configuration code
   - Standardize error handling and logging

## Success Criteria

The implementation is successful when:
1. All components use shared bash utilities
2. All components register with Hermes using tekton-register
3. Components use enhanced LLM client where appropriate
4. No duplicated utility code remains across components
5. Documentation is updated to reflect the new approach
6. All tests pass successfully