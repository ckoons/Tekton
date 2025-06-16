# Tekton Development Sprints

This directory contains documentation and artifacts for Tekton Development Sprints.

## Recent Updates

### Debug Instrumentation Requirements

**All Tekton Development Sprints must now follow the [Debug Instrumentation Guidelines](/MetaData/TektonDocumentation/DeveloperGuides/Debugging/DebuggingInstrumentation.md).**

This comprehensive instrumentation approach:
- Provides zero-overhead debugging capabilities when disabled
- Enables rich diagnostics when enabled
- Supports both frontend (JavaScript) and backend (Python) components
- Integrates with existing logging systems

All new code and significant modifications to existing code must include appropriate debug instrumentation as specified in the guidelines.

## What is a Development Sprint?

A Development Sprint is a structured approach to implementing new features, addressing technical debt, and improving the Tekton ecosystem. Each sprint follows a defined process with clear roles, phases, and deliverables.

Tekton is an intelligent orchestration system that coordinates multiple AI models and resources to efficiently solve complex software engineering problems. This Development Sprint process is designed to facilitate the continuous improvement of Tekton in a systematic and documented way.

## Sprint Directory Structure

Each Development Sprint has its own directory under `MetaData/DevelopmentSprints/`:

```
MetaData/DevelopmentSprints/
├── README.md                         # This file explaining the overall process
├── Templates/                        # Templates for standard sprint documents
│   ├── SprintPlan.md
│   ├── ArchitecturalDecisions.md
│   ├── ImplementationPlan.md
│   ├── StatusReport.md
│   ├── Retrospective.md
│   └── PromptTemplate.md
└── [SprintName]/                     # One directory per sprint
    ├── README.md                     # Sprint-specific guidance
    ├── SprintPlan.md                 # High-level sprint plan
    ├── ArchitecturalDecisions.md     # Key architectural decisions
    ├── ImplementationPlan.md         # Detailed implementation plan
    ├── ClaudeCodePrompt.md           # Initial prompt for Working Claude
    ├── StatusReports/                # Directory for status reports
    │   ├── Phase1Status.md
    │   └── FinalStatus.md
    ├── Instructions/                 # Instructions for subsequent phases
    │   └── Phase2Instructions.md
    └── Retrospective.md              # Sprint retrospective
```

Each sprint directory may also contain additional documents specific to that sprint.

## Current Active Sprints

- [Clean Slate Sprint](/MetaData/DevelopmentSprints/Clean_Slate_Sprint/) - Improving component reliability and isolation
- [Logging Clarity Sprint](/MetaData/DevelopmentSprints/Logging_Clarity_Sprint/) - Implementing standardized debugging instrumentation

## Completed Sprints

See the [Completed](/MetaData/DevelopmentSprints/Completed/) directory for documentation of completed sprints.

## Code Quality Requirements

All code produced in Tekton Development Sprints must adhere to our established quality standards:

### 1. Debug Instrumentation

All code must include appropriate debug instrumentation following the [Debug Instrumentation Guidelines](/MetaData/TektonDocumentation/DeveloperGuides/Debugging/DebuggingInstrumentation.md):

- Frontend JavaScript must use conditional `TektonDebug` calls
- Backend Python must use the `debug_log` utility and `@log_function` decorators
- All debug calls must include appropriate component names and log levels
- Error handling must include contextual debug information

This instrumentation enables efficient debugging and diagnostics without impacting performance when disabled.

### 2. Testing

All code must include appropriate tests:

- Unit tests for core functionality
- Integration tests for component interactions
- Performance tests for critical paths

### 3. Documentation

All code must be properly documented:

- Class and method documentation with clear purpose statements
- API contracts and parameter descriptions
- Requirements for component initialization
- Error handling strategy

## Sprint Process Overview

1. **Inception**: Casey discusses a potential sprint idea with Claude
2. **Planning and Architecture**: Architect Claude creates detailed plans and architectural decisions
3. **Implementation**: Working Claude implements the code according to the plan
4. **Continuation and Handoff**: Working Claude prepares detailed instructions for the next phase
5. **Completion and Retrospective**: Working Claude finalizes all changes and creates a retrospective
6. **Merge and Integration**: Casey approves and coordinates the merge into the main branch

For complete details on the sprint process, see the main [README.md](/MetaData/DevelopmentSprints/README.md) file.