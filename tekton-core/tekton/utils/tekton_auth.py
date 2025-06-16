"""
Tekton Authentication Utility

This module provides standardized authentication mechanisms for Tekton components,
including token generation, validation, and permission checking.

Usage:
    from tekton.utils.tekton_auth import (
        create_token,
        validate_token,
        AuthManager,
        protect_route
    )
    
    # Create a token with permissions
    token = create_token(
        subject="user123",
        permissions=["read:components", "write:components"]
    )
    
    # Validate a token with required permissions
    payload = validate_token(
        token,
        required_permissions=["read:components"]
    )
    
    # Use with FastAPI routes
    @app.get("/api/protected")
    @protect_route(["read:data"])
    async def protected_route(token_payload: dict = Depends(get_token_payload)):
        return {"message": "This is protected", "user": token_payload["sub"]}
"""

import os
import json
import time
import secrets
import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, Optional, List, Set, Union, Callable, TypeVar, cast

from functools import wraps

# Import for JWT support
try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False

# Import for FastAPI support
try:
    from fastapi import Depends, HTTPException, Security, status
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    
    # Create stub classes for type checking
    class HTTPBearer:
        pass
    
    class HTTPAuthorizationCredentials:
        pass

# Import Tekton errors
from .tekton_errors import (
    TektonError,
    AuthenticationError,
    AuthorizationError,
    TokenExpiredError,
    InvalidCredentialsError,
    ConfigurationError
)

# Set up logger
logger = logging.getLogger(__name__)

# Default environment variable for auth secret
DEFAULT_SECRET_ENV_VAR = "TEKTON_AUTH_SECRET"

# Default token expiration (1 hour)
DEFAULT_TOKEN_EXPIRATION = 3600

# Type variable for decorator
F = TypeVar('F', bound=Callable[..., Any])


class AuthType(Enum):
    """Authentication types."""
    NONE = "none"
    JWT = "jwt"
    API_KEY = "api_key"
    BASIC = "basic"
    OAUTH = "oauth"


class Permission:
    """Standard permission constants."""
    # Component permissions
    COMPONENT_READ = "components:read"
    COMPONENT_WRITE = "components:write"
    COMPONENT_ADMIN = "components:admin"
    
    # Memory permissions
    MEMORY_READ = "memory:read"
    MEMORY_WRITE = "memory:write"
    MEMORY_ADMIN = "memory:admin"
    
    # LLM permissions
    LLM_READ = "llm:read"
    LLM_INVOKE = "llm:invoke"
    LLM_ADMIN = "llm:admin"
    
    # User permissions
    USER_READ = "users:read"
    USER_WRITE = "users:write"
    USER_ADMIN = "users:admin"
    
    # Admin permissions
    ADMIN = "admin"
    
    @classmethod
    def get_all(cls) -> List[str]:
        """Get all defined permissions."""
        return [
            value for name, value in vars(cls).items()
            if not name.startswith('_') and isinstance(value, str)
        ]


def create_token(
    subject: str,
    permissions: List[str],
    expiration: int = DEFAULT_TOKEN_EXPIRATION,
    secret_key: Optional[str] = None,
    algorithm: str = "HS256",
    issuer: Optional[str] = None,
    audience: Optional[str] = None,
    additional_claims: Optional[Dict[str, Any]] = None
) -> str:
    """
    Create a JWT authentication token.
    
    Args:
        subject: Token subject (user or component ID)
        permissions: List of permissions
        expiration: Token lifetime in seconds (default: 3600)
        secret_key: Secret key (from TEKTON_AUTH_SECRET env var if not provided)
        algorithm: JWT algorithm (default: HS256)
        issuer: Token issuer
        audience: Token audience
        additional_claims: Additional JWT claims
        
    Returns:
        JWT token string
        
    Raises:
        ConfigurationError: If secret key is not available
        AuthenticationError: If JWT module is not available
    """
    if not JWT_AVAILABLE:
        raise AuthenticationError("JWT module not available, install with: pip install pyjwt")
    
    # Get secret key from environment if not provided
    if secret_key is None:
        secret_key = os.environ.get(DEFAULT_SECRET_ENV_VAR)
        if not secret_key:
            raise ConfigurationError(f"Secret key not provided and {DEFAULT_SECRET_ENV_VAR} not set")
    
    # Create claims
    now = int(time.time())
    claims = {
        "sub": subject,
        "permissions": permissions,
        "iat": now,
        "exp": now + expiration
    }
    
    # Add optional claims
    if issuer:
        claims["iss"] = issuer
    
    if audience:
        claims["aud"] = audience
    
    # Add additional claims
    if additional_claims:
        claims.update(additional_claims)
    
    # Create token
    token = jwt.encode(claims, secret_key, algorithm=algorithm)
    
    return token


def validate_token(
    token: str,
    required_permissions: Optional[List[str]] = None,
    secret_key: Optional[str] = None,
    algorithms: Optional[List[str]] = None,
    verify_exp: bool = True,
    audience: Optional[Union[str, List[str]]] = None,
    issuer: Optional[str] = None
) -> Dict[str, Any]:
    """
    Validate an authentication token.
    
    Args:
        token: JWT token string
        required_permissions: Optional list of required permissions
        secret_key: Secret key (from TEKTON_AUTH_SECRET env var if not provided)
        algorithms: JWT algorithms to accept (default: ["HS256"])
        verify_exp: Whether to verify token expiration
        audience: Expected audience
        issuer: Expected issuer
        
    Returns:
        Token payload if valid
        
    Raises:
        ConfigurationError: If secret key is not available
        AuthenticationError: If token is invalid
        TokenExpiredError: If token is expired
        AuthorizationError: If token lacks required permissions
    """
    if not JWT_AVAILABLE:
        raise AuthenticationError("JWT module not available, install with: pip install pyjwt")
    
    # Get secret key from environment if not provided
    if secret_key is None:
        secret_key = os.environ.get(DEFAULT_SECRET_ENV_VAR)
        if not secret_key:
            raise ConfigurationError(f"Secret key not provided and {DEFAULT_SECRET_ENV_VAR} not set")
    
    # Default algorithms
    if algorithms is None:
        algorithms = ["HS256"]
    
    try:
        # Decode and verify token
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=algorithms,
            options={"verify_exp": verify_exp},
            audience=audience,
            issuer=issuer
        )
        
        # Check permissions if required
        if required_permissions:
            token_permissions = payload.get("permissions", [])
            
            # Check if token has admin permission
            if "admin" in token_permissions:
                # Admin has all permissions
                return payload
            
            # Check each required permission
            for permission in required_permissions:
                if permission not in token_permissions:
                    raise AuthorizationError(
                        f"Token lacks required permission: {permission}"
                    )
        
        return payload
    
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError("Token has expired")
    except jwt.InvalidTokenError as e:
        raise AuthenticationError(f"Invalid token: {str(e)}")


def create_api_key(length: int = 32) -> str:
    """
    Create a random API key.
    
    Args:
        length: Key length in bytes (default: 32)
        
    Returns:
        Random API key
    """
    return secrets.token_hex(length)


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key for storage.
    
    Args:
        api_key: API key to hash
        
    Returns:
        Hashed API key
    """
    import hashlib
    
    # Create salted hash
    salt = os.urandom(16)
    hash_obj = hashlib.sha256()
    hash_obj.update(salt)
    hash_obj.update(api_key.encode('utf-8'))
    
    # Return base64-encoded salt and hash
    import base64
    return base64.b64encode(salt + hash_obj.digest()).decode('utf-8')


def verify_api_key(api_key: str, hashed_key: str) -> bool:
    """
    Verify an API key against a stored hash.
    
    Args:
        api_key: API key to verify
        hashed_key: Previously hashed key
        
    Returns:
        True if API key is valid
    """
    import hashlib
    import base64
    
    try:
        # Decode hashed key
        decoded = base64.b64decode(hashed_key)
        
        # Extract salt and stored hash
        salt = decoded[:16]
        stored_hash = decoded[16:]
        
        # Hash the provided key with the same salt
        hash_obj = hashlib.sha256()
        hash_obj.update(salt)
        hash_obj.update(api_key.encode('utf-8'))
        
        # Compare hashes
        return hash_obj.digest() == stored_hash
    
    except Exception:
        return False


class AuthManager:
    """
    Authentication manager for Tekton components.
    
    This class provides a unified interface for component authentication,
    including token validation, permission checking, and API key management.
    """
    
    def __init__(
        self,
        auth_type: AuthType = AuthType.JWT,
        secret_key: Optional[str] = None,
        token_expiration: int = DEFAULT_TOKEN_EXPIRATION,
        jwt_algorithm: str = "HS256",
        jwt_issuer: Optional[str] = None,
        jwt_audience: Optional[str] = None
    ):
        """
        Initialize the authentication manager.
        
        Args:
            auth_type: Authentication type
            secret_key: Secret key (from TEKTON_AUTH_SECRET env var if not provided)
            token_expiration: Token lifetime in seconds
            jwt_algorithm: JWT algorithm
            jwt_issuer: JWT issuer
            jwt_audience: JWT audience
        """
        self.auth_type = auth_type
        self.token_expiration = token_expiration
        self.jwt_algorithm = jwt_algorithm
        self.jwt_issuer = jwt_issuer
        self.jwt_audience = jwt_audience
        
        # Get secret key from environment if not provided
        if secret_key is None and auth_type != AuthType.NONE:
            secret_key = os.environ.get(DEFAULT_SECRET_ENV_VAR)
            if not secret_key:
                secret_key = secrets.token_hex(32)
                logger.warning(
                    f"Secret key not provided and {DEFAULT_SECRET_ENV_VAR} not set, "
                    f"using generated key. This key will change on restart."
                )
        
        self.secret_key = secret_key
        
        # API key storage
        self.api_keys: Dict[str, Dict[str, Any]] = {}
    
    def create_token(
        self,
        subject: str,
        permissions: List[str],
        expiration: Optional[int] = None,
        additional_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a JWT authentication token.
        
        Args:
            subject: Token subject (user or component ID)
            permissions: List of permissions
            expiration: Token lifetime in seconds (default: from instance)
            additional_claims: Additional JWT claims
            
        Returns:
            JWT token string
            
        Raises:
            AuthenticationError: If auth type is not JWT or module not available
        """
        if self.auth_type != AuthType.JWT:
            raise AuthenticationError(f"Auth type is {self.auth_type.value}, not JWT")
        
        return create_token(
            subject=subject,
            permissions=permissions,
            expiration=expiration or self.token_expiration,
            secret_key=self.secret_key,
            algorithm=self.jwt_algorithm,
            issuer=self.jwt_issuer,
            audience=self.jwt_audience,
            additional_claims=additional_claims
        )
    
    def validate_token(
        self,
        token: str,
        required_permissions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Validate a JWT authentication token.
        
        Args:
            token: JWT token string
            required_permissions: Optional list of required permissions
            
        Returns:
            Token payload if valid
            
        Raises:
            AuthenticationError: If auth type is not JWT or token is invalid
            TokenExpiredError: If token is expired
            AuthorizationError: If token lacks required permissions
        """
        if self.auth_type != AuthType.JWT:
            raise AuthenticationError(f"Auth type is {self.auth_type.value}, not JWT")
        
        return validate_token(
            token=token,
            required_permissions=required_permissions,
            secret_key=self.secret_key,
            algorithms=[self.jwt_algorithm],
            audience=self.jwt_audience,
            issuer=self.jwt_issuer
        )
    
    def create_api_key(self, owner: str, permissions: List[str], expires_at: Optional[datetime] = None) -> str:
        """
        Create and store an API key.
        
        Args:
            owner: Key owner
            permissions: Key permissions
            expires_at: Optional expiration date
            
        Returns:
            API key
        """
        if self.auth_type != AuthType.API_KEY:
            raise AuthenticationError(f"Auth type is {self.auth_type.value}, not API_KEY")
        
        # Create key
        api_key = create_api_key()
        hashed_key = hash_api_key(api_key)
        
        # Store key info
        self.api_keys[hashed_key] = {
            "owner": owner,
            "permissions": permissions,
            "created_at": datetime.now().isoformat(),
            "expires_at": expires_at.isoformat() if expires_at else None
        }
        
        return api_key
    
    def validate_api_key(
        self,
        api_key: str,
        required_permissions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Validate an API key.
        
        Args:
            api_key: API key to validate
            required_permissions: Optional list of required permissions
            
        Returns:
            API key information if valid
            
        Raises:
            AuthenticationError: If auth type is not API_KEY or key is invalid
            TokenExpiredError: If key is expired
            AuthorizationError: If key lacks required permissions
        """
        if self.auth_type != AuthType.API_KEY:
            raise AuthenticationError(f"Auth type is {self.auth_type.value}, not API_KEY")
        
        # Find key in storage
        for hashed_key, key_info in self.api_keys.items():
            if verify_api_key(api_key, hashed_key):
                # Check expiration
                if key_info.get("expires_at"):
                    expires_at = datetime.fromisoformat(key_info["expires_at"])
                    if expires_at < datetime.now():
                        raise TokenExpiredError("API key has expired")
                
                # Check permissions if required
                if required_permissions:
                    key_permissions = key_info.get("permissions", [])
                    
                    # Check if key has admin permission
                    if "admin" in key_permissions:
                        # Admin has all permissions
                        return key_info
                    
                    # Check each required permission
                    for permission in required_permissions:
                        if permission not in key_permissions:
                            raise AuthorizationError(
                                f"API key lacks required permission: {permission}"
                            )
                
                return key_info
        
        raise AuthenticationError("Invalid API key")
    
    def revoke_api_key(self, api_key: str) -> bool:
        """
        Revoke an API key.
        
        Args:
            api_key: API key to revoke
            
        Returns:
            True if key was revoked
        """
        if self.auth_type != AuthType.API_KEY:
            raise AuthenticationError(f"Auth type is {self.auth_type.value}, not API_KEY")
        
        # Find and remove key
        for hashed_key, key_info in list(self.api_keys.items()):
            if verify_api_key(api_key, hashed_key):
                del self.api_keys[hashed_key]
                return True
        
        return False
    
    def get_all_api_keys(self) -> List[Dict[str, Any]]:
        """
        Get all API keys (without the keys themselves).
        
        Returns:
            List of API key information
        """
        if self.auth_type != AuthType.API_KEY:
            raise AuthenticationError(f"Auth type is {self.auth_type.value}, not API_KEY")
        
        return list(self.api_keys.values())


# FastAPI integration
if FASTAPI_AVAILABLE:
    # Security scheme
    security = HTTPBearer()
    
    def get_token_payload(credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict[str, Any]:
        """
        Get token payload from request.
        
        This function is intended to be used with FastAPI's dependency injection.
        
        Args:
            credentials: HTTP authorization credentials
            
        Returns:
            Token payload
            
        Raises:
            HTTPException: If token is invalid
        """
        try:
            payload = validate_token(credentials.credentials)
            return payload
        except TokenExpiredError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except AuthenticationError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"}
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Authentication error: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"}
            )
    
    def protect_route(required_permissions: Optional[List[str]] = None) -> Callable[[F], F]:
        """
        Decorator to protect a FastAPI route with permission requirements.
        
        Args:
            required_permissions: List of required permissions
            
        Returns:
            Route decorator
        """
        def decorator(func: F) -> F:
            @wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                # Get the token payload from kwargs
                token_payload = None
                for arg_name, arg_value in kwargs.items():
                    if isinstance(arg_value, dict) and "sub" in arg_value and "permissions" in arg_value:
                        token_payload = arg_value
                        break
                
                if not token_payload:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token payload not found in request",
                        headers={"WWW-Authenticate": "Bearer"}
                    )
                
                # Check permissions
                if required_permissions:
                    token_permissions = token_payload.get("permissions", [])
                    
                    # Check if token has admin permission
                    if "admin" in token_permissions:
                        # Admin has all permissions
                        return await func(*args, **kwargs)
                    
                    # Check each required permission
                    missing_permissions = []
                    for permission in required_permissions:
                        if permission not in token_permissions:
                            missing_permissions.append(permission)
                    
                    if missing_permissions:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Insufficient permissions. Missing: {', '.join(missing_permissions)}",
                            headers={"WWW-Authenticate": "Bearer"}
                        )
                
                # Call the original function
                return await func(*args, **kwargs)
            
            return cast(F, wrapper)
        
        return decorator
    
    def get_api_key(api_key: Optional[str] = None) -> str:
        """
        Get API key from request.
        
        This function is intended to be used with FastAPI's dependency injection.
        
        Args:
            api_key: API key from query parameter
            
        Returns:
            API key
            
        Raises:
            HTTPException: If API key is not provided
        """
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key required",
                headers={"WWW-Authenticate": "ApiKey"}
            )
        
        return api_key
    
    def protect_api_route(
        auth_manager: AuthManager,
        required_permissions: Optional[List[str]] = None
    ) -> Callable[[F], F]:
        """
        Decorator to protect a FastAPI route with API key permission requirements.
        
        Args:
            auth_manager: Authentication manager instance
            required_permissions: List of required permissions
            
        Returns:
            Route decorator
        """
        def decorator(func: F) -> F:
            @wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                # Get the API key from kwargs
                api_key = None
                for arg_name, arg_value in kwargs.items():
                    if arg_name == "api_key" and isinstance(arg_value, str):
                        api_key = arg_value
                        break
                
                if not api_key:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="API key not found in request",
                        headers={"WWW-Authenticate": "ApiKey"}
                    )
                
                # Validate API key
                try:
                    key_info = auth_manager.validate_api_key(
                        api_key,
                        required_permissions
                    )
                    
                    # Store key info in kwargs
                    kwargs["key_info"] = key_info
                    
                    # Call the original function
                    return await func(*args, **kwargs)
                
                except TokenExpiredError:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="API key has expired",
                        headers={"WWW-Authenticate": "ApiKey"}
                    )
                except AuthenticationError as e:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=str(e),
                        headers={"WWW-Authenticate": "ApiKey"}
                    )
                except AuthorizationError as e:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=str(e),
                        headers={"WWW-Authenticate": "ApiKey"}
                    )
                except Exception as e:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"Authentication error: {str(e)}",
                        headers={"WWW-Authenticate": "ApiKey"}
                    )
            
            return cast(F, wrapper)
        
        return decorator


# Utility functions

def get_secret_key() -> str:
    """
    Get the authentication secret key from environment.
    
    Returns:
        Secret key
        
    Raises:
        ConfigurationError: If secret key is not available
    """
    secret_key = os.environ.get(DEFAULT_SECRET_ENV_VAR)
    if not secret_key:
        raise ConfigurationError(f"{DEFAULT_SECRET_ENV_VAR} environment variable not set")
    
    return secret_key


def has_permission(token_permissions: List[str], required_permission: str) -> bool:
    """
    Check if token permissions include a required permission.
    
    Args:
        token_permissions: Permissions from token
        required_permission: Required permission
        
    Returns:
        True if token has the required permission
    """
    # Admin permission grants all permissions
    if "admin" in token_permissions:
        return True
    
    # Check for exact match
    if required_permission in token_permissions:
        return True
    
    # Check for wildcard patterns
    parts = required_permission.split(':')
    if len(parts) == 2:
        resource, action = parts
        
        # Check for resource wildcard
        if f"{resource}:*" in token_permissions:
            return True
    
    return False


def has_all_permissions(token_permissions: List[str], required_permissions: List[str]) -> bool:
    """
    Check if token permissions include all required permissions.
    
    Args:
        token_permissions: Permissions from token
        required_permissions: Required permissions
        
    Returns:
        True if token has all required permissions
    """
    # Admin permission grants all permissions
    if "admin" in token_permissions:
        return True
    
    # Check each required permission
    for permission in required_permissions:
        if not has_permission(token_permissions, permission):
            return False
    
    return True


def has_any_permission(token_permissions: List[str], required_permissions: List[str]) -> bool:
    """
    Check if token permissions include any required permission.
    
    Args:
        token_permissions: Permissions from token
        required_permissions: Required permissions
        
    Returns:
        True if token has any required permission
    """
    # Admin permission grants all permissions
    if "admin" in token_permissions:
        return True
    
    # Check each required permission
    for permission in required_permissions:
        if has_permission(token_permissions, permission):
            return True
    
    return False