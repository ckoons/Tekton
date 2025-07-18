# Tekton Documentation

This is the streamlined documentation structure containing only actively maintained documents.

## Core Philosophy
- **Philosophy.md** - Fundamental design beliefs and principles

## Documentation Categories

### Architecture
System design, patterns, and architectural decisions. Critical for understanding how Tekton works.

### Standards  
Coding standards, API design principles, UI conventions. Must be kept current with code.

### ComponentGuides
Step-by-step guides for building new Tekton components. Essential for development.

### DeveloperGuides
Debugging, instrumentation, and development practices for both human and CI developers.

### AITraining
Training documentation for AI components. Focus on core components:
- tekton-core - System orchestration
- aish - AI shell and communication
- terma - Terminal management
- numa, apollo, athena, rhetor - Primary specialists

### MCP
Model Context Protocol documentation for AI tool integration.

### QuickStart
Getting started guides for new users and developers.

### UserGuides
End-user documentation (needs content development).

### Releases
Release notes and test suite documentation (to be created).

## Maintenance Priority

1. **Always Current**: Philosophy, Architecture, Standards
2. **Update with Changes**: ComponentGuides, AITraining (for affected components)
3. **Update with Features**: QuickStart, MCP, DeveloperGuides
4. **Update as Needed**: UserGuides, Releases

## Documentation Philosophy

- Keep what developers/CIs actually use
- Update documentation after code, not before
- Let documentation follow the natural flow of development
- Prefer examples and patterns over lengthy explanations