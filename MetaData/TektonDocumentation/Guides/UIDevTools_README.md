# UI DevTools Documentation

## Quick Navigation

**Start Here:**
- 🔧 **[UIDevToolsCookbook.md](UIDevToolsCookbook.md)** - Practical examples and patterns (START HERE)
- 📖 **[UIDevToolsReference.md](UIDevToolsReference.md)** - Complete API reference

**Related Documentation:**
- 🏷️ **[SemanticUINavigationGuide.md](../SemanticUINavigationGuide.md)** - Semantic tagging system

## Current Status

**Version:** 0.1.0  
**Port:** 8088  
**Status:** Active with known issues

### Known Major Issue
- **DynamicContentView Problem**: DevTools cannot see dynamically loaded component content
- **Workaround**: Edit component HTML files directly for structural changes
- **Details**: See UIDevToolsCookbook.md section on Known Issues

## Documentation Rules

⚠️ **NO NEW DOCUMENTATION WITHOUT CASEY'S APPROVAL**

All DevTools documentation has been consolidated from 33 files into these 2 core documents. Do not create new documentation files.

## Quick Start

```bash
# 1. Check if running
curl http://localhost:8088/health

# 2. Start if needed
cd $TEKTON_ROOT/Hephaestus && ./run_mcp.sh

# 3. Use Python (recommended)
# See UIDevToolsCookbook.md for examples
```

## For Claude Sessions

When working with Hephaestus UI, you MUST:
1. Read the UIDevToolsCookbook.md FIRST
2. Use DevTools for ALL UI work (no blind changes)
3. Always use preview mode before applying changes
4. Document known issues encountered

Remember: UI DevTools are MANDATORY for all Hephaestus UI work.