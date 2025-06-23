# UI DevTools V2 - Quick Start Guide

Get up and running with the new UI DevTools in 5 minutes!

## Prerequisites

- Hephaestus repository cloned
- Python 3.8+ installed
- Hephaestus UI running (for browser verification)

## Step 1: Launch the DevTools (30 seconds)

```bash
cd /Users/cskoons/projects/github/Tekton/Hephaestus
./run_mcp.sh
```

You should see:
```
Starting Hephaestus UI DevTools MCP Server...
Port: 8088
Component: hephaestus_mcp
```

## Step 2: Try Your First Tool - CodeReader (1 minute)

In a new terminal:
```bash
cd /Users/cskoons/projects/github/Tekton/Hephaestus
python ui_dev_tools/try_code_reader.py
```

This shows you the TRUTH - what's in your source files:
- Lists all components
- Shows rhetor has 75 semantic tags
- Displays tag breakdown

Key insight: Your components ARE fully instrumented!

## Step 3: Compare Source vs Browser (2 minutes)

Make sure Hephaestus UI is running, then:
```bash
python ui_dev_tools/try_comparator.py
```

This reveals the magic:
```
Source code: 75 tags (what you wrote)
Browser DOM: 146 tags (what's running)
Difference: 71 additional tags added by the system!
```

## Step 4: Understand What You're Seeing (1 minute)

The 71 extra tags are FEATURES, not bugs:
- **Navigation tags** (nav-item, nav-target) - For UI routing
- **Loading tags** (loading-state, loading-component) - Track load progress
- **State tags** (state, active) - Runtime behavior

Your components work perfectly - the system enhances them!

## Step 5: Basic Workflow (30 seconds)

When debugging UI issues:

```python
# 1. Check source truth
from ui_dev_tools.tools.code_reader import CodeReader
reader = CodeReader()
result = reader.list_semantic_tags("rhetor")
if result.status == ToolStatus.SUCCESS:
    tags = result.data['semantic_tags']
    print(f"Source tags: {tags['total_count']}")
    print(f"Tag types: {', '.join(tags['summary']['tag_types'])}")

# 2. Verify browser result  
from ui_dev_tools.tools.browser_verifier import BrowserVerifier
verifier = BrowserVerifier()
result = await verifier.get_dom_semantic_tags("rhetor")
if result.status == ToolStatus.SUCCESS:
    tags = result.data['semantic_tags']
    print(f"Browser tags: {tags['total_count']}")
    print(f"Dynamic types: {', '.join(tags['found'])}")

# 3. Compare and understand
from ui_dev_tools.tools.comparator import Comparator
comparator = Comparator()
result = await comparator.compare_component("rhetor")
if result.status == ToolStatus.SUCCESS:
    summary = result.data['summary']
    print(f"Static tags preserved: {summary['static_tags_preserved']}")
    print(f"Dynamic tags added: {summary['dynamic_tags_added']}")
```

## Common Tasks

### "My component seems broken"
```bash
# First, check if it's really broken
python ui_dev_tools/try_comparator.py

# Look for:
# - "Missing from DOM: 0" (good - all source tags loaded)
# - Dynamic tags listed (normal system behavior)
```

### "I need to add semantic tags"
```bash
# First, verify they're not already there
python ui_dev_tools/try_code_reader.py

# You might discover the tags exist in source!
```

### "Something's not loading"
Check if static tags made it to DOM:
- If yes: Component loaded fine, might be a different issue
- If no: Check MinimalLoader and component pipeline

## Next Steps

1. Read [CorePhilosophy.md](CorePhilosophy.md) to understand the paradigm
2. Explore [StaticVsDynamicTags.md](StaticVsDynamicTags.md) for deep dive
3. Check [UIDevToolsCookbook.md](../UIDevToolsCookbook.md) for recipes

## Remember

> **Code is Truth, Browser is Result**

The browser having MORE tags than source is a FEATURE showing the system is working correctly!