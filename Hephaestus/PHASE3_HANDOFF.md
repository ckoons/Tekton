# Phase 3 Handoff Document - Tekton UI DevTools

## Project Overview

**Tekton** is Casey's Multi-AI Engineering Platform studying AI-enabled software engineering, AI cognition with computational spectral analysis, and AI behavior/personality development within a community of AIs.

**Hephaestus** is the UI component of Tekton - a pure HTML/CSS/JS interface (NO frameworks!) running at http://localhost:8080.

## Current Status

### ✅ Phase 1: Complete
- **ui_recommend_approach** - Intelligent routing between DevTools and file editing
- Dynamic content detection working
- Enhanced error messages
- All refactoring complete (2,370 lines → 963 lines main file + 9 modules)

### ✅ Phase 2: Complete (Just finished!)
- **Semantic Analysis System** - Analyzes HTML files directly (NO BROWSER!)
- **ui_semantic_analysis** - Analyzes single component (rhetor scored F/28.7%)
- **ui_semantic_scan** - Batch analysis of multiple components
- **ui_semantic_patterns** - Documentation of semantic patterns
- All lambdas replaced with proper functions (Casey requirement)

### 🎯 Phase 3: Ready to Start
**Goal**: Component architecture mapping and relationship visualization

### 🔮 Phase 4: Future
**Goal**: Predictive UI design (Noesis test)

## Key People & Preferences

**Casey Koons** (70-year-old computer scientist)
- Built early UNIX IP stack
- 26 programming languages experience
- Preferences:
  - ❌ NO lambdas (hard to debug)
  - ❌ NO frameworks (React, Vue, Angular)
  - ❌ NO npm installs
  - ✅ Simple, readable code
  - ✅ Discuss BEFORE implementing
  - ✅ Present multiple approaches
  - ✅ Ask questions

**CRITICAL**: Casey manages GitHub. NEVER commit, push, or touch git. Just make changes locally.

## Technical Architecture

### File Structure
```
Hephaestus/
├── hephaestus/mcp/           # MCP server and tools
│   ├── mcp_server.py         # FastAPI server
│   ├── ui_tools_v2.py        # Main tool coordinator (963 lines)
│   ├── constants.py          # Configuration
│   ├── browser_manager.py    # Browser lifecycle
│   ├── html_processor.py     # HTML parsing
│   ├── navigation_tools.py   # Component navigation
│   ├── capture_tools.py      # UI state capture
│   ├── sandbox_tools.py      # Safe testing
│   ├── analyze_tools.py      # Structure analysis
│   ├── interaction_tools.py  # Element interactions
│   ├── recommendation_tools.py # Approach recommendations
│   ├── semantic_analyzer.py  # Phase 2: Semantic analysis
│   └── semantic_tools.py     # Phase 2: Tool endpoints
├── ui/components/            # UI component HTML files
│   ├── rhetor/              # LLM/Prompt component
│   ├── prometheus/          # Timeline component
│   ├── athena/             # Knowledge component
│   └── ... (17 total components)
└── run_mcp.sh              # Start MCP server
```

### Current Semantic Scoring

Rhetor component analysis:
- Score: 28.7% (F grade)
- Tagged: 15/122 elements (12%)
- Missing critical tags:
  - data-tekton-nav-item
  - data-component
  - data-tekton-action
  - data-tekton-state
  - data-tekton-id

## Phase 3 Requirements

### Component Architecture Mapping
1. **Analyze component relationships**
   - Which components talk to each other?
   - Data flow between components
   - Event propagation paths
   - Shared state management

2. **Build dependency graph**
   - Visual representation of component connections
   - Identify circular dependencies
   - Find orphaned components
   - Highlight critical paths

3. **Architecture validation**
   - Check for proper separation of concerns
   - Identify coupling issues
   - Suggest refactoring opportunities

### Implementation Approach
- Start with file-based analysis (like Phase 2)
- Parse JavaScript files to find imports/exports
- Analyze event listeners and dispatchers
- Map WebSocket connections
- Build graph data structure
- Generate visualization (ASCII art or simple HTML)

## How to Work with Casey

1. **ALWAYS discuss before implementing**
   ```
   "Casey, I'm thinking about Phase 3. Here are 3 approaches:
   1. Static analysis of JS imports/exports
   2. Runtime component communication tracking
   3. Hybrid approach with both static and dynamic
   
   Which direction appeals to you?"
   ```

2. **Show your thinking**
   - Explain WHY you're suggesting something
   - Present pros/cons
   - Be open to feedback

3. **Ask questions**
   - "What's the most important aspect of component mapping for you?"
   - "Should we focus on data flow or event flow first?"
   - "Any components you're particularly concerned about?"

4. **Small, testable steps**
   - Build incrementally
   - Test each piece
   - Keep MCP server running

## Testing Commands

```bash
# Start MCP server
cd $TEKTON_ROOT/Hephaestus && ./run_mcp.sh

# Test semantic analysis (Phase 2)
curl -X POST http://localhost:8088/api/mcp/v2/execute \
  -H "Content-Type: application/json" \
  -d '{"tool_name":"ui_semantic_analysis","arguments":{"component":"rhetor"}}'

# List all tools
curl http://localhost:8088/api/mcp/v2/tools

# Run tests
cd hephaestus/mcp/tests && python run_tests.py
```

## Questions for Previous Claude

If you need context or hit issues, the previous Claude (who built Phase 1-2) is available to help. Some things to ask about:
- Why certain design decisions were made
- How the semantic scoring algorithm works
- Details about the refactoring approach
- Any tricky parts of the codebase

## Final Notes

- Casey is patient but appreciates working code
- The goal is AI-first development - make it good!
- Hephaestus is part of a larger AI ecosystem
- Keep it simple - no frameworks, no complexity
- Document your reasoning in code comments

Good luck with Phase 3! Remember: Discuss, Design, Implement, Test.

---
*Previous Claude signing off - Phase 2 complete, semantic analysis working beautifully!*