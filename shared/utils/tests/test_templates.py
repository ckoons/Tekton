"""
Tests for component template utilities.
"""
import pytest
import tempfile
import os
from pathlib import Path

from shared.utils.templates import (
    create_main_function_template,
    create_fastapi_app_template,
    create_health_endpoint_template,
    create_component_scaffolding,
    create_requirements_template,
    create_run_script_template,
    append_main_to_file
)


def test_create_main_function_template():
    """Test creating main function template."""
    template = create_main_function_template("test_component", 8000)
    
    # Check basic structure
    assert 'if __name__ == "__main__":' in template
    assert 'import argparse' in template
    assert 'import uvicorn' in template
    assert 'TEST_COMPONENT_PORT' in template
    assert '8000' in template
    assert 'test_component' in template
    
    # Check argparse setup
    assert '--port' in template
    assert '--host' in template
    assert 'uvicorn.run(app' in template


def test_create_fastapi_app_template():
    """Test creating FastAPI app template."""
    template = create_fastapi_app_template("test_component", 8000, "Test API Server")
    
    # Check imports
    assert 'from fastapi import FastAPI' in template
    assert 'from shared.utils.shutdown import component_lifespan' in template
    assert 'from shared.utils.startup import component_startup' in template
    
    # Check app creation with lifespan
    assert 'app = FastAPI(' in template
    assert 'title="Test_Component API"' in template
    assert 'lifespan=' in template
    
    # Check startup/shutdown functions
    assert 'async def startup_tasks():' in template
    assert 'async def cleanup_tasks():' in template


def test_create_health_endpoint_template():
    """Test creating health endpoint template."""
    template = create_health_endpoint_template("test_component")
    
    # Check imports
    assert 'from datetime import datetime' in template
    assert 'from shared.utils.health_check import create_health_response' in template
    
    # Check endpoints
    assert '@router.get("/health")' in template
    assert '@router.get("/api/health")' in template
    assert 'async def health_check():' in template
    assert 'return create_health_response' in template


def test_create_requirements_template():
    """Test creating requirements.txt template."""
    template = create_requirements_template()
    
    # Check essential dependencies
    assert 'fastapi' in template
    assert 'uvicorn' in template
    assert 'httpx' in template
    assert 'pydantic' in template
    
    # Check shared requirements reference
    assert '-r ../shared/requirements/base.txt' in template


def test_create_run_script_template():
    """Test creating run script template."""
    template = create_run_script_template("test_component", 8000)
    
    # Check shebang and basics
    assert '#!/bin/bash' in template
    assert 'TEST_COMPONENT_PORT=' in template
    assert '8000' in template
    
    # Check port checking
    assert 'nc -z localhost' in template
    
    # Check PYTHONPATH setup
    assert 'PYTHONPATH=' in template
    assert 'TEKTON_ROOT' in template
    
    # Check uvicorn command
    assert 'uvicorn' in template
    assert 'test_component.api.app:app' in template
    assert '--reload' in template


def test_create_component_scaffolding():
    """Test creating complete component scaffolding."""
    scaffolding = create_component_scaffolding("test_component", 8000)
    
    # Check all expected files
    expected_files = [
        "api/app.py",
        "api/__init__.py", 
        "api/endpoints.py",
        "api/models.py",
        "core/__init__.py",
        "core/engine.py",
        "__init__.py",
        "requirements.txt",
        "run_test_component.sh"
    ]
    
    for file_path in expected_files:
        assert file_path in scaffolding
        assert scaffolding[file_path] is not None
        assert len(scaffolding[file_path]) > 0


def test_append_main_to_file():
    """Test appending main function to existing file."""
    # Create a temporary file with some content
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write('"""Test module."""\n')
        f.write('import os\n\n')
        f.write('def some_function():\n')
        f.write('    pass\n')
        temp_path = f.name
    
    try:
        # Append main function
        append_main_to_file(temp_path, "test_component", 8000)
        
        # Read the file back
        with open(temp_path, 'r') as f:
            content = f.read()
        
        # Check main function was appended
        assert 'if __name__ == "__main__":' in content
        assert 'some_function()' in content  # Original content preserved
        assert 'test_component' in content
        assert '8000' in content
    finally:
        # Clean up
        os.unlink(temp_path)


def test_append_main_to_file_already_has_main():
    """Test appending main function when file already has one."""
    # Create a file that already has a main block
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write('"""Test module."""\n')
        f.write('import os\n\n')
        f.write('if __name__ == "__main__":\n')
        f.write('    print("Already has main")\n')
        temp_path = f.name
    
    try:
        # Try to append main function
        result = append_main_to_file(temp_path, "test_component", 8000)
        
        # Should return False indicating no changes made
        assert result is False
        
        # Read the file back
        with open(temp_path, 'r') as f:
            content = f.read()
        
        # Check original main is preserved
        assert content.count('if __name__ == "__main__":') == 1
        assert 'Already has main' in content
    finally:
        # Clean up
        os.unlink(temp_path)


def test_create_main_function_with_custom_app_path():
    """Test creating main function with custom app path."""
    template = create_main_function_template(
        "test_component", 
        8000,
        app_module_path="test_component.server:application"
    )
    
    assert 'from test_component.server import application as app' in template
    assert 'uvicorn.run(app' in template


def test_scaffolding_with_options():
    """Test component scaffolding with various options."""
    scaffolding = create_component_scaffolding(
        "test_component",
        8000,
        include_mcp=True,
        include_database=True,
        include_ui=True
    )
    
    # Check MCP files
    assert "api/mcp_server.py" in scaffolding
    
    # Check database files
    assert "models/database.py" in scaffolding
    assert "alembic.ini" in scaffolding
    
    # Check UI files
    assert "ui/test_component-component.html" in scaffolding


if __name__ == "__main__":
    pytest.main([__file__, "-v"])