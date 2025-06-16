# Starting the UI DevTools MCP

## IMPORTANT: The MCP Must Be Running First!

The UI DevTools MCP is NOT automatically started with Tekton. You must start it manually before using the tools.

## Quick Start

### 1. Check if MCP is Running
```bash
# Check if it's already running
curl http://localhost:8088/health

# If you get a connection error, it's NOT running
```

### 2. Start the MCP
```bash
# From the Hephaestus directory
cd /path/to/Tekton/Hephaestus
./run_mcp.sh

# Or from anywhere in Tekton
$TEKTON_ROOT/Hephaestus/run_mcp.sh
```

### 3. Verify It's Running
```bash
# Should return: {"status":"healthy","component":"hephaestus_ui_devtools","version":"0.1.0"}
curl http://localhost:8088/health

# Check registration with Hermes
curl http://localhost:8001/api/components | grep hephaestus_ui_devtools
```

## For Claude Code Sessions

When starting work on UI tasks, ALWAYS:

```python
# 1. First check if MCP is available
import httpx
import asyncio

async def check_mcp():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8088/health")
            if response.status_code == 200:
                print("✓ UI DevTools MCP is running")
                return True
    except:
        print("✗ UI DevTools MCP is NOT running")
        print("  Please run: ./Hephaestus/run_mcp.sh")
        return False

# Check before any UI work
if not await check_mcp():
    print("Cannot proceed without UI DevTools MCP")
    # Ask user to start it
```

## Running in Background

The MCP can run in the background:

```bash
# Start in background
nohup ./run_mcp.sh > mcp.log 2>&1 &

# Check the log
tail -f mcp.log

# Stop it later
pkill -f "hephaestus.mcp.mcp_server"
```

## Common Issues

### Port Already in Use
```bash
# Check what's using port 8088
lsof -i :8088

# Kill if needed
kill -9 <PID>
```

### MCP Fails to Start
```bash
# Check logs
cat $TEKTON_ROOT/.tekton/logs/hephaestus_mcp.log

# Common fixes:
# 1. Make sure Hephaestus UI is running first
# 2. Check Python dependencies: pip install playwright beautifulsoup4
# 3. Install Playwright browsers: playwright install chromium
```

## Integration with Tekton Startup

While the MCP isn't part of automatic Tekton startup, you can:

### Option 1: Add to Your Workflow
```bash
# Create a UI development startup script
#!/bin/bash
# start_ui_dev.sh

# Start necessary components
./run_hephaestus.sh
./Rhetor/run_rhetor.sh
./Hephaestus/run_mcp.sh

echo "UI Development environment ready!"
```

### Option 2: Add Check to Component Scripts
Add to any UI-related scripts:
```bash
# Check if MCP is needed
if [[ "$1" == "--with-ui-tools" ]]; then
    echo "Starting UI DevTools MCP..."
    $TEKTON_ROOT/Hephaestus/run_mcp.sh &
fi
```

## For New Claude Sessions

At the start of ANY UI work, Claude should:

1. **Check MCP Status**
   ```bash
   curl http://localhost:8088/health || echo "MCP not running - start with ./Hephaestus/run_mcp.sh"
   ```

2. **Start if Needed**
   ```bash
   # If not running
   cd $TEKTON_ROOT/Hephaestus && ./run_mcp.sh
   ```

3. **Wait for Ready**
   ```bash
   # Give it a few seconds to start
   sleep 5
   curl http://localhost:8088/health
   ```

## Remember

- The MCP is a SEPARATE service from Hephaestus UI
- It needs to be started MANUALLY for UI work
- It provides the tools to PREVENT framework installation
- Without it running, Claude might revert to bad habits (React, screenshots, etc.)

**Bottom Line**: No MCP = No UI DevTools = Risk of Nuclear Destruction