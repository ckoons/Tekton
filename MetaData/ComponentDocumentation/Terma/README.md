# Terma: Terminal Integration for Tekton

## Overview

Terma is an advanced terminal system designed for integration with the Tekton ecosystem. It provides rich terminal functionality with features such as PTY-based terminal sessions, WebSocket communication, LLM assistance, and Hephaestus UI integration.

As a core infrastructure component, Terma enables users to interact with the underlying operating system and execute commands while providing intelligent assistance, session persistence, and a consistent user experience. It serves as both a standalone terminal and an embeddable component that can be integrated into other Tekton interfaces.

## Key Features

- **PTY-based Terminal**: Full terminal emulation with support for interactive applications
- **WebSocket Communication**: Real-time terminal interaction with reconnection support
- **Session Management**: Create, manage, and monitor terminal sessions with recovery
- **LLM Assistance**: AI-powered help with terminal commands and output analysis
- **Hermes Integration**: Seamless communication with other Tekton components
- **Hephaestus UI Integration**: Rich terminal UI with theme support
- **Multiple LLM Providers**: Support for Claude, OpenAI, and other LLM services
- **Markdown Rendering**: Beautiful rendering of LLM responses with syntax highlighting
- **Single Port Architecture**: Compatible with Tekton's unified port management system

## Architecture

Terma follows a layered architecture with clear separation of concerns:

```
┌───────────────────────────────────────────┐
│                   UI Layer                │
│ (terma-component.html, terma-terminal.js) │
└───────────────────────────────────────────┘
                     ▲
                     │
                     ▼
┌───────────────────────────────────────────┐
│               API Layer                   │
│       (app.py, websocket.py, ui_server.py)│
└───────────────────────────────────────────┘
                     ▲
                     │
                     ▼
┌───────────────────────────────────────────┐
│               Core Layer                  │
│ (terminal.py, session_manager.py, llm_adapter.py) │
└───────────────────────────────────────────┘
                     ▲
                     │
                     ▼
┌───────────────────────────────────────────┐
│           Integration Layer               │
│       (hermes_integration.py)             │
└───────────────────────────────────────────┘
```

Terma implements the Single Port Architecture pattern with all communication consolidated through path-based routing:

- **HTTP API**: Available at `/api/*` endpoints
- **WebSocket**: Available at `/ws/{session_id}` endpoint 
- **UI**: Available at `/terminal/launch` endpoint
- **Standard Port**: 8767 (configurable via environment variables)

## Installation

### Prerequisites

- Python 3.8 or higher
- FastAPI and Uvicorn
- WebSockets support
- PTY process support (Linux, macOS, or WSL on Windows)

### Setup Options

#### Standalone Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/Tekton.git
cd Tekton/Terma

# Install dependencies
pip install -r requirements.txt

# Start the server
python -m terma.cli.main
```

#### Installation with Tekton

```bash
# Run the setup script
cd Tekton/Terma
./setup.sh

# Register with Hermes
python register_with_hermes.py

# Start with Tekton launcher
cd ..
./scripts/tekton-launch --components terma
```

## Quick Start

### REST API Usage

Create a terminal session:

```bash
curl -X POST http://localhost:8767/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"shell_command": "/bin/bash"}'
```

Response:

```json
{
  "session_id": "sess-abc123",
  "created_at": "2025-04-15T12:00:00Z",
  "shell_command": "/bin/bash",
  "status": "active"
}
```

List active sessions:

```bash
curl http://localhost:8767/api/sessions
```

Send input to a session:

```bash
curl -X POST http://localhost:8767/api/sessions/sess-abc123/input \
  -H "Content-Type: application/json" \
  -d '{"data": "ls -la\n"}'
```

### WebSocket Usage

Connect to a terminal session via WebSocket:

```javascript
const socket = new WebSocket("ws://localhost:8767/ws/sess-abc123");

socket.onmessage = (event) => {
    const message = JSON.parse(event.data);
    if (message.type === "output") {
        console.log(message.data);
    }
};

socket.send(JSON.stringify({
    type: "input",
    data: "ls -la\n"
}));
```

### LLM Assistance

Request LLM assistance:

```javascript
socket.send(JSON.stringify({
    type: "llm_assist",
    data: "How do I find all files larger than 10MB?",
    options: {
        model: "claude-3-sonnet-20240229"
    }
}));
```

## UI Integration

Terma provides web components for easy integration into the Hephaestus UI:

```html
<!-- Basic usage -->
<terma-terminal></terma-terminal>

<!-- Advanced configuration -->
<terma-terminal
  id="my-terminal"
  theme="dark"
  font-size="14"
  shell-command="/bin/bash"
  initial-directory="/home/user/projects"
  show-assist-button="true">
</terma-terminal>
```

## Integration with Tekton Components

Terma integrates with other Tekton components:

1. **Hermes**: For service registration and discovery
2. **LLM Adapter**: For AI-assisted terminal capabilities 
3. **Hephaestus UI**: For visual presentation and user interaction

## Configuration

Terma can be configured through environment variables:

- `TERMA_PORT`: HTTP server port (default: 8767)
- `TERMA_HOST`: HTTP server host (default: 0.0.0.0)
- `TERMA_LOG_LEVEL`: Logging level (default: info)
- `TERMA_SESSION_TIMEOUT`: Idle session timeout in seconds (default: 3600)
- `TERMA_CLEANUP_INTERVAL`: Cleanup interval in seconds (default: 300)
- `TERMA_MAX_SESSIONS`: Maximum number of sessions (default: 100)
- `TERMA_DEFAULT_SHELL`: Default shell command (default: system shell)
- `TERMA_LLM_PROVIDER`: Default LLM provider (default: rhetor)
- `TERMA_LLM_MODEL`: Default LLM model (default: depends on provider)
- `TERMA_UI_THEME`: Default UI theme (default: light)

## Documentation

For more detailed information, see the following documentation:

- [Technical Documentation](./TECHNICAL_DOCUMENTATION.md) - Detailed technical specifications
- [API Reference](./API_REFERENCE.md) - Complete API documentation
- [Integration Guide](./INTEGRATION_GUIDE.md) - Information on integrating with Terma
- [User Guide](./USER_GUIDE.md) - Guide for using Terma features

## Security Considerations

- Terminal sessions run with the permissions of the server process
- No built-in authentication (rely on external authentication mechanisms)
- WebSocket connections should be secured in production environments
- Consider resource limits for production deployments

## License

This project is licensed under the MIT License - see the LICENSE file for details.