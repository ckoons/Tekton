# Engram Simplification Sprint - Sprint Plan

## Overview

This document outlines the high-level plan for the Engram Simplification Development Sprint. It focuses on transforming Engram from an over-engineered system with multiple overlapping APIs into a simple, reliable memory service for AI assistants.

Tekton is an intelligent orchestration system that coordinates multiple AI models and resources. This sprint ensures Engram provides clean, efficient memory services without unnecessary complexity.

## Sprint Goals

The primary goals of this sprint are:

1. **Radical Simplification**: Reduce the API surface from 5+ interfaces to 1 simple class with 3 methods
2. **Silent Operation**: Eliminate verbose logging except when explicitly debugging
3. **Preserve Core Functionality**: Maintain all features that other Tekton components actually use

## Business Value

This sprint delivers value by:

- Reducing cognitive load for AI assistants using memory functions
- Eliminating confusion from multiple overlapping APIs
- Improving performance by removing unnecessary abstractions
- Making the system maintainable and understandable

## Current State Assessment

### Existing Implementation

Engram currently provides memory services through:
- REST API (`server.py`)
- Legacy MCP server (`mcp_server.py`) 
- FastMCP server (`fastmcp_server.py`)
- CLI interfaces (`quickmem.py`, `ez.py`)
- Cognitive layer (`natural_interface.py`)
- Multiple storage backends with overlapping abstractions

### Pain Points

- **API Confusion**: Developers don't know which interface to use
- **Logging Overload**: Simple operations produce 40+ lines of debug output
- **Incomplete Features**: Katra, dreams, emotional memory add complexity without working
- **Documentation Mismatch**: Docs describe aspirational features, not reality
- **Over-abstraction**: Multiple layers doing the same thing

## Proposed Approach

### Key Components Affected

- **API Layer**: Consolidate to single `Memory` class
- **Storage Layer**: One abstraction, pluggable backends
- **Logging**: All behind ENGRAM_DEBUG flag
- **Experimental Features**: Remove katra, dreams, emotional memory, peer awareness

### Technical Approach

1. Create new `engram/simple.py` with clean API
2. Preserve existing storage functionality behind simple interface
3. Remove experimental cognitive features
4. Wrap all logging in debug conditionals
5. Update MCP tools to use new simplified interface

## Code Quality Requirements

### Debug Instrumentation

All code will follow debug patterns but default to SILENT:
- Use ENGRAM_DEBUG environment variable
- Log only errors by default
- Provide rich debugging when explicitly enabled

### Documentation

- Document only what exists
- 5-line quickstart example
- Clear API reference for 3 methods
- Migration guide from old APIs

### Testing

- Unit tests for Memory class
- Integration tests with storage backends
- Smoke tests for MCP tools

## Out of Scope

The following items are explicitly out of scope:

- Rewriting storage backends (keep what works)
- Changing MCP protocol interfaces
- Modifying how other components use Engram

## Dependencies

This sprint depends on:
- Understanding which Engram features other components actually use
- Preserving MCP tool interfaces for backward compatibility

## Timeline and Phases

### Phase 1: Core Simplification (Current)
- **Duration**: 1 session
- **Focus**: Create simple API, remove experimental features
- **Key Deliverables**: 
  - `engram/simple.py` with Memory class
  - Removed experimental features
  - Debug logging wrapper

### Phase 2: Migration and Testing
- **Duration**: 1 session
- **Focus**: Update components to use new API
- **Key Deliverables**:
  - Updated MCP tools
  - Migration of existing APIs
  - Test suite

### Phase 3: Documentation
- **Duration**: 1 session
- **Focus**: Accurate, simple documentation
- **Key Deliverables**:
  - Rewritten README
  - API reference
  - Migration guide

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Breaking component dependencies | High | Medium | Careful analysis of component usage |
| Losing important functionality | Medium | Low | Preserve all actually-used features |
| Migration complexity | Medium | Medium | Provide compatibility layer if needed |

## Success Criteria

This sprint will be considered successful if:

- Engram can be used with this code:
  ```python
  from engram import Memory
  mem = Memory()
  await mem.store("Important thought")
  result = await mem.recall("important")
  ```
- No logs appear unless ENGRAM_DEBUG=true
- All Tekton components continue working
- Documentation matches implementation

## Key Stakeholders

- **Casey**: Human-in-the-loop project manager and system architect
- **Vertex**: Current implementing AI
- **Other AI Instances**: Will benefit from simplified interface
- **Tekton Components**: Must continue functioning

## References

- Current Engram implementation: `/Engram/`
- Example of overengineering: `/Engram/engram/cognitive/`
- Sprint documentation guidelines: `/MetaData/DevelopmentSprints/README.md`