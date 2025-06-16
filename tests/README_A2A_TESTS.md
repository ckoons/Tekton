# A2A Protocol Test Suite

This document describes the comprehensive test suite for the Tekton A2A Protocol v0.2.1 implementation.

## Test Runner

The main test runner is `run_a2a_all_tests.py` which provides a unified interface for all A2A tests.

### Usage

```bash
# Run all tests
./run_a2a_all_tests.py

# Run specific test categories
./run_a2a_all_tests.py --unit        # Unit tests only
./run_a2a_all_tests.py --integration # Integration tests only
./run_a2a_all_tests.py --manual      # Manual API tests only
./run_a2a_all_tests.py --streaming   # Streaming tests only (unit + integration)

# Short forms
./run_a2a_all_tests.py -u  # Unit tests
./run_a2a_all_tests.py -i  # Integration tests
./run_a2a_all_tests.py -m  # Manual tests
./run_a2a_all_tests.py -s  # Streaming tests
```

## Test Categories

### Unit Tests (No External Dependencies)

1. **JSON-RPC** (`test_jsonrpc_messages.py`)
   - JSON-RPC 2.0 message parsing and validation
   - Request/response formatting
   - Batch request handling
   - Error response generation

2. **Agent Cards** (`test_agent_cards.py`)
   - Agent Card creation and validation
   - Agent Registry operations
   - Agent status management
   - Heartbeat tracking

3. **Task Lifecycle** (`test_task_lifecycle.py`)
   - Task state transitions
   - Progress tracking
   - Task assignment and completion
   - Event emission

4. **Discovery** (`test_discovery.py`)
   - Agent discovery by capability
   - Method-based agent lookup
   - Query filtering

5. **SSE Streaming** (`test_streaming.py`)
   - SSE event formatting
   - Connection management
   - Event filtering
   - Subscription management

### Integration Tests (Requires Running Hermes)

1. **Hermes A2A** (`test_hermes_a2a_simple.py`)
   - Basic A2A protocol operations via Hermes
   - Agent registration and discovery
   - Task creation and management

2. **SSE Streaming** (`test_streaming_integration.py`)
   - End-to-end SSE streaming
   - Real-time event delivery
   - Connection filtering
   - Subscription CRUD operations

### Manual Tests

1. **Basic API Tests** (`test_a2a_manual.sh`)
   - Command-line based API testing
   - Useful for debugging and manual verification
   - Tests basic A2A protocol operations

2. **Security Tests** (`test_a2a_security.sh`)
   - Tests A2A security implementation comprehensively
   - Validates auth-exempt methods always work
   - When security is enabled:
     - Tests that protected methods fail without auth
     - Tests that protected methods work with auth headers
   - When security is disabled:
     - Tests that all methods work without auth
   - Adapts tests based on current .env.tekton setting

## Test Statistics

- **Total Test Files**: 7
- **Unit Test Suites**: 5
- **Integration Test Suites**: 2
- **Manual Test Scripts**: 2 (basic + security)

### Coverage

- **Core Protocol**: 100% coverage
- **Streaming**: 100% unit test coverage
- **Integration**: Requires running Hermes

## Running Streaming Tests

For focused streaming testing:

```bash
# Run only streaming tests
./run_a2a_all_tests.py -s

# Manual SSE testing
python tests/manual/test_sse_complete.py
```

## Prerequisites

### For Unit Tests
- Python 3.8+
- pytest
- pytest-asyncio

### For Integration Tests
- Hermes running on port 8001
- Updated with latest A2A code

### For Manual Tests
- curl or httpie
- jq (optional, for JSON formatting)

## Security Configuration

By default, the A2A service in Hermes enables security features that require authorization headers for most methods. For testing purposes, you can disable security by editing the `.env.tekton` file:

```bash
# Edit .env.tekton and set:
TEKTON_A2A_ENABLE_SECURITY=false

# Then restart Hermes normally:
./Hermes/run_hermes.sh
```

To re-enable security for production:
```bash
# Edit .env.tekton and set:
TEKTON_A2A_ENABLE_SECURITY=true
```

Methods that are exempt from authorization (even with security enabled):
- `agent.register`
- `discovery.capability_map`
- `discovery.find_for_capability`
- `discovery.query`
- `auth.login`
- `auth.refresh`

### Testing A2A Security

To validate the A2A security implementation:

```bash
# Test current security configuration
./tests/test_a2a_security.sh
```

This intelligent test script:
- Reads current security setting from .env.tekton
- Tests auth-exempt methods (should always work)
- When security is enabled:
  - Tests protected methods without auth (should fail)
  - Tests protected methods with auth headers (should succeed)
- When security is disabled:
  - Tests that all methods work without authentication

Expected behavior:
- **Security ENABLED**: Non-exempt methods require authentication
- **Security DISABLED**: All methods work without authentication  
- **Auth-exempt methods**: Always work regardless of security setting

## Troubleshooting

### Integration Tests Failing

1. **Ensure Hermes is running**:
   ```bash
   # Just run Hermes normally - it will read settings from .env.tekton
   ./Hermes/run_hermes.sh
   ```

2. **Check Hermes has latest code**:
   - Restart Hermes after code changes
   - Verify port 8001 is accessible

3. **SSE Streaming Issues**:
   - Check Hermes logs for errors
   - Verify SSE endpoints are registered
   - Use manual test scripts for debugging

4. **Authorization Errors**:
   - If you see "No authorization header provided" errors, restart Hermes with security disabled
   - For production testing, implement proper authentication using the auth.login method

### Common Issues

- **Import Errors**: Ensure PYTHONPATH includes project root
- **Timeout Errors**: SSE tests may timeout if no events are sent
- **Port Conflicts**: Ensure port 8001 is free for Hermes

## Adding New Tests

1. **Unit Tests**: Add to appropriate test file in `tests/unit/a2a/`
2. **Integration Tests**: Add to `tests/integration/a2a/`
3. **Update Test Runner**: Add new test files to `UNIT_TESTS` or `INTEGRATION_TESTS` in `run_a2a_all_tests.py`

## Continuous Integration

The test suite is designed to be CI-friendly:

```bash
# CI command
python tests/run_a2a_all_tests.py --unit

# Full test with services
docker-compose up -d hermes
python tests/run_a2a_all_tests.py
```