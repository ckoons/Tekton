# Athena Backend Routing Issue

## Problem
The Athena backend is running on port 8105 and health check works, but API endpoints return 404:
- `/api/v1/entities` - 404 Not Found
- `/api/v1/visualization/graph` - 404 Not Found
- Even root `/` returns 404

## Discovery
The `/api/v1/discovery` endpoint lists the correct routes, but they're not accessible.

## Suspected Cause
The standard router mounting in `athena/api/app.py` may have an issue with the path prefixes.

## Temporary Solution
Created `athena-service-mock.js` with mock data so UI development can continue.

## Fix Required
1. Debug why routes aren't accessible
2. Check mount_standard_routers implementation
3. Verify path prefixes are correct
4. Remove mock service once fixed

## Test Commands
```bash
# These should work but currently return 404:
curl http://localhost:8105/api/v1/entities
curl http://localhost:8105/api/v1/visualization/graph
```