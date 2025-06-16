"""
Mail Provider Adapters for Ergon Mail Agent.

This module defines the interfaces and implementations for different
email service providers (Gmail, Outlook, etc.).
"""

from typing import Optional

from ergon.core.agents.mail.providers.base import MailProvider
from ergon.core.agents.mail.providers.gmail import GmailProvider
from ergon.core.agents.mail.providers.outlook import OutlookProvider

# Lazy import for IMAP to avoid circular imports
def _get_imap_provider():
    """Lazily import the IMAP provider class."""
    from ergon.core.agents.mail.imap_provider import ImapSmtpProvider
    return ImapSmtpProvider


def get_mail_provider(provider_type: str = "gmail", **kwargs) -> Optional[MailProvider]:
    """
    Factory function to create a mail provider instance.
    
    Args:
        provider_type: Type of provider to create (gmail, outlook, imap, etc.)
        **kwargs: Provider-specific arguments
        
    Returns:
        Provider instance or None if invalid type
    """
    if provider_type.lower() == "gmail":
        return GmailProvider(**kwargs)
    elif provider_type.lower() == "outlook":
        return OutlookProvider(**kwargs)
    elif provider_type.lower() == "imap":
        # Import lazily to avoid circular imports
        ImapSmtpProvider = _get_imap_provider()
        
        # Get email domain for auto-configuration
        email = kwargs.get('email_address', '')
        email_domain = email.split('@')[-1] if '@' in email else ''
        
        # Set default servers based on common email providers if not specified
        if email_domain == 'gmail.com' and 'imap_server' not in kwargs:
            kwargs['imap_server'] = 'imap.gmail.com'
            kwargs['smtp_server'] = 'smtp.gmail.com'
        elif email_domain in ('outlook.com', 'hotmail.com', 'live.com') and 'imap_server' not in kwargs:
            kwargs['imap_server'] = 'outlook.office365.com'
            kwargs['smtp_server'] = 'smtp.office365.com'
        elif email_domain == 'yahoo.com' and 'imap_server' not in kwargs:
            kwargs['imap_server'] = 'imap.mail.yahoo.com'
            kwargs['smtp_server'] = 'smtp.mail.yahoo.com'
        
        return ImapSmtpProvider(**kwargs)
    
    # Unknown provider type
    from ergon.core.logging import get_logger
    logger = get_logger(__name__)
    logger.error(f"Unsupported mail provider type: {provider_type}")
    return None


__all__ = ["MailProvider", "GmailProvider", "OutlookProvider", "get_mail_provider"]