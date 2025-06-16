# Architectural Decisions - MCP Unified Integration

This document captures the key architectural decisions for the MCP Unified Integration Sprint.

## ADR-1: Unified MCP Implementation Based on FastMCP

### Context
Tekton currently uses a custom MCP implementation that is verbose, difficult to maintain, and inconsistent across components. FastMCP offers a more elegant, decorator-based approach that could significantly reduce boilerplate code and improve developer experience.

### Decision
We will replace Tekton's existing MCP implementation with a standardized approach based on FastMCP's decorator pattern. This will be implemented in the tekton-core package and used consistently across all components.

### Consequences
- **Positive**: Reduced boilerplate, improved developer experience, consistent patterns
- **Negative**: One-time migration effort for all components, learning curve for developers
- **Risks**: Potential incompatibilities with existing code, temporary disruption during migration

### Implementation Notes
- FastMCP will be integrated as a core dependency in tekton-core
- All existing MCP interfaces will be reimplemented using FastMCP decorators
- Helper utilities will be provided to ease migration for component developers

## ADR-2: Separation of Internal vs. External MCP Responsibilities

### Context
Tekton needs to handle both internal component communication and integration with external MCP servers. Mixing these concerns can lead to confusion, security issues, and maintenance challenges.

### Decision
We will implement a clear separation of responsibilities:
- **Hermes**: Will handle internal component communication, registration, and routing
- **Ergon**: Will handle external MCP server integration, tool management, and security

### Consequences
- **Positive**: Clearer boundaries, improved security, separation of concerns
- **Negative**: Potential duplication of some functionality, more complex architecture
- **Risks**: Additional coordination required, potential for divergent implementations

### Implementation Notes
- Hermes will focus on being a component registry and communication hub
- Ergon will provide adapters for external MCP servers with proper sandboxing
- Standardized interfaces will ensure consistent behavior between internal and external integrations

## ADR-3: Protocol-First Development Approach

### Context
Previous MCP implementations have focused on implementation details first, leading to inconsistencies and integration challenges. A protocol-first approach would define clear interfaces before implementation.

### Decision
We will adopt a protocol-first development approach where:
1. Message formats and interfaces are clearly defined
2. Validation rules are explicit and enforced
3. Contract tests verify compliance

### Consequences
- **Positive**: Improved interoperability, clearer expectations, easier testing
- **Negative**: More upfront design work, potential for overly rigid structures
- **Risks**: Analysis paralysis, over-engineering

### Implementation Notes
- Define JSON schemas for all MCP message types
- Create interface definitions for all MCP operations
- Implement validation libraries to enforce the protocol
- Create contract tests that verify compliance

## ADR-4: MCP Server Composition Through Adapter Pattern

### Context
Tekton needs to integrate with various external MCP servers (open-mcp, pluggedin-mcp-proxy, etc.) that may have different implementations, capabilities, and interface patterns.

### Decision
We will implement an adapter pattern in Ergon that:
1. Provides a standardized interface for different MCP server types
2. Enables composition of multiple MCP servers
3. Handles capability discovery and routing
4. Maintains proper security boundaries

### Consequences
- **Positive**: Unified interface, flexible composition, future-proof architecture
- **Negative**: Additional abstraction layer, potential performance impact
- **Risks**: Adapters might not capture all server-specific capabilities

### Implementation Notes
- Create base adapter interface in Ergon
- Implement specific adapters for different server types
- Provide capability aggregation and conflict resolution
- Implement security sandboxing for external servers

## ADR-5: Standardized Registration Protocol

### Context
Component registration has been a persistent issue with validation errors and inconsistent behavior. A standardized registration protocol would ensure reliable component discovery and communication.

### Decision
We will implement a standardized registration protocol that:
1. Uses a well-defined schema for registration requests
2. Includes capability declarations during registration
3. Provides clear validation errors
4. Supports health monitoring

### Consequences
- **Positive**: Reliable registration, improved error handling, better debugging
- **Negative**: More complex registration process, potential backward compatibility issues
- **Risks**: Migration challenges for existing components

### Implementation Notes
- Define a JSON schema for registration requests
- Create validation utilities for registration data
- Implement detailed error reporting
- Provide a registration client in tekton-core

## ADR-6: Multi-Modal Capability Registry

### Context
Tekton components handle various data modalities (text, code, images, etc.) and it's important to route requests to the appropriate component based on the required modalities and capabilities.

### Decision
We will implement a multi-modal capability registry in Hermes that:
1. Tracks capabilities by modality (text, code, image, etc.)
2. Supports capability scoring and ranking
3. Enables routing based on best capability match
4. Supports composition of capabilities across components

### Consequences
- **Positive**: Optimal request routing, flexible capability discovery, extensible system
- **Negative**: More complex routing logic, potential performance impact
- **Risks**: Ranking algorithms might not always select the optimal component

### Implementation Notes
- Implement capability scoring system
- Create modality-specific capability registries
- Develop composite capability matcher
- Implement performance optimizations for lookup

## ADR-7: Claude Code Integration Strategy

### Context
Claude Code represents an important external MCP client that Tekton should integrate with. The integration approach will impact how users can leverage Tekton components from Claude Code.

### Decision
We will implement a Claude Code integration strategy that:
1. Exposes Tekton components as MCP tools to Claude Code
2. Provides clear documentation and examples
3. Ensures consistent error handling and response formats
4. Supports bidirectional communication

### Consequences
- **Positive**: Seamless Claude Code integration, improved user experience
- **Negative**: Additional compatibility concerns, potential feature limitations
- **Risks**: Changes in Claude Code API might impact integration

### Implementation Notes
- Implement Claude Code MCP client in tekton-core
- Create examples for common integration patterns
- Ensure consistent error handling
- Provide clear documentation