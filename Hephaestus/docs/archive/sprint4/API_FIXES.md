# API Parameter Fixes

## Summary
Fixed incorrect API parameter usage in test files. The UI DevTools v2 uses 'area' parameter instead of 'component'.

## Files Fixed

### 1. test_ui_devtools.py
- Changed 4 occurrences of `"component": "rhetor"` to `"area": "rhetor"`
- Lines: 52, 90, 143, 199

### 2. test_ui_devtools_enhanced.py
- Changed 6 occurrences of component parameter to area:
  - Line 23: `"component": "invalid_component"` → `"area": "invalid_area"`
  - Line 63: `"component": component` → `"area": area`
  - Line 95: `"component": "rhetor"` → `"area": "rhetor"`
  - Line 122: `"component": "hermes"` → `"area": "hephaestus"`
  - Line 181: `"component": "rhetor"` → `"area": "rhetor"`
  - Line 234: `"component": component` → `"area": area`
- Changed loop variable from `component` to `area` on line 228

## Correct API Usage

### ❌ Wrong (old API):
```python
{
    "tool_name": "ui_capture",
    "arguments": {
        "component": "rhetor"  # WRONG
    }
}
```

### ✅ Correct (v2 API):
```python
{
    "tool_name": "ui_capture", 
    "arguments": {
        "area": "rhetor"  # CORRECT
    }
}
```

## Valid Areas
- `hephaestus` - The main UI container
- `rhetor` - LLM component area
- `hermes` - Messaging area
- `athena` - Knowledge base area
- `navigation` - Navigation sidebar
- `content` - Main content area
- `panel` - Right panel area

## Note
The remaining error in test_ui_devtools.py ("'str' object has no attribute 'keys'") appears to be a different issue, possibly related to the response format or parsing.