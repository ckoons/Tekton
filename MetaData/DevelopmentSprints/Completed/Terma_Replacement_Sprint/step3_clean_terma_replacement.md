# Step 3: Clean Terma Replacement - COMPLETE ✅

## What We Built

A **complete replacement** for the old PTY-based Terma. The new Terma is a native terminal orchestrator that launches Terminal.app, iTerm2, Warp, etc. with aish-proxy for CI enhancement. 

**No web terminals. No backward compatibility. Clean slate.**

## Architecture

```
Terma v2.0 Service (Port 8004)
    │
    ├── /api/terminals/types      # List native terminals
    ├── /api/terminals/templates  # Configuration templates
    ├── /api/terminals/launch     # Launch native terminal
    ├── /api/terminals            # List active terminals
    ├── /api/terminals/{pid}      # Get/control specific terminal
    └── /api/terminals/ai-request # CI components request terminals
```

## Key Features

### 1. Native Terminal Only
- Launches real desktop terminals (Terminal.app, iTerm2, Warp)
- Uses aish-proxy as the shell for CI enhancement
- PID-based tracking and management
- Platform auto-detection (macOS/Linux)

### 2. Clean API Design
```python
# Launch a terminal
POST /api/terminals/launch
{
    "template": "ai_workspace",
    "purpose": "Debug the API server"
}

# Response
{
    "pid": 12345,
    "app": "Terminal.app",
    "status": "running",
    "launched_at": "2025-07-01T12:00:00"
}
```

### 3. CI Integration
Other Tekton components can request terminals:
```python
POST /api/terminals/ai-request
{
    "requester_id": "sophia-ai",
    "purpose": "Run training script",
    "working_dir": "/workspace"
}
```

### 4. Templates
Pre-configured terminal profiles:
- `default` - Basic aish terminal
- `development` - Dev environment with TEKTON_ROOT
- `ai_workspace` - AI-assisted development
- `data_science` - Jupyter/Python setup

## Implementation

### Service Structure
```
Tekton/Terma/
├── terma/
│   ├── api/
│   │   ├── terminal_service.py  # Clean FastAPI service
│   │   └── main.py              # Entry point
│   └── core/
│       ├── terminal_launcher.py     # Interface
│       └── terminal_launcher_impl.py # Implementation
└── run_terma_v2.sh              # Run script
```

### No Legacy Code
- **Removed**: All PTY session management
- **Removed**: WebSocket terminal connections
- **Removed**: Web-based terminal UI
- **Removed**: xterm.js and related dependencies

### Clean Dependencies
```python
# Only what we need
fastapi
uvicorn
pydantic
httpx  # For Hermes registration
```

## Running the New Terma

```bash
cd Tekton/Terma
./run_terma_v2.sh
```

Output:
```
🚀 Starting Terma v2 - Native Terminal Orchestrator
   This is the NEW Terma - no web terminals, just native!

Configuration:
  Port: 8004
  Hermes URL: http://localhost:8001
  Register with Hermes: true

✅ Found aish-proxy at /Users/cskoons/projects/github/aish/aish-proxy
```

## API Examples

### List Available Terminals
```bash
curl http://localhost:8004/api/terminals/types

[
  {
    "id": "Terminal.app",
    "display_name": "Terminal.app (native)",
    "is_default": true
  },
  {
    "id": "WarpPreview.app",
    "display_name": "WarpPreview.app (modern preview)",
    "is_default": false
  }
]
```

### Launch a Terminal
```bash
curl -X POST http://localhost:8004/api/terminals/launch \
  -H "Content-Type: application/json" \
  -d '{
    "template": "development",
    "purpose": "Work on Tekton UI"
  }'

{
  "pid": 45678,
  "app": "Terminal.app",
  "status": "running",
  "launched_at": "2025-07-01T12:30:00",
  "purpose": "Work on Tekton UI"
}
```

### List Active Terminals
```bash
curl http://localhost:8004/api/terminals

{
  "terminals": [
    {
      "pid": 45678,
      "app": "Terminal.app",
      "status": "running",
      "launched_at": "2025-07-01T12:30:00",
      "purpose": "Work on Tekton UI"
    }
  ],
  "count": 1
}
```

## Next Steps: UI Integration

The Hephaestus UI needs to be updated to:

1. **Remove** all web terminal UI code
2. **Add** native terminal launcher UI:
   - Terminal type selector
   - Template chooser
   - Purpose/context input
   - Launch button
3. **Add** terminal dashboard:
   - List active terminals
   - Show/hide terminals (macOS)
   - Terminate terminals

## Benefits of Clean Replacement

1. **Simplicity**: No complex PTY management
2. **Native Experience**: Users get their preferred terminal
3. **CI Integration**: Transparent aish enhancement
4. **Maintainability**: Much less code to maintain
5. **Performance**: No web terminal overhead

---

## Status: ✅ COMPLETE - Ready for UI

The clean Terma replacement is ready:

1. ✅ **Complete replacement** - No legacy code
2. ✅ **Native terminals only** - Real desktop applications
3. ✅ **Clean API** - Simple REST endpoints
4. ✅ **CI ready** - aish-proxy integration
5. ✅ **Tekton integrated** - Hermes registration, standard patterns

**The old Terma is dead. Long live the new Terma!**

Ready for Step 4: Hephaestus UI update to use the new native terminal orchestrator.