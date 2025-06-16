"""
Mail Agent Generator for Ergon.

This module defines the generator functions for creating mail agents.
"""

import logging
from typing import Dict, Any, List

from ergon.utils.config.settings import settings
from ergon.core.agents.mail.tools import mail_tool_definitions

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, settings.log_level.value))


def generate_mail_agent(name: str, description: str, model_name: str) -> Dict[str, Any]:
    """
    Generate a new mail agent.
    
    Args:
        name: Agent name
        description: Agent description
        model_name: Model to use
        
    Returns:
        Agent configuration
    """
    # Generate system prompt
    system_prompt = _generate_mail_system_prompt(name)
    
    # Get tool definitions
    tool_defs = mail_tool_definitions()
    
    # Create agent configuration
    agent_config = {
        "name": name,
        "description": description or f"Mail agent that can read, send, and manage emails named {name}",
        "model_name": model_name,
        "system_prompt": system_prompt,
        "tools": tool_defs,
        "files": [
            {
                "filename": "mail_setup_instructions.md",
                "file_type": "text/markdown",
                "content": _generate_mail_setup_instructions()
            }
        ]
    }
    
    return agent_config


def _generate_mail_system_prompt(agent_name: str) -> str:
    """
    Generate the system prompt for the mail agent.
    
    Args:
        agent_name: Name of the agent
    
    Returns:
        System prompt string
    """
    return f"""You are {agent_name}, an AI assistant specialized in managing emails. You can help users read their inbox, send emails, search for messages, and manage their email efficiently.

## Capabilities
- Read the user's inbox
- Read specific email messages
- Send new emails
- Reply to existing emails
- Search for emails using different criteria
- List available folders/labels

## Guidelines
1. Before you can use email functionality, you need to help the user set up authentication using the setup_mail tool. You must do this first before any other mail operations.
2. When sending emails, always confirm the recipients and content with the user before sending.
3. For sensitive emails, summarize the content rather than displaying the full message.
4. Format email content in a readable way, clearly identifying sender, subject, and date.
5. When searching, explain what query syntax is being used.
6. Always respect user privacy and data security.

## Initial setup
First-time users will need to authenticate with their email provider. Guide them through this process using the setup_mail tool.

Let the user know they can ask for help with any email-related task, and you're ready to assist them."""


def _generate_mail_setup_instructions() -> str:
    """
    Generate mail setup instructions.
    
    Returns:
        Setup instructions string
    """
    return """# Mail Agent Setup Instructions

This agent allows you to manage your emails with natural language. Before using the email features, you need to set up authentication.

## Mail Provider Setup

### Gmail Setup

1. Run the `setup_mail` command with "gmail" as the provider
2. You will be prompted to allow access to your Gmail account
3. Follow the browser instructions to complete authentication
4. Once authenticated, you can use all email features

### Outlook Setup

1. Run the `setup_mail` command with "outlook" as the provider
2. You will be prompted to allow access to your Microsoft account
3. Follow the browser instructions to complete authentication
4. Once authenticated, you can use all email features

## Usage Examples

After setup, you can use commands like:

- "Show me my recent emails"
- "Read the email from John about the meeting"
- "Send an email to jane@example.com about the project update"
- "Send an HTML email with formatting to jane@example.com"
- "Reply to the last email from my boss"
- "Search for emails containing 'invoice'"
- "Show me my email folders"

## Privacy & Security Notes

- Your email credentials are securely stored using OAuth
- The agent only has access to the specific permissions you grant
- No email data is stored permanently by the agent
- You can revoke access at any time through your email provider's security settings

## Troubleshooting

If you encounter authentication issues:
1. Check your internet connection
2. Ensure you completed the OAuth flow in your browser
3. Try the setup process again
4. Check if you need to enable "Less secure app access" in your Gmail settings

For persistent issues, check the application logs for more detailed error information."""