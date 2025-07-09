# Metis Tests

This directory contains the test suite for the Metis component of Tekton.

## Test Structure

The test suite is organized as follows:

- `unit/`: Unit tests for individual components
  - `test_models.py`: Tests for data models
  - `test_task_manager.py`: Tests for task management functionality
- `integration/`: Integration tests for API endpoints
  - `test_api.py`: Tests for API endpoints and responses
- `conftest.py`: Pytest configuration and shared fixtures

## Running Tests

To run the tests, use the following command from the Metis directory:

```bash
pytest
```

To run specific test files or directories:

```bash
# Run unit tests only
pytest tests/unit/

# Run specific test file
pytest tests/unit/test_models.py

# Run with coverage
pytest --cov=metis
```

## Mocking

The tests use mocking for external dependencies such as:

- Hermes client for service registration
- Telos client for requirement integration

This ensures that tests can run independently without requiring the full Tekton ecosystem to be running.

## Requirements

Test dependencies are included in the `requirements.txt` file. Key testing libraries include:

- pytest: Test framework
- pytest-asyncio: Support for testing async functions
- pytest-cov: Code coverage reporting
- httpx: HTTP client for testing API endpoints
- fastapi.testclient: Test client for FastAPI applications