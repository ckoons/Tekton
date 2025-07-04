# aish Help System and Communication - Architectural Decisions

## Overview

This document records the architectural decisions made for the aish help system and communication enhancements. Key decisions include the unified command syntax, in-memory message system, and documentation path pattern.

## Decision 1: Documentation Path Pattern

### Context

We need a help system that:
- Serves both humans and Companion Intelligences equally
- Scales with new components without code changes
- Maintains the thin client philosophy
- Allows documentation to evolve independently

### Decision

Implement help commands that return documentation paths rather than help content.

### Alternatives Considered

#### Alternative 1: Embedded Help Text

Embed help text directly in the aish command.

**Pros:**
- Works offline
- Fast response
- No external dependencies

**Cons:**
- Requires code changes for documentation updates
- Duplicates information
- Hard to maintain
- Limited formatting options

#### Alternative 2: Dynamic Help from AI Specialists

Query each AI specialist for their help content.

**Pros:**
- Rich, contextual help
- AI specialists own their documentation
- Can provide examples based on context

**Cons:**
- Requires AI specialists to be running
- Network latency
- Complex implementation
- Not available offline

#### Alternative 3: Documentation Path Pattern (Chosen)

Return paths to documentation directories.

**Pros:**
- Minimal code surface
- Documentation can evolve independently
- Equal treatment for all users
- Discoverable by exploration
- Sets foundation for future enhancements

**Cons:**
- Requires users to navigate to documentation
- Not as immediate as embedded help

### Decision Rationale

The documentation path pattern was chosen because:
1. It keeps the aish command minimal and focused
2. Documentation can be rich and evolve without code changes
3. It treats humans and AIs as equal citizens
4. It's simple to implement and understand
5. It scales naturally with new components

### Implementation Guidelines

1. Help output format should be consistent:
   ```
   Usage: [usage information]
   AI Training: [path to AI training docs]
   User Guides: [path to user guides]
   ```

2. Paths should be absolute for clarity
3. Component names should map directly to directory names

## Decision 2: Single File Implementation

### Context

We need to decide where to implement the help logic.

### Decision

Implement all help logic within the aish command file itself.

### Rationale

- Maintains the thin client philosophy
- No need to modify other components
- Simple to understand and maintain
- All help logic in one place

## Decision 3: Directory Structure

### Context

We need a clear, scalable structure for documentation.

### Decision

Use this hierarchy:
```
MetaData/TektonDocumentation/
├── AITraining/
│   └── [component]/
└── UserGuides/
    └── [component]/
```

### Rationale

- Clear separation between AI and human documentation
- Component names map directly to directories
- Easy to navigate and discover
- Supports future growth

## Decision 4: Unified Command Syntax

### Context

Current aish has inconsistent command patterns and fails on direct AI messaging.

### Decision

Implement unified syntax: `aish [component] [command/message] [options]`

### Rationale

- Consistent interface across all operations
- Eliminates synthetic pipeline construction
- Natural extension point for new features
- Matches git/docker subcommand patterns

## Decision 5: In-Memory Message System

### Context

AI sessions need to see messages sent between terminals.

### Decision

Implement in-memory two-inbox system (new/keep) without disk persistence.

### Rationale

- Simple: No file I/O or cleanup needed
- Natural: Matches terminal session lifecycle
- Privacy: Nothing persisted to disk
- Future-ready: Easy to add Engram integration
- Human-like: Mirrors email triage behavior

## Decision 6: Message Display via /dev/tty

### Context

Async messages interfere with command prompts when using stdout.

### Decision

Write messages directly to /dev/tty to avoid prompt interference.

### Rationale

- Clean separation of message display and command I/O
- Works with all terminal types
- No prompt corruption

## Future Considerations

1. **Conversational Help**: The pattern "Help: I need..." could trigger richer responses
2. **Context-Aware Help**: Help could eventually consider user's current task
3. **Help Indexing**: Could add search capabilities across documentation
4. **Multi-Language Support**: Documentation directories could have language subdirectories
5. **Persistent Messages**: Engram integration for long-term message storage
6. **Real-time Delivery**: WebSocket for immediate message delivery

These are explicitly out of scope for this sprint but the chosen patterns support them.

## References

- [Thin Client Philosophy](https://en.wikipedia.org/wiki/Thin_client)
- [Unix Philosophy](https://en.wikipedia.org/wiki/Unix_philosophy)
- [Tekton Architecture](/Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/Architecture/)