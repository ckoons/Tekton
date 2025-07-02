# aish Integration Landmarks

**Date**: July 2, 2025  
**Components**: Terma, aish  
**Purpose**: Document landmarks added during aish-Tekton integration

## Overview

This document describes the landmarks added to capture the architectural decisions and integration points created during the aish-Tekton integration. These landmarks will be automatically discovered by Athena and added to the Knowledge Graph.

## Landmarks Added

### 1. Terminal Launcher Architecture Decision

**File**: `/Tekton/Terma/terma/core/terminal_launcher_impl.py`  
**Class**: `TerminalLauncher`  
**Type**: `@architecture_decision`

```python
@architecture_decision(
    title="Native Terminal Integration with aish",
    rationale="Use native terminal apps (Terminal.app, iTerm, etc.) enhanced with aish-proxy for AI capabilities",
    alternatives_considered=["Custom terminal emulator", "Web-based terminal", "PTY manipulation"],
    impacts=["platform_compatibility", "user_experience", "maintenance"],
    decision_date="2025-07-02"
)
```

**Captures**: The key architectural decision to use native terminal applications rather than building a custom terminal emulator. This decision prioritizes user familiarity and platform compatibility.

### 2. aish-proxy Path Resolution

**File**: `/Tekton/Terma/terma/core/terminal_launcher_impl.py`  
**Method**: `_find_aish_proxy`  
**Type**: `@integration_point`

```python
@integration_point(
    title="aish-proxy Path Resolution",
    target_component="aish",
    protocol="File system lookup",
    data_flow="Terma finds aish-proxy executable at Tekton/shared/aish",
    integration_date="2025-07-02"
)
```

**Captures**: The integration mechanism where Terma locates the aish-proxy executable. Documents the file system path resolution order and the new standard location in Tekton/shared/aish.

### 3. Terminal Launch API

**File**: `/Tekton/Terma/terma/core/terminal_launcher_impl.py`  
**Method**: `launch_terminal`  
**Type**: `@api_contract`

```python
@api_contract(
    title="Terminal Launch API",
    endpoint="launch_terminal",
    method="CALL",
    request_schema={"config": "TerminalConfig"},
    response_schema={"pid": "int"},
    description="Launches aish-enabled terminal in user's home directory with their shell"
)
```

**Captures**: The internal API contract for launching terminals. Documents that terminals now launch in the user's home directory with their preferred shell.

### 4. MCP Terminal Launch Endpoint

**File**: `/Tekton/Terma/terma/api/fastmcp_endpoints.py`  
**Function**: `mcp_launch_terminal`  
**Type**: `@api_contract` and `@integration_point`

```python
@api_contract(
    title="Launch aish Terminal via MCP",
    endpoint="/api/mcp/v2/tools/launch_terminal",
    method="POST",
    request_schema={...},
    response_schema={...},
    integration_date="2025-07-02"
)
@integration_point(
    title="MCP to Terminal Launcher Bridge",
    target_component="terminal_launcher_impl",
    protocol="Function call",
    data_flow="MCP request → TerminalLauncher → aish-proxy → Native terminal",
    description="Bridges MCP API requests to native terminal launching with aish"
)
```

**Captures**: 
- The external MCP API endpoint for launching terminals
- The integration flow from MCP request through to native terminal
- Request/response schemas for API consumers

## Knowledge Graph Impact

These landmarks will enable Athena to:

1. **Track Integration Dependencies**: Understanding that Terma depends on aish being present in Tekton/shared/aish
2. **Document API Surface**: Both internal (launch_terminal) and external (MCP endpoint) APIs are captured
3. **Architectural Lineage**: The decision to use native terminals and its rationale is preserved
4. **Integration Flow**: The complete flow from MCP request to terminal launch is documented

## Querying These Landmarks

Once indexed by Athena, you can query:

```
# Find all integration points with aish
"Show integration points targeting aish"

# Understand terminal launching architecture
"Explain the terminal launcher architecture decisions"

# Find MCP endpoints for terminal management
"List MCP endpoints in Terma"

# Trace the flow from MCP to terminal
"Show the data flow for launching terminals"
```

## Best Practices Demonstrated

1. **Graceful Degradation**: Landmarks imports use try/except to work even if landmarks aren't available
2. **Comprehensive Metadata**: Each landmark includes all relevant fields (title, rationale, schemas, etc.)
3. **Integration Documentation**: Both sides of integrations are documented (Terma→aish connection)
4. **API Documentation**: External APIs include full request/response schemas

## Next Steps

As the integration evolves, additional landmarks should be added for:
- Terminal registration with Terma (when implemented)
- Health monitoring between aish and Terma
- Session persistence and recovery features
- Any new architectural decisions or integration points

Remember: Landmarks capture the "why" and "how" of the system for future developers and AI assistants!