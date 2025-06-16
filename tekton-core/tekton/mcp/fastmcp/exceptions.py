"""
FastMCP Exceptions - Exception classes for MCP operations.

This module provides exception classes for various MCP error conditions.
"""

from typing import Optional, Any, Dict

class FastMCPError(Exception):
    """Base exception for FastMCP operations."""
    
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """
        Initialize FastMCP error.
        
        Args:
            message: Error message
            code: Optional error code
            details: Optional additional error details
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

class MCPProcessingError(FastMCPError):
    """Exception for MCP processing errors."""
    
    def __init__(self, message: str, tool_name: Optional[str] = None, **kwargs):
        """
        Initialize MCP processing error.
        
        Args:
            message: Error message
            tool_name: Optional tool name that caused the error
            **kwargs: Additional arguments passed to FastMCPError
        """
        super().__init__(message, **kwargs)
        self.tool_name = tool_name

class MCPValidationError(FastMCPError):
    """Exception for MCP validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None, **kwargs):
        """
        Initialize MCP validation error.
        
        Args:
            message: Error message
            field: Optional field name that failed validation
            **kwargs: Additional arguments passed to FastMCPError
        """
        super().__init__(message, **kwargs)
        self.field = field

class MCPConnectionError(FastMCPError):
    """Exception for MCP connection errors."""
    pass

class MCPTimeoutError(FastMCPError):
    """Exception for MCP timeout errors."""
    pass

class MCPAuthenticationError(FastMCPError):
    """Exception for MCP authentication errors."""
    pass