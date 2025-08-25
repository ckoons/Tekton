# aish Help System - Sprint Plan

## Overview

This document outlines the plan for implementing a minimal help system for the aish command. The system provides documentation paths for both CI Training and User Guides, maintaining equal treatment for humans and Companion Intelligences.

Tekton is an intelligent orchestration system that coordinates multiple CI models and resources. This sprint focuses on creating a foundational help pattern that can serve the platform for years to come.

## Sprint Goals

1. **Fix aish syntax**: Implement unified `aish [component] [command/message]` pattern
2. **Enable CI message visibility**: In-memory two-inbox system for inter-terminal messages
3. **Implement help command recognition**: Add logic to aish to recognize help requests
4. **Return documentation paths**: Display paths to CI Training and User Guides
5. **Create documentation structure**: Establish directory hierarchy for component docs

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
- CI Training documentation exists but isn't easily discoverable

### Pain Points

- New users (human or AI) don't know where to find documentation
- No standardized way to get component-specific help
- Help information is not equally accessible to humans and CIs

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
- Dynamic content from CI specialists
- Modification of other components
- Rich formatting or interactive help

## Timeline and Phases

Expanded sprint with four implementation phases:

### Phase 1: Fix aish Syntax (30 minutes)
- Implement unified router in aish command
- Fix direct CI messaging (no synthetic pipelines)
- Test with all CI components

### Phase 2: Fix Message Display (15 minutes)
- Update aish-proxy to write to /dev/tty
- Ensure messages don't interfere with prompts
- Test inter-terminal messaging

### Phase 3: Implement Two-Inbox System (45 minutes)
- Add in-memory message storage to aish-proxy
- Implement inbox commands in terma.py
- Test inbox operations (new, keep, read, trash)

### Phase 4: Add Help System (30 minutes)
- Integrate help command with unified router
- Create documentation directory structure
- Test help for all components

## Success Criteria

- `aish help` displays usage and documentation paths
- `aish <component> help` displays component-specific paths
- Documentation directories exist with README files
- Implementation is contained entirely within aish
- Code is clean and well-commented

## Key Stakeholders

- **Casey**: Human-in-the-loop project lead
- **CI Community**: Companion Intelligences using aish
- **Human Users**: Developers working with Tekton

## References

- [aish command source](/Users/cskoons/projects/github/Tekton/shared/aish/aish)
- [CI Training Documentation](/Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/AITraining/)
- [Sprint Process Documentation](/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/README.md)