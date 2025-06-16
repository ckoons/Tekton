"""
IMAP/SMTP Mail Provider for Ergon Mail Agent.

This module implements an IMAP/SMTP based provider that works with most email services.
"""

import os
import email
import imaplib
import smtplib
import logging
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate, make_msgid
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from ergon.utils.config.settings import settings
from ergon.core.agents.mail.providers import MailProvider

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, settings.log_level.value))


class ImapSmtpProvider(MailProvider):
    """IMAP/SMTP based mail provider that works with most email services."""
    
    def __init__(self, 
                email_address: str, 
                password: str, 
                imap_server: str, 
                imap_port: int = 993, 
                smtp_server: Optional[str] = None, 
                smtp_port: int = 587, 
                use_ssl: bool = True,
                smtp_use_tls: bool = True):
        """Initialize the IMAP/SMTP provider."""
        self.email = email_address
        self.password = password
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.smtp_server = smtp_server or imap_server
        self.smtp_port = smtp_port
        self.use_ssl = use_ssl
        self.smtp_use_tls = smtp_use_tls
        self.imap = None
        self.authenticated = False
    
    async def authenticate(self) -> bool:
        """Authenticate with IMAP and test SMTP connection."""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._authenticate_sync)
            return result
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            self.authenticated = False
            return False
    
    def _authenticate_sync(self) -> bool:
        """Synchronous authentication implementation."""
        try:
            # Connect to IMAP server
            if self.use_ssl:
                self.imap = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            else:
                self.imap = imaplib.IMAP4(self.imap_server, self.imap_port)
            
            # Login to IMAP
            self.imap.login(self.email, self.password)
            
            # Test SMTP connection
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as smtp:
                smtp.ehlo()
                if self.smtp_use_tls:
                    smtp.starttls()
                    smtp.ehlo()
                smtp.login(self.email, self.password)
            
            self.authenticated = True
            logger.info(f"Successfully authenticated {self.email} to {self.imap_server}")
            return True
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            self.authenticated = False
            return False
    
    async def get_inbox(self, limit: int = 20, page: int = 1) -> List[Dict[str, Any]]:
        """Get inbox messages using IMAP."""
        if not self.authenticated or not self.imap:
            if not await self.authenticate():
                return []
        
        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._get_inbox_sync, limit, page)
        except Exception as e:
            logger.error(f"Error getting inbox: {str(e)}")
            return []
    
    def _get_inbox_sync(self, limit: int, page: int) -> List[Dict[str, Any]]:
        """Synchronous inbox retrieval implementation."""
        messages = []
        try:
            # Select inbox
            self.imap.select('INBOX')
            
            # Search for all messages
            status, data = self.imap.search(None, 'ALL')
            if status != 'OK':
                return messages
            
            # Calculate pagination
            message_ids = data[0].split()
            total_messages = len(message_ids)
            
            # Reverse to get newest first
            message_ids = message_ids[::-1]
            
            # Apply pagination
            start_idx = (page - 1) * limit
            if start_idx >= total_messages:
                return messages
                
            end_idx = min(start_idx + limit, total_messages)
            paged_ids = message_ids[start_idx:end_idx]
            
            # Fetch messages
            for msg_id in paged_ids:
                status, msg_data = self.imap.fetch(msg_id, '(BODY.PEEK[HEADER] BODY.PEEK[1]<0.500>)')
                if status != 'OK':
                    continue
                
                # Process headers
                header_data = msg_data[0][1]
                email_message = email.message_from_bytes(header_data)
                
                # Extract metadata
                subject = email_message.get('Subject', '(No subject)')
                from_addr = email_message.get('From', '')
                to_addr = email_message.get('To', '')
                date_str = email_message.get('Date', '')
                message_id = msg_id.decode()
                
                # Get body preview
                body_preview = ""
                if len(msg_data) > 1 and msg_data[1][1]:
                    try:
                        body_data = msg_data[1][1]
                        if isinstance(body_data, bytes):
                            body_preview = body_data.decode('utf-8', errors='replace')
                    except Exception as e:
                        logger.error(f"Error extracting body preview: {str(e)}")
                
                messages.append({
                    'id': message_id,
                    'subject': subject,
                    'from': from_addr,
                    'to': to_addr,
                    'date': date_str,
                    'snippet': body_preview[:100] + '...' if len(body_preview) > 100 else body_preview
                })
            
            return messages
        except Exception as e:
            logger.error(f"Error getting inbox: {str(e)}")
            return messages
    
    async def get_message(self, message_id: str) -> Dict[str, Any]:
        """Get a specific message by ID."""
        if not self.authenticated or not self.imap:
            if not await self.authenticate():
                return {}
        
        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._get_message_sync, message_id)
        except Exception as e:
            logger.error(f"Error getting message {message_id}: {str(e)}")
            return {}
    
    def _get_message_sync(self, message_id: str) -> Dict[str, Any]:
        """Synchronous message retrieval implementation."""
        try:
            # Convert string ID to bytes if needed
            msg_id = message_id.encode() if isinstance(message_id, str) else message_id
            
            # Fetch the entire message
            status, msg_data = self.imap.fetch(msg_id, '(RFC822)')
            if status != 'OK':
                logger.error(f"Failed to fetch message {message_id}")
                return {}
            
            # Parse the email message
            email_message = email.message_from_bytes(msg_data[0][1])
            
            # Extract headers
            subject = email_message.get('Subject', '(No subject)')
            from_addr = email_message.get('From', '')
            to_addr = email_message.get('To', '')
            cc_addr = email_message.get('Cc', '')
            date_str = email_message.get('Date', '')
            message_id_header = email_message.get('Message-ID', '')
            in_reply_to = email_message.get('In-Reply-To', '')
            references = email_message.get('References', '')
            
            # Extract body
            body, content_type = self._extract_body(email_message)
            
            # Format message
            message = {
                'id': message_id,
                'subject': subject,
                'from': from_addr,
                'to': to_addr,
                'cc': cc_addr,
                'date': date_str,
                'body': body,
                'content_type': content_type,
                'message_id': message_id_header,
                'in_reply_to': in_reply_to,
                'references': references,
                'thread_id': in_reply_to or message_id_header
            }
            
            return message
        except Exception as e:
            logger.error(f"Error getting message {message_id}: {str(e)}")
            return {}
    
    def _extract_body(self, email_message) -> Tuple[str, str]:
        """Extract body text from email message."""
        # Default values
        body = ""
        content_type = "text/plain"
        
        # Check if the message is multipart
        if email_message.is_multipart():
            html_part = None
            text_part = None
            
            for part in email_message.walk():
                part_content_type = part.get_content_type()
                
                if part_content_type == "text/html":
                    html_part = part
                elif part_content_type == "text/plain":
                    text_part = part
            
            # Prefer HTML if available
            if html_part is not None:
                body = html_part.get_payload(decode=True).decode('utf-8', errors='replace')
                content_type = "text/html"
            # Fall back to plain text
            elif text_part is not None:
                body = text_part.get_payload(decode=True).decode('utf-8', errors='replace')
                content_type = "text/plain"
        else:
            # Not multipart, just get the payload
            payload = email_message.get_payload(decode=True)
            if payload:
                body = payload.decode('utf-8', errors='replace')
                content_type = email_message.get_content_type()
        
        return body, content_type
    
    async def send_message(self, to: List[str], subject: str, body: str, 
                         cc: Optional[List[str]] = None,
                         bcc: Optional[List[str]] = None) -> bool:
        """Send a new email message."""
        if not self.authenticated:
            if not await self.authenticate():
                return False
        
        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._send_message_sync, to, subject, body, cc, bcc)
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return False
    
    def _send_message_sync(self, to: List[str], subject: str, body: str, 
                          cc: Optional[List[str]], bcc: Optional[List[str]]) -> bool:
        """Synchronous message sending implementation."""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = ', '.join(to)
            msg['Subject'] = subject
            msg['Date'] = formatdate(localtime=True)
            msg['Message-ID'] = make_msgid(domain=self.email.split('@')[1])
            
            if cc:
                msg['Cc'] = ', '.join(cc)
            
            # Attach body
            msg.attach(MIMEText(body, 'plain'))
            
            # Determine all recipients
            recipients = to.copy()
            if cc:
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)
            
            # Connect to SMTP server and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as smtp:
                smtp.ehlo()
                if self.smtp_use_tls:
                    smtp.starttls()
                    smtp.ehlo()
                smtp.login(self.email, self.password)
                smtp.send_message(msg)
            
            logger.info(f"Message sent successfully to {', '.join(to)}")
            return True
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return False
    
    async def reply_to_message(self, message_id: str, body: str) -> bool:
        """Reply to a specific message."""
        if not self.authenticated:
            if not await self.authenticate():
                return False
        
        try:
            # Get the original message
            original = await self.get_message(message_id)
            if not original:
                logger.error(f"Could not find original message {message_id}")
                return False
            
            # Extract from address to reply to
            from_addr = original.get('from', '')
            # Extract email address if in format "Name <email@example.com>"
            if '<' in from_addr and '>' in from_addr:
                from_addr = from_addr[from_addr.find('<')+1:from_addr.find('>')]
            
            # Extract subject
            subject = original.get('subject', '')
            if not subject.lower().startswith('re:'):
                subject = f"Re: {subject}"
            
            # Create reply
            return await self.send_message(
                to=[from_addr],
                subject=subject,
                body=body,
                # Add original recipients in CC
                cc=[addr.strip() for addr in original.get('to', '').split(',') 
                   if addr.strip() and addr.strip() != self.email]
            )
        except Exception as e:
            logger.error(f"Error replying to message: {str(e)}")
            return False
    
    async def search_messages(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for messages using IMAP search."""
        if not self.authenticated or not self.imap:
            if not await self.authenticate():
                return []
        
        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._search_messages_sync, query, limit)
        except Exception as e:
            logger.error(f"Error searching messages: {str(e)}")
            return []
    
    def _search_messages_sync(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Synchronous message search implementation."""
        messages = []
        try:
            # Select inbox
            self.imap.select('INBOX')
            
            # Prepare search criteria
            if '@' in query:  # Assume it's an email address
                status, data = self.imap.search(None, f'FROM "{query}"')
            elif query.startswith('subject:'):
                subject = query[8:].strip()
                status, data = self.imap.search(None, f'SUBJECT "{subject}"')
            else:
                status, data = self.imap.search(None, f'OR SUBJECT "{query}" TEXT "{query}"')
            
            if status != 'OK':
                return messages
            
            # Get message IDs and limit results
            message_ids = data[0].split()[::-1][:limit]
            
            # Fetch messages
            for msg_id in message_ids:
                # Fetch headers
                status, msg_data = self.imap.fetch(msg_id, '(BODY.PEEK[HEADER])')
                if status != 'OK':
                    continue
                
                # Process headers
                header_data = msg_data[0][1]
                email_message = email.message_from_bytes(header_data)
                
                # Extract metadata
                subject = email_message.get('Subject', '(No subject)')
                from_addr = email_message.get('From', '')
                date_str = email_message.get('Date', '')
                
                messages.append({
                    'id': msg_id.decode(),
                    'subject': subject,
                    'from': from_addr,
                    'date': date_str,
                    'snippet': f"Search result for '{query}'"
                })
            
            return messages
        except Exception as e:
            logger.error(f"Error searching messages: {str(e)}")
            return messages
    
    async def get_folders(self) -> List[Dict[str, Any]]:
        """Get available mail folders."""
        if not self.authenticated or not self.imap:
            if not await self.authenticate():
                return []
        
        try:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._get_folders_sync)
        except Exception as e:
            logger.error(f"Error getting folders: {str(e)}")
            return []
    
    def _get_folders_sync(self) -> List[Dict[str, Any]]:
        """Synchronous folder retrieval implementation."""
        folders = []
        try:
            # Get list of folders
            status, folder_list = self.imap.list()
            if status != 'OK':
                return folders
            
            # Process folders
            for folder_data in folder_list:
                if isinstance(folder_data, bytes):
                    folder_str = folder_data.decode()
                    
                    # Extract folder name
                    if '"' in folder_str:
                        name = folder_str.split('"')[-2]
                    else:
                        continue
                    
                    # Get counts
                    try:
                        self.imap.select(f'"{name}"', readonly=True)
                        status, data = self.imap.search(None, 'ALL')
                        total_count = len(data[0].split()) if status == 'OK' else 0
                        
                        status, data = self.imap.search(None, 'UNSEEN')
                        unread_count = len(data[0].split()) if status == 'OK' else 0
                    except Exception:
                        total_count = 0
                        unread_count = 0
                    
                    folders.append({
                        'id': name,
                        'name': name,
                        'total_items': total_count,
                        'unread_items': unread_count
                    })
            
            return folders
        except Exception as e:
            logger.error(f"Error getting folders: {str(e)}")
            return folders