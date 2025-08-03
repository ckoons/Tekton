# CI Tools Integration Notes

## Claude Code Integration Status

### Current State
- **Executable**: `/Users/cskoons/.claude/local/claude`
- **Mode**: Plain text with `--print` flag
- **Status**: Partially working

### Known Issues

1. **Batch Processing Mode**
   - The `claude --print` command expects EOF before processing
   - This doesn't work well with our interactive socket bridge model
   - Each message would need to close stdin, ending the session

2. **Stream-JSON Format**
   - The `--input-format stream-json` has specific requirements we haven't decoded yet
   - Getting errors like "Expected message type 'user', got 'undefined'"

3. **Interactive Mode**
   - Without `--print`, claude expects an interactive TTY session
   - This might not work well with our pipe-based communication

### Potential Solutions

1. **Session-per-Message**: Accept the limitation and create a new process for each message
2. **TTY Emulation**: Use a pseudo-TTY to run claude in interactive mode
3. **API Integration**: Check if Claude Code has an API mode or SDK
4. **Custom Wrapper**: Create a wrapper that manages the claude process differently

### Other AI Tools to Integrate

- **aider**: Located at `../aider`
- **codex**: Located at `../codex`
- **gemini-cli**: Located at `../gemini-cli`
- **grok-cli**: Located at `../grok-cli`

Each tool will need:
1. Checking command-line interface options
2. Understanding input/output formats
3. Creating appropriate adapter configurations
4. Testing integration with our infrastructure