# Metis Documentation Index

Metis is the comprehensive task management system for the Tekton ecosystem. It serves as an intermediary layer between requirements management (Telos) and planning (Prometheus), providing structured task tracking, dependency management, and real-time updates through a RESTful API with WebSocket support.

## Documentation

### Core Documentation

- [README.md](./README.md): Overview of Metis, key features, and basic usage
- [TECHNICAL_DOCUMENTATION.md](./TECHNICAL_DOCUMENTATION.md): Detailed technical specifications and architecture
- [API_REFERENCE.md](./API_REFERENCE.md): Comprehensive API documentation
- [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md): Guide for integrating with other components and systems
- [USER_GUIDE.md](./USER_GUIDE.md): Guide for using Metis features effectively
- [INSTALLATION_GUIDE.md](./INSTALLATION_GUIDE.md): Instructions for installing and configuring Metis

### Related Documentation

- [Telos Documentation](../Telos/README.md): Requirements management component that integrates with Metis
- [Prometheus Documentation](../Prometheus/README.md): Planning component that integrates with Metis
- [Hermes Documentation](../Hermes/README.md): Service registry used by Metis for integration

## Features Overview

- **Task Management**: Create, update, delete, and track tasks with rich metadata
- **Dependency Tracking**: Define and manage task dependencies with validation
- **Complexity Analysis**: Score and evaluate task complexity to assist planning
- **Real-time Updates**: Subscribe to task changes via WebSocket
- **Telos Integration**: Import requirements and maintain requirements traceability
- **Hermes Integration**: Service registration and discovery
- **Single Port Architecture**: Consolidated HTTP, WebSocket, and Event communication
- **Subtask Management**: Break down complex tasks into manageable units
- **Requirement References**: Link tasks to requirements in Telos
- **Task Filtering**: Advanced search and filtering capabilities
- **In-Memory and Persistent Storage**: Flexible storage options with persistence
- **REST API**: Full-featured API for programmatic integration

## Integration Points

Metis integrates with several Tekton components:

1. **Hermes**: Service registration and discovery
2. **Telos**: Requirements management and requirement references
3. **Prometheus**: Planning and scheduling
4. **Engram**: Memory integration (future)
5. **Tekton Core**: Core orchestration layer

## Quick Links

- [Component Overview](./README.md#overview)
- [Key Features](./README.md#key-features)
- [Architecture](./TECHNICAL_DOCUMENTATION.md#architecture-overview)
- [API Endpoints](./API_REFERENCE.md#task-management)
- [WebSocket API](./API_REFERENCE.md#websocket-interface)
- [Core Domain Model](./TECHNICAL_DOCUMENTATION.md#core-domain-model)
- [Integration Patterns](./INTEGRATION_GUIDE.md#integration-patterns)
- [Best Practices](./USER_GUIDE.md#best-practices)