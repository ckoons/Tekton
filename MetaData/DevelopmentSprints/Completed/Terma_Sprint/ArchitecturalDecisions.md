# Terma Architectural Decisions

## Core Architecture

### Decision: Launch Real Terminals, Don't Embed
**Rationale**: Embedding terminals leads to rendering issues, scrolling problems, and reinventing what OS already does well. Instead, launch real terminal emulators with Rhetor attached.

**Implementation**:
```bash
# Launch terminal with Rhetor wrapper
xterm -e "rhetor-wrap bash"
iTerm2 -e "rhetor-wrap zsh"
Terminal.app with "rhetor-wrap bash"
```

### Decision: Rhetor as stdin/stdout Wrapper
**Rationale**: Rhetor monitors and enhances terminal interaction without interfering with normal operation. Acts as intelligent middleware.

**Architecture**:
```
Terminal → stdin → Rhetor Monitor → bash/zsh
                        ↓
                  Intelligence Layer
                        ↓
         stdout ← Rhetor Enhancement ← 
```

## Key Design Choices

### 1. Stateful Session Management
Each Terma instance maintains:
- Current working directory
- Environment variables
- Command history
- Learned patterns
- Active processes

### 2. Safety Layers
Three levels of protection:
1. **Pattern Detection**: Recognize dangerous patterns (`rm -rf`, `>`, `dd`)
2. **Rhetor Analysis**: AI evaluates potential impact
3. **User Confirmation**: Explicit approval for destructive operations

### 3. Output Parsing Strategy
- **Structured Commands**: Parse known outputs (ps, ls, etc.) into structured data
- **Streaming**: Handle long-running commands with progressive output
- **Error Detection**: Recognize common error patterns and suggest fixes

### 4. Learning Architecture
```python
class PatternLearner:
    def observe(self, intent: str, command: str, success: bool):
        # Store successful patterns
        if success:
            self.patterns[intent].append(command)
```

## Integration Points

### Rhetor Integration
- Rhetor runs as a separate process
- Communicates via structured messages
- Can be swapped for different AI backends

### Engram Integration
- Store successful command patterns
- Retrieve patterns for similar intents
- Share learning across Terma instances

### Tekton Integration
- Special commands for component management
- Direct integration with Hermes for status
- Ability to debug other components

## Data Flow

1. **Input Phase**
   ```
   Natural Language → Rhetor → Intent + Entities
   ```

2. **Planning Phase**
   ```
   Intent → Pattern Matcher → Command Candidates → Safety Check
   ```

3. **Execution Phase**
   ```
   Command → Shell → Output Stream → Parser
   ```

4. **Learning Phase**
   ```
   Result → Success Evaluation → Pattern Storage → Engram
   ```

## Error Handling Strategy

1. **Command Failures**: Capture stderr, parse error, suggest fixes
2. **Timeout Handling**: Configurable timeouts with graceful termination
3. **Resource Limits**: Monitor memory/CPU usage of spawned processes
4. **Recovery**: Maintain enough state to recover from crashes

## Performance Considerations

- Command translation cached for common patterns
- Streaming output to prevent memory buildup
- Background pattern learning (non-blocking)
- Lazy loading of historical patterns

## Security Considerations

- No execution of commands from untrusted sources
- Sanitization of all inputs before shell execution
- Audit logging of all executed commands
- Configurable restrictions on available commands