# UI DevTools Phase 2-4 Handoff Document

## Current Status

**Phase 1: COMPLETE** ✅
- `ui_recommend_approach` - Intelligent tool routing works perfectly
- Dynamic content detection works
- Enhanced error messages work
- All Phase 1 tests pass when MCP server is running

**Phase 2: BROKEN** ❌
- `ui_semantic_analysis` - Has a `'str' object has no attribute 'keys'` error
- The error occurs in `_analyze_semantic_gaps` function
- Even with function disabled, MCP server crashes
- Browser initialization may be interfering

## Critical Issues

### 1. MCP Server Won't Stay Running
- Server starts successfully
- Dies after browser initialization or first health check
- Casey disabled browser init but server still crashes
- Need to completely remove Phase 2 code, not just disable

### 2. File Too Large (2600+ lines)
- `ui_tools_v2.py` violates 500-line guideline
- Makes debugging nearly impossible
- Casey wants it broken into 5-6 separate programs

### 3. No Lambdas!
- Casey (C engineer, 26 languages) says lambdas are hard to debug
- Replace ALL lambdas with proper functions
- Real functions can have logging and error handling

## What You Need to Do

### Step 1: Verify Clean State
1. Start fresh - ensure MCP server runs WITHOUT Phase 2
2. Test that Phase 1 tools work:
   ```bash
   curl http://localhost:8088/health
   curl -X POST http://localhost:8088/api/mcp/v2/execute -H "Content-Type: application/json" -d '{"tool_name":"ui_recommend_approach","arguments":{"target_description":"navigation","intended_change":"modify","area":"navigation"}}'
   ```

### Step 2: Refactor Into Smaller Files
Casey wants this structure:
- `mcp_server.py` - Just the FastAPI server (~200 lines)
- `ui_capture_tool.py` - Capture functionality only
- `ui_sandbox_tool.py` - Sandbox operations only
- `semantic_analyzer.py` - Phase 2 semantic analysis
- `browser_service.py` - Shared browser management
- `tool_router.py` - Maps tool names to programs

Each file should be ~200-300 lines MAX!

### Step 3: Fix Phase 2 Bug
The error is in the BeautifulSoup attribute handling:
```python
# This breaks:
soup.find_all(attrs=lambda x: any(k.startswith('data-tekton-') for k in x.keys()) if x and hasattr(x, 'keys') else False)
```

Replace with simple, debuggable code:
```python
def has_tekton_attrs(tag):
    if not tag.attrs:
        return False
    return any(attr.startswith('data-tekton-') for attr in tag.attrs.keys())

soup.find_all(has_tekton_attrs)
```

### Step 4: Phase 2 Requirements
- Scan component files on disk (NO BROWSER)
- Identify semantic gaps in HTML files
- Score semantic completeness (0.0 to 1.0)
- Only test on 'rhetor' component initially
- Must work without browser!

## Casey's Preferences
- Simple, readable code over clever solutions
- Explicit error handling with clear messages
- Small, focused functions that do one thing
- Test each component independently
- Always verify MCP server stays running

## Phase 3-4 Roadmap
**Phase 3**: Component architecture mapping
**Phase 4**: Predictive UI design (Noesis test)

## Key Files
- `/Users/cskoons/projects/github/Tekton/Hephaestus/hephaestus/mcp/ui_tools_v2.py` - Needs refactoring
- `/Users/cskoons/projects/github/Tekton/Hephaestus/hephaestus/mcp/mcp_server.py` - MCP server
- `/Users/cskoons/projects/github/Tekton/.tekton/logs/hephaestus_mcp.log` - Check for errors

## Testing Commands
```bash
# Start server
cd /Users/cskoons/projects/github/Tekton/Hephaestus && ./run_mcp.sh

# Check if running
ps aux | grep mcp_server
curl http://localhost:8088/health

# Stop server
pkill -f "mcp_server"
```

## Final Advice
1. Start by making sure EVERYTHING works without Phase 2
2. Refactor into small files BEFORE adding new features
3. No lambdas - Casey hates them
4. Test constantly - server must stay running
5. Casey is patient but wants working code

Good luck!