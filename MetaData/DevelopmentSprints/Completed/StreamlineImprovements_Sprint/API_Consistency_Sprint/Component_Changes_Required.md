# API Consistency Sprint - Component Changes Required

## Overview

This document identifies the specific changes required for each Tekton component to achieve API consistency according to the defined standards.

## Summary of Required Changes

### Universal Changes (All Components)

1. **Version Standardization**: Update all components to version "0.1.0"
2. **Ready Endpoint**: Add `/ready` endpoint for startup readiness
3. **API Versioning**: Change business endpoints from `/api/*` or `/*` to `/api/v1/*`
4. **Service Discovery**: Add `/api/v1/discovery` endpoint
5. **OpenAPI URLs**: Update docs to `/api/v1/docs` and `/api/v1/openapi.json`

## Component-Specific Changes

### Apollo (Port 8000)
**Current Version**: 0.1.0 ✅
**Current Structure**: Well-organized with `/api` prefix

**Required Changes**:
- [ ] Add `/ready` endpoint
- [ ] Change `/api/*` routes to `/api/v1/*`
- [ ] Add `/api/v1/discovery` endpoint
- [ ] Update OpenAPI URLs to versioned paths

**Files to Modify**:
- `apollo/api/app.py` - Update router prefixes
- `apollo/api/routes.py` - Add ready and discovery endpoints

### Athena (Port 8001)
**Current Version**: 1.0.0 ❌ (should be 0.1.0)
**Current Structure**: No API prefix on business routers

**Required Changes**:
- [ ] Change version from "1.0.0" to "0.1.0"
- [ ] Add `/ready` endpoint
- [ ] Add `/api/v1/` prefix to knowledge, entities, and query routers
- [ ] Add `/api/v1/discovery` endpoint
- [ ] Update OpenAPI URLs

**Files to Modify**:
- `athena/api/app.py` - Update version and add API prefix
- `athena/api/knowledge_routes.py` - Update router prefix
- `athena/api/entity_routes.py` - Update router prefix
- `athena/api/query_routes.py` - Update router prefix

### Budget (Port 8002)
**Current Version**: 0.1.0 ✅
**Current Structure**: No API prefix on business routers

**Required Changes**:
- [ ] Add `/ready` endpoint
- [ ] Add `/api/v1/` prefix to budget, assistant routers
- [ ] Add `/api/v1/discovery` endpoint
- [ ] Update OpenAPI URLs

**Files to Modify**:
- `budget/api/app.py` - Add API versioning
- `budget/api/endpoints.py` - Update router configuration
- `budget/api/assistant_endpoints.py` - Update router configuration

### Engram (Port 8004)
**Current Version**: Not defined ❌
**Current Structure**: Basic, no structured routers

**Required Changes**:
- [ ] Add version "0.1.0"
- [ ] Add `/ready` endpoint
- [ ] Create proper router structure with `/api/v1/` prefix
- [ ] Add `/api/v1/discovery` endpoint
- [ ] Update OpenAPI URLs

**Files to Modify**:
- `engram/api/app.py` - Add version and restructure
- Create new router files for better organization

### Ergon (Port 8005)
**Current Version**: 0.1.0 ✅
**Current Structure**: Basic structure without API prefix

**Required Changes**:
- [ ] Add `/ready` endpoint
- [ ] Add `/api/v1/` prefix for business endpoints
- [ ] Add `/api/v1/discovery` endpoint
- [ ] Update OpenAPI URLs

**Files to Modify**:
- `ergon/api/app.py` - Add API versioning
- `ergon/api/a2a_endpoints.py` - Update router prefix

### Harmonia (Port 8006)
**Current Version**: 0.1.0 ✅
**Current Structure**: Good structure with `/api` prefix

**Required Changes**:
- [ ] Add `/ready` endpoint
- [ ] Change `/api/*` to `/api/v1/*`
- [ ] Add `/api/v1/discovery` endpoint
- [ ] Update OpenAPI URLs

**Files to Modify**:
- `harmonia/api/app.py` - Update API prefix to include version

### Hermes (Port 8001)
**Current Version**: 0.1.0 ✅
**Current Structure**: Multiple routers without API prefix

**Required Changes**:
- [ ] Add `/ready` endpoint
- [ ] Add `/api/v1/` prefix to database, llm, a2a routers
- [ ] Add `/api/v1/discovery` endpoint
- [ ] Update OpenAPI URLs

**Files to Modify**:
- `hermes/api/app.py` - Add API versioning
- `hermes/api/database_endpoints.py` - Update prefix
- `hermes/api/llm_endpoints.py` - Update prefix
- `hermes/api/a2a_endpoints.py` - Update prefix

### Metis (Port 8011)
**Current Version**: 0.1.0 ✅
**Current Structure**: Basic structure

**Required Changes**:
- [ ] Add `/ready` endpoint
- [ ] Create proper router structure with `/api/v1/` prefix
- [ ] Add `/api/v1/discovery` endpoint
- [ ] Update OpenAPI URLs

**Files to Modify**:
- `metis/api/app.py` - Add structured routers and API versioning

### Prometheus (Port 8007)
**Current Version**: 0.1.0 ✅
**Current Structure**: Has `/api` prefix

**Required Changes**:
- [ ] Add `/ready` endpoint
- [ ] Change `/api/*` to `/api/v1/*`
- [ ] Add `/api/v1/discovery` endpoint
- [ ] Update OpenAPI URLs

**Files to Modify**:
- `prometheus/api/app.py` - Update API prefix

### Rhetor (Port 8003)
**Current Version**: 1.0.0 ❌ (should be 0.1.0)
**Current Structure**: Many direct app routes

**Required Changes**:
- [ ] Change version from "1.0.0" to "0.1.0"
- [ ] Add `/ready` endpoint
- [ ] Consolidate routes into organized routers with `/api/v1/` prefix
- [ ] Add `/api/v1/discovery` endpoint
- [ ] Update OpenAPI URLs

**Files to Modify**:
- `rhetor/api/app.py` - Major restructuring needed
- Create new router files for better organization

### Sophia (Port 8010)
**Current Version**: 0.1.0 ✅
**Current Structure**: Has `/api` prefix

**Required Changes**:
- [ ] Add `/ready` endpoint
- [ ] Change `/api/*` to `/api/v1/*`
- [ ] Add `/api/v1/discovery` endpoint
- [ ] Update OpenAPI URLs

**Files to Modify**:
- `sophia/api/app.py` - Update API prefix

### Synthesis (Port 8009)
**Current Version**: 1.0.0 ❌ (should be 0.1.0)
**Current Structure**: Good structure with `/api` prefix

**Required Changes**:
- [ ] Change version from "1.0.0" to "0.1.0"
- [ ] Add `/ready` endpoint
- [ ] Change `/api/*` to `/api/v1/*`
- [ ] Add `/api/v1/discovery` endpoint
- [ ] Update OpenAPI URLs

**Files to Modify**:
- `synthesis/api/app.py` - Update version and API prefix

### Telos (Port 8012)
**Current Version**: Not defined ❌
**Current Structure**: Basic structure

**Required Changes**:
- [ ] Add version "0.1.0"
- [ ] Add `/ready` endpoint
- [ ] Create proper router structure with `/api/v1/` prefix
- [ ] Add `/api/v1/discovery` endpoint
- [ ] Update OpenAPI URLs

**Files to Modify**:
- `telos/api/app.py` - Add version and restructure

## Implementation Priority

### High Priority (Version fixes and missing versions)
1. Athena - Change version to 0.1.0
2. Rhetor - Change version to 0.1.0
3. Synthesis - Change version to 0.1.0
4. Engram - Add version 0.1.0
5. Telos - Add version 0.1.0

### Medium Priority (Well-structured components)
1. Apollo - Already well-structured, just needs versioning
2. Harmonia - Good structure, easy to update
3. Prometheus - Simple update needed
4. Sophia - Simple update needed

### Lower Priority (Need restructuring)
1. Budget - Needs API prefix addition
2. Ergon - Needs API organization
3. Hermes - Central hub, needs careful updates
4. Metis - Needs router structure

## Testing Strategy

After each component update:
1. Test with `tekton-launch [component]`
2. Verify health endpoint: `curl http://localhost:[port]/health`
3. Verify ready endpoint: `curl http://localhost:[port]/ready`
4. Check API docs: `http://localhost:[port]/api/v1/docs`
5. Test discovery: `curl http://localhost:[port]/api/v1/discovery`
6. Verify with `tekton-status`
7. Clean shutdown with `tekton-kill`

## Notes

- DO NOT modify MCP endpoints (leave for YetAnotherMCP_Sprint)
- DO NOT break existing functionality
- FOCUS on API consistency and standardization
- TEST thoroughly after each change