"""
Registration Token - Security tokens for component authentication.

This module provides token generation and validation for the Unified Registration Protocol.
"""

import time
import uuid
import hmac
import hashlib
import json
import logging
from typing import Dict, Any, Optional

# Configure logger
logger = logging.getLogger(__name__)

class RegistrationToken:
    """
    Security token for authenticating components with the registration system.
    
    Tokens are used to validate component identity and authorize registration
    with the Tekton ecosystem.
    """
    
    def __init__(self, component_id: str, secret_key: str, expiration: int = 3600):
        """
        Initialize a registration token.
        
        Args:
            component_id: Unique identifier for the component
            secret_key: Secret key for signing the token
            expiration: Token validity period in seconds (default: 1 hour)
        """
        self.component_id = component_id
        self.secret_key = secret_key
        self.issued_at = int(time.time())
        self.expires_at = self.issued_at + expiration
        self.token_id = str(uuid.uuid4())
    
    def generate(self) -> str:
        """
        Generate a signed token string.
        
        Returns:
            Signed token as a string
        """
        payload = {
            "component_id": self.component_id,
            "token_id": self.token_id,
            "iat": self.issued_at,
            "exp": self.expires_at
        }
        
        # Create JSON string of payload
        payload_str = json.dumps(payload, sort_keys=True)
        
        # Create signature using HMAC-SHA256
        signature = hmac.new(
            self.secret_key.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Combine payload and signature
        token = {
            "payload": payload,
            "signature": signature
        }
        
        return json.dumps(token)
    
    @staticmethod
    def validate(token_str: str, secret_key: str) -> Optional[Dict[str, Any]]:
        """
        Validate a token string.
        
        Args:
            token_str: Token string to validate
            secret_key: Secret key for verification
            
        Returns:
            Token payload if valid, None otherwise
        """
        try:
            # Parse token
            token = json.loads(token_str)
            payload = token["payload"]
            signature = token["signature"]
            
            # Check expiration
            current_time = int(time.time())
            if current_time > payload["exp"]:
                logger.warning("Token expired")
                return None
            
            # Verify signature
            payload_str = json.dumps(payload, sort_keys=True)
            expected_signature = hmac.new(
                secret_key.encode(),
                payload_str.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if signature != expected_signature:
                logger.warning("Invalid token signature")
                return None
            
            return payload
            
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error validating token: {e}")
            return None