# Ergon Quick Reference

## Component Overview

Ergon is Tekton's container management platform with three main systems:
1. **Registry**: Store and manage deployable solutions
2. **Sandbox**: Test solutions in isolated environments  
3. **Construct**: Build new solutions from Registry components (coming in Phase 2)

## Quick Start

### Testing a Solution from UI
1. Navigate to Ergon → Registry tab
2. Click "Test" button on any solution card
3. Watch real-time output in sandbox panel
4. Review results when complete

### Adding a Solution via API
```bash
curl -X POST http://localhost:8102/api/ergon/registry/store \
  -H "Content-Type: application/json" \
  -d '{
    "type": "solution",
    "name": "My Tool",
    "version": "1.0.0",
    "content": {
      "description": "A helpful tool",
      "code": "print(\"Hello World\")",
      "main_file": "tool.py"
    }
  }'
```

### Testing via API
```bash
# Start test
curl -X POST http://localhost:8102/api/ergon/sandbox/test \
  -H "Content-Type: application/json" \
  -d '{"solution_id": "abc123"}'

# Returns: {"sandbox_id": "xyz789"}

# Get results
curl http://localhost:8102/api/ergon/sandbox/results/xyz789
```

## File Locations

### Core Files
- **Registry Storage**: `ergon/registry/storage.py`
- **Sandbox Runner**: `ergon/sandbox/runner.py`
- **API Endpoints**: `ergon/api/registry.py`, `ergon/api/sandbox.py`
- **UI Components**: `Hephaestus/ui/components/ergon/ergon-component.html`
- **JavaScript**: `Hephaestus/ui/scripts/ergon/*.js`

### Data Storage
- **Registry Database**: `.tekton/data/ergon/registry.db`
- **Sandbox Temp Files**: `/tmp/ergon-sandbox-*`
- **Standards Document**: `standards/tekton_ergon_standards.json`

## Key APIs

### Registry
- `POST /api/ergon/registry/store` - Add new solution
- `GET /api/ergon/registry/search` - Search solutions
- `GET /api/ergon/registry/{id}` - Get specific solution
- `POST /api/ergon/registry/import-completed` - Import from TektonCore

### Sandbox  
- `POST /api/ergon/sandbox/test` - Start test
- `POST /api/ergon/sandbox/execute` - Run command
- `GET /api/ergon/sandbox/results/{id}` - Get results
- `DELETE /api/ergon/sandbox/{id}` - Clean up
- `GET /api/ergon/sandbox/health` - Check providers

## Solution Schema

### Minimal Solution
```json
{
  "type": "solution",
  "name": "My Solution",
  "content": {
    "code": "print('Hello')"
  }
}
```

### Full Solution
```json
{
  "type": "solution",
  "name": "My Solution",
  "version": "1.0.0",
  "content": {
    "description": "Does something useful",
    "code": "import sys\n...",
    "main_file": "main.py",
    "requirements": ["requests>=2.28.0"],
    "run_command": ["python", "main.py"],
    "requires_network": true,
    "memory_limit": "2g",
    "environment": {
      "API_KEY": "${MY_API_KEY}"
    }
  }
}
```

## Sandbox Providers

### macOS (sandbox-exec)
- Lightweight filesystem isolation
- Network access allowed
- Best for simple scripts
- No Docker required

### Docker
- Full container isolation
- Resource limits enforced
- GPU support available
- Any base image

### Provider Selection
```python
# Auto-select best provider
POST /api/ergon/sandbox/test
{"solution_id": "abc123"}

# Force specific provider
POST /api/ergon/sandbox/test
{"solution_id": "abc123", "provider": "docker"}
```

## UI Components

### Registry Tab
- Browse all solutions
- Filter by type
- Search by name
- Standards badges
- Test/Details/Check buttons

### Sandbox Output Panel
- Real-time log streaming
- Color-coded output
- Stop/Clear/Close controls
- Execution metrics

## Common Tasks

### Import from TektonCore
```javascript
// Click button in UI
document.getElementById('check-completed-projects').click()

// Or via API
fetch('/api/ergon/registry/import-completed', {method: 'POST'})
```

### Check Standards Compliance
```python
# Check specific solution
POST /api/ergon/registry/{id}/check-standards

# Response
{
  "meets_standards": true,
  "score": 85,
  "issues": ["Missing tests", "No documentation"]
}
```

### Stream Sandbox Output
```javascript
// Server-Sent Events
const eventSource = new EventSource('/api/ergon/sandbox/execute?sandbox_id=xyz');
eventSource.onmessage = (e) => {
  const data = JSON.parse(e.data);
  console.log(data.line);
};

// WebSocket
const ws = new WebSocket('ws://localhost:8102/api/ergon/sandbox/ws/xyz');
ws.onmessage = (e) => {
  const data = JSON.parse(e.data);
  console.log(data.line);
};
```

## Environment Variables

- `ERGON_PORT` - API port (default: 8102)
- `ERGON_LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)
- `ERGON_SANDBOX_PROVIDER` - Force provider (sandbox-exec, docker)
- `ERGON_MAX_SANDBOXES` - Concurrent limit (default: 10)

## Debugging

### Check Component Status
```bash
# Registry health
curl http://localhost:8102/api/ergon/registry/health

# Sandbox providers
curl http://localhost:8102/api/ergon/sandbox/providers

# Active sandboxes
curl http://localhost:8102/api/ergon/sandbox/active
```

### View Logs
```bash
# Ergon logs
tail -f logs/ergon.log

# Sandbox output
ls -la /tmp/ergon-sandbox-*/output/
```

### Database Queries
```bash
sqlite3 .tekton/data/ergon/registry.db
> SELECT id, name, type, meets_standards FROM registry;
> SELECT COUNT(*) FROM registry WHERE meets_standards = 1;
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No sandbox provider available" | Install Docker or check sandbox-exec (macOS) |
| "Solution not found" | Verify ID, check if deleted, search by name |
| "Maximum sandboxes reached" | Clean up with `/api/ergon/sandbox/cleanup-all` |
| "Import failed" | Check TektonCore connection and project status |
| "Test button not working" | Check browser console, verify Ergon is running |

## Casey Method Principles

The implementation follows Casey's principles:
- **Simple**: Clear APIs, obvious workflows
- **Works**: Reliable storage, predictable behavior
- **Hard to screw up**: Validation, safe defaults, clear errors

## Phase Roadmap

- ✅ **Phase 0**: Clean up and move Analyzer to TektonCore
- ✅ **Phase 1**: Registry system with storage and API
- ✅ **Phase 1.5**: Sandbox testing environment
- ⏳ **Phase 2**: Construct system for solution assembly
- ⏳ **Phase 3**: Refine/Refactor engine for standards