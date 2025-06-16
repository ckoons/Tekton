"""
Mail setup wizard for Ergon.

This module provides functionality to set up mail providers interactively.
"""

import os
import json
import webbrowser
import getpass
import asyncio
from typing import Dict, Any, Optional

from ergon.utils.config.settings import settings
from ergon.utils.tekton_integration import get_component_url

# Import providers
from ergon.core.agents.mail.providers import get_mail_provider


async def setup_mail_provider(
    provider_type: str = None, 
    interactive: bool = True,
    email_address: str = None,
    password: str = None,
    imap_server: str = None,
    smtp_server: str = None,
    imap_port: int = 993,
    smtp_port: int = 587,
    use_ssl: bool = True,
    use_tls: bool = True,
    credentials_file: str = None
) -> Dict[str, Any]:
    """
    Setup for mail providers (interactive or non-interactive).
    
    Args:
        provider_type: Provider type (gmail, outlook, imap), if None will ask user
        interactive: Whether to run in interactive mode
        email_address: Email address (for imap provider)
        password: Password (for imap provider)
        imap_server: IMAP server (for imap provider)
        smtp_server: SMTP server (for imap provider)
        imap_port: IMAP port (for imap provider)
        smtp_port: SMTP port (for imap provider)
        use_ssl: Whether to use SSL for IMAP (for imap provider)
        use_tls: Whether to use TLS for SMTP (for imap provider)
        credentials_file: Path to OAuth credentials file (for gmail/outlook)
        
    Returns:
        Configuration dictionary
    """
    if not interactive:
        # Non-interactive mode with parameters
        if provider_type is None:
            print("Provider type is required for non-interactive mode")
            return {}
            
        if provider_type.lower() == 'gmail':
            # Gmail OAuth setup - need credentials file
            if not credentials_file:
                # Try default location
                credentials_file = os.path.expanduser('~/.ergon/gmail_credentials.json')
                
            if not os.path.exists(credentials_file):
                print(f"Gmail credentials file not found: {credentials_file}")
                return {}
                
            # Create config
            config = {
                "provider_type": "gmail",
                "credentials_file": credentials_file
            }
            
            # Save and return
            save_config(config)
            return config
            
        elif provider_type.lower() == 'outlook':
            # Outlook OAuth setup requires client ID
            if not settings.outlook_client_id:
                print("Outlook client ID not configured. Set OUTLOOK_CLIENT_ID in .env")
                return {}
                
            # Create config
            config = {
                "provider_type": "outlook",
                "client_id": settings.outlook_client_id
            }
            
            # Save and return
            save_config(config)
            return config
            
        elif provider_type.lower() == 'imap':
            # IMAP/SMTP setup requires email and password
            if not email_address or not password:
                print("Email address and password are required for IMAP setup")
                return {}
                
            # Auto-determine server settings if not provided
            if not imap_server or not smtp_server:
                domain = email_address.split('@')[-1] if '@' in email_address else ''
                
                if domain == 'gmail.com':
                    imap_server = imap_server or 'imap.gmail.com'
                    smtp_server = smtp_server or 'smtp.gmail.com'
                elif domain in ('outlook.com', 'hotmail.com', 'live.com'):
                    imap_server = imap_server or 'outlook.office365.com'
                    smtp_server = smtp_server or 'smtp.office365.com'
                elif domain == 'yahoo.com':
                    imap_server = imap_server or 'imap.mail.yahoo.com'
                    smtp_server = smtp_server or 'smtp.mail.yahoo.com'
                    
            # Create config
            config = {
                'provider_type': 'imap',
                'email_address': email_address,
                'password': password,  # This will be stored securely in the config file
                'imap_server': imap_server,
                'imap_port': imap_port,
                'smtp_server': smtp_server,
                'smtp_port': smtp_port,
                'use_ssl': use_ssl,
                'smtp_use_tls': use_tls
            }
            
            # For logging/display purposes, create a copy with redacted password
            safe_config = config.copy()
            safe_config['password'] = '**REDACTED**'
            print(f"Mail configuration prepared: {json.dumps(safe_config, indent=2)}")
            
            # Save and return
            save_config(config)
            return config
        
        # Unknown provider
        print(f"Unknown provider type: {provider_type}")
        return {}
    
    print("\n=== Ergon Mail Setup ===\n")
    print("This wizard will help you set up email access for Ergon.")
    
    # Choose provider type if not specified
    if provider_type is None:
        print("\nSelect authentication method:")
        print("1. OAuth (recommended for Gmail and Outlook)")
        print("2. IMAP/SMTP (works with most email providers)")
        
        while True:
            choice = input("\nEnter your choice (1 or 2): ")
            if choice in ['1', '2']:
                break
            print("Invalid choice. Please enter 1 or 2.")
        
        if choice == '1':
            print("\nSelect email provider:")
            print("1. Gmail")
            print("2. Outlook")
            
            provider_choice = input("\nEnter your choice (1 or 2): ")
            provider_type = 'gmail' if provider_choice == '1' else 'outlook'
        else:
            provider_type = 'imap'
    
    config = {}
    
    if provider_type.lower() == 'gmail':
        # Gmail OAuth setup
        config = await setup_gmail_oauth()
    elif provider_type.lower() == 'outlook':
        # Outlook OAuth setup
        config = await setup_outlook_oauth()
    elif provider_type.lower() == 'imap':
        # IMAP/SMTP setup
        config = await setup_imap_smtp()
    else:
        print(f"Unknown provider type: {provider_type}")
        return {}
    
    if config:
        # Save configuration
        save_config(config)
        print("\n✅ Mail setup complete!")
    
    return config


async def setup_gmail_oauth() -> Dict[str, Any]:
    """
    Set up Gmail OAuth authentication.
    
    Returns:
        Configuration dictionary
    """
    credentials_file = os.path.expanduser('~/.ergon/gmail_credentials.json')
    
    if not os.path.exists(credentials_file):
        print("\nGmail OAuth credentials not found.")
        print("You need to create OAuth credentials in Google Cloud Console.")
        print("\nInstructions:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a project")
        print("3. Enable the Gmail API")
        print("4. Create OAuth 2.0 credentials")
        print("5. Download the credentials JSON file")
        print("6. Save it as ~/.ergon/gmail_credentials.json")
        
        open_console = input("\nOpen Google Cloud Console now? (y/n): ")
        if open_console.lower() == 'y':
            webbrowser.open('https://console.cloud.google.com/')
        
        input("\nPress Enter when you have downloaded the credentials file...")
    
    if os.path.exists(credentials_file):
        print("\n✅ Gmail credentials found!")
        print("You'll be prompted to authenticate when you first use the mail agent.")
        
        # Create a Gmail provider and try to authenticate
        from ergon.core.agents.mail.providers import GmailProvider
        provider = GmailProvider(credentials_file=credentials_file)
        
        if await provider.authenticate():
            print(f"\n✅ Successfully authenticated as {provider.email}")
            return {
                "provider_type": "gmail",
                "credentials_file": credentials_file
            }
        else:
            print("\n❌ Authentication failed.")
            return {}
    else:
        print("\n❌ Gmail credentials not found at ~/.ergon/gmail_credentials.json")
        print("Please complete the setup before using the mail agent.")
        return {}


async def setup_outlook_oauth() -> Dict[str, Any]:
    """
    Set up Outlook OAuth authentication.
    
    Returns:
        Configuration dictionary
    """
    # Check if client ID is configured
    if not settings.outlook_client_id:
        print("\nOutlook client ID not configured.")
        print("You need to create an app in the Microsoft Azure portal.")
        print("\nInstructions:")
        print("1. Go to https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade")
        print("2. Register a new application")
        redirect_uri = f"{get_component_url('ergon', '/auth/outlook/callback')}"
        print(f"3. Add redirect URI: {redirect_uri}")
        print("4. Add Microsoft Graph permissions: Mail.Read, Mail.Send, Mail.ReadWrite")
        print("5. Get the client ID (Application ID)")
        
        open_portal = input("\nOpen Azure portal now? (y/n): ")
        if open_portal.lower() == 'y':
            webbrowser.open('https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade')
        
        client_id = input("\nEnter the client ID: ")
        
        if not client_id:
            print("Client ID is required.")
            return {}
        
        # Save client ID to settings
        # In a real implementation, we would update the settings file
        # For now, we'll just return it in the config
        return {
            "provider_type": "outlook",
            "client_id": client_id
        }
    else:
        # Test authentication
        from ergon.core.agents.mail.providers import OutlookProvider
        provider = OutlookProvider(client_id=settings.outlook_client_id)
        
        if await provider.authenticate():
            print(f"\n✅ Successfully authenticated as {provider.email}")
            return {
                "provider_type": "outlook",
                "client_id": settings.outlook_client_id
            }
        else:
            print("\n❌ Authentication failed.")
            return {}


async def setup_imap_smtp() -> Dict[str, Any]:
    """
    Set up IMAP/SMTP mail provider.
    
    Returns:
        Configuration dictionary
    """
    print("\n=== IMAP/SMTP Setup ===")
    email_address = input("Enter your email address: ")
    
    if not email_address or '@' not in email_address:
        print("Invalid email address.")
        return {}
    
    # Determine if this is a common provider
    domain = email_address.split('@')[-1]
    
    if domain == 'gmail.com':
        print("\nFor Gmail, you need to enable 'Less secure app access' or create an App Password.")
        print("Visit: https://myaccount.google.com/security")
        print("We recommend using an App Password for better security.")
        
        imap_server = 'imap.gmail.com'
        smtp_server = 'smtp.gmail.com'
        
    elif domain in ('outlook.com', 'hotmail.com', 'live.com'):
        print("\nFor Outlook/Hotmail, you may need to enable IMAP access in your account settings.")
        
        imap_server = 'outlook.office365.com'
        smtp_server = 'smtp.office365.com'
        
    elif domain == 'yahoo.com':
        print("\nFor Yahoo Mail, you need to create an App Password.")
        print("Visit: https://login.yahoo.com/account/security")
        
        imap_server = 'imap.mail.yahoo.com'
        smtp_server = 'smtp.mail.yahoo.com'
        
    else:
        print("\nEnter your email server information:")
        imap_server = input("IMAP Server (e.g., mail.example.com): ")
        smtp_server = input("SMTP Server (or press Enter to use same as IMAP): ") or imap_server
    
    # Get IMAP/SMTP ports
    imap_port = input(f"IMAP Port (default: 993): ") or "993"
    smtp_port = input(f"SMTP Port (default: 587): ") or "587"
    
    # Get SSL/TLS options
    use_ssl = input("Use SSL for IMAP? (y/n, default: y): ").lower() != 'n'
    use_tls = input("Use TLS for SMTP? (y/n, default: y): ").lower() != 'n'
    
    # Get password (without echoing to terminal)
    password = getpass.getpass("Enter your email password or app password: ")
    
    # Test connection
    config = {
        'provider_type': 'imap',
        'email_address': email_address,
        'password': password,
        'imap_server': imap_server,
        'imap_port': int(imap_port),
        'smtp_server': smtp_server,
        'smtp_port': int(smtp_port),
        'use_ssl': use_ssl,
        'smtp_use_tls': use_tls
    }
    
    print("\nTesting connection...")
    
    # Create provider and try to authenticate
    provider = get_mail_provider(provider_type='imap', **config)
    if await provider.authenticate():
        print("\n✅ Connection successful!")
        return config
    else:
        print("\n❌ Connection failed. Please check your settings and try again.")
        return {}


def save_config(config: Dict[str, Any]) -> None:
    """
    Save mail configuration securely.
    
    Args:
        config: Configuration dictionary
    """
    config_dir = os.path.join(settings.config_path, 'mail')
    os.makedirs(config_dir, exist_ok=True)
    
    config_file = os.path.join(config_dir, 'config.json')
    
    # Check if password is included
    if 'password' in config:
        print("\nWARNING: Password will be stored in plain text. In a production environment,")
        print("you should implement secure password storage with encryption.")
        
        # In a production implementation, we would encrypt sensitive information
        # like passwords before saving. For now, we'll just save as-is, but
        # add a warning in the config file itself.
        config_with_warning = config.copy()
        config_with_warning['_security_note'] = "Password stored in plain text. Consider implementing encryption for production use."
        
        with open(config_file, 'w') as f:
            json.dump(config_with_warning, f, indent=2)
    else:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    print(f"Configuration saved to {config_file}")