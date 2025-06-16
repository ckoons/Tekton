# Codex Aider Adapter for Tekton

This adapter integrates the [Aider](https://github.com/paul-gauthier/aider) AI programming assistant with the Tekton platform, providing a seamless interface for AI-assisted coding directly in the Tekton UI.

## Features

- WebSocket-based communication between Aider and Tekton
- Real-time code editing and suggestions
- File management integration
- Persistent chat context
- Git integration

## Setup

1. **Install Dependencies**:

```bash
cd /path/to/Tekton/Codex/adapter
pip install -r requirements.txt
```

2. **Run Initialization Script**:

```bash
python init_codex.py
```

This initializes the integration and registers Codex with Hermes.

## Launch Options

The Codex/Aider component can be launched in several ways:

### Option 1: Using launch-tekton.sh with --aider flag

```bash
./launch-tekton.sh --aider
```

This launches Engram, Hermes, Hephaestus, and Codex components.

### Option 2: Using launch-tekton.sh with --full-stack flag

```bash
./launch-tekton.sh --full-stack
```

This launches all necessary components including Codex.

### Option 3: Specifying components manually

```bash
./launch-tekton.sh --components engram,hermes,hephaestus,codex
```

## Troubleshooting

- **WebSocket Connection Issues**: Ensure the Codex server is running on port 8082. Check the logs at `~/.tekton/logs/codex.log`.
- **Import Errors**: Make sure the Python path includes the Tekton directory.
- **UI Not Showing**: Verify that the codex.html file exists in the Hephaestus component directory.

## Architecture

The integration consists of:

1. **Aider Adapter**: Interfaces with Aider's core functionality
2. **WebSocket Handler**: Manages communication with the UI
3. **HTML Component**: UI integration for the Tekton interface
4. **Server**: FastAPI server for hosting the WebSocket endpoint

## Development

When extending the adapter:

1. Implement changes in the appropriate files
2. Test thoroughly with simplified components first
3. Integrate with the full Tekton stack

For debugging, use the `--aider` launch flag to focus just on the components needed for Aider development.