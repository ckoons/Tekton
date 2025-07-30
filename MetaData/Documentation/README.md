# Tekton Documentation

This is the streamlined documentation structure containing only actively maintained documents.

## 🚀 Quick Starts
- **[Planning Workflow Quick Start](UserGuides/PlanningWorkflowQuickStart.md)** - Transform ideas into code in 5 minutes
- **[A2A Quick Start](UserGuides/A2A_Quick_Start.md)** - Get started with AI-to-AI communication
- **[Engram Quickstart](UserGuides/Engram_Quickstart.md)** - Working with the engram system
- **[Rhetor Quick Reference](UserGuides/Rhetor_Quick_Reference.md)** - Quick guide to Rhetor AI

## Core Philosophy
- **Philosophy.md** - Fundamental design beliefs and principles

## Documentation Categories

### Architecture
System design, patterns, and architectural decisions. Critical for understanding how Tekton works.

**Key Documents**:
- **[CI Registry Architecture](Architecture/CI-Registry-Architecture.md)** - Central CI coordination and Apollo-Rhetor collaboration
- **[Development Sprint Workflow](Architecture/DevelopmentSprintWorkflow.md)** - Complete guide to the planning pipeline
- **[Workflow Endpoint Standard](Architecture/WorkflowEndpointStandard.md)** - Unified component communication

### Standards  
Coding standards, API design principles, UI conventions. Must be kept current with code.

**🎯 Essential Standard**: 
- **Landmarks_and_Semantic_Tags_Standard.md** - THE authoritative guide for marking code architecture with landmarks and UI elements with semantic tags. All sprints must follow this standard to maintain consistency and build our knowledge graph.

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

### UserGuides
End-user documentation and quick start guides for new users and developers.

### Releases
Release notes and test suite documentation (to be created).

## Maintenance Priority

1. **Always Current**: Philosophy, Architecture, Standards (especially Landmarks_and_Semantic_Tags_Standard.md)
2. **Update with Changes**: ComponentGuides, AITraining (for affected components)
3. **Update with Features**: UserGuides, MCP, DeveloperGuides
4. **Update as Needed**: UserGuides, Releases

**Sprint Completion Requirement**: Always verify compliance with Standards/Landmarks_and_Semantic_Tags_Standard.md before closing any sprint.

## Documentation Philosophy

- Keep what developers/CIs actually use
- Update documentation after code, not before
- Let documentation follow the natural flow of development
- Prefer examples and patterns over lengthy explanations