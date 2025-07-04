# Terma Replacement Sprint - Terminal Orchestrator

## Overview

Complete rewrite of Terma as a **Terminal Orchestrator** that launches and manages native terminal applications with aish integration. This is a ground-up replacement, not an evolution of the old embedded terminal approach.

## Vision

Terma becomes the intelligent terminal management layer for Tekton, enabling both users and AIs to spawn, configure, and manage native terminal sessions with AI-powered shell capabilities through aish.

## Core Principles

1. **Native Terminals First**: Leverage existing terminal emulators (Terminal.app, iTerm2, Warp, Claude Code)
2. **Simple Unix Philosophy**: Track terminals by PID, use signals for control
3. **AI-Powered Shell**: aish as the intelligent shell wrapper
4. **Clean Architecture**: Borrow successful patterns from Numa/Noesis
5. **User & AI Friendly**: Both can request and manage terminals

## What We're Building

### Terminal Orchestrator Service
- Launches native terminal applications
- Injects aish as shell or ensures it's in PATH
- Tracks all terminals by PID
- Provides lifecycle management (show/hide/terminate)
- Maintains configuration templates

### Terma UI (Hephaestus Component)
- **Dashboard**: View and manage active terminals
- **Launch Terminal**: Configure and spawn new terminals
- **Terminal Chat**: Communicate with specific terminal's aish
- **Team Chat**: Shared Rhetor team collaboration

### aish Shell Enhancement
- Refactor to be a true shell wrapper
- Transparent command passthrough
- AI pattern interception
- Context preservation

## What We're NOT Building

- ❌ Terminal emulator
- ❌ Embedded web terminals
- ❌ Complex terminal rendering
- ❌ Shell replacement (aish wraps, not replaces)

## Success Criteria

1. Launch native terminals with single click
2. aish available in all spawned terminals
3. Track and manage terminals by PID
4. Both users and AIs can spawn terminals
5. Clean, simple UI following Numa/Noesis patterns

## Architecture

```
Terma UI (Hephaestus) → Terma Service → Native Terminal App
                            |                    |
                            |                   aish
                            |                    |
                        PID Tracking         bash/zsh
```

## Sprint Phases

### Phase 1: aish Shell Wrapper (Week 1)
- Refactor aish as transparent shell wrapper
- Command interception and AI routing
- Subprocess and tool compatibility

### Phase 2: Terminal Launch Service (Week 2)
- Multi-terminal launcher (macOS + Linux)
- PID-based lifecycle management
- Configuration template system

### Phase 3: Terma UI Implementation (Week 3)
- Port Numa/Noesis UI patterns
- Four-tab interface with unified chat
- Terminal dashboard and controls

### Phase 4: Integration & Polish (Week 4)
- AI terminal request API
- Testing across terminal types
- Documentation and examples

## Key Features

1. **Terminal Templates**: Pre-configured launch profiles
2. **AI Context Injection**: Pass purpose/context to aish
3. **Multi-Terminal Support**: Terminal.app, iTerm2, Warp, Claude Code
4. **Cross-Platform**: macOS first, Linux compatible
5. **Simple Management**: PID-based tracking and control

## Technical Stack

- **Backend**: Python (FastAPI) - Terma service
- **Frontend**: HTML/CSS/Vanilla JS - Following Numa/Noesis
- **Shell**: aish (enhanced) wrapping bash/zsh
- **OS Integration**: Native terminal launching APIs