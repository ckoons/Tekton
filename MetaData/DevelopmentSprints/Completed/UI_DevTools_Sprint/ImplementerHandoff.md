# UI DevTools Sprint - Implementer Handoff

## Your Mission

You are the Implementation Claude for the UI_DevTools Sprint. The Architect Claude (at 29% context) has designed MCP tools to solve a critical problem: Claude keeps destroying UIs when trying to make simple changes. Casey has had to use `tekton-revert --nuclear-destruction` twice this week just from adding footer widgets.

## The Problem You're Solving

Currently, when working with UI:
- You can't see what you're changing
- You request 20 screenshots for simple tasks
- You add React/Vue/frameworks when asked to add 3 lines of HTML
- You refactor everything when asked to change one thing
- Casey's blood pressure is dangerously high

## What You're Building

Four MCP tools in Hephaestus that let Claude work with UI like backend code:

1. **ui_capture** - See UI state without screenshots
2. **ui_interact** - Click/type and see what happens
3. **ui_sandbox** - Test changes safely before applying
4. **ui_analyze** - Understand structure without guessing

## Resources & Documentation

### Must Read First:
1. **Sprint Documentation**:
   - `/MetaData/DevelopmentSprints/UI_DevTools_Sprint/README.md` - Overview
   - `/MetaData/DevelopmentSprints/UI_DevTools_Sprint/TechnicalImplementation.md` - Complete implementation details
   - `/MetaData/DevelopmentSprints/UI_DevTools_Sprint/SprintPlan.md` - Timeline and approach

2. **Tekton Standards**:
   - `/Tekton/.env.tekton` - Check port allocations (UI is 8080, suggest 8088 for MCP)
   - `/MetaData/TektonDocumentation/` - FastMCP setup and Hermes registration patterns
   - Look at Rhetor or Apollo's MCP implementation as examples

3. **Key Patterns**:
   - All Tekton UIs use simple HTML injection (NOT React/Vue)
   - Components share similar UI structure
   - MCP tools must register with Hermes

## Implementation Steps

### 1. Set Up MCP Structure
```bash
# Already created by Casey:
Hephaestus/hephaestus/
Hephaestus/hephaestus/mcp/
Hephaestus/hephaestus/__init__.py
Hephaestus/hephaestus/mcp/__init__.py

# You need to create:
Hephaestus/hephaestus/mcp/ui_tools.py
Hephaestus/hephaestus/mcp/mcp_server.py
Hephaestus/run_mcp.sh
```

### 2. Environment Setup
```bash
# Already installed:
- playwright (via command line)
- beautifulsoup4, lxml, cssselect (via uv)
- Playwright browsers (chromium)

# Already added to requirements.txt:
beautifulsoup4>=4.12.0
lxml>=5.0.0
cssselect>=1.2.0
```

### 3. Implement the Tools

Follow the detailed implementation in `TechnicalImplementation.md`. Key points:
- Use Playwright for browser automation
- Return structured data, not screenshots (unless specifically requested)
- Detect frameworks and PREVENT their addition
- Sandbox all changes before applying

### 4. Create MCP Server

Follow Tekton's FastMCP pattern:
- Register with Hermes on startup
- Provide health/ready endpoints
- Use port 8088 (or check .env.tekton)
- Create run_mcp.sh script

## Success Criteria

1. **Tools Work**: All 4 tools function as designed
2. **No Screenshots**: UI state captured as structured data
3. **Framework Detection**: Warns when detecting React/Vue/etc
4. **Safe Preview**: Changes tested before applying
5. **Hermes Integration**: MCP registered and discoverable
6. **Simple Test**: Can add a footer widget with 3 lines of HTML, not a framework

## Testing Your Implementation

Casey hasn't set up the Tekton MCP yet. To test:

1. **Start Hephaestus UI**: `./run_hephaestus.sh`
2. **Start your MCP server**: `./run_mcp.sh`
3. **Test directly**:
   ```python
   # Test the tools work
   result = await ui_capture("rhetor", "footer")
   print(result)  # Should show structured data, not image
   ```

4. **The Acid Test**: 
   - Task: "Add a timestamp to Rhetor's footer"
   - Success: Adds `<span id="timestamp">2024-06-12 17:45:00</span>`
   - Failure: Installs React

## Working with the Team

- **Architect Claude**: Has the vision and design (29% context)
- **You (Implementer)**: Fresh context for clean implementation
- **Casey**: Will test and provide feedback

## Important Reminders

1. **SIMPLE HTML ONLY** - These tools should PREVENT framework additions
2. **Structured data > Screenshots** - Save context
3. **Preview everything** - No surprises
4. **Follow existing patterns** - Check how other MCPs work
5. **Test the simple case** - Footer widget without destroying everything

## Your First Steps

1. Read all the documentation mentioned above
2. Look at existing MCP implementations (Rhetor, Apollo)
3. Start with ui_capture (most fundamental)
4. Build up from there
5. Test each tool thoroughly
6. Remember: You're building tools to PREVENT the very behavior Claude usually exhibits

Good luck! Casey's sanity (and the retirement of `--nuclear-destruction`) depends on this!