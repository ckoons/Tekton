"""Special agent type handlers."""

from .browser import handle_browser_direct_workflow
from .github import handle_github_agent
from .mail import setup_mail_agent

__all__ = ["handle_browser_direct_workflow", "handle_github_agent", "setup_mail_agent"]