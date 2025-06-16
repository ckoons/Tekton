# Tekton Documentation

This directory contains the centralized documentation for the Tekton project. The structure is organized as follows:

## 🎯 Critical Configuration Files

**IMPORTANT**: When adding or modifying Tekton components, these are the ONLY files that need to be updated:

1. **`/config/tekton_components.yaml`** - Single source of truth for ALL component definitions
   - Component names, ports, descriptions, categories
   - Startup priorities and dependencies
   - Used by all Python scripts and tools

2. **`/config/port_assignments.md`** - Official port assignments document
   - Port numbers and environment variables
   - Read by `/tekton/utils/port_config.py`

See `/config/CENTRALIZED_CONFIG.md` for detailed usage instructions.

## Directory Structure

- **ComponentDocumentation/**: Documentation specific to individual Tekton components
  - Each component has its own subdirectory (e.g., `Hermes/`, `Engram/`, etc.)
  - Component-specific documentation follows a standardized format

- **TektonDocumentation/**: Project-level documentation
  - **Architecture/**: System architecture, design patterns, and integration guides
  - **UserGuides/**: End-user guides for using Tekton and its components
  - **DeveloperGuides/**: Guidelines for developers working on Tekton
  - **APIReference/**: API documentation for inter-component communication
  - **Tutorials/**: Step-by-step tutorials for common tasks

- **Templates/**: Standardized templates for documentation
  - **ComponentREADME/**: Templates for component README files
  - **APIReference/**: Templates for API documentation
  - **UserGuide/**: Templates for user guides
  - **DeveloperGuide/**: Templates for developer guides
  - **Implementation/**: Templates for implementation documentation

- **DevelopmentSprints/**: Documentation from development sprints
  - Organized by sprint or feature branch

## Documentation Standards

All documentation should:
1. Follow the templates provided in the Templates directory
2. Include clear examples where appropriate
3. Be kept up-to-date with code changes
4. Use consistent terminology across components
5. Include links to related documentation

## Contributing to Documentation

When contributing to the documentation:
1. Use the appropriate template for new documents
2. Place component-specific documentation in the corresponding component directory
3. Update cross-references when adding or modifying documents
4. Submit documentation changes with related code changes