# aish Integration Documentation Updates

**Date**: July 2, 2025  
**Integration**: aish moved to Tekton/shared/aish

## Documents Requiring Updates

### 1. AI_Interface_Implementation_Guide.md

**Location**: `TektonDocumentation/Building_New_Tekton_Components/`

**Updates Needed**:
- Add section showing aish as the primary AI interface
- Update examples to use `aish <ai-name>` pattern
- Remove references to individual AI commands (apollo, athena)
- Add note that components should integrate with Rhetor for AI access

### 2. AIDiscoveryForAish.md

**Location**: `TektonDocumentation/Guides/`

**Updates Needed**:
- Update to show `aish -l` for listing available AIs
- Explain that aish discovers AIs through Rhetor
- Remove old discovery patterns
- Add examples of dynamic AI discovery

### 3. AI_DISCOVER_USAGE.md

**Location**: `TektonDocumentation/API/`

**Updates Needed**:
- Update all usage examples to use aish
- Show `aish -l` instead of ai-discover command
- Explain that discovery is now integrated into aish

### 4. AI_Orchestration_Architecture.md

**Location**: `TektonDocumentation/Architecture/`

**Minor Updates**:
- Add note that aish is the client interface
- Reference the new Terma_aish_Integration.md
- Core architecture unchanged (Rhetor as hub)

## Documents That Remain Accurate

These documents describe internal architecture and remain valid:

- **AIRegistry.md** - Internal registry mechanism unchanged
- **AI_Communication_Architecture.md** - Socket architecture still accurate
- **AI_Platform_Instrumentation.md** - Platform instrumentation unchanged
- **AI_Socket_Communication_Guide.md** - Technical implementation valid
- **AIDiscoveryQuickReference.md** - API reference for internal use
- **AIDiscoveryAPITreaty.md** - Component contracts unchanged

## New Documentation Created

1. **Terma_aish_Integration.md** - Complete integration architecture
2. **aish_Terminal_Guide.md** - User guide for aish in terminals
3. **Terma_MCP_Endpoints.md** - API documentation for new endpoints
4. **This file** - Tracking needed updates

## Implementation Notes

The key principle is that aish is now the user-facing interface for AI interaction, while the internal architecture (Rhetor, AI specialists, socket communication) remains unchanged. Documentation should reflect this separation of concerns:

- **User-facing docs**: Focus on aish commands
- **Developer docs**: Explain both aish and internal architecture
- **API docs**: Show MCP/REST endpoints that support aish

Individual AI commands (apollo, athena, etc.) are deprecated in favor of the unified `aish` command pattern.