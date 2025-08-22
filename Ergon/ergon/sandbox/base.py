"""
Abstract base classes for sandbox providers.

Defines the interface that all sandbox implementations must follow,
enabling easy swapping of sandbox technologies.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, AsyncIterator
from datetime import datetime
from enum import Enum

# Landmark imports with fallback
try:
    from landmarks import (
        architecture_decision,
        api_contract,
        state_checkpoint
    )
except ImportError:
    def architecture_decision(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def api_contract(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def state_checkpoint(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator


class SandboxStatus(Enum):
    """Sandbox execution status"""
    PREPARING = "preparing"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CLEANED = "cleaned"


@dataclass
class SandboxResult:
    """Result from sandbox execution"""
    sandbox_id: str
    solution_id: str
    status: SandboxStatus
    exit_code: Optional[int] = None
    execution_time: Optional[float] = None
    stdout: str = ""
    stderr: str = ""
    metrics: Dict[str, Any] = None
    errors: List[str] = None
    
    def __post_init__(self):
        if self.metrics is None:
            self.metrics = {}
        if self.errors is None:
            self.errors = []


@architecture_decision(
    title="Pluggable Sandbox Architecture",
    description="Abstract interface enabling multiple sandbox implementations",
    rationale="Allows easy replacement of sandbox technology without changing client code. Start with sandbox-exec for Mac, can add Docker, Firecracker, WASM later.",
    alternatives_considered=["Hard-coded Docker", "VM-only", "Single implementation"],
    impacts=["sandbox_flexibility", "testing_isolation", "platform_compatibility"],
    decided_by="Casey, Ani",
    decision_date="2025-08-22"
)
class SandboxProvider(ABC):
    """
    Abstract base class for all sandbox providers.
    
    Implementations must provide methods for preparing, executing,
    and cleaning up isolated test environments.
    """
    
    @abstractmethod
    async def prepare(self, solution_id: str, solution_path: str, config: Dict[str, Any]) -> str:
        """
        Prepare the sandbox environment.
        
        Args:
            solution_id: Registry solution ID
            solution_path: Path to solution files
            config: Provider-specific configuration
            
        Returns:
            sandbox_id: Unique identifier for this sandbox instance
        """
        pass
    
    @abstractmethod
    async def execute(self, sandbox_id: str, command: List[str], timeout: int = 300) -> AsyncIterator[str]:
        """
        Execute a command in the sandbox, streaming output.
        
        Args:
            sandbox_id: Sandbox instance identifier
            command: Command and arguments to execute
            timeout: Maximum execution time in seconds
            
        Yields:
            Output lines from the command
        """
        pass
    
    @abstractmethod
    async def get_result(self, sandbox_id: str) -> SandboxResult:
        """
        Get the final result after execution completes.
        
        Args:
            sandbox_id: Sandbox instance identifier
            
        Returns:
            SandboxResult with status, exit code, metrics, etc.
        """
        pass
    
    @abstractmethod
    async def cleanup(self, sandbox_id: str) -> bool:
        """
        Clean up all sandbox resources.
        
        Args:
            sandbox_id: Sandbox instance identifier
            
        Returns:
            True if cleanup successful
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Return provider capabilities and requirements.
        
        Returns:
            Dictionary describing what this provider supports:
            - platform: Operating system (darwin, linux, any)
            - isolation: Level of isolation (filesystem, process, full)
            - network: Whether network access is allowed
            - gpu: Whether GPU passthrough is supported
            - persistent: Whether state can persist between runs
        """
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """
        Check if this provider is available on the current system.
        
        Returns:
            True if provider can be used
        """
        pass
    
    def get_name(self) -> str:
        """Get provider name (defaults to class name)"""
        return self.__class__.__name__.replace('Provider', '').lower()
    
    async def stop(self, sandbox_id: str) -> bool:
        """
        Stop a running sandbox (optional - not all providers support this).
        
        Args:
            sandbox_id: Sandbox instance identifier
            
        Returns:
            True if stopped successfully
        """
        # Default implementation - providers can override
        return await self.cleanup(sandbox_id)