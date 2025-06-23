# UI DevTools Architecture

## Overview

The UI DevTools provide Claude with the ability to interact with Tekton's UI without screenshots or browser automation chaos. After a significant architectural discovery, the tools were redesigned (v2) to properly understand how Tekton's UI actually works.

## The Critical Insight: Hephaestus Contains Everything

### The Wrong Mental Model (v1)
```
❌ INCORRECT:
Apollo UI → http://localhost:8012
Rhetor UI → http://localhost:8003
Hermes UI → http://localhost:8001
```

### The Correct Mental Model (v2)
```
✅ CORRECT:
Hephaestus UI (http://localhost:8080)
├── Apollo Area (#apollo-chat-area)
├── Rhetor Area (#rhetor-chat-area)  
├── Hermes Area (#hermes-chat-area)
└── ... all other component areas
```

**Key Understanding**: Hephaestus is the single UI container. Components are not separate UIs - they are areas within Hephaestus.

## Architecture Components

### 1. Browser Management Layer
- Single browser instance for efficiency
- Targets Hephaestus UI at port 8080
- Maintains state across operations
- Auto-recovery on browser crashes

### 2. MCP Integration
- FastMCP server on port 8088
- Registered with Hermes for discovery
- HTTP API at `/api/mcp/v2/execute`
- Proper Tekton logging to `.tekton/logs/`

### 3. The Four Core Tools

#### ui_capture
- Extracts UI structure as data (not screenshots)
- Returns forms, inputs, buttons, links
- Efficient context usage

#### ui_sandbox  
- Tests changes in isolation
- Detects and rejects frameworks
- Preview mode by default
- Prevents "nuclear destruction" scenarios

#### ui_interact
- Clicks, types, selects elements
- Captures before/after states
- Shows what changed

#### ui_analyze
- Detects frameworks and complexity
- Provides recommendations
- Helps understand UI structure

### 4. Help System (v2)
- Built-in `ui_help()` function
- Topics: areas, selectors, frameworks, errors, tasks, architecture
- Embeds Casey's philosophy
- Teaches correct mental models

## Technical Stack

- **Playwright**: Browser automation (headless Chromium)
- **BeautifulSoup4**: HTML parsing and analysis
- **FastMCP**: Tool exposure and Hermes integration
- **httpx**: Async HTTP client

## Key Design Decisions

### 1. Area-Based Navigation
All tools use "area" parameter, not "component":
```python
# Correct
ui_capture(area="rhetor")

# Wrong (v1 thinking)
ui_capture(component="rhetor")
```

### 2. Framework Prevention
Aggressive detection and rejection of:
- React, Vue, Angular, Svelte
- npm, webpack, build systems
- Any complexity beyond simple HTML/CSS

### 3. Preview by Default
`ui_sandbox` defaults to preview mode to prevent accidents:
```python
ui_sandbox(area="rhetor", changes=[...], preview=True)
```

### 4. Structured Data Over Images
Returns parsed HTML structure, not screenshots:
- Reduces context usage
- Enables programmatic analysis
- Faster processing

## Integration Points

### With Hermes
- Registers as `hephaestus_ui_devtools`
- Provides tool discovery
- Heartbeat for health monitoring

### With Rhetor
- Can be used by AI specialists
- Enables UI automation in workflows

### With Future Training AI
- Help content provides knowledge base
- Architecture understanding built-in
- Error patterns documented

## Common Patterns

### Finding Component Areas
```python
# List all available areas
areas = await ui_capture(area="hephaestus", selector="[id$='-area']")

# Target specific component area
rhetor_ui = await ui_capture(area="rhetor")
```

### Safe UI Modifications
```python
# Always preview first
result = await ui_sandbox(
    area="rhetor",
    changes=[{
        "type": "html",
        "selector": "#footer",
        "content": "<span>Status: Active</span>",
        "action": "append"
    }],
    preview=True
)

# Apply if safe
if result["safe_to_apply"]:
    result = await ui_sandbox(..., preview=False)
```

## Error Prevention

The architecture prevents common Claude mistakes:
1. **Wrong Port Access**: Only targets 8080
2. **Framework Addition**: Detected and rejected
3. **Over-Engineering**: Simple HTML enforced
4. **Context Explosion**: Structured data, not images

## Future Evolution

The UI DevTools architecture supports:
- Additional tool methods
- Enhanced pattern detection  
- Integration with component AI specialists
- Automated UI testing capabilities

This architecture embodies Casey's philosophy: "Simple tools for simple tasks, preventing complex disasters."