# Metis Task Management Integration - Claude Code Prompt

## Context

You are Working Claude, tasked with implementing the Metis component for the Tekton ecosystem. Metis is a Python-based task management system inspired by Claude Task Master that will serve as an intermediary layer between requirements management (Telos) and planning (Prometheus).

This sprint aims to create a structured task management component that enhances Tekton's workflow from requirements to planning, providing dependency tracking, complexity analysis, and automated task generation from PRD documents.

## Sprint Documentation

Before beginning implementation, please review these documents:

1. [Sprint Plan](./SprintPlan.md): High-level plan outlining goals, approach, and expected outcomes
2. [Architectural Decisions](./ArchitecturalDecisions.md): Key architectural decisions and their rationale
3. [Implementation Plan](./ImplementationPlan.md): Detailed implementation tasks, phasing, and requirements

## Environment Setup

First, verify you are on the correct branch using the `tekton-branch-verify` utility:

```bash
scripts/github/tekton-branch-verify sprint/metis-task-management-MMDDYY
```

Then, prepare your environment using the `prepare-session.sh` script:

```bash
scripts/github/claude/prepare-session.sh -c -p sprint/metis-task-management-MMDDYY
```

## Implementation Guidelines

### Phase 1: Core Implementation

1. Begin by setting up the project structure according to Tekton standards
2. Implement the core data models for tasks, dependencies, and complexity
3. Create the task management service with basic CRUD operations
4. Implement the API layer following Tekton's REST patterns
5. Integrate with Hermes for service registration and discovery

### Development Standards

- Follow Python best practices (PEP 8) for code style
- Write comprehensive docstrings for all classes and functions
- Create unit tests for all functionality (aim for >90% coverage)
- Validate all inputs to ensure data integrity
- Follow Tekton's architectural patterns, especially Single Port Architecture
- Use Tekton's standard logging patterns for consistency

### Integration Guidelines

- Follow event-driven patterns for component communication
- Use standardized error handling for API endpoints
- Create client modules for interacting with other components
- Implement WebSocket support for real-time updates
- Document all integration points clearly

## Resources

- Existing Tekton components (Telos, Prometheus, Ergon, Hermes) for reference
- Claude Task Master project for understanding the core functionality
- Tekton documentation for architectural patterns and conventions

## Deliverables

For Phase 1, the deliverables include:

- Project structure with proper setup
- Core data models for tasks and dependencies
- Task management service with CRUD operations
- API layer with documented endpoints
- Hermes integration for service registration
- Unit tests for all functionality
- Documentation for the implemented features

## Next Steps

After completing Phase 1, you'll move on to Phase 2, focusing on Telos integration and PRD parsing capabilities. The detailed tasks for Phase 2 are outlined in the Implementation Plan.

## Questions

If you have any questions or encounter any issues during implementation, please ask before proceeding. It's important to maintain alignment with Tekton's architecture and standards throughout the sprint.

## Let's Get Started

Using the information provided, please begin implementing the Metis component for Tekton, starting with Phase 1 as outlined in the Implementation Plan.