# Rhetor AI Specialist API Migration Guide

## Overview
The internal AI specialist management system has been replaced with a unified AI Registry system. This guide documents the API changes.

## Old System (Removed)
The old system used internal specialist management with these endpoints:
- `GET /api/v1/specialists`
- `POST /api/v1/specialists/{id}/start` 
- `POST /api/v1/specialists/{id}/stop`
- `GET /api/v1/specialists/{id}`

## New Unified System
All AI management now goes through the AI Registry with these endpoints:

### List AIs
```bash
GET /api/ai/specialists
```
Query parameters:
- `active_only`: Show only hired specialists
- `role_filter`: Filter by role (e.g., "planning", "code-analysis")

### Hire an AI
```bash
POST /api/ai/specialists/{ai_id}/hire
```
Body:
```json
{
  "ai_id": "apollo-ai",
  "role": "code-analysis",
  "reason": "Need code review capabilities"
}
```

### Fire an AI
```bash
POST /api/ai/specialists/{ai_id}/fire
```
Body:
```json
{
  "ai_id": "apollo-ai",
  "reason": "Project completed"
}
```

### Get Current Roster
```bash
GET /api/ai/roster
```
Returns Rhetor's currently hired AIs with enriched information.

### Reassign AI Role
```bash
POST /api/ai/specialists/{ai_id}/reassign?new_role=planning
```

### Find Candidates
```bash
GET /api/ai/candidates/{role}
```
Find AIs that can fulfill a specific role.

## Client Updates

### Apollo
Apollo's `rhetor.py` interface has been updated:
- `/api/v1/specialists` → `/api/ai/specialists`
- `/api/v1/specialists/{id}/stop` → `/api/ai/specialists/{id}/fire`
- `/api/v1/specialists/{id}/start` → `/api/ai/specialists/{id}/hire`

### aish
The `aish` tool now uses the AI Discovery Service with smart routing:
```bash
# List all AIs (discovers both Greek Chorus and Rhetor specialists)
aish -l

# Use Greek Chorus AI (direct socket communication)
echo "Hello" | aish --ai apollo

# Use Rhetor specialist (HTTP API communication)
echo "Hello" | aish --ai rhetor-ai

# Let discovery find best AI (auto-routes to appropriate communication method)
echo "Write Python code" | aish
```

**Communication Methods**:
- **Greek Chorus AIs**: Direct TCP socket (ports 45000-50000)
- **Rhetor Specialists**: HTTP API via `/api/ai/specialists`
- **aish**: Automatically detects AI type and uses correct protocol

## MCP Tools
MCP tools now use the unified integration:
- `ListAISpecialists` - Uses AI Registry
- `ActivateAISpecialist` - Maps to hire/fire
- `SendMessageToSpecialist` - Uses Registry for discovery

## Backward Compatibility
A compatibility endpoint maps old specialist IDs:
- `POST /api/ai/specialists/{old_id}/activate` 
- Maps: `rhetor-orchestrator` → `rhetor-ai`
- Maps: `apollo-coordinator` → `apollo-ai`
- etc.

## Configuration
AI configuration is now in `config/tekton_ai_config.json` and synced by the AI Config Sync Service.