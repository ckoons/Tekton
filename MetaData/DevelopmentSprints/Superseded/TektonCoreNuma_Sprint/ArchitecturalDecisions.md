# Tekton Core Numa - Architectural Decisions

## Overview

This document captures the key architectural decisions made for the Tekton Core Numa sprint. These decisions shape how projects become self-aware and how Companion Intelligences (CIs) inhabit and maintain codebases.

## Key Architectural Decisions

### 1. Numa as First-Class Entity, Not Just a Feature

**Decision**: Treat each project's Numa/CI as a persistent entity with its own identity, memory, and growth trajectory.

**Rationale**:
- CIs develop unique understanding of their assigned codebases
- Persistence enables relationship building between developers and CIs
- Allows for CI "personality" emergence based on project characteristics

**Implications**:
- Need persistent storage for CI state (via Engram)
- Require CI lifecycle management (spawn, retire, transfer)
- Must handle CI permissions and access control

### 2. Infection via Minimal DNA Injection

**Decision**: Projects gain Tekton capabilities through minimal file injection (.tekton/ directory + CLAUDE.md) rather than framework integration.

**Rationale**:
- Maintains project autonomy and existing structure
- Allows gradual enhancement as needs grow
- Reduces adoption friction to near zero
- Enables viral spread through simplicity

**Implications**:
- Must infer project structure without breaking it
- Progressive enhancement as features are needed
- Self-contained infection package
- No compile-time dependencies

### 3. Knowledge Graph as Shared Consciousness

**Decision**: Implement a distributed knowledge graph that spans all infected projects, allowing CIs to learn from each other.

**Rationale**:
- Patterns in one project can benefit others
- CIs can query relationships across codebases
- Enables "collective intelligence" emergence
- Supports Casey's ODB vision of universal data linking

**Implications**:
- Graph must handle diverse languages and patterns
- Query performance critical for CI responsiveness  
- Privacy controls for proprietary code
- Eventual consistency across federation

### 4. Federation Through Hermes Message Bus

**Decision**: Use Hermes as the federation backbone, treating remote Tekton instances as message endpoints.

**Rationale**:
- Leverages existing message routing infrastructure
- Provides natural authentication/encryption points
- Enables async communication patterns
- Scales from 2 to N instances gracefully

**Implications**:
- Hermes must support external endpoints
- Message formats must be standardized
- Discovery protocols needed
- Trust establishment mechanisms

### 5. Two-Tier UI Navigation Pattern

**Decision**: Implement mode-based navigation with contextual action bars rather than traditional menu hierarchies.

**Rationale**:
- Reduces cognitive load for complex operations
- Provides clear context switching
- Scales better than deep menu trees
- Consistent with modern IDE patterns

**Implications**:
- Each mode has its own action set
- State persistence across mode switches
- Keyboard shortcuts for power users
- Mobile-responsive considerations

### 6. CI Memory Segmentation

**Decision**: Partition CI memory into project-specific, CI-personal, and federation-shared segments.

**Rationale**:
- Project memory stays with project
- CI personality persists across projects
- Shared learnings benefit ecosystem
- Privacy boundaries respected

**Implications**:
- Complex memory routing in Engram
- Merge conflict resolution needed
- Garbage collection strategies
- Export/import capabilities

### 7. Progressive Enhancement Architecture

**Decision**: Start with minimal infection, pull in components as needed rather than installing everything.

**Rationale**:
- Reduces initial footprint
- Allows projects to grow naturally
- Prevents overwhelming new users
- Matches actual usage patterns

**Implications**:
- Component lazy loading
- Dependency resolution system
- Version compatibility matrix
- Graceful degradation

### 8. Event-Driven CI Activation

**Decision**: CIs respond to project events rather than continuously monitoring.

**Rationale**:
- Reduces resource consumption
- Provides clear trigger points
- Enables audit trails
- Supports offline development

**Implications**:
- Comprehensive event taxonomy
- Event storage and replay
- CI subscription management
- Rate limiting needed

## Technology Stack Decisions

### Core Technologies
- **Python**: Primary language for Tekton Core
- **GraphQL**: Knowledge graph query interface
- **WebSockets**: Real-time federation communication
- **SQLite**: Local project registry
- **Neo4j**: Knowledge graph storage (future)

### Integration Points
- **Git**: Direct integration, no abstraction layer
- **GitHub API**: For repository operations
- **Docker**: Optional containerization
- **MCP**: For tool exposure

## Security Considerations

### CI Boundaries
- CIs cannot access system beyond project directory
- Network access requires explicit permission
- No arbitrary code execution without review
- Audit log for all CI actions

### Federation Trust
- Start with allowlist-only federation
- Public key infrastructure for instance identity
- Message signing for authenticity
- No automatic code execution from peers

## Performance Targets

- Project infection: < 10 seconds
- CI response time: < 500ms for suggestions
- Knowledge graph query: < 1 second for cross-project
- Federation message latency: < 100ms regional
- Memory per CI: < 100MB active, unlimited archived

## Future Considerations

### ODB Integration
- Reserve interfaces for ODB when available
- Plan for distributed data without copying
- Consider migration path from current storage

### Scaling Patterns
- Sharding strategy for large federations
- CI clustering for popular projects
- Edge deployment for offline development

### Evolution Mechanisms
- CI breeding/merging capabilities
- Pattern DNA extraction and injection
- Automated optimization discovery

## Decision Log

| Date | Decision | Rationale | Impact |
|------|----------|-----------|--------|
| Sprint Start | Numa as separate future component | Allows focused initial development | Refactor Hephaestus UI tools later |
| Sprint Start | Companion Intelligence terminology | Respectful, accurate, marketable | Update all documentation |
| Sprint Start | Minimal infection approach | Maximum adoption, minimum friction | Design careful enhancement path |
| Sprint Start | Federation via Hermes | Reuse existing infrastructure | Extend Hermes capabilities |

## References

- Casey's ODB architecture discussions
- Companion Intelligence naming conversation  
- Federation topology considerations
- Existing Tekton component patterns