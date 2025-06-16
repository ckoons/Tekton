# Codex Technical Documentation

## Overview

Codex is an AI-powered design and coding platform integrated with the Tekton ecosystem. Based on Aider (an AI pair programming tool), Codex provides Tekton users with a powerful coding assistant that can help with code generation, modification, and optimization across 100+ programming languages.

This document provides detailed technical information about the Codex component, its architecture, integration points, and usage patterns.

## Architecture

### Component Structure

Codex is organized into the following key components:

1. **Adapter Layer**: Handles the integration between Aider and the Tekton platform
   - `codex_server.py`: FastAPI server providing HTTP and WebSocket endpoints
   - `aider_adapter.py`: Interface to the Aider core functionality
   - `websocket_handler.py`: Manages real-time communication with the UI

2. **Aider Core**: The underlying AI pair programming engine
   - Supports 100+ programming languages
   - Provides intelligent code editing, generation, and refactoring
   - Manages repository interaction and version control

3. **UI Integration**: Front-end components for the Tekton interface
   - `component_template.html`: Base HTML template for the Codex UI
   - `codex_connector.js`: JavaScript integration for the Tekton UI

4. **Hermes Registration**: Component discovery and capabilities declaration
   - `register_with_hermes.py`: Registers Codex with the Hermes service registry

### Communication Flow

Codex employs a multi-layered communication architecture:

1. **HTTP API**
   - `/api/codex/status`: Get component status
   - `/api/codex/start`: Start a new Aider session
   - `/api/codex/stop`: Stop the current Aider session
   - `/api/codex/input`: Send input text to Aider

2. **WebSocket API**
   - `/ws/codex`: Bidirectional communication channel for:
     - Real-time output streaming
     - Session status updates
     - File tracking
     - Input handling

3. **Process Management**
   - `AiderProcess`: Managed subprocess running Aider
   - Separate queue-based communication for input/output
   - Isolation for stability and resource management

### Integration with Tekton

Codex integrates with Tekton through several key mechanisms:

1. **UI Rendering**
   - Renders in the RIGHT PANEL of the Tekton UI
   - Receives input from the RIGHT FOOTER chat interface
   - Supports panel-based UI with console, file list, and settings views

2. **Component Registration**
   - Registers with Hermes as a component with capabilities:
     - `code_editing`
     - `programming_assistance`
     - `code_generation`
     - `ai_pair_programming`
   - Exposes metadata for discovery and UI integration

3. **Input/Output Management**
   - Seamlessly routes user input from Tekton's chat interface to Aider
   - Streams output from Aider to the Tekton UI in real-time
   - Maintains persistent context across the session

## Implementation Details

### Backend Components

#### CodexAiderAdapter

The `CodexAiderAdapter` class in `aider_adapter.py` serves as the core integration layer between Aider and Tekton:

- **Initialization**: Sets up communication channels and prepares Aider
- **Input Handling**: Routes input from the UI to the Aider process
- **Output Monitoring**: Continuously monitors Aider output and forwards to the UI
- **Session Management**: Controls the lifecycle of Aider sessions

#### AiderProcess

The `AiderProcess` class manages Aider in a separate Python process:

- **Process Isolation**: Runs Aider in a dedicated process for stability
- **Queue-Based Communication**: Uses multiprocessing queues for input/output
- **Custom IO Handling**: Replaces Aider's IO implementation for integration
- **Resource Management**: Ensures proper cleanup of resources on termination

#### WebSocketHandler

The `WebSocketHandler` class manages WebSocket communication with the UI:

- **Message Routing**: Forwards different message types to the UI
- **Message Formatting**: Formats output for rendering in the UI
- **Status Updates**: Provides real-time status updates to the UI
- **File Tracking**: Sends active file lists to the UI

### Frontend Components

#### Codex Connector

The `codexConnector` JavaScript module provides the UI integration:

- **WebSocket Management**: Handles connection, reconnection, and fallback
- **UI Rendering**: Dynamically renders messages, file lists, and status indicators
- **Input Integration**: Connects to Tekton's RIGHT FOOTER for input handling
- **Panel Management**: Provides different UI panels (console, files, settings)
- **Session Control**: Offers controls for starting and stopping sessions

### HTTP API

The FastAPI server in `codex_server.py` provides the following endpoints:

- **GET `/api/codex/status`**: Returns the current status of the Codex component
- **POST `/api/codex/start`**: Starts a new Aider session
- **POST `/api/codex/stop`**: Stops the current Aider session
- **POST `/api/codex/input`**: Sends user input to the current Aider session

### WebSocket API

The WebSocket endpoint at `/ws/codex` supports bidirectional communication with message types:

- **From Client to Server**
  - `start_session`: Request to start a new session
  - `stop_session`: Request to stop the current session
  - `input`: User input to be processed
  - `ping`: Connection keepalive

- **From Server to Client**
  - `output`: Output from Aider
  - `error`: Error messages
  - `warning`: Warning messages
  - `active_files`: List of files in the current context
  - `input_request`: Request for user input
  - `input_received`: Confirmation of received input
  - `session_status`: Status updates for the session
  - `pong`: Response to ping

## Usage Patterns

### Session Lifecycle

1. **Initialization**
   - Component loads in Tekton UI
   - WebSocket connection established
   - Session auto-starts when first input is received

2. **Interaction**
   - User sends input through Tekton's RIGHT FOOTER chat
   - Input is processed by Aider
   - Output is streamed back to the UI
   - Active files are tracked and displayed

3. **Termination**
   - Session can be manually stopped via UI controls
   - Session terminates when component is unloaded
   - Resources are properly cleaned up

### Code Editing Workflow

1. User requests code changes through natural language input
2. Aider interprets the request and identifies relevant files
3. Changes are made to the code based on the request
4. Modified files are displayed in the file list
5. Output provides explanation of changes made
6. Git integration can automatically commit changes

### File Management

- Active files are tracked and displayed in the Files panel
- Users can focus on specific files using `/focus <filename>` command
- Users can add files to the context using `/add <filename>` command
- Git integration provides version control capabilities

## Configuration

### Launch Options

Codex can be launched with Tekton in several ways:

1. **Using launch-tekton.sh with --aider flag**
   ```bash
   ./launch-tekton.sh --aider
   ```

2. **Using launch-tekton.sh with --full-stack flag**
   ```bash
   ./launch-tekton.sh --full-stack
   ```

3. **Specifying components manually**
   ```bash
   ./launch-tekton.sh --components engram,hermes,hephaestus,codex
   ```

### Component Registration

Codex registers with Hermes with the following capabilities:

```json
{
  "service_id": "codex",
  "name": "Codex Aider",
  "capabilities": [
    "code_editing",
    "programming_assistance",
    "code_generation",
    "ai_pair_programming"
  ],
  "metadata": {
    "component_type": "tool",
    "description": "AI pair programming tool",
    "ui_enabled": true,
    "ui_component": "codex",
    "indicator": "green"
  }
}
```

## Troubleshooting

### Common Issues

1. **WebSocket Connection Failures**
   - Check if the Codex server is running on port 8082
   - Verify network connectivity between UI and server
   - Check for logs in `~/.tekton/logs/codex.log`

2. **Session Start Failures**
   - Ensure Aider dependencies are installed
   - Verify Python environment has required packages
   - Check for error messages in server logs

3. **Input/Output Issues**
   - Verify WebSocket connection is established
   - Check browser console for errors
   - Ensure Tekton's chat input is properly configured

### Logging

Logs are available in the following locations:

- Server logs: `~/.tekton/logs/codex.log`
- Browser console: Check browser developer tools
- Aider process logs: In the standard output of the process

## Performance Considerations

1. **Memory Usage**
   - The Aider process can use significant memory for large codebases
   - Recommended minimum: 4GB RAM

2. **Startup Time**
   - Initial session startup may take 5-10 seconds
   - Subsequent operations are faster once session is established

3. **WebSocket Traffic**
   - Real-time streaming can generate significant WebSocket traffic
   - Connection keepalive ensures persistent connection

## Security Considerations

1. **Code Access**
   - Codex has full access to the local filesystem
   - Operates within the context of the current user
   - Should only be used in trusted environments

2. **API Exposure**
   - HTTP and WebSocket endpoints should not be exposed publicly
   - CORS is configured to allow all origins for local development

3. **Process Isolation**
   - Aider runs in a separate process for stability and resource control
   - Process is terminated when session ends or component unloads

## Future Improvements

1. **Enhanced Authentication**
   - Implement user-based authentication for API endpoints
   - Integrate with Tekton's authentication system

2. **Improved Error Handling**
   - More robust error recovery for network issues
   - Better error messages and debugging information

3. **Advanced UI Features**
   - File diff visualization
   - Syntax highlighting in code blocks
   - Interactive file exploration

4. **Performance Optimizations**
   - Caching for frequently accessed files
   - Incremental updates for large outputs
   - Optimized WebSocket message formatting

## References

- [Aider GitHub Repository](https://github.com/paul-gauthier/aider)
- [Aider Documentation](https://aider.chat/docs/)
- [Tekton Single Port Architecture](../../docs/SINGLE_PORT_ARCHITECTURE.md)
- [Hermes Component Registration](../../Hermes/README.md)