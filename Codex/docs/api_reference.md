# Codex API Reference

This document provides a comprehensive reference for the HTTP and WebSocket APIs exposed by the Codex component in the Tekton platform.

## HTTP API

The Codex HTTP API provides endpoints for controlling the Aider session and sending input. All endpoints are relative to the Codex server base URL (typically `http://localhost:8082`).

### Status Endpoint

**GET** `/api/codex/status`

Returns the current status of the Codex component.

#### Response

```json
{
  "status": "active",
  "name": "Codex Aider",
  "description": "AI pair programming tool",
  "input_destination": "right_footer",
  "session_active": true|false
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Component status (active, error, etc.) |
| `name` | string | Display name of the component |
| `description` | string | Brief description of the component |
| `input_destination` | string | Where input should be sent in the Tekton UI |
| `session_active` | boolean | Whether an Aider session is currently active |

### Start Session Endpoint

**POST** `/api/codex/start`

Starts a new Aider session.

#### Response

```json
{
  "status": "success",
  "message": "Aider session started successfully",
  "session_id": "session_1234567890"
}
```

or, if there was an error:

```json
{
  "status": "error",
  "message": "Error message"
}
```

or, if a session is already starting:

```json
{
  "status": "warning",
  "message": "Session startup already in progress"
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Result status (success, error, warning) |
| `message` | string | Human-readable message |
| `session_id` | string | Unique identifier for the session (only on success) |

### Stop Session Endpoint

**POST** `/api/codex/stop`

Stops the current Aider session.

#### Response

```json
{
  "status": "success",
  "message": "Aider session stopped successfully"
}
```

or, if there was an error:

```json
{
  "status": "error",
  "message": "Error message"
}
```

or, if no session is active:

```json
{
  "status": "warning",
  "message": "No active session to stop"
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Result status (success, error, warning) |
| `message` | string | Human-readable message |

### Input Endpoint

**POST** `/api/codex/input`

Sends input text to the current Aider session.

#### Request Body

```json
{
  "text": "Your input text here"
}
```

#### Request Fields

| Field | Type | Description |
|-------|------|-------------|
| `text` | string | The input text to send to Aider |

#### Response

```json
{
  "status": "success",
  "message": "Input received and processed",
  "session_id": "session_1234567890"
}
```

or, if there was an error:

```json
{
  "status": "error",
  "message": "Error message"
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | Result status (success, error) |
| `message` | string | Human-readable message |
| `session_id` | string | Unique identifier for the session (only on success) |

## WebSocket API

The Codex WebSocket API provides real-time bidirectional communication with the Aider session. The WebSocket endpoint is located at `/ws/codex`.

### Client-to-Server Messages

These are messages sent from the client to the server through the WebSocket connection.

#### Start Session Message

Requests the server to start a new Aider session.

```json
{
  "type": "start_session",
  "content": {
    "timestamp": 1619712345678
  }
}
```

#### Stop Session Message

Requests the server to stop the current Aider session.

```json
{
  "type": "stop_session"
}
```

#### Input Message

Sends user input to be processed by Aider.

```json
{
  "type": "input",
  "content": "Your input text here"
}
```

#### Ping Message

Keeps the WebSocket connection alive.

```json
{
  "type": "ping",
  "content": ""
}
```

### Server-to-Client Messages

These are messages sent from the server to the client through the WebSocket connection.

#### Output Message

Contains output text from Aider.

```json
{
  "type": "output",
  "content": "Output text from Aider"
}
```

#### Error Message

Contains error messages.

```json
{
  "type": "error",
  "content": "Error message"
}
```

#### Warning Message

Contains warning messages.

```json
{
  "type": "warning",
  "content": "Warning message"
}
```

#### Active Files Message

Contains a list of files that are currently in context.

```json
{
  "type": "active_files",
  "content": [
    "path/to/file1.py",
    "path/to/file2.js",
    "path/to/file3.html"
  ]
}
```

#### Input Request Message

Indicates that Aider is requesting input from the user.

```json
{
  "type": "input_request",
  "content": {
    "prompt": "Type a message to Aider..."
  }
}
```

#### Input Received Message

Confirms that input was received.

```json
{
  "type": "input_received",
  "content": {
    "text": "The input text that was received",
    "timestamp": 1619712345678
  }
}
```

#### Session Status Message

Provides updates about the session status.

```json
{
  "type": "session_status",
  "content": {
    "active": true,
    "session_id": "session_1234567890",
    "timestamp": 1619712345678
  }
}
```

#### Pong Message

Response to a ping message.

```json
{
  "type": "pong"
}
```

## JavaScript API

The Codex component includes a JavaScript API for integration with the Tekton UI. This API is exposed through the `codexConnector` object.

### Methods

#### initialize()

Initializes the connector and establishes a WebSocket connection.

```javascript
codexConnector.initialize();
```

#### connectWebSocket()

Establishes a WebSocket connection to the Codex server.

```javascript
codexConnector.connectWebSocket();
```

#### startSession()

Starts a new Aider session.

```javascript
codexConnector.startSession();
```

#### stopSession()

Stops the current Aider session.

```javascript
codexConnector.stopSession();
```

#### sendInput(text)

Sends input text to Aider.

```javascript
codexConnector.sendInput("Your input text here");
```

#### cleanup()

Cleans up resources used by the connector.

```javascript
codexConnector.cleanup();
```

### Events

The JavaScript API uses the browser's event system to communicate with the Tekton UI. The main event is:

#### right-footer-input

Triggered when input is received from the RIGHT FOOTER chat input.

```javascript
window.addEventListener('right-footer-input', (event) => {
  const text = event.detail && event.detail.text;
  // Process input
});
```

## Integration Examples

### HTTP API Example

```javascript
// Start a new session
fetch('/api/codex/start', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => console.log('Session started:', data));

// Send input to Aider
fetch('/api/codex/input', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    text: 'Create a simple Flask application'
  })
})
.then(response => response.json())
.then(data => console.log('Input sent:', data));
```

### WebSocket API Example

```javascript
// Connect to WebSocket
const socket = new WebSocket('ws://localhost:8082/ws/codex');

// Handle incoming messages
socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received message:', data);
  
  // Handle different message types
  switch(data.type) {
    case 'output':
      displayOutput(data.content);
      break;
    case 'error':
      displayError(data.content);
      break;
    // Handle other message types...
  }
};

// Start a session
socket.send(JSON.stringify({
  type: 'start_session',
  content: {
    timestamp: Date.now()
  }
}));

// Send input
socket.send(JSON.stringify({
  type: 'input',
  content: 'Create a simple Flask application'
}));
```

## Error Handling

### HTTP Error Status Codes

The HTTP API may return the following status codes:

| Status Code | Description |
|-------------|-------------|
| 200 | OK - The request was successful |
| 400 | Bad Request - The request was malformed |
| 404 | Not Found - The requested resource was not found |
| 500 | Internal Server Error - An error occurred on the server |

### Error Responses

Error responses from the HTTP API will have the following format:

```json
{
  "status": "error",
  "message": "Detailed error message"
}
```

### WebSocket Error Handling

If an error occurs during WebSocket communication, an error message will be sent with the type "error":

```json
{
  "type": "error",
  "content": "Detailed error message"
}
```

## Rate Limiting and Performance

- The Codex server does not impose explicit rate limits, but clients should avoid sending too many requests in a short period
- For streaming output, prefer using the WebSocket API over polling the HTTP API
- The server may take several seconds to process complex requests, especially for large codebases

## Security Considerations

- The Codex API is designed for internal use within the Tekton environment and should not be exposed to the public internet
- No authentication is currently implemented for the API endpoints
- The server has full access to the local filesystem within the user's permissions

## Versioning

The current API version is 0.1.0. Any breaking changes will be communicated through the Tekton release notes.