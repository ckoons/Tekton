# Sprint: MCP & Distributed Tekton

## Overview
Transform Tekton to use MCP (Model Context Protocol) as the primary interface for all actions, removing redundant HTTP interfaces and preparing for distributed Tekton systems with manifest-based discovery.

## Goals
1. **MCP-Only Architecture**: Make aish an MCP server, remove HTTP duplication
2. **Manifest System**: Enable Tekton systems to discover and communicate
3. **Distributed Commands**: Support `-s <system>` for remote Tekton access

## Phase 1: aish MCP Server [0% Complete]

### Tasks
- [ ] Create `/shared/aish/src/mcp/server.py` with FastAPI
- [ ] Implement MCP discovery endpoint `/mcp/capabilities`
- [ ] Create `/mcp/tools/send-message` - wraps MessageHandler.send()
- [ ] Create `/mcp/tools/team-chat` - wraps AIShell.broadcast_message()
- [ ] Create `/mcp/tools/forward` - wraps forward commands
- [ ] Create `/mcp/tools/project-forward` - wraps project forwards
- [ ] Create `/mcp/tools/list-ais` - returns available AIs
- [ ] Create `/mcp/tools/terma/*` - all terma functionality
- [ ] Create `/mcp/tools/purpose` - purpose-based routing
- [ ] Add authentication/security layer
- [ ] Create MCP test suite
- [ ] Update aish to run MCP server on startup

### Success Criteria
- [ ] All aish functionality exposed via MCP
- [ ] Forwarding works through MCP
- [ ] MCP endpoints documented
- [ ] External tools can connect

### Blocked On
- [ ] Nothing currently

## Phase 2: UI Migration to MCP [0% Complete]

### Tasks
- [ ] Update `window.AIChat` to use aish MCP endpoints
- [ ] Update Projects Chat to use MCP
- [ ] Update Builder Chat to use MCP  
- [ ] Update Team Chat to use MCP
- [ ] Update all specialist UIs (Numa, Sophia, etc.)
- [ ] Remove direct Rhetor specialist endpoints
- [ ] Test forwarding works in all UIs
- [ ] Update error handling for MCP responses
- [ ] Performance test vs current HTTP

### Success Criteria
- [ ] All UI chat works through aish MCP
- [ ] Forwarding works everywhere
- [ ] No regression in performance
- [ ] Error handling improved

### Blocked On
- [ ] Phase 1 MCP server completion

## Phase 3: Remove Redundant HTTP [0% Complete]

### Tasks
- [ ] Remove `/api/v1/ai/specialists/*/message` from Rhetor
- [ ] Remove `/api/projects/chat` from Tekton Core
- [ ] Remove message routing from Hermes
- [ ] Clean up each component's redundant endpoints
- [ ] Update all component MCP capabilities
- [ ] Remove unused HTTP client code
- [ ] Update API documentation
- [ ] Verify nothing breaks

### Success Criteria
- [ ] 30-40% less HTTP code
- [ ] All messaging through aish MCP
- [ ] No duplicate message paths
- [ ] Cleaner component APIs

### Blocked On
- [ ] Phase 2 UI migration

## Phase 4: Manifest System Foundation [0% Complete]

### Tasks
- [ ] Design manifest schema for Tekton systems
- [ ] Create `$TEKTON_ROOT/.tekton/manifest.json`
- [ ] Add manifest endpoint to MCP server
- [ ] Implement Tekton system discovery
- [ ] Create manifest update mechanism
- [ ] Add `-s <system>` support to tekton command
- [ ] Add `-s <system>` support to aish command
- [ ] Create remote MCP proxy functionality
- [ ] Test with local "remote" Tekton

### Success Criteria
- [ ] Can discover other Tekton systems
- [ ] Can route commands to remote systems
- [ ] Manifest auto-updates
- [ ] Security model defined

### Blocked On
- [ ] Phases 1-3 complete

## Phase 5: GitHub Integration Prep [0% Complete]

### Tasks
- [ ] Design GitHub webhook integration
- [ ] Create PR-triggered manifest updates
- [ ] Implement fork detection
- [ ] Add fork metadata to manifest
- [ ] Create fork communication protocol
- [ ] Document distributed Tekton model
- [ ] Create example multi-Tekton setup

### Success Criteria
- [ ] GitHub forks auto-register
- [ ] PRs can trigger cross-Tekton actions
- [ ] Distributed model documented
- [ ] Security model implemented

### Blocked On
- [ ] Phase 4 manifest system

## Technical Decisions
- Use FastAPI for MCP server (standard for MCP implementations)
- Keep aish as single source of truth for message routing
- Manifest uses JSON for simplicity
- Remote commands use same MCP protocol

## Out of Scope
- Complete GitHub integration (next sprint)
- Distributed CI orchestration (future)
- Cross-Tekton authentication (needs design)

## Files to Update
```
# New files
/shared/aish/src/mcp/server.py
/shared/aish/src/mcp/manifest.py
/tekton/core/manifest_manager.py

# Updated files
/shared/aish/aish
/Hephaestus/ui/scripts/shared/ai-chat.js
/Rhetor/rhetor/api/ai_routes.py
/TektonCore/tekton/api/projects.py
/bin/tekton

# Config files
/.tekton/manifest.json
```