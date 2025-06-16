"""
Integration tests for repository module.
"""

import os
import pytest
import tempfile
import shutil
from typing import Dict, List, Any
import json

from ergon.core.database.engine import get_db_session, init_db
from ergon.core.database.models import Component, Tool, Agent, Workflow
from ergon.core.repository.models import ComponentType
from ergon.core.repository.repository import RepositoryService
from ergon.core.repository.tool_generator import generate_tool
from ergon.core.docs.document_store import document_store
from ergon.utils.config.settings import settings


@pytest.fixture
def temp_db():
    """Create a temporary database."""
    # Save original database URL
    original_db_url = settings.database_url
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp()
    temp_db_path = os.path.join(temp_dir, "test.db")
    
    # Set database URL to temporary database
    settings.database_url = f"sqlite:///{temp_db_path}"
    
    # Initialize database
    init_db()
    
    yield
    
    # Reset database URL
    settings.database_url = original_db_url
    
    # Clean up
    shutil.rmtree(temp_dir)


@pytest.fixture
def repo_service():
    """Create a repository service."""
    return RepositoryService()


def test_create_tool(temp_db, repo_service):
    """Test creating a tool."""
    # Create a tool
    tool_data = {
        "name": "TestTool",
        "description": "A test tool",
        "implementation_type": "python",
        "entry_point": "test_tool.py"
    }
    
    tool_id = repo_service.create_tool(**tool_data)
    
    # Verify tool was created
    with get_db_session() as db:
        tool = db.query(Tool).filter(Tool.id == tool_id).first()
        assert tool is not None
        assert tool.name == "TestTool"
        assert tool.description == "A test tool"
        assert tool.implementation_type == "python"
        assert tool.entry_point == "test_tool.py"


def test_create_agent(temp_db, repo_service):
    """Test creating an agent."""
    # Create an agent
    agent_data = {
        "name": "TestAgent",
        "description": "A test agent",
        "model": "gpt-4o",
        "system_prompt": "You are a test agent",
        "tools": [{"name": "test_tool", "description": "A tool for testing"}]
    }
    
    agent_id = repo_service.create_agent(**agent_data)
    
    # Verify agent was created
    with get_db_session() as db:
        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        assert agent is not None
        assert agent.name == "TestAgent"
        assert agent.description == "A test agent"
        assert agent.model == "gpt-4o"
        assert agent.system_prompt == "You are a test agent"
        assert len(json.loads(agent.tools)) == 1


def test_create_workflow(temp_db, repo_service):
    """Test creating a workflow."""
    # Create a workflow
    workflow_data = {
        "name": "TestWorkflow",
        "description": "A test workflow",
        "definition": {
            "nodes": ["node1", "node2"],
            "edges": [{"from": "node1", "to": "node2"}]
        }
    }
    
    workflow_id = repo_service.create_workflow(**workflow_data)
    
    # Verify workflow was created
    with get_db_session() as db:
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        assert workflow is not None
        assert workflow.name == "TestWorkflow"
        assert workflow.description == "A test workflow"
        assert workflow.definition["nodes"] == ["node1", "node2"]


def test_get_component(temp_db, repo_service):
    """Test getting a component."""
    # Create a tool
    tool_data = {
        "name": "GetTool",
        "description": "A tool to get",
        "implementation_type": "python",
        "entry_point": "get_tool.py"
    }
    
    tool_id = repo_service.create_tool(**tool_data)
    
    # Get the tool
    component = repo_service.get_component(tool_id)
    
    # Verify tool was retrieved
    assert component is not None
    assert component.name == "GetTool"
    assert component.description == "A tool to get"
    assert component.type == "tool"


def test_list_components(temp_db, repo_service):
    """Test listing components."""
    # Create a tool and agent
    tool_data = {
        "name": "ListTool",
        "description": "A tool to list",
        "implementation_type": "python",
        "entry_point": "list_tool.py"
    }
    
    agent_data = {
        "name": "ListAgent",
        "description": "An agent to list",
        "model": "gpt-4o",
        "system_prompt": "You are a test agent",
        "tools": []
    }
    
    repo_service.create_tool(**tool_data)
    repo_service.create_agent(**agent_data)
    
    # List components
    components = repo_service.list_components()
    
    # Verify components were listed
    assert len(components) >= 2
    
    # Test filtering by type
    tools = repo_service.list_components(component_type=ComponentType.TOOL)
    agents = repo_service.list_components(component_type=ComponentType.AGENT)
    
    assert len(tools) >= 1
    assert len(agents) >= 1
    
    # Verify tool and agent are in their respective lists
    assert any(c.name == "ListTool" for c in tools)
    assert any(c.name == "ListAgent" for c in agents)


def test_search_components(temp_db, repo_service):
    """Test searching components."""
    # Create components with different names
    tool_data = {
        "name": "SearchTool",
        "description": "A tool for searching",
        "implementation_type": "python",
        "entry_point": "search_tool.py"
    }
    
    agent_data = {
        "name": "FindAgent",
        "description": "An agent for finding",
        "model": "gpt-4o",
        "system_prompt": "You are a test agent",
        "tools": []
    }
    
    repo_service.create_tool(**tool_data)
    repo_service.create_agent(**agent_data)
    
    # Search by name
    search_results = repo_service.search_components("Search")
    
    # Verify search results
    assert len(search_results) >= 1
    assert any(c.name == "SearchTool" for c in search_results)
    
    # Search by description
    find_results = repo_service.search_components("finding")
    
    # Verify search results
    assert len(find_results) >= 1
    assert any(c.name == "FindAgent" for c in find_results)


def test_update_component(temp_db, repo_service):
    """Test updating a component."""
    # Create a tool
    tool_data = {
        "name": "UpdateTool",
        "description": "A tool to update",
        "implementation_type": "python",
        "entry_point": "update_tool.py"
    }
    
    tool_id = repo_service.create_tool(**tool_data)
    
    # Update the tool
    repo_service.update_component(tool_id, description="Updated description")
    
    # Verify tool was updated
    with get_db_session() as db:
        tool = db.query(Tool).filter(Tool.id == tool_id).first()
        assert tool is not None
        assert tool.description == "Updated description"


def test_delete_component(temp_db, repo_service):
    """Test deleting a component."""
    # Create a tool
    tool_data = {
        "name": "DeleteTool",
        "description": "A tool to delete",
        "implementation_type": "python",
        "entry_point": "delete_tool.py"
    }
    
    tool_id = repo_service.create_tool(**tool_data)
    
    # Delete the tool
    success = repo_service.delete_component(tool_id)
    
    # Verify tool was deleted
    assert success is True
    with get_db_session() as db:
        tool = db.query(Tool).filter(Tool.id == tool_id).first()
        assert tool is None


def test_tool_generator_integration(temp_db):
    """Test integration with tool generator."""
    # Generate a tool
    tool_data = generate_tool(
        name="TestGeneratedTool",
        description="A tool for testing generator integration",
        implementation_type="python"
    )
    
    # Create the tool in the repository
    repo_service = RepositoryService()
    tool_id = repo_service.create_tool(
        name=tool_data["name"],
        description=tool_data["description"],
        implementation_type=tool_data["implementation_type"],
        entry_point=tool_data["entry_point"]
    )
    
    # Verify tool was created
    with get_db_session() as db:
        tool = db.query(Tool).filter(Tool.id == tool_id).first()
        assert tool is not None
        assert tool.name == "TestGeneratedTool"
        
        # Add capabilities
        for capability in tool_data["capabilities"]:
            repo_service.add_capability(
                component_id=tool_id,
                name=capability["name"],
                description=capability["description"]
            )
        
        # Add parameters
        for parameter in tool_data["parameters"]:
            repo_service.add_parameter(
                component_id=tool_id,
                name=parameter["name"],
                description=parameter["description"],
                param_type=parameter["type"],
                required=parameter.get("required", False),
                default_value=parameter.get("default_value")
            )
        
        # Add files
        for file in tool_data["files"]:
            repo_service.add_file(
                component_id=tool_id,
                filename=file["filename"],
                content=file["content"],
                file_type=file["file_type"]
            )
        
        # Verify capabilities, parameters, and files were added
        component = repo_service.get_component(tool_id)
        assert len(component.capabilities) == len(tool_data["capabilities"])
        assert len(component.parameters) == len(tool_data["parameters"])
        assert len(component.files) == len(tool_data["files"])


def test_document_store_integration(temp_db, repo_service):
    """Test integration with document store."""
    # Create a tool
    tool_data = {
        "name": "DocsTool",
        "description": "A tool for document store testing",
        "implementation_type": "python",
        "entry_point": "docs_tool.py"
    }
    
    tool_id = repo_service.create_tool(**tool_data)
    
    # Index components
    document_store.index_components()
    
    # Search for the tool in documentation
    results = document_store.search_documentation("document store testing")
    
    # Verify tool was found
    assert len(results) > 0
    assert any("DocsTool" in result["content"] for result in results)