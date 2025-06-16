"""
Tests for Mail Agent Generator.
"""

from ergon.core.agents.generators.mail_generator import generate_mail_agent
from ergon.core.agents.mail.tools import mail_tool_definitions


def test_generate_mail_agent():
    """Test mail agent generator."""
    # Generate a mail agent
    agent_config = generate_mail_agent(
        name="TestMailAgent",
        description="A test mail agent",
        model_name="claude-3-7-sonnet-20250219"
    )
    
    # Verify the agent configuration
    assert agent_config["name"] == "TestMailAgent"
    assert agent_config["description"] == "A test mail agent"
    assert agent_config["model_name"] == "claude-3-7-sonnet-20250219"
    
    # Verify system prompt
    system_prompt = agent_config["system_prompt"]
    assert "TestMailAgent" in system_prompt
    assert "managing emails" in system_prompt
    
    # Verify tools
    tool_defs = mail_tool_definitions()
    assert len(agent_config["tools"]) == len(tool_defs)
    
    # Verify files
    assert len(agent_config["files"]) == 1
    assert agent_config["files"][0]["filename"] == "mail_setup_instructions.md"
    assert "Mail Agent Setup Instructions" in agent_config["files"][0]["content"]