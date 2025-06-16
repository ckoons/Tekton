"""
Exceptions for the agent runner.
"""

class AgentException(Exception):
    """Base exception for agent runner errors."""
    pass


class AgentToolException(AgentException):
    """Exception raised when there's an error with agent tools."""
    pass


class AgentTimeoutException(AgentException):
    """Exception raised when an agent execution times out."""
    pass


class AgentMemoryException(AgentException):
    """Exception raised when there's an error with agent memory operations."""
    pass