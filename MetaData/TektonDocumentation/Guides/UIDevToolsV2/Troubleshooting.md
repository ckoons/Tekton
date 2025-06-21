# UI DevTools V2 Troubleshooting Guide

## Common Issues and Solutions

### "Cannot connect to MCP server"

**Symptom**: Tools fail with connection errors

**Solution**:
```bash
# Check if MCP is running
curl http://localhost:8088/health

# If not, start it
cd /Users/cskoons/projects/github/Tekton/Hephaestus
./run_mcp.sh
```

### "Component not found"

**Symptom**: CodeReader reports component doesn't exist

**Solutions**:
1. Check component name spelling
2. List available components:
   ```python
   result = code_reader.list_components()
   print(result.data['components'])
   ```
3. Verify path: Components should be in `ui/components/{name}/{name}-component.html`

### "Browser has 0 tags"

**Symptom**: BrowserVerifier finds no semantic tags

**Solutions**:
1. Ensure Hephaestus UI is running (`http://localhost:8080`)
2. Check if component loaded:
   ```python
   result = await navigator.navigate_to_component("rhetor")
   print(result.data['component_ready'])
   ```
3. Wait for component to fully load before checking

### "Playwright errors"

**Symptom**: Browser automation failures

**Solutions**:
1. Install playwright browsers:
   ```bash
   playwright install chromium
   ```
2. Check for headless compatibility:
   ```python
   # Browser runs headless by default
   # If issues persist, try visible mode for debugging
   ```

### "Changes not applying"

**Symptom**: SafeTester preview works but changes don't apply

**Solutions**:
1. Check selector specificity - too broad selectors are rejected
2. Verify element exists:
   ```python
   result = await safe_tester.preview_change("rhetor", changes)
   print(result.data['preview_results'])
   ```
3. Look for validation errors in the preview

### "Import errors"

**Symptom**: Cannot import ui_dev_tools modules

**Solutions**:
1. Ensure you're in the right directory:
   ```python
   import sys
   sys.path.append('/Users/cskoons/projects/github/Tekton/Hephaestus')
   from ui_dev_tools.tools.code_reader import CodeReader
   ```
2. Check Python version (requires 3.8+)

### "Async/await errors"

**Symptom**: "object is not awaitable" or similar

**Solutions**:
1. Remember which tools are async:
   - **Sync**: CodeReader (all methods)
   - **Async**: BrowserVerifier, Comparator, Navigator, SafeTester
2. Use proper async context:
   ```python
   import asyncio
   
   async def main():
       result = await browser_verifier.verify_component_loaded("rhetor")
       print(result.status)
   
   asyncio.run(main())
   ```

### "Too many/few tags reported"

**Symptom**: Tag counts seem wrong

**Understanding**:
- Source tags (CodeReader): What YOU wrote
- Browser tags (BrowserVerifier): What's RUNNING
- Difference is NORMAL - browser adds dynamic tags

**Verification**:
```python
# Use Comparator to understand
result = await comparator.compare_component("rhetor")
print(result.data['insights'])
```

### "Component not navigating"

**Symptom**: Navigator reports success but component doesn't appear

**Solutions**:
1. Check current component first:
   ```python
   result = await navigator.get_current_component()
   print(result.data['current_component'])
   ```
2. Use wait_for_ready:
   ```python
   result = await navigator.navigate_to_component("rhetor", wait_for_ready=True)
   ```
3. Verify component is in navigation menu

### "Memory/resource issues"

**Symptom**: Browser processes accumulating

**Solutions**:
1. Always cleanup after use:
   ```python
   try:
       # Your code here
       result = await browser_verifier.verify_component_loaded("rhetor")
   finally:
       await browser_verifier.cleanup()
   ```
2. Use context managers when available
3. Don't create multiple browser instances

## Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.INFO)

# Now tools will log detailed information
```

## Getting Help

1. Check test files for examples:
   - `ui_dev_tools/tests/test_*.py`
   - `ui_dev_tools/try_*.py`

2. Review API Reference:
   - `/MetaData/TektonDocumentation/Guides/UIDevToolsV2/APIReference.md`

3. Look at the source:
   - Tool implementations in `ui_dev_tools/tools/`
   - Core utilities in `ui_dev_tools/core/`

## Remember

The tools are designed to reveal that components work correctly:
- 75 tags in source ✓ (your design)
- 146 tags in browser ✓ (enriched with functionality)
- 0 missing static tags ✓ (all preserved)

If you see different numbers, use the Comparator to understand why!