# Rhetor API Reorganization Plan

## Current State

Rhetor has many endpoints directly on the app object that need to be reorganized into the standard router structure.

## Reorganization Strategy

### Infrastructure Endpoints (Root Router - `/`)
- `GET /health` - Health check (needs update to use shared utility)
- `GET /ready` - Ready check (needs creation)
- `GET /` - Root info endpoint

### Business Endpoints (V1 Router - `/api/v1/`)

#### Provider Management
- `GET /api/v1/providers` - List available providers
- `POST /api/v1/provider` - Set active provider
- `GET /api/v1/provider/{provider_id}/models` - Get provider models

#### Message Processing
- `POST /api/v1/send` - Send message
- `POST /api/v1/chat` - Chat conversation
- `POST /api/v1/stream` - Stream response

#### Template Management
- `GET /api/v1/templates` - List templates
- `POST /api/v1/templates` - Create template
- `GET /api/v1/templates/{template_id}` - Get template
- `PUT /api/v1/templates/{template_id}` - Update template
- `DELETE /api/v1/templates/{template_id}` - Delete template
- `GET /api/v1/templates/{template_id}/versions` - List versions
- `POST /api/v1/templates/render` - Render template

#### Prompt Management  
- `GET /api/v1/prompts` - List prompts
- `POST /api/v1/prompts` - Create prompt
- `GET /api/v1/prompts/{prompt_id}` - Get prompt
- `PUT /api/v1/prompts/{prompt_id}` - Update prompt
- `DELETE /api/v1/prompts/{prompt_id}` - Delete prompt
- `POST /api/v1/prompts/compare` - Compare prompts

#### Context Management
- `GET /api/v1/contexts` - List contexts
- `GET /api/v1/contexts/{context_id}` - Get context
- `DELETE /api/v1/contexts/{context_id}` - Clear context

#### Budget Management
- `GET /api/v1/budget/usage` - Get usage
- `POST /api/v1/budget/limit` - Set budget limit
- `GET /api/v1/budget/limits` - Get budget limits
- `POST /api/v1/budget/policy` - Set enforcement policy

#### Discovery
- `GET /api/v1/discovery` - Service discovery

### WebSocket Endpoints (remain at root)
- `/ws` - WebSocket connection

### MCP Endpoints (remain as-is)
- `/api/mcp/v2/*` - MCP endpoints (handled in YetAnotherMCP_Sprint)

## Implementation Approach

Due to the large number of endpoints, I recommend:

1. Create separate router files for each domain:
   - `provider_routes.py`
   - `message_routes.py`
   - `template_routes.py`
   - `prompt_routes.py`
   - `context_routes.py`
   - `budget_routes.py`

2. Move endpoints incrementally to avoid breaking functionality

3. Test thoroughly after each move

This would be a significant refactoring that might be better suited for a dedicated sprint.