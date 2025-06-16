"""
Constants and configurations for the Ergon chatbot.

Provides default settings, configurations, and static data structures.
"""

# Agent metadata for better recommendations
agent_metadata = {
    # Mail agent capabilities
    "mail": {
        "keywords": ["mail", "email", "gmail", "outlook", "message", "send", "inbox", "imap", "smtp"],
        "capabilities": ["send emails", "read emails", "search inbox", "manage drafts", "handle attachments"],
        "desc": "Email management agent that can read, send, and organize emails"
    },
    # Browser agent capabilities
    "browser": {
        "keywords": ["browser", "web", "chrome", "firefox", "internet", "website", "browse", "surf"],
        "capabilities": ["navigate websites", "extract content", "fill forms", "click buttons", "take screenshots"],
        "desc": "Web browsing agent that can navigate and interact with websites"
    },
    # GitHub agent capabilities
    "github": {
        "keywords": ["github", "git", "repo", "repository", "code", "pull", "commit", "issue", "branch"],
        "capabilities": ["manage repositories", "create issues", "handle pull requests", "view code"],
        "desc": "GitHub integration agent for repository and issue management"
    },
    # Nexus agent capabilities
    "nexus": {
        "keywords": ["nexus", "memory", "remember", "context", "conversation", "recall"],
        "capabilities": ["remember conversations", "maintain context", "recall previous interactions"],
        "desc": "Memory-enabled agent that maintains context across conversations"
    },
    # Standard agent capabilities
    "standard": {
        "keywords": ["standard", "basic", "default", "general", "assistant"],
        "capabilities": ["answer questions", "provide information", "general assistance"],
        "desc": "General-purpose agent for basic tasks and assistance"
    }
}

# Styles for the chat interface
custom_styles = """
<style>
/* Reduce top spacing */
.stApp > header {
    height: 0px;
}

/* Make chat more prominent */
[data-testid="stChatInput"] > div {
    border-color: #2196F3 !important;
}
</style>
"""

# Default welcome message for first-time users
welcome_message = """
👋 Welcome to Nexus! I'm your AI assistant for working with memory-enabled agents.

You can start immediately by:
- Just ask me about any task (e.g., "I need a mail agent" or "Help me browse the web")
- I'll help you find the right agent for your task
- Create a new Nexus agent using the sidebar if needed
- Use special commands like `!rate` and `!plan` to provide feedback

What would you like help with today?
"""

# Sample implementation plan template
sample_plan = [
    {
        "name": "Memory-Enhanced Chat Interface",
        "description": "Implement the basic memory-enabled chat interface",
        "tasks": [
            {
                "description": "Create chatbot UI page",
                "priority": "High"
            },
            {
                "description": "Connect to memory service",
                "priority": "High"
            },
            {
                "description": "Implement persistent conversation history",
                "priority": "Medium"
            },
            {
                "description": "Add agent awareness features",
                "priority": "Medium"
            }
        ]
    },
    {
        "name": "Agent Management via Chat",
        "description": "Allow creating and running agents through conversation",
        "tasks": [
            {
                "description": "Implement natural language agent creation",
                "priority": "High"
            },
            {
                "description": "Extract parameters from dialogue",
                "priority": "Medium"
            },
            {
                "description": "Add agent utilization capabilities",
                "priority": "High"
            },
            {
                "description": "Implement conversation context maintenance",
                "priority": "Low"
            }
        ]
    }
]