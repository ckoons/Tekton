"""
Pytest configuration for Tekton tests
"""

import sys
import os
from pathlib import Path

# Get the project root
tests_dir = Path(__file__).parent
project_root = tests_dir.parent

# Add project root to Python path
sys.path.insert(0, str(project_root))

# Add Hermes to Python path for integration tests
hermes_path = project_root / "Hermes"
if hermes_path.exists():
    sys.path.insert(0, str(hermes_path))

# Add other component paths as needed
for component in ['Ergon', 'Apollo', 'Athena', 'Budget', 'Engram']:
    component_path = project_root / component
    if component_path.exists():
        sys.path.insert(0, str(component_path))

# Configure pytest-asyncio
import pytest

pytest_plugins = ['pytest_asyncio']

# Set asyncio mode
def pytest_configure(config):
    """Configure pytest"""
    # Set asyncio mode to avoid warnings
    config.option.asyncio_mode = "auto"
