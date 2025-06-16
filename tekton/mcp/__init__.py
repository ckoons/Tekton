"""
Multimodal Cognitive Protocol (MCP)

This package provides the core components for multimodal information processing,
enabling standardized handling of text, code, images, and structured data.

The MCP implementation offers two approaches:
1. Legacy API: The original MCP implementation with class-based approach
2. FastMCP API: A decorator-based approach inspired by FastMCP
"""

from tekton.mcp.message import (
    MCPMessage, 
    MCPResponse,
    MCPContentItem,
    MCPContentType,
    validate_message
)
from tekton.mcp.context import (
    ContextManager,
    ContextMetadata,
    create_context,
    merge_contexts,
    enhance_context
)
from tekton.mcp.processor import (
    MessageProcessor,
    process_message,
    extract_content
)
from tekton.mcp.modality import (
    ModalityProcessor,
    TextProcessor,
    CodeProcessor,
    ImageProcessor,
    StructuredDataProcessor
)
from tekton.mcp.tool_registry import (
    ToolRegistry,
    register_tool,
    find_tools_by_capability,
    execute_tool
)

# Import FastMCP integration
try:
    from tekton.mcp.fastmcp import (
        mcp_tool,
        mcp_capability,
        mcp_processor,
        mcp_context,
        adapt_tool,
        adapt_processor,
        adapt_context,
        ToolSchema,
        ProcessorSchema,
        CapabilitySchema,
        ContextSchema,
        MCPClient,
        register_component
    )
    # FastMCP successfully imported
    _fastmcp_available = True
except ImportError:
    # FastMCP not available
    _fastmcp_available = False

__all__ = [
    # Message module
    "MCPMessage", "MCPResponse", "MCPContentItem", "MCPContentType", "validate_message",
    
    # Context module
    "ContextManager", "ContextMetadata", "create_context", "merge_contexts", "enhance_context",
    
    # Processor module
    "MessageProcessor", "process_message", "extract_content",
    
    # Modality module
    "ModalityProcessor", "TextProcessor", "CodeProcessor", "ImageProcessor", "StructuredDataProcessor",
    
    # Tool registry module
    "ToolRegistry", "register_tool", "find_tools_by_capability", "execute_tool"
]

# Add FastMCP exports if available
if _fastmcp_available:
    __all__.extend([
        # FastMCP decorators
        "mcp_tool", "mcp_capability", "mcp_processor", "mcp_context",
        
        # FastMCP adapters
        "adapt_tool", "adapt_processor", "adapt_context",
        
        # FastMCP schemas
        "ToolSchema", "ProcessorSchema", "CapabilitySchema", "ContextSchema",
        
        # FastMCP client
        "MCPClient", "register_component"
    ])