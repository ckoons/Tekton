# MCP Distributed Tekton Sprint Release Notes

## Release Date: 2025-01-18

## What Changed

### New Features
- **MCP Server**: aish now runs an MCP (Model Context Protocol) server on port 8118
- **Unified AI Interface**: All UI chat components now route through aish MCP
- **Management Commands**: Added `aish status`, `aish restart`, `aish logs`, and `aish debug-mcp` commands
- **Streaming Support**: MCP server supports Server-Sent Events for streaming AI responses
- **Comprehensive Testing**: Full test suite for MCP endpoints

### API Changes
- **New MCP Endpoints**:
  - `/api/mcp/v2/health` - Health check
  - `/api/mcp/v2/capabilities` - MCP discovery
  - `/api/mcp/v2/tools/send-message` - Send message to specific AI
  - `/api/mcp/v2/tools/team-chat` - Broadcast to all team members
  - `/api/mcp/v2/tools/list-ais` - List available AIs
  - `/api/mcp/v2/tools/forward` - Manage AI forwarding
  - `/api/mcp/v2/tools/project-forward` - Project CI forwarding
  - `/api/mcp/v2/tools/purpose` - Terminal purpose management
  - `/api/mcp/v2/tools/terma-*` - Terminal communication

### UI Updates
- **window.AIChat**: Now routes all messages through aish MCP
- **aishUrl() function**: Added to tekton-urls.js for MCP URL building
- **AI Name Fixes**: All UI components use correct AI names without '-ai' suffix

### Infrastructure Changes
- **Port Configuration**: AISH_MCP_PORT (8118) exported to UI environment
- **Auto-start**: MCP server starts automatically with aish

## Breaking Changes

1. **AI Names**: UI components must use base AI names without '-ai' suffix
   - Before: `numa-ai`, `apollo-ai`, `athena-ai`
   - After: `numa`, `apollo`, `athena`

2. **Chat Routing**: All UI chat must go through aish MCP
   - Before: Direct HTTP calls to specialist endpoints
   - After: Route through `window.AIChat` using aish MCP

3. **Port Usage**: MCP server uses dedicated port 8118
   - aish shell: port 8117 (AISH_PORT)
   - aish MCP: port 8118 (AISH_MCP_PORT)

## Migration Steps

### For UI Components

1. Update AI names in your component:
   ```javascript
   // Before
   window.AIChat.sendMessage('numa-ai', message);
   
   // After
   window.AIChat.sendMessage('numa', message);
   ```

2. Ensure using window.AIChat for all AI communication:
   ```javascript
   // All messages now route through aish MCP
   const response = await window.AIChat.sendMessage('numa', message);
   ```

3. Use aishUrl() for MCP endpoints:
   ```javascript
   // Import from tekton-urls.js
   const url = aishUrl('/api/mcp/v2/tools/send-message');
   ```

### For Developers

1. Start aish to enable MCP server:
   ```bash
   aish
   # MCP server starts automatically on port 8118
   ```

2. Check MCP server status:
   ```bash
   aish status
   ```

3. Debug MCP operations:
   ```bash
   aish debug-mcp
   ```

## Testing

Run the MCP test suite:
```bash
cd $TEKTON_ROOT/shared/aish/tests
./test_mcp.sh
```

Or run Python tests directly:
```bash
python3 -m pytest test_mcp_server.py -v
```

## Known Issues

- Authentication layer for MCP not yet implemented
- Some specialist endpoints still exist (to be removed in Phase 3)
- Performance testing vs direct HTTP not yet complete

## Next Steps

- Phase 3: Remove redundant HTTP endpoints from all components
- Phase 4: Implement manifest system for distributed Tekton
- Phase 5: GitHub integration preparation

## Documentation

- MCP Server Guide: `/MetaData/Documentation/MCP/aish_MCP_Server.md`
- Updated aish Command Reference with debug commands
- Updated UI Implementation Guide for MCP integration