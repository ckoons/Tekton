# UI DevTools Test Suite

## Overview

This test suite validates the Hephaestus UI DevTools MCP server functionality. It ensures all tools work correctly and handle errors gracefully.

## Test Structure

```
/Hephaestus/hephaestus/mcp/tests/
├── __init__.py           # Package marker
├── test_ui_tools.py      # Comprehensive pytest test suite
├── run_tests.py          # Simple standalone test runner
└── README.md             # This file
```

## Running Tests

### Quick Test (No Dependencies)
```bash
cd /Hephaestus/hephaestus/mcp/tests
python3 run_tests.py
```

### Full Test Suite (Requires pytest)
```bash
cd /Hephaestus/hephaestus/mcp/tests
pytest test_ui_tools.py -v
```

### Prerequisites
- MCP server must be running on port 8088
- Hephaestus UI must be accessible on port 8080

## What We Test

### Core Functionality
1. **ui_capture** - Captures UI structure without screenshots
2. **ui_navigate** - Navigates to components by clicking nav items
3. **ui_sandbox** - Tests UI changes in preview mode
4. **ui_validate** - Validates UI instrumentation quality
5. **ui_analyze** - Analyzes UI patterns and frameworks
6. **ui_interact** - Simulates user interactions

### Key Principles
- **No nav state dependency** - We only trust what's loaded in content area
- **Graceful error handling** - All errors return structured responses
- **Fast timeouts** - 2-second timeouts prevent hanging
- **Real browser testing** - Uses Playwright for actual UI interaction

## Test Categories

### Unit Tests
- Individual tool functionality
- Parameter validation
- Error handling

### Integration Tests
- Navigate → Capture workflow
- Capture → Modify → Validate workflow
- Multi-tool operations

### Performance Tests (Optional)
- Response time validation
- Timeout behavior
- Concurrent operations

## Design Decisions

1. **Simple test runner** - `run_tests.py` requires no dependencies beyond httpx
2. **Shared logging** - Tests use the MCP log for simplicity
3. **Actual UI interaction** - Tests run against real UI, not mocks
4. **Focus on reliability** - Tests what actually works, not theoretical behavior

## Common Issues and Solutions

### Tests Timing Out
- Check if UI is actually running on port 8080
- Verify MCP server is healthy
- Some components may not be implemented yet

### Navigation Not Working
- UI state may reset after navigation
- Some components load default views
- This is expected behavior - we validate what loads

### Validation Scores Low
- Components need semantic tagging
- This is what the instrumentation sprint will fix
- Low scores are expected for un-instrumented components

## Future Improvements

1. Add test data fixtures
2. Create mock UI for isolated testing
3. Add performance benchmarks
4. Implement continuous testing in CI/CD