# Workflow Handler Test Suite

This directory contains comprehensive tests for the Tekton workflow handler implementation.

## Test Files

1. **test_workflow_handler.py**
   - Core handler functionality tests
   - Message routing and action handling
   - Base class methods
   - Status tracking

2. **test_workflow_data.py**
   - Workflow data storage in `.tekton/workflows/data/`
   - Data size threshold handling (10KB)
   - Workflow ID generation
   - Import/export functionality
   - Backward compatibility

3. **test_component_integration.py**
   - Component-to-component handoffs
   - Full workflow pipeline tests
   - Error handling scenarios
   - Mock implementations of Metis and Harmonia

## Running Tests

### Run all tests:
```bash
./run_tests.py
```

### Run specific test file:
```bash
pytest test_workflow_handler.py -v
```

### Run with coverage:
```bash
pytest --cov=workflow_handler --cov-report=html
```

## Test Coverage

The test suite covers:

- ✅ Workflow message structure and routing
- ✅ Action handlers (look_for_work, process_sprint, etc.)
- ✅ Data storage and retrieval
- ✅ Embedded vs reference data handling
- ✅ Status updates in DAILY_LOG.md
- ✅ Backward compatibility with sprint directories
- ✅ Component handoff scenarios
- ✅ Error handling and edge cases
- ✅ Async operations

## Mock Components

The tests include mock implementations:
- **MockComponent**: Basic handler for unit tests
- **MetisHandler**: Simulates task breakdown
- **HarmoniaHandler**: Simulates workflow creation

## Environment Setup

Tests use temporary directories to avoid affecting real data:
- Creates temp `TEKTON_ROOT`
- Sets up sprint directories as needed
- Cleans up after each test

## Adding New Tests

When adding new workflow features:
1. Add unit tests to `test_workflow_handler.py`
2. Add data tests to `test_workflow_data.py`
3. Add integration tests to `test_component_integration.py`
4. Update this README with new coverage areas