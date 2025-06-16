"""
Mail Provider Adapters for Ergon Mail Agent.

This module has been refactored into a more modular structure.
It now serves as a compatibility layer that imports from the new structure.
"""

# Re-export classes and functions from new structure
from ergon.core.agents.mail.providers.base import MailProvider
from ergon.core.agents.mail.providers.gmail import GmailProvider
from ergon.core.agents.mail.providers.outlook import OutlookProvider
from ergon.core.agents.mail.providers import get_mail_provider

# For backward compatibility
__all__ = ["MailProvider", "GmailProvider", "OutlookProvider", "get_mail_provider"]