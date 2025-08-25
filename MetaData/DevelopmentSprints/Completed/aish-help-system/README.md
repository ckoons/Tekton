# aish Help System and Communication Enhancement Sprint

## Overview

This sprint implements three integrated improvements to aish:
1. **Unified syntax**: Fix the `aish [component] [command/message]` pattern
2. **Message visibility**: In-memory two-inbox system for AI-to-AI communication
3. **Help system**: Documentation path pattern for discoverability

## Sprint Status

**Status:** Implementation Phase  
**Created:** 2025-01-03  
**Updated:** 2025-01-04  
**Scope:** Expanded to include syntax fixes and message system

## Key Design Decision

Help commands return paths to documentation rather than help content:

```
$ aish help
Usage: aish [options] [ai] [message]
AI Training: /Users/.../MetaData/TektonDocumentation/AITraining/aish/
User Guides: /Users/.../MetaData/TektonDocumentation/UserGuides/aish/

$ aish terma help
Usage: aish terma [command] [args]
AI Training: /Users/.../MetaData/TektonDocumentation/AITraining/Terma/
User Guides: /Users/.../MetaData/TektonDocumentation/UserGuides/Terma/
```

## Implementation

Changes span three files:
- `/Users/cskoons/projects/github/Tekton/shared/aish/aish` - Unified syntax and help
- `/Users/cskoons/projects/github/Tekton/shared/aish/aish-proxy` - Message display fix
- `/Users/cskoons/projects/github/Tekton/shared/aish/src/commands/terma.py` - Inbox commands

## Key Features

### 1. Unified Syntax
- Direct CI messaging: `aish apollo "message"`
- Component commands: `aish terma list`
- Help integration: `aish apollo help`

### 2. In-Memory Message System
- Two-inbox design: new and keep
- No disk persistence (session-based)
- Future Engram integration ready

### 3. Message Visibility for AIs
- `aish terma inbox` - View new messages
- `aish terma inbox keep` - View saved messages
- `aish terma inbox read N` - Move message to keep

## Documentation

- [Sprint Plan](./SprintPlan.md) - Detailed planning document
- [Architectural Decisions](./ArchitecturalDecisions.md) - Key design decisions and rationale

## Why This Matters

This sprint establishes patterns that will serve Tekton for years:
- Consistent command interface across all components
- Natural AI-to-AI communication
- Equal treatment for humans and Companion Intelligences
- Documentation can evolve without code changes
- Simple, discoverable, and scalable