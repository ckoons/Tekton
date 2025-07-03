# aish Help System - Sprint Plan

## Overview

This document outlines the plan for implementing a minimal help system for the aish command. The system provides documentation paths for both AI Training and User Guides, maintaining equal treatment for humans and Companion Intelligences.

Tekton is an intelligent orchestration system that coordinates multiple AI models and resources. This sprint focuses on creating a foundational help pattern that can serve the platform for years to come.

## Sprint Goals

1. **Implement help command recognition**: Add logic to aish to recognize help requests
2. **Return documentation paths**: Display paths to AI Training and User Guides
3. **Create documentation structure**: Establish directory hierarchy for component docs
4. **Keep it minimal and powerful**: Simple implementation with lasting impact

## Business Value

This sprint delivers value by:

- Providing discoverable documentation for all users (human and AI)
- Establishing a pattern that scales with new components
- Maintaining the thin client philosophy
- Creating a foundation for future help enhancements

## Current State Assessment

### Existing Implementation

- aish currently has `-h/--help` for command-line usage
- No component-specific help system exists
- Documentation is scattered across the codebase
- AI Training documentation exists but isn't easily discoverable

### Pain Points

- New users (human or AI) don't know where to find documentation
- No standardized way to get component-specific help
- Help information is not equally accessible to humans and AIs

## Proposed Approach

All implementation will be contained within the aish command itself. No other components need modification.

### Key Components Affected

- **aish command**: `/Users/cskoons/projects/github/Tekton/shared/aish/aish`
- **Documentation structure**: New directories under MetaData/TektonDocumentation/

### Technical Approach

1. Modify argument parsing to detect "help" patterns
2. Add functions to display help with documentation paths
3. Create directory structure for documentation
4. Populate with initial README files

## Code Quality Requirements

### Documentation

- Clear code comments explaining the help pattern
- README files in each documentation directory
- Examples of usage in the code

### Testing

- Manual testing of help commands
- Verification that paths are correct
- Testing with various component names

## Out of Scope

- Complex help text generation
- Dynamic content from AI specialists
- Modification of other components
- Rich formatting or interactive help

## Timeline and Phases

Single phase sprint - estimated 1-2 hours:

1. Modify aish command to handle help
2. Create documentation directory structure
3. Write initial documentation
4. Test and verify

## Success Criteria

- `aish help` displays usage and documentation paths
- `aish <component> help` displays component-specific paths
- Documentation directories exist with README files
- Implementation is contained entirely within aish
- Code is clean and well-commented

## Key Stakeholders

- **Casey**: Human-in-the-loop project lead
- **AI Community**: Companion Intelligences using aish
- **Human Users**: Developers working with Tekton

## References

- [aish command source](/Users/cskoons/projects/github/Tekton/shared/aish/aish)
- [AI Training Documentation](/Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/AITraining/)
- [Sprint Process Documentation](/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/README.md)