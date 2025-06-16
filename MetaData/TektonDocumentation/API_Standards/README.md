# Tekton API Standards

This directory contains the official API standards and guidelines for all Tekton components, established during the API Consistency Sprint.

## Overview

All Tekton components must follow these API standards to ensure consistency, discoverability, and maintainability across the ecosystem.

## Documentation Structure

1. **[API_Design_Principles.md](./API_Design_Principles.md)** - Core principles and patterns
2. **[Endpoint_Standards.md](./Endpoint_Standards.md)** - Detailed endpoint requirements
3. **[Migration_Guide.md](./Migration_Guide.md)** - Guide for updating existing components
4. **[API_Testing_Guide.md](./API_Testing_Guide.md)** - Testing standards for APIs
5. **[OpenAPI_Standards.md](./OpenAPI_Standards.md)** - Documentation requirements
6. **[A2A_Protocol_API_Reference.md](./A2A_Protocol_API_Reference.md)** - A2A Protocol v0.2.1 API reference

## Quick Reference

### Component Version
All components must use version `"0.1.0"`

### Endpoint Structure
```
/                    # Root endpoint
/health              # Health check (infrastructure)
/ready               # Readiness check (infrastructure)
/status              # Status for tekton-status (infrastructure)
/shutdown            # Graceful shutdown (infrastructure)
/api/v1/             # All business logic endpoints
/api/v1/discovery    # Service discovery endpoint
/api/v1/docs         # OpenAPI documentation
/api/mcp/v2/         # MCP endpoints (unchanged)
```

### Required Imports
```python
from shared.api import (
    create_standard_routers,
    mount_standard_routers,
    create_ready_endpoint,
    create_discovery_endpoint,
    get_openapi_configuration,
    EndpointInfo
)
```

## Compliance Checklist

- [ ] Component version is "0.1.0"
- [ ] Uses shared API utilities
- [ ] Health endpoint returns standardized response
- [ ] Ready endpoint implemented
- [ ] Discovery endpoint lists all capabilities
- [ ] Business logic under /api/v1/
- [ ] MCP endpoints at /api/mcp/v2/
- [ ] OpenAPI docs at /api/v1/docs
- [ ] Uses standard routers pattern

## Implementation Status

As of the API Consistency Sprint completion:
- ✅ 13/13 components updated to new standards
- ✅ Shared API utilities created in `/Tekton/shared/api/`
- ✅ Documentation updated in Building_New_Tekton_Components
- ✅ Migration guides created

## Support

For questions about API standards:
1. Check the detailed guides in this directory
2. Review reference implementations (Athena, Apollo, Synthesis)
3. Consult the shared API example at `/Tekton/shared/api/example_usage.py`