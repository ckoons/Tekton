# Sunset/Sunrise Test Suite

Comprehensive tests for the Apollo/Rhetor consciousness management system.

## Overview

These tests verify the complete sunset/sunrise workflow that maintains CI cognitive freshness through managed rest cycles.

## Test Files

- **`test_registry_sunset_sunrise.py`** - Core registry operations
  - Basic CRUD operations for sunset/sunrise state
  - Auto-detection of sunset responses
  - Thread safety with concurrent access
  - State persistence across restarts
  - Complete state machine flow

- **`test_sunset_sunrise_integration.py`** - Full system integration
  - Rhetor stress detection
  - Apollo whisper reception
  - Sunset triggering
  - Sunrise preparation
  - Claude integration points

- **`verify_sunset_sunrise.py`** - Status verification utility
  - Shows current sunset/sunrise states
  - Cleans up test data
  - Useful for debugging

- **`run_all_tests.py`** - Test runner
  - Runs all tests in sequence
  - Provides summary report
  - Exit code for CI/CD integration

## Running Tests

### Run All Tests
```bash
cd /path/to/Tekton
python tests/sunset_sunrise/run_all_tests.py
```

### Run Individual Tests
```bash
# Registry tests
python tests/sunset_sunrise/test_registry_sunset_sunrise.py

# Integration tests
python tests/sunset_sunrise/test_sunset_sunrise_integration.py

# Status verification
python tests/sunset_sunrise/verify_sunset_sunrise.py
```

## Test Coverage

The tests verify:

1. **Registry Operations**
   - Setting/getting next_prompt
   - Setting/getting sunrise_context
   - Clearing states
   - Auto-detection of sunset responses
   - Thread-safe concurrent access
   - Persistence to disk

2. **Integration Flow**
   - Stress detection by Rhetor
   - Whisper communication to Apollo
   - Sunset decision making
   - State transitions
   - Sunrise preparation
   - Return to normal state

3. **Claude Integration**
   - SUNSET_PROTOCOL detection
   - Pattern-based sunset detection
   - System prompt injection
   - --continue flag management

## Expected Output

All tests passing:
```
🎉 ALL SUNSET/SUNRISE TESTS PASSED! 🎉

The consciousness management system is fully operational:
  • Registry state management ✅
  • Apollo orchestration ✅
  • Rhetor monitoring ✅
  • Claude integration ✅
  • Thread safety ✅
  • Persistence ✅
```

## Implementation Files

The sunset/sunrise system consists of:

- **Registry**: `shared/aish/src/registry/ci_registry.py`
  - State management methods
  - Auto-detection logic

- **Apollo**: `Apollo/apollo/sunset_manager.py`
  - Whisper reception
  - Sunset triggering
  - Sunrise preparation

- **Rhetor**: `Rhetor/rhetor/core/stress_monitor.py`
  - Stress analysis
  - Mood detection
  - Whisper protocol

- **Integration**: `shared/ai/claude_handler.py`
  - Sunset/sunrise prompt handling
  - Claude command building

## Debugging

If tests fail, check:

1. **Registry State**: Run `verify_sunset_sunrise.py` to see current states
2. **Permissions**: Ensure write access to `.tekton/aish/ci-registry/`
3. **Imports**: Verify all modules are in PYTHONPATH
4. **Async Issues**: Check for hanging background tasks

## Architecture

The sunset/sunrise mechanism implements a sophisticated consciousness management system:

```
Rhetor (Observer) → Apollo (Conductor) → Registry (State) → Claude (Execution)
```

1. Rhetor monitors CI stress indicators
2. Apollo receives whispers and orchestrates
3. Registry maintains persistent state
4. Claude executes with special prompts

See `/MetaData/Documentation/Architecture/Apollo_Rhetor_Sunset_Sunrise_Architecture.md` for full details.