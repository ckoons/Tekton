# Codex (Aider) Integration Plan

This document outlines the plan for integrating the Aider programming assistant into Tekton via the Codex component.

## Current Status

- Basic UI integration completed (tabs for Chat/Files/Settings)
- Aider startup implemented but has threading/asyncio issues
- Communication between RIGHT FOOTER input and Aider not fully working

## Known Issues

1. **Threading/Asyncio Conflict**: The current approach of starting Aider in a thread and communicating back to the main asyncio loop is causing errors:
   ```
   RuntimeError: There is no current event loop in thread 'Thread-1 (_start_aider)'
   ```

2. **Startup Reliability**: Aider sometimes fails to start properly, displaying only "Initializing Aider session..."

3. **Input Handling**: Input from the RIGHT FOOTER is not consistently being delivered to Aider

## Integration Architecture

The integration has these components:

- **codex_server.py**: FastAPI server that handles WebSocket connections and REST endpoints
- **aider_adapter.py**: Adapter that starts and manages Aider
- **websocket_handler.py**: Handles WebSocket communication between UI and Aider
- **codex.html**: The UI component for the Hephaestus interface

## Tabs Functionality

1. **Chat**: Main terminal interface for interacting with Aider
2. **Files**: Displays files that Aider is currently working with
3. **Settings**: Allows configuration of Aider (model selection, git integration, etc.)

## Next Steps

### Phase 1: Fix Core Functionality

1. Simplify the Aider startup process:
   - Remove complex threading model
   - Start Aider with a more direct approach
   - Implement more robust error handling

2. Fix input handling:
   - Ensure RIGHT FOOTER input is properly delivered to Aider
   - Add clear visual feedback for input delivery

3. Improve the session management:
   - Make "New Session" button work reliably
   - Add proper cleanup on session end

### Phase 2: Enhance User Experience

1. Improve Files tab functionality:
   - Show real-time file list updates
   - Allow clicking files to focus Aider on them

2. Implement Settings tab:
   - Model selection
   - Git integration toggle
   - Editor preferences

3. Add session persistence:
   - Remember active files between sessions
   - Store conversation history

## Implementation Notes

For fixing the threading/asyncio issue, consider these approaches:

1. Use a dedicated thread with its own event loop
2. Use the main event loop and avoid threading for Aider startup
3. Implement a process-based approach instead of threading

The recommended approach is to simplify the architecture and use minimal threading.

## Testing Plan

1. Test basic input/output functionality
2. Test session restart functionality
3. Test file tracking
4. Test with various model configurations