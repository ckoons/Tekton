# Terma Documentation Index

Terma is an advanced terminal system designed for integration with the Tekton ecosystem. It provides rich terminal functionality with features such as PTY-based terminal sessions, WebSocket communication, LLM assistance, and Hephaestus UI integration.

## Documentation

### Core Documentation

- [README.md](./README.md): Overview of Terma, key features, and basic usage
- [TECHNICAL_DOCUMENTATION.md](./TECHNICAL_DOCUMENTATION.md): Detailed technical specifications and architecture
- [API_REFERENCE.md](./API_REFERENCE.md): Comprehensive API documentation
- [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md): Guide for integrating with other components and systems
- [USER_GUIDE.md](./USER_GUIDE.md): Guide for using Terma features effectively

### Related Documentation

- [Single Port Architecture](../../docs/SINGLE_PORT_ARCHITECTURE.md): Information on the architecture pattern used by Terma
- [LLM Adapter Documentation](../LLMAdapter/README.md): Documentation for the LLM Adapter used by Terma

## Features Overview

- **PTY-based Terminal**: Full terminal emulation with support for interactive applications
- **WebSocket Communication**: Real-time terminal interaction with reconnection support
- **Session Management**: Create, manage, and monitor terminal sessions with recovery
- **LLM Assistance**: AI-powered help with terminal commands and output analysis
- **Hermes Integration**: Seamless communication with other Tekton components
- **Hephaestus UI Integration**: Rich terminal UI with theme support
- **Multiple LLM Providers**: Support for Claude, OpenAI, and other LLM services
- **Markdown Rendering**: Beautiful rendering of LLM responses with syntax highlighting
- **Single Port Architecture**: Compatible with Tekton's unified port management system

## Integration Points

Terma integrates with several Tekton components:

1. **Hermes**: For service registration and discovery
2. **LLM Adapter**: For AI-assisted terminal capabilities 
3. **Hephaestus UI**: For visual presentation and user interaction

## Quick Links

- [Component Overview](./README.md#overview)
- [Key Features](./README.md#key-features)
- [Architecture](./TECHNICAL_DOCUMENTATION.md#system-architecture)
- [API Endpoints](./API_REFERENCE.md#rest-api)
- [WebSocket Protocol](./API_REFERENCE.md#websocket-api)
- [Web Component](./API_REFERENCE.md#web-component-api)
- [Integration Examples](./INTEGRATION_GUIDE.md#integration-examples)
- [Terminal Usage](./USER_GUIDE.md#terminal-interaction)
- [LLM Assistance](./USER_GUIDE.md#llm-assistance)
- [Advanced Features](./USER_GUIDE.md#advanced-features)
- [Troubleshooting](./USER_GUIDE.md#troubleshooting)