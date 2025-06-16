# Terma API Reference

This document provides a comprehensive reference for Terma's API, including both REST and WebSocket interfaces.

## Base URLs

- **REST API**: `http://localhost:8767/api`
- **WebSocket API**: `ws://localhost:8767/ws`
- **UI Endpoints**: `http://localhost:8767/terminal`

## Authentication

*Note: Authentication is not currently implemented and will be added in future releases.*

## REST API

### Health Check

#### Get Health Status

```
GET /api/health
```

Returns the health status of the Terma service.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": 1719875632.123456
}
```

### Session Management

#### Create a Terminal Session

```
POST /api/sessions
```

Creates a new terminal session.

**Request Body:**
```json
{
  "shell_command": "/bin/bash",
  "cwd": "/home/user",
  "env": {
    "TERM": "xterm-256color",
    "CUSTOM_VAR": "custom_value"
  },
  "cols": 80,
  "rows": 24
}
```

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `shell_command` | String | The shell command to execute (default: system shell) | No |
| `cwd` | String | The working directory (default: home directory) | No |
| `env` | Object | Environment variables (default: inherited from server) | No |
| `cols` | Number | Terminal width in columns (default: 80) | No |
| `rows` | Number | Terminal height in rows (default: 24) | No |

**Response:**
```json
{
  "session_id": "sess-abc123",
  "created_at": 1719875632.123456,
  "shell_command": "/bin/bash",
  "status": "active"
}
```

#### List Terminal Sessions

```
GET /api/sessions
```

Returns a list of active terminal sessions.

**Response:**
```json
{
  "sessions": [
    {
      "session_id": "sess-abc123",
      "created_at": 1719875632.123456,
      "last_activity": 1719875732.123456,
      "shell_command": "/bin/bash",
      "cwd": "/home/user",
      "active": true,
      "idle_time": 100.0
    },
    {
      "session_id": "sess-def456",
      "created_at": 1719875732.123456,
      "last_activity": 1719875832.123456,
      "shell_command": "/bin/zsh",
      "cwd": "/home/user/projects",
      "active": true,
      "idle_time": 100.0
    }
  ],
  "count": 2
}
```

#### Get Terminal Session

```
GET /api/sessions/{session_id}
```

Returns details for a specific terminal session.

**Path Parameters:**
- `session_id`: The ID of the terminal session

**Response:**
```json
{
  "session_id": "sess-abc123",
  "created_at": 1719875632.123456,
  "last_activity": 1719875732.123456,
  "shell_command": "/bin/bash",
  "cwd": "/home/user",
  "active": true,
  "idle_time": 100.0
}
```

#### Close Terminal Session

```
DELETE /api/sessions/{session_id}
```

Closes a terminal session.

**Path Parameters:**
- `session_id`: The ID of the terminal session

**Response:**
```json
{
  "status": "closed",
  "session_id": "sess-abc123"
}
```

### Terminal I/O

#### Send Input to Terminal

```
POST /api/sessions/{session_id}/input
```

Sends input data to a terminal session.

**Path Parameters:**
- `session_id`: The ID of the terminal session

**Request Body:**
```json
{
  "data": "ls -la\n"
}
```

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `data` | String | The input data to send to the terminal | Yes |

**Response:**
```json
{
  "status": "sent",
  "session_id": "sess-abc123"
}
```

#### Get Output from Terminal

```
GET /api/sessions/{session_id}/output
```

Gets output data from a terminal session.

**Path Parameters:**
- `session_id`: The ID of the terminal session

**Query Parameters:**
- `timeout`: Timeout in seconds (default: 0.1, range: 0.1-5.0)

**Response:**
```json
{
  "output": "total 32\ndrwxr-xr-x  5 user user 4096 Mar 15 10:30 .\ndrwxr-xr-x 28 user user 4096 Mar 15 10:30 ..\n-rw-r--r--  1 user user  220 Mar 15 10:30 .bash_logout\n-rw-r--r--  1 user user 3771 Mar 15 10:30 .bashrc\n-rw-r--r--  1 user user  807 Mar 15 10:30 .profile\n",
  "session_id": "sess-abc123"
}
```

#### Resize Terminal

```
POST /api/sessions/{session_id}/resize
```

Resizes a terminal session.

**Path Parameters:**
- `session_id`: The ID of the terminal session

**Request Body:**
```json
{
  "cols": 120,
  "rows": 40
}
```

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `cols` | Number | Terminal width in columns | Yes |
| `rows` | Number | Terminal height in rows | Yes |

**Response:**
```json
{
  "status": "resized",
  "session_id": "sess-abc123"
}
```

### LLM Integration

#### Get LLM Assistance

```
POST /api/sessions/{session_id}/llm-assist
```

Gets LLM assistance for a terminal query.

**Path Parameters:**
- `session_id`: The ID of the terminal session

**Request Body:**
```json
{
  "query": "How do I find files larger than 10MB?",
  "context": "user@host:~$ ls -la\ntotal 32\n...",
  "model": "claude-3-sonnet-20240229"
}
```

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `query` | String | The query for the LLM | Yes |
| `context` | String | Optional additional context (default: recent terminal output) | No |
| `model` | String | The LLM model to use (default: configured default) | No |

**Response:**
```json
{
  "response": "To find files larger than 10MB, you can use the `find` command with the `-size` option:\n\n```bash\nfind /path/to/search -type f -size +10M\n```\n\nThis will search for files (`-type f`) in the specified directory that are larger than 10 megabytes (`-size +10M`).\n\nFor example, to search in the current directory and all subdirectories:\n\n```bash\nfind . -type f -size +10M\n```\n\nTo also show the file sizes, you can combine it with `ls`:\n\n```bash\nfind . -type f -size +10M -exec ls -lh {} \\;\n```\n\nOr use `du` for a more readable output:\n\n```bash\nfind . -type f -size +10M -exec du -h {} \\; | sort -hr\n```",
  "session_id": "sess-abc123"
}
```

## WebSocket API

### Connection

Connect to a terminal session via WebSocket:

```
WebSocket: ws://localhost:8767/ws/{session_id}
```

Where `{session_id}` is the ID of the terminal session.

### Message Format

All WebSocket messages follow a standard JSON format:

**Client to Server:**
```json
{
  "type": "message_type",
  "data": "message_data"
}
```

**Server to Client:**
```json
{
  "type": "message_type",
  "data": "message_data"
}
```

### Client to Server Messages

#### Terminal Input

Send input to the terminal:

```json
{
  "type": "input",
  "data": "ls -la\n"
}
```

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `type` | String | Message type: "input" | Yes |
| `data` | String | The input data to send to the terminal | Yes |

#### Terminal Resize

Resize the terminal:

```json
{
  "type": "resize",
  "cols": 120,
  "rows": 40
}
```

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `type` | String | Message type: "resize" | Yes |
| `cols` | Number | Terminal width in columns | Yes |
| `rows` | Number | Terminal height in rows | Yes |

#### LLM Assistance

Request LLM assistance:

```json
{
  "type": "llm_assist",
  "data": "How do I find files larger than 10MB?",
  "context": "user@host:~$ ls -la\ntotal 32\n...",
  "options": {
    "model": "claude-3-sonnet-20240229",
    "stream": true
  }
}
```

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `type` | String | Message type: "llm_assist" | Yes |
| `data` | String | The query for the LLM | Yes |
| `context` | String | Optional additional context | No |
| `options` | Object | Additional options | No |
| `options.model` | String | The LLM model to use | No |
| `options.stream` | Boolean | Whether to stream the response | No |

#### Ping

Send a ping to keep the connection alive:

```json
{
  "type": "ping",
  "data": "1719875632123"
}
```

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `type` | String | Message type: "ping" | Yes |
| `data` | String | Optional data to echo back | No |

### Server to Client Messages

#### Connected

Sent when the WebSocket connection is established:

```json
{
  "type": "connected",
  "data": {
    "session_id": "sess-abc123",
    "message": "Connected to terminal session"
  }
}
```

#### Terminal Output

Terminal output:

```json
{
  "type": "output",
  "data": "total 32\ndrwxr-xr-x  5 user user 4096 Mar 15 10:30 .\ndrwxr-xr-x 28 user user 4096 Mar 15 10:30 ..\n-rw-r--r--  1 user user  220 Mar 15 10:30 .bash_logout\n-rw-r--r--  1 user user 3771 Mar 15 10:30 .bashrc\n-rw-r--r--  1 user user  807 Mar 15 10:30 .profile\n"
}
```

#### Error

Error message:

```json
{
  "type": "error",
  "data": "Session not found",
  "code": "session_not_found"
}
```

#### LLM Response

LLM assistance response:

```json
{
  "type": "llm_response",
  "data": "To find files larger than 10MB, you can use the `find` command with the `-size` option:\n\n```bash\nfind /path/to/search -type f -size +10M\n```\n\nThis will search for files (`-type f`) in the specified directory that are larger than 10 megabytes (`-size +10M`).\n\nFor example, to search in the current directory and all subdirectories:\n\n```bash\nfind . -type f -size +10M\n```\n\nTo also show the file sizes, you can combine it with `ls`:\n\n```bash\nfind . -type f -size +10M -exec ls -lh {} \\;\n```\n\nOr use `du` for a more readable output:\n\n```bash\nfind . -type f -size +10M -exec du -h {} \\; | sort -hr\n```"
}
```

#### LLM Response Streaming

When streaming is enabled, LLM responses come in multiple messages:

Start of streaming:
```json
{
  "type": "llm_response_start",
  "data": ""
}
```

Chunks of the response:
```json
{
  "type": "llm_response_chunk",
  "data": "To find files larger than 10MB, you can use the `find` command with the `-size` option:"
}
```

```json
{
  "type": "llm_response_chunk",
  "data": "\n\n```bash\nfind /path/to/search -type f -size +10M\n```"
}
```

End of streaming:
```json
{
  "type": "llm_response_end",
  "data": ""
}
```

#### Pong

Response to a ping:

```json
{
  "type": "pong",
  "data": "1719875632123"
}
```

## UI Endpoints

### Launch Terminal UI

```
GET /terminal/launch
```

Launches the terminal UI as a standalone application.

**Query Parameters:**
- `theme`: UI theme ("dark" or "light", default: "dark")
- `font_size`: Font size (default: 14)
- `shell_command`: Shell command to execute (default: system shell)

**Response:**
HTML page with embedded terminal component.

### Get Terminal Component

```
GET /terminal/component
```

Returns the terminal web component HTML.

**Response:**
HTML markup for the terminal web component.

## Error Codes

| Code | Description |
|------|-------------|
| `session_not_found` | The specified session was not found |
| `session_closed` | The session has been closed |
| `input_error` | Failed to send input to the terminal |
| `output_error` | Failed to read output from the terminal |
| `resize_error` | Failed to resize the terminal |
| `llm_error` | Error with LLM assistance |
| `unknown_message_type` | Unknown WebSocket message type |
| `websocket_error` | Generic WebSocket error |

## Environment Variables

Terma's API behavior can be configured using the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `TERMA_PORT` | HTTP server port | 8767 |
| `TERMA_HOST` | HTTP server host | 0.0.0.0 |
| `TERMA_LOG_LEVEL` | Logging level | info |
| `TERMA_SESSION_TIMEOUT` | Idle session timeout in seconds | 3600 |
| `TERMA_CLEANUP_INTERVAL` | Cleanup interval in seconds | 300 |
| `TERMA_MAX_SESSIONS` | Maximum number of sessions | 100 |
| `TERMA_DEFAULT_SHELL` | Default shell command | system shell |
| `TERMA_LLM_PROVIDER` | Default LLM provider | rhetor |
| `TERMA_LLM_MODEL` | Default LLM model | depends on provider |

## Web Component API

The `terma-terminal` web component provides a JavaScript API for integration into web applications:

### Properties

| Property | Type | Description | Default |
|----------|------|-------------|---------|
| `theme` | String | UI theme ("dark" or "light") | "dark" |
| `font-size` | Number | Font size | 14 |
| `font-family` | String | Font family | "monospace" |
| `shell-command` | String | Shell command to execute | system shell |
| `cwd` | String | Working directory | home directory |
| `cols` | Number | Terminal width in columns | 80 |
| `rows` | Number | Terminal height in rows | 24 |
| `auto-connect` | Boolean | Whether to connect automatically | false |
| `show-assist-button` | Boolean | Whether to show the LLM assist button | false |
| `llm-model` | String | LLM model to use | default model |

### Methods

| Method | Description |
|--------|-------------|
| `createSession()` | Creates a new terminal session |
| `connect()` | Connects to the terminal session |
| `disconnect()` | Disconnects from the terminal session |
| `sendInput(data)` | Sends input to the terminal |
| `clear()` | Clears the terminal |
| `focus()` | Focuses the terminal |
| `write(data)` | Writes data to the terminal |
| `setTheme(theme)` | Sets the terminal theme |
| `setFontSize(size)` | Sets the terminal font size |
| `getLlmAssistance(query)` | Gets LLM assistance |

### Events

| Event | Description |
|-------|-------------|
| `terminalReady` | Fired when the terminal component is ready |
| `terminalConnected` | Fired when the terminal connects to a session |
| `terminalDisconnected` | Fired when the terminal disconnects from a session |
| `terminalError` | Fired when an error occurs |
| `llmResponse` | Fired when an LLM response is received |

### Usage Example

```html
<terma-terminal
  id="my-terminal"
  theme="dark"
  font-size="14"
  shell-command="/bin/bash"
  auto-connect="true"
  show-assist-button="true">
</terma-terminal>

<script>
  document.addEventListener('DOMContentLoaded', function() {
    const terminal = document.getElementById('my-terminal');
    
    terminal.addEventListener('terminalReady', function(event) {
      console.log('Terminal ready:', event.detail);
    });
    
    terminal.addEventListener('terminalConnected', function(event) {
      console.log('Terminal connected:', event.detail);
      terminal.sendInput('echo "Hello, Terminal!"\n');
    });
    
    terminal.addEventListener('llmResponse', function(event) {
      console.log('LLM response:', event.detail);
    });
    
    // Methods can be called after the terminal is ready
    terminal.setTheme('dark');
    terminal.setFontSize(16);
  });
</script>
```