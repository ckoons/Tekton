"""
Security features for A2A Protocol v0.2.1

Provides JWT-based authentication, role-based access control,
and secure communication capabilities.
"""

import os
import secrets
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Set, Callable
from functools import wraps
import jwt
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import hmac

from tekton.models.base import TektonBaseModel
from .errors import UnauthorizedError, InvalidRequestError


# Configuration
JWT_SECRET_KEY = os.getenv("A2A_JWT_SECRET", secrets.token_urlsafe(32))
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24
JWT_REFRESH_EXPIRATION_DAYS = 30


class Permission(str, Enum):
    """A2A permissions"""
    # Agent management
    AGENT_REGISTER = "agent.register"
    AGENT_UPDATE = "agent.update"
    AGENT_DELETE = "agent.delete"
    AGENT_VIEW = "agent.view"
    
    # Task management
    TASK_CREATE = "task.create"
    TASK_ASSIGN = "task.assign"
    TASK_UPDATE = "task.update"
    TASK_DELETE = "task.delete"
    TASK_VIEW = "task.view"
    
    # Workflow management
    WORKFLOW_CREATE = "workflow.create"
    WORKFLOW_START = "workflow.start"
    WORKFLOW_CANCEL = "workflow.cancel"
    WORKFLOW_VIEW = "workflow.view"
    
    # Conversation management
    CONVERSATION_CREATE = "conversation.create"
    CONVERSATION_JOIN = "conversation.join"
    CONVERSATION_MODERATE = "conversation.moderate"
    CONVERSATION_VIEW = "conversation.view"
    
    # Channel management
    CHANNEL_CREATE = "channel.create"
    CHANNEL_PUBLISH = "channel.publish"
    CHANNEL_SUBSCRIBE = "channel.subscribe"
    CHANNEL_MANAGE = "channel.manage"
    
    # System permissions
    SYSTEM_ADMIN = "system.admin"
    SYSTEM_MONITOR = "system.monitor"


class Role(str, Enum):
    """A2A roles with associated permissions"""
    ADMIN = "admin"
    OPERATOR = "operator"
    AGENT = "agent"
    OBSERVER = "observer"
    GUEST = "guest"


# Role to permissions mapping
ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.ADMIN: {
        # Admins have all permissions
        Permission.AGENT_REGISTER, Permission.AGENT_UPDATE, Permission.AGENT_DELETE, Permission.AGENT_VIEW,
        Permission.TASK_CREATE, Permission.TASK_ASSIGN, Permission.TASK_UPDATE, Permission.TASK_DELETE, Permission.TASK_VIEW,
        Permission.WORKFLOW_CREATE, Permission.WORKFLOW_START, Permission.WORKFLOW_CANCEL, Permission.WORKFLOW_VIEW,
        Permission.CONVERSATION_CREATE, Permission.CONVERSATION_JOIN, Permission.CONVERSATION_MODERATE, Permission.CONVERSATION_VIEW,
        Permission.CHANNEL_CREATE, Permission.CHANNEL_PUBLISH, Permission.CHANNEL_SUBSCRIBE, Permission.CHANNEL_MANAGE,
        Permission.SYSTEM_ADMIN, Permission.SYSTEM_MONITOR
    },
    Role.OPERATOR: {
        # Operators can manage tasks and workflows
        Permission.AGENT_VIEW,
        Permission.TASK_CREATE, Permission.TASK_ASSIGN, Permission.TASK_UPDATE, Permission.TASK_VIEW,
        Permission.WORKFLOW_CREATE, Permission.WORKFLOW_START, Permission.WORKFLOW_CANCEL, Permission.WORKFLOW_VIEW,
        Permission.CONVERSATION_CREATE, Permission.CONVERSATION_JOIN, Permission.CONVERSATION_VIEW,
        Permission.CHANNEL_PUBLISH, Permission.CHANNEL_SUBSCRIBE,
        Permission.SYSTEM_MONITOR
    },
    Role.AGENT: {
        # Agents can work on tasks and participate in conversations
        Permission.AGENT_VIEW,
        Permission.TASK_CREATE, Permission.TASK_UPDATE, Permission.TASK_VIEW,
        Permission.WORKFLOW_VIEW,
        Permission.CONVERSATION_JOIN, Permission.CONVERSATION_VIEW,
        Permission.CHANNEL_PUBLISH, Permission.CHANNEL_SUBSCRIBE
    },
    Role.OBSERVER: {
        # Observers can only view
        Permission.AGENT_VIEW,
        Permission.TASK_VIEW,
        Permission.WORKFLOW_VIEW,
        Permission.CONVERSATION_VIEW,
        Permission.CHANNEL_SUBSCRIBE
    },
    Role.GUEST: {
        # Guests have minimal permissions
        Permission.AGENT_VIEW
    }
}


@dataclass
class SecurityContext:
    """Security context for authenticated requests"""
    agent_id: str
    role: Role
    permissions: Set[Permission] = field(default_factory=set)
    token_id: str = field(default_factory=lambda: secrets.token_urlsafe(16))
    issued_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    custom_claims: Dict[str, Any] = field(default_factory=dict)
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if context has a specific permission"""
        return permission in self.permissions
    
    def has_any_permission(self, permissions: List[Permission]) -> bool:
        """Check if context has any of the given permissions"""
        return any(p in self.permissions for p in permissions)
    
    def has_all_permissions(self, permissions: List[Permission]) -> bool:
        """Check if context has all of the given permissions"""
        return all(p in self.permissions for p in permissions)


class TokenManager:
    """Manages JWT tokens for authentication"""
    
    def __init__(self, secret_key: str = JWT_SECRET_KEY):
        self.secret_key = secret_key
        self._revoked_tokens: Set[str] = set()
        self._refresh_tokens: Dict[str, str] = {}  # refresh_token -> agent_id
    
    def create_token(
        self,
        agent_id: str,
        role: Role,
        permissions: Optional[Set[Permission]] = None,
        custom_claims: Optional[Dict[str, Any]] = None,
        expiration_hours: int = JWT_EXPIRATION_HOURS
    ) -> tuple[str, str]:
        """
        Create JWT access and refresh tokens.
        
        Returns:
            Tuple of (access_token, refresh_token)
        """
        now = datetime.now(timezone.utc)
        token_id = secrets.token_urlsafe(16)
        
        # If no permissions specified, use role defaults
        if permissions is None:
            permissions = ROLE_PERMISSIONS.get(role, set())
        
        # Access token payload
        payload = {
            "sub": agent_id,
            "role": role.value,
            "permissions": [p.value for p in permissions],
            "jti": token_id,
            "iat": now,
            "exp": now + timedelta(hours=expiration_hours),
        }
        
        # Add custom claims
        if custom_claims:
            payload.update(custom_claims)
        
        # Create access token
        access_token = jwt.encode(payload, self.secret_key, algorithm=JWT_ALGORITHM)
        
        # Create refresh token
        refresh_token_id = secrets.token_urlsafe(32)
        refresh_payload = {
            "sub": agent_id,
            "jti": refresh_token_id,
            "iat": now,
            "exp": now + timedelta(days=JWT_REFRESH_EXPIRATION_DAYS),
            "type": "refresh"
        }
        refresh_token = jwt.encode(refresh_payload, self.secret_key, algorithm=JWT_ALGORITHM)
        
        # Store refresh token
        self._refresh_tokens[refresh_token_id] = agent_id
        
        return access_token, refresh_token
    
    def verify_token(self, token: str) -> SecurityContext:
        """
        Verify and decode a JWT token.
        
        Returns:
            SecurityContext for the authenticated request
            
        Raises:
            UnauthorizedError: If token is invalid or expired
        """
        try:
            # Decode token
            payload = jwt.decode(token, self.secret_key, algorithms=[JWT_ALGORITHM])
            
            # Check if token is revoked
            token_id = payload.get("jti")
            if token_id in self._revoked_tokens:
                raise UnauthorizedError("Token has been revoked")
            
            # Check token type
            if payload.get("type") == "refresh":
                raise UnauthorizedError("Cannot use refresh token for authentication")
            
            # Create security context
            context = SecurityContext(
                agent_id=payload["sub"],
                role=Role(payload["role"]),
                permissions={Permission(p) for p in payload.get("permissions", [])},
                token_id=token_id,
                issued_at=datetime.fromtimestamp(payload["iat"], tz=timezone.utc),
                expires_at=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
                custom_claims={k: v for k, v in payload.items() 
                              if k not in ["sub", "role", "permissions", "jti", "iat", "exp"]}
            )
            
            return context
            
        except jwt.ExpiredSignatureError:
            raise UnauthorizedError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise UnauthorizedError(f"Invalid token: {str(e)}")
    
    def refresh_token(self, refresh_token: str, role: Optional[Role] = None) -> tuple[str, str]:
        """
        Refresh an access token using a refresh token.
        
        Returns:
            Tuple of (new_access_token, new_refresh_token)
        """
        try:
            # Decode refresh token
            payload = jwt.decode(refresh_token, self.secret_key, algorithms=[JWT_ALGORITHM])
            
            # Verify it's a refresh token
            if payload.get("type") != "refresh":
                raise UnauthorizedError("Not a refresh token")
            
            # Check if refresh token is valid
            refresh_token_id = payload.get("jti")
            if refresh_token_id not in self._refresh_tokens:
                raise UnauthorizedError("Invalid refresh token")
            
            agent_id = payload["sub"]
            
            # Revoke old refresh token
            del self._refresh_tokens[refresh_token_id]
            
            # Create new tokens
            return self.create_token(agent_id, role or Role.AGENT)
            
        except jwt.ExpiredSignatureError:
            raise UnauthorizedError("Refresh token has expired")
        except jwt.InvalidTokenError as e:
            raise UnauthorizedError(f"Invalid refresh token: {str(e)}")
    
    def revoke_token(self, token_id: str) -> None:
        """Revoke a token by its ID"""
        self._revoked_tokens.add(token_id)
    
    def revoke_refresh_token(self, refresh_token_id: str) -> None:
        """Revoke a refresh token"""
        self._refresh_tokens.pop(refresh_token_id, None)


class AccessControl:
    """Role-based access control system"""
    
    def __init__(self):
        self._custom_permissions: Dict[str, Set[Permission]] = {}
        self._resource_permissions: Dict[str, Dict[str, Set[Permission]]] = {}
    
    def grant_permission(self, agent_id: str, permission: Permission) -> None:
        """Grant a specific permission to an agent"""
        if agent_id not in self._custom_permissions:
            self._custom_permissions[agent_id] = set()
        self._custom_permissions[agent_id].add(permission)
    
    def revoke_permission(self, agent_id: str, permission: Permission) -> None:
        """Revoke a specific permission from an agent"""
        if agent_id in self._custom_permissions:
            self._custom_permissions[agent_id].discard(permission)
    
    def set_resource_permission(
        self,
        resource_type: str,
        resource_id: str,
        agent_id: str,
        permissions: Set[Permission]
    ) -> None:
        """Set permissions for a specific resource"""
        if resource_type not in self._resource_permissions:
            self._resource_permissions[resource_type] = {}
        
        if resource_id not in self._resource_permissions[resource_type]:
            self._resource_permissions[resource_type][resource_id] = {}
        
        self._resource_permissions[resource_type][resource_id][agent_id] = permissions
    
    def check_permission(
        self,
        context: SecurityContext,
        permission: Permission,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None
    ) -> bool:
        """Check if a security context has permission for an action"""
        # Check role-based permissions
        if permission in context.permissions:
            return True
        
        # Check custom permissions
        custom_perms = self._custom_permissions.get(context.agent_id, set())
        if permission in custom_perms:
            return True
        
        # Check resource-specific permissions
        if resource_type and resource_id:
            resource_perms = (self._resource_permissions
                            .get(resource_type, {})
                            .get(resource_id, {})
                            .get(context.agent_id, set()))
            if permission in resource_perms:
                return True
        
        # Check for system admin override
        if Permission.SYSTEM_ADMIN in context.permissions:
            return True
        
        return False
    
    def filter_by_permission(
        self,
        context: SecurityContext,
        items: List[Dict[str, Any]],
        permission: Permission,
        resource_type: str,
        id_field: str = "id"
    ) -> List[Dict[str, Any]]:
        """Filter a list of items by permission"""
        filtered = []
        
        for item in items:
            resource_id = item.get(id_field)
            if self.check_permission(context, permission, resource_type, resource_id):
                filtered.append(item)
        
        return filtered


def require_permission(permission: Permission, resource_type: Optional[str] = None):
    """
    Decorator to require a specific permission for a method.
    
    The decorated function must accept 'security_context' as a keyword argument.
    If resource_type is specified, the function must also return or accept a
    resource_id parameter.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Extract security context
            context = kwargs.get('security_context')
            if not context or not isinstance(context, SecurityContext):
                raise UnauthorizedError("No valid security context provided")
            
            # Extract resource_id if needed
            resource_id = None
            if resource_type:
                # Try to get from kwargs first
                resource_id = kwargs.get('resource_id') or kwargs.get(f'{resource_type}_id')
                
                # Try to get from positional args if it's the first argument
                if not resource_id and args:
                    resource_id = args[0] if isinstance(args[0], str) else None
            
            # Get access control instance (should be injected or global)
            access_control = kwargs.get('access_control') or AccessControl()
            
            # Check permission
            if not access_control.check_permission(context, permission, resource_type, resource_id):
                raise UnauthorizedError(
                    f"Permission denied: {permission.value} required"
                )
            
            return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Extract security context
            context = kwargs.get('security_context')
            if not context or not isinstance(context, SecurityContext):
                raise UnauthorizedError("No valid security context provided")
            
            # Extract resource_id if needed
            resource_id = None
            if resource_type:
                resource_id = kwargs.get('resource_id') or kwargs.get(f'{resource_type}_id')
                if not resource_id and args:
                    resource_id = args[0] if isinstance(args[0], str) else None
            
            # Get access control instance
            access_control = kwargs.get('access_control') or AccessControl()
            
            # Check permission
            if not access_control.check_permission(context, permission, resource_type, resource_id):
                raise UnauthorizedError(
                    f"Permission denied: {permission.value} required"
                )
            
            return func(*args, **kwargs)
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def require_any_permission(*permissions: Permission):
    """Decorator to require any of the specified permissions"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            context = kwargs.get('security_context')
            if not context or not isinstance(context, SecurityContext):
                raise UnauthorizedError("No valid security context provided")
            
            if not context.has_any_permission(list(permissions)):
                raise UnauthorizedError(
                    f"Permission denied: one of {[p.value for p in permissions]} required"
                )
            
            return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            context = kwargs.get('security_context')
            if not context or not isinstance(context, SecurityContext):
                raise UnauthorizedError("No valid security context provided")
            
            if not context.has_any_permission(list(permissions)):
                raise UnauthorizedError(
                    f"Permission denied: one of {[p.value for p in permissions]} required"
                )
            
            return func(*args, **kwargs)
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class MessageSigner:
    """Signs and verifies messages for secure communication"""
    
    def __init__(self, secret_key: str = JWT_SECRET_KEY):
        self.secret_key = secret_key.encode()
    
    def sign_message(self, message: Dict[str, Any], agent_id: str) -> str:
        """Sign a message with HMAC"""
        # Create canonical representation
        message_copy = message.copy()
        message_copy['agent_id'] = agent_id
        message_copy['timestamp'] = datetime.now(timezone.utc).isoformat()
        
        # Sort keys for consistent hashing
        canonical = json.dumps(message_copy, sort_keys=True)
        
        # Create signature
        signature = hmac.new(
            self.secret_key,
            canonical.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def verify_message(
        self,
        message: Dict[str, Any],
        signature: str,
        agent_id: str,
        max_age_seconds: int = 300
    ) -> bool:
        """Verify a message signature"""
        try:
            # Check timestamp
            timestamp_str = message.get('timestamp')
            if not timestamp_str:
                return False
            
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            age = (datetime.now(timezone.utc) - timestamp).total_seconds()
            
            if age > max_age_seconds:
                return False
            
            # Verify agent_id matches
            if message.get('agent_id') != agent_id:
                return False
            
            # Recreate signature with same canonical representation
            canonical = json.dumps(message, sort_keys=True)
            expected_signature = hmac.new(
                self.secret_key,
                canonical.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Constant-time comparison
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception:
            return False


# Import json for message signing
import json