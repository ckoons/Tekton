# AISH Review Implementation - Architectural Decisions

## Overview

This document captures the key architectural decisions made for the AISH Review implementation. These decisions balance simplicity, extensibility, and research flexibility.

## Key Decisions

### 1. Session Capture Method

**Decision**: Use Unix `script` command for terminal session capture

**Rationale**:
- Standard Unix tool, available on all target platforms
- Captures complete terminal I/O including control sequences
- No custom implementation needed
- Battle-tested and reliable

**Alternatives Considered**:
- Custom Python pty implementation: Too complex, reinventing the wheel
- Simple stdout/stderr redirection: Misses interactive elements
- Third-party recording tools: Unnecessary dependencies

### 2. Session Storage Format

**Decision**: Raw script output with metadata trailer

**Format**:
```
[Raw script session output]
...
...
[END OF SESSION]
--- TEKTON SESSION METADATA ---
{
  "start_time": "2025-01-08T10:30:00Z",
  "end_time": "2025-01-08T11:45:00Z", 
  "terminal_name": "Amy",
  "terminal_purpose": "CI workflow testing",
  "terminal_role": "senior engineering coordinator",
  "session_version": "1.0"
}
--- END METADATA ---
```

**Rationale**:
- Preserves complete session fidelity
- Metadata is human-readable and parseable
- Easy to extend metadata format
- Compatible with existing Unix tools

**Implementation Notes**:
- Metadata added after script exits
- JSON format for structured data
- Clear delimiters for parsing
- Version field for future format changes

### 3. Storage Location and Naming

**Decision**: Store in `$TEKTON_MAIN_ROOT/.tekton/terminal-sessions/`

**Naming Convention**: `{terminal_name}-{YYYYMMDD}-{HHMMSS}.log.gz`

**Example**: `amy-20250108-143000.log.gz`

**Rationale**:
- Centralized location for all coder environments
- Sortable by date/time
- Terminal name first for easy filtering
- Extension indicates compression status

### 4. Compression Strategy

**Decision**: Store all sessions compressed immediately

**Implementation**:
- Use gzip compression during session finalization
- All files stored as .log.gz
- No uncompressed files in storage

**Rationale**:
- Terminal sessions can be large
- These are for long-term research, not immediate access
- Standard tools (vim, less, zcat) handle .gz transparently
- Simplifies storage management

### 5. Session Lifecycle

**Decision**: Keep all sessions indefinitely (for now)

**Rationale**:
- Research value increases over time
- Storage is relatively cheap
- Patterns may only emerge with large datasets
- Can implement retention policies later if needed

### 6. Future Extensibility Points

**Planned But Not Implemented**:

1. **Sanitization Function**:
   - Placeholder for `sanitize_store()` function
   - Would remove sensitive data before storage
   - Not needed currently but architecture supports it

2. **Format Versioning**:
   - `session_version` field in metadata
   - Allows format evolution without breaking parsers
   - Research tools can handle multiple versions

3. **Additional Metadata**:
   - Easy to add fields to JSON structure
   - Examples: git branch, task ID, error count
   - Parser should ignore unknown fields

### 7. Integration Architecture

**Decision**: Loose coupling with analysis pipeline

**Design**:
- Session capture is independent of analysis
- No real-time processing requirements
- Analysis tools read files asynchronously
- Multiple analyses can run on same session

**Rationale**:
- Research needs will evolve
- Allows experimentation with different approaches
- No performance impact on terminal operations
- Enables reprocessing with new algorithms

### 8. Command Interface

**Decision**: Single `aish review` command with subcommands

**Proposed Interface**:
```bash
aish review start              # Start recording current terminal
aish review stop               # Stop recording and compress
aish review list               # List sessions
```

**Rationale**:
- Consistent with existing aish patterns
- Room for growth with subcommands
- Clear and intuitive usage

## Security Considerations

- No passwords or API keys expected in sessions
- File permissions set to user-only access
- Future sanitization can be added transparently
- Sessions contain only terminal I/O, not system internals

## Performance Considerations

- Script command has minimal overhead
- Compression happens asynchronously
- No impact on terminal responsiveness
- Storage growth is predictable and manageable

## Future Research Considerations

This architecture specifically enables:

1. **Temporal Analysis**: How CI behavior changes over time
2. **Pattern Mining**: Common command sequences and workflows
3. **Error Analysis**: Learning from mistakes and corrections
4. **Collaboration Studies**: Human-CI interaction patterns
5. **Performance Studies**: Task completion efficiency
6. **Learning Curves**: How quickly CIs adapt to new tasks

The loose coupling and raw data preservation ensure maximum flexibility for future research directions.