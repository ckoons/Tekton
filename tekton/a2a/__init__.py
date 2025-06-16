"""
Tekton A2A (Agent-to-Agent) Protocol v2 Implementation

This module implements the A2A Protocol v0.2.1 specification for inter-agent
communication within the Tekton ecosystem, using JSON-RPC 2.0 as the message format.

Key Components:
- JSON-RPC 2.0 message handling
- Agent registration and discovery
- Task lifecycle management
- Agent Card format compliance
"""

from .jsonrpc import (
    JSONRPCRequest,
    JSONRPCResponse,
    JSONRPCError,
    JSONRPCBatch,
    parse_jsonrpc_message,
    create_error_response,
    create_success_response
)

from .agent import (
    AgentCard,
    AgentRegistry,
    AgentStatus
)

from .task import (
    Task,
    TaskState,
    TaskManager,
    TaskUpdate
)

from .discovery import (
    DiscoveryService,
    AgentQuery
)

from .errors import (
    A2AError,
    InvalidRequestError,
    MethodNotFoundError,
    InvalidParamsError,
    InternalError,
    ParseError
)

from .methods import (
    MethodDispatcher,
    StandardA2AMethods,
    create_standard_dispatcher
)

# Import streaming components
from .streaming import (
    SSEManager,
    SSEEvent,
    create_sse_response,
    EventType,
    StreamEvent,
    TaskEvent,
    AgentEvent,
    SubscriptionManager,
    Subscription,
    websocket_manager,
    handle_websocket
)

# Import conversation components
from .conversation import (
    Conversation,
    ConversationRole,
    ConversationState,
    TurnTakingMode,
    ConversationParticipant,
    ConversationMessage
)
from .conversation_manager import ConversationManager

# Import task coordination components
from .task_coordination import (
    TaskCoordinator,
    CoordinationPattern,
    DependencyType,
    TaskWorkflow,
    TaskDependency,
    ConditionalRule
)

# Import security components
from .security import (
    TokenManager,
    AccessControl,
    SecurityContext,
    Permission,
    Role,
    MessageSigner,
    require_permission,
    require_any_permission
)

from .middleware import (
    SecurityMiddleware,
    apply_security_middleware,
    secure_method
)

__all__ = [
    # JSON-RPC
    'JSONRPCRequest',
    'JSONRPCResponse',
    'JSONRPCError',
    'JSONRPCBatch',
    'parse_jsonrpc_message',
    'create_error_response',
    'create_success_response',
    
    # Agent
    'AgentCard',
    'AgentRegistry',
    'AgentStatus',
    
    # Task
    'Task',
    'TaskState',
    'TaskManager',
    'TaskUpdate',
    
    # Discovery
    'DiscoveryService',
    'AgentQuery',
    
    # Methods
    'MethodDispatcher',
    'StandardA2AMethods',
    'create_standard_dispatcher',
    
    # Errors
    'A2AError',
    'InvalidRequestError',
    'MethodNotFoundError',
    'InvalidParamsError',
    'InternalError',
    'ParseError',
    
    # Streaming
    'SSEManager',
    'SSEEvent',
    'create_sse_response',
    'EventType',
    'StreamEvent',
    'TaskEvent',
    'AgentEvent',
    'SubscriptionManager',
    'Subscription',
    'websocket_manager',
    'handle_websocket',
    
    # Conversations
    'Conversation',
    'ConversationRole',
    'ConversationState',
    'TurnTakingMode',
    'ConversationParticipant',
    'ConversationMessage',
    'ConversationManager',
    
    # Task Coordination
    'TaskCoordinator',
    'CoordinationPattern',
    'DependencyType',
    'TaskWorkflow',
    'TaskDependency',
    'ConditionalRule',
    
    # Security
    'TokenManager',
    'AccessControl',
    'SecurityContext',
    'Permission',
    'Role',
    'MessageSigner',
    'require_permission',
    'require_any_permission',
    'SecurityMiddleware',
    'apply_security_middleware',
    'secure_method'
]

__version__ = '2.0.0'