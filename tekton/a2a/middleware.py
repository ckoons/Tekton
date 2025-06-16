"""
Security middleware for A2A Protocol v0.2.1

Provides authentication and authorization middleware for
securing A2A protocol communications.
"""

from typing import Dict, Any, Optional, Callable, List
from functools import wraps
import logging

from .jsonrpc import JSONRPCRequest, JSONRPCResponse, create_error_response
from .errors import UnauthorizedError, InvalidRequestError
from .security import (
    TokenManager, SecurityContext, AccessControl,
    Permission, Role, MessageSigner
)


logger = logging.getLogger(__name__)


class SecurityMiddleware:
    """Middleware for handling authentication and authorization"""
    
    def __init__(
        self,
        token_manager: TokenManager,
        access_control: AccessControl,
        message_signer: Optional[MessageSigner] = None,
        exempt_methods: Optional[List[str]] = None
    ):
        """
        Initialize security middleware.
        
        Args:
            token_manager: Token manager for JWT operations
            access_control: Access control system
            message_signer: Optional message signer for secure communication
            exempt_methods: List of methods that don't require authentication
        """
        self.token_manager = token_manager
        self.access_control = access_control
        self.message_signer = message_signer or MessageSigner()
        
        # Methods that don't require authentication
        self.exempt_methods = set(exempt_methods or [
            "agent.register",  # Allow agents to register
            "auth.login",      # Allow login without auth
            "auth.refresh",    # Allow token refresh
            "discovery.list",  # Allow public discovery
        ])
        
        # Method to required permissions mapping
        self.method_permissions: Dict[str, List[Permission]] = {
            # Agent methods
            "agent.update": [Permission.AGENT_UPDATE],
            "agent.delete": [Permission.AGENT_DELETE],
            "agent.status": [Permission.AGENT_VIEW],
            "agent.list": [Permission.AGENT_VIEW],
            
            # Task methods
            "task.create": [Permission.TASK_CREATE],
            "task.assign": [Permission.TASK_ASSIGN],
            "task.update": [Permission.TASK_UPDATE],
            "task.complete": [Permission.TASK_UPDATE],
            "task.fail": [Permission.TASK_UPDATE],
            "task.cancel": [Permission.TASK_UPDATE],
            "task.list": [Permission.TASK_VIEW],
            "task.get": [Permission.TASK_VIEW],
            
            # Workflow methods
            "workflow.create": [Permission.WORKFLOW_CREATE],
            "workflow.create_sequential": [Permission.WORKFLOW_CREATE],
            "workflow.create_parallel": [Permission.WORKFLOW_CREATE],
            "workflow.create_pipeline": [Permission.WORKFLOW_CREATE],
            "workflow.create_fanout": [Permission.WORKFLOW_CREATE],
            "workflow.start": [Permission.WORKFLOW_START],
            "workflow.cancel": [Permission.WORKFLOW_CANCEL],
            "workflow.list": [Permission.WORKFLOW_VIEW],
            "workflow.info": [Permission.WORKFLOW_VIEW],
            
            # Conversation methods
            "conversation.create": [Permission.CONVERSATION_CREATE],
            "conversation.join": [Permission.CONVERSATION_JOIN],
            "conversation.leave": [Permission.CONVERSATION_JOIN],
            "conversation.send": [Permission.CONVERSATION_JOIN],
            "conversation.grant_turn": [Permission.CONVERSATION_MODERATE],
            "conversation.end": [Permission.CONVERSATION_MODERATE],
            "conversation.list": [Permission.CONVERSATION_VIEW],
            "conversation.info": [Permission.CONVERSATION_VIEW],
            
            # Channel methods
            "channel.create": [Permission.CHANNEL_CREATE],
            "channel.publish": [Permission.CHANNEL_PUBLISH],
            "channel.subscribe": [Permission.CHANNEL_SUBSCRIBE],
            "channel.unsubscribe": [Permission.CHANNEL_SUBSCRIBE],
            "channel.list": [Permission.CHANNEL_SUBSCRIBE],
            "channel.info": [Permission.CHANNEL_SUBSCRIBE],
        }
    
    async def process_request(
        self,
        request: JSONRPCRequest,
        headers: Optional[Dict[str, str]] = None
    ) -> tuple[JSONRPCRequest, Optional[SecurityContext]]:
        """
        Process incoming request for security.
        
        Returns:
            Tuple of (processed_request, security_context)
            
        Raises:
            UnauthorizedError: If authentication fails
        """
        # Check if method is exempt from authentication
        if request.method in self.exempt_methods:
            return request, None
        
        # Extract token from headers
        if not headers:
            raise UnauthorizedError("No authorization header provided")
        
        auth_header = headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise UnauthorizedError("Invalid authorization header format")
        
        token = auth_header[7:]  # Remove "Bearer " prefix
        
        # Verify token
        try:
            security_context = self.token_manager.verify_token(token)
        except UnauthorizedError:
            raise
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            raise UnauthorizedError("Token verification failed")
        
        # Check method permissions
        required_permissions = self.method_permissions.get(request.method, [])
        if required_permissions:
            has_permission = any(
                self.access_control.check_permission(security_context, perm)
                for perm in required_permissions
            )
            
            if not has_permission:
                raise UnauthorizedError(
                    f"Insufficient permissions for method: {request.method}"
                )
        
        # Verify message signature if provided
        if headers.get("X-A2A-Signature"):
            signature = headers["X-A2A-Signature"]
            message_data = {
                "method": request.method,
                "params": request.params,
                "id": request.id
            }
            
            if not self.message_signer.verify_message(
                message_data,
                signature,
                security_context.agent_id
            ):
                raise UnauthorizedError("Invalid message signature")
        
        # Add security context to request params
        if isinstance(request.params, dict):
            request.params["_security_context"] = security_context
        
        return request, security_context
    
    def create_auth_methods(self) -> Dict[str, Callable]:
        """Create authentication-related RPC methods"""
        
        async def auth_login(username: str, password: str) -> Dict[str, Any]:
            """Authenticate and receive tokens"""
            # In production, verify credentials against a database
            # For now, simple demo authentication
            if username == "admin" and password == "admin":
                agent_id = "admin-agent"
                role = Role.ADMIN
            elif username == "agent" and password == "agent":
                agent_id = f"agent-{username}"
                role = Role.AGENT
            else:
                raise UnauthorizedError("Invalid credentials")
            
            # Create tokens
            access_token, refresh_token = self.token_manager.create_token(
                agent_id=agent_id,
                role=role
            )
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "agent_id": agent_id,
                "role": role.value
            }
        
        async def auth_refresh(refresh_token: str) -> Dict[str, Any]:
            """Refresh access token"""
            try:
                access_token, new_refresh_token = self.token_manager.refresh_token(
                    refresh_token
                )
                
                return {
                    "access_token": access_token,
                    "refresh_token": new_refresh_token
                }
            except UnauthorizedError:
                raise
            except Exception as e:
                raise InvalidRequestError(f"Token refresh failed: {str(e)}")
        
        async def auth_logout(
            token_id: Optional[str] = None,
            _security_context: Optional[SecurityContext] = None
        ) -> Dict[str, Any]:
            """Logout and revoke tokens"""
            if _security_context:
                # Revoke current token
                self.token_manager.revoke_token(_security_context.token_id)
            elif token_id:
                # Revoke specific token
                self.token_manager.revoke_token(token_id)
            
            return {"success": True}
        
        async def auth_verify(
            _security_context: Optional[SecurityContext] = None
        ) -> Dict[str, Any]:
            """Verify current authentication status"""
            if not _security_context:
                raise UnauthorizedError("Not authenticated")
            
            return {
                "agent_id": _security_context.agent_id,
                "role": _security_context.role.value,
                "permissions": [p.value for p in _security_context.permissions],
                "expires_at": _security_context.expires_at.isoformat() if _security_context.expires_at else None
            }
        
        return {
            "auth.login": auth_login,
            "auth.refresh": auth_refresh,
            "auth.logout": auth_logout,
            "auth.verify": auth_verify
        }


def apply_security_middleware(
    dispatcher,
    token_manager: TokenManager,
    access_control: AccessControl,
    exempt_methods: Optional[List[str]] = None
) -> SecurityMiddleware:
    """
    Apply security middleware to a method dispatcher.
    
    This wraps all methods to check authentication and authorization
    before execution.
    """
    middleware = SecurityMiddleware(
        token_manager=token_manager,
        access_control=access_control,
        exempt_methods=exempt_methods
    )
    
    # Register auth methods
    auth_methods = middleware.create_auth_methods()
    for method_name, method_func in auth_methods.items():
        dispatcher.register_method(method_name, method_func)
    
    # Wrap existing methods with security checks
    original_dispatch = dispatcher.dispatch
    
    async def secure_dispatch(request: JSONRPCRequest, **kwargs) -> JSONRPCResponse:
        """Dispatch with security checks"""
        try:
            # Get headers from kwargs
            headers = kwargs.get("headers", {})
            
            # Process security
            processed_request, security_context = await middleware.process_request(
                request, headers
            )
            
            # Add security context to kwargs
            if security_context:
                kwargs["security_context"] = security_context
                kwargs["access_control"] = middleware.access_control
            
            # Call original dispatch (remove headers from kwargs as original doesn't accept it)
            clean_kwargs = {k: v for k, v in kwargs.items() if k != 'headers'}
            return await original_dispatch(processed_request, **clean_kwargs)
            
        except UnauthorizedError as e:
            return create_error_response(
                request.id,
                code=-32002,  # Unauthorized error code
                message=str(e)
            )
        except Exception as e:
            logger.error(f"Security middleware error: {e}")
            return create_error_response(
                request.id,
                code=-32603,  # Internal error
                message="Security processing failed"
            )
    
    # Replace dispatch method
    dispatcher.dispatch = secure_dispatch
    
    return middleware


def secure_method(permission: Permission):
    """
    Decorator to secure individual methods with permission checks.
    
    Can be used on methods registered with the dispatcher.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract security context
            security_context = kwargs.get("_security_context")
            if not security_context:
                raise UnauthorizedError("No security context available")
            
            # Check permission
            access_control = kwargs.get("access_control", AccessControl())
            if not access_control.check_permission(security_context, permission):
                raise UnauthorizedError(
                    f"Permission denied: {permission.value} required"
                )
            
            # Call original function
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator