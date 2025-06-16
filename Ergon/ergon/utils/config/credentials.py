"""
Secure credential management for Ergon.
Handles user authentication and secure storage of credentials.
"""

import os
import json
import base64
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import getpass

from ergon.utils.config.settings import settings


class CredentialManager:
    """
    Secure credential manager for Ergon.
    - Encrypts and stores user credentials
    - Handles authentication and login
    - Provides secure storage for API keys and service credentials
    """
    
    # Constants
    CRED_FILE_NAME = "ergon_credentials.enc"
    SALT_FILE_NAME = "ergon_salt"
    
    def __init__(self):
        """Initialize credential manager"""
        self.config_path = settings.config_path
        self.credentials_file = self.config_path / self.CRED_FILE_NAME
        self.salt_file = self.config_path / self.SALT_FILE_NAME
        self.current_user = None
        self.fernet = None
    
    def _generate_key(self, password: str) -> bytes:
        """Generate encryption key from password and salt"""
        # Ensure config path exists
        os.makedirs(self.config_path, exist_ok=True)
        
        # Load or create salt
        if os.path.exists(self.salt_file):
            with open(self.salt_file, "rb") as f:
                salt = f.read()
        else:
            # Create a new random salt
            salt = os.urandom(16)
            with open(self.salt_file, "wb") as f:
                f.write(salt)
        
        # Generate key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def _initialize_encryption(self, password: str):
        """Initialize encryption with user password"""
        key = self._generate_key(password)
        self.fernet = Fernet(key)
    
    def authenticate(self, email: str, password: str) -> bool:
        """
        Authenticate user with email and password
        
        Args:
            email: User email address (username)
            password: User password
            
        Returns:
            bool: True if authentication is successful
        """
        # Prevent empty email or password
        if not email or not password:
            return False
        
        self._initialize_encryption(password)
        
        if not os.path.exists(self.credentials_file):
            # First-time user, register automatically
            return self.register(email, password)
        
        try:
            credentials = self._load_credentials()
            if email in credentials:
                # Verify password (implicitly done by successful decryption)
                self.current_user = email
                return True
            return False
        except Exception:
            # Decryption failed - wrong password
            return False
    
    def register(self, email: str, password: str) -> bool:
        """
        Register a new user
        
        Args:
            email: User email address (username)
            password: User password
            
        Returns:
            bool: True if registration is successful
        """
        # Prevent empty email or password
        if not email or not password:
            return False
            
        # Minimum password length check (8 characters)
        if len(password) < 8:
            return False
        
        self._initialize_encryption(password)
        
        # Check if credentials file exists
        if os.path.exists(self.credentials_file):
            # Load existing credentials
            try:
                credentials = self._load_credentials()
                if email in credentials:
                    # User already exists
                    return False
            except Exception:
                # Can't decrypt existing file with this password
                return False
        else:
            # New credentials file
            credentials = {}
        
        # Add new user
        credentials[email] = {
            "created_at": str(datetime.now()),
            "settings": {}
        }
        
        # Save credentials
        self._save_credentials(credentials)
        self.current_user = email
        return True
    
    def _load_credentials(self) -> Dict[str, Any]:
        """Load and decrypt credentials"""
        if not self.fernet:
            raise ValueError("Encryption not initialized")
        
        if not os.path.exists(self.credentials_file):
            return {}
        
        with open(self.credentials_file, "rb") as f:
            encrypted_data = f.read()
            
        decrypted_data = self.fernet.decrypt(encrypted_data)
        return json.loads(decrypted_data)
    
    def _save_credentials(self, credentials: Dict[str, Any]):
        """Encrypt and save credentials"""
        if not self.fernet:
            raise ValueError("Encryption not initialized")
        
        encrypted_data = self.fernet.encrypt(json.dumps(credentials).encode())
        
        with open(self.credentials_file, "wb") as f:
            f.write(encrypted_data)
    
    def store_credential(self, service: str, credentials: Dict[str, Any]) -> bool:
        """
        Store credentials for a specific service
        
        Args:
            service: Service name (e.g., 'gmail', 'github')
            credentials: Dictionary of credentials to store
            
        Returns:
            bool: True if storage is successful
        """
        if not self.current_user:
            return False
        
        try:
            all_credentials = self._load_credentials()
            user_creds = all_credentials[self.current_user]
            
            # Initialize settings if not exists
            if "settings" not in user_creds:
                user_creds["settings"] = {}
                
            # Store service credentials
            user_creds["settings"][service] = credentials
            
            self._save_credentials(all_credentials)
            return True
        except Exception:
            return False
    
    def get_credential(self, service: str) -> Optional[Dict[str, Any]]:
        """
        Get credentials for a specific service
        
        Args:
            service: Service name (e.g., 'gmail', 'github')
            
        Returns:
            Optional[Dict[str, Any]]: Credentials if found
        """
        if not self.current_user:
            return None
        
        try:
            all_credentials = self._load_credentials()
            user_creds = all_credentials[self.current_user]
            
            if "settings" in user_creds and service in user_creds["settings"]:
                return user_creds["settings"][service]
            return None
        except Exception:
            return None
    
    def delete_credential(self, service: str) -> bool:
        """
        Delete credentials for a specific service
        
        Args:
            service: Service name (e.g., 'gmail', 'github')
            
        Returns:
            bool: True if deletion is successful
        """
        if not self.current_user:
            return False
        
        try:
            all_credentials = self._load_credentials()
            user_creds = all_credentials[self.current_user]
            
            if "settings" in user_creds and service in user_creds["settings"]:
                del user_creds["settings"][service]
                self._save_credentials(all_credentials)
                return True
            return False
        except Exception:
            return False
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.current_user is not None
    
    def get_current_user(self) -> Optional[str]:
        """Get current authenticated user email"""
        return self.current_user
    
    def logout(self):
        """Log out current user"""
        self.current_user = None
        self.fernet = None


# Create global credential manager
credential_manager = CredentialManager()