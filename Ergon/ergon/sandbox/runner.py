"""
Main sandbox runner interface.

High-level API for testing Registry solutions in isolated environments
with automatic dependency installation and result tracking.
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional, AsyncIterator
from datetime import datetime
import logging

from .factory import SandboxFactory
from .base import SandboxProvider, SandboxResult, SandboxStatus
from ..registry.storage import RegistryStorage

# Landmark imports with fallback
try:
    from landmarks import (
        api_contract,
        performance_boundary,
        state_checkpoint,
        danger_zone
    )
except ImportError:
    def api_contract(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def performance_boundary(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def state_checkpoint(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def danger_zone(**kwargs):
        def decorator(func):
            return func
        return decorator

logger = logging.getLogger(__name__)


@api_contract(
    endpoint="SandboxRunner",
    title="Sandbox Runner Interface",
    description="High-level API for testing Registry solutions",
    endpoints=["test_solution", "stream_output", "get_results", "cleanup"],
    authentication="None (local only)",
    rate_limits="Concurrent sandbox limit: 10",
    error_codes={
        "SANDBOX001": "Provider not available",
        "SANDBOX002": "Solution not found",
        "SANDBOX003": "Execution timeout",
        "SANDBOX004": "Resource limit exceeded"
    }
)
class SandboxRunner:
    """
    Main interface for running Registry solutions in sandboxes.
    
    Handles:
    - Provider selection via factory
    - Solution retrieval from Registry
    - Dependency installation
    - Command execution
    - Result tracking
    """
    
    def __init__(self, registry_storage: Optional[RegistryStorage] = None):
        self.factory = SandboxFactory()
        self.registry = registry_storage or RegistryStorage()
        self.active_sandboxes = {}
        self.max_concurrent = 10
    
    @performance_boundary(
        title="Solution Testing",
        description="Full solution test from Registry to results",
        sla="<5 seconds to start execution",
        optimization_notes="Pre-pull Docker images, cache dependencies"
    )
    async def test_solution(
        self,
        solution_id: str,
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Test a Registry solution in an isolated sandbox.
        
        Args:
            solution_id: Registry entry ID
            config: Optional sandbox configuration:
                - provider: Force specific provider
                - timeout: Execution timeout in seconds
                - memory_limit: Max memory (e.g., "4g")
                - cpu_limit: Max CPUs
                - environment: Additional env vars
                
        Returns:
            sandbox_id for tracking execution
        """
        
        # Check concurrent limit
        if len(self.active_sandboxes) >= self.max_concurrent:
            raise RuntimeError(f"Maximum concurrent sandboxes ({self.max_concurrent}) reached")
        
        # Retrieve solution from Registry
        solution = self.registry.retrieve(solution_id)
        if not solution:
            raise ValueError(f"Solution {solution_id} not found in Registry")
        
        # Prepare configuration
        config = config or {}
        config.setdefault("timeout", 300)
        config.setdefault("memory_limit", "4g")
        config.setdefault("cpu_limit", 4)
        
        # Extract solution requirements
        requirements = self._extract_requirements(solution)
        
        # Get appropriate provider
        provider = await self.factory.get_provider(
            requirements,
            user_preference=config.get("provider")
        )
        
        # Prepare solution files
        solution_path = await self._prepare_solution_files(solution)
        
        # Create sandbox
        sandbox_id = await provider.prepare(solution_id, solution_path, config)
        
        # Track sandbox
        self.active_sandboxes[sandbox_id] = {
            "provider": provider,
            "solution_id": solution_id,
            "started": datetime.utcnow(),
            "config": config,
            "status": SandboxStatus.READY
        }
        
        logger.info(f"Created sandbox {sandbox_id} for solution {solution_id}")
        return sandbox_id
    
    @danger_zone(
        title="Execute in Sandbox",
        description="Run untrusted code in isolated environment",
        risk_level="medium",
        risks=["code_execution", "resource_exhaustion"],
        mitigation="Timeout enforcement, resource limits, isolation"
    )
    async def execute(
        self,
        sandbox_id: str,
        command: Optional[List[str]] = None
    ) -> AsyncIterator[str]:
        """
        Execute command in sandbox, streaming output.
        
        Args:
            sandbox_id: Sandbox instance ID
            command: Command to run (defaults to solution's run command)
            
        Yields:
            Output lines prefixed with [stdout] or [stderr]
        """
        
        if sandbox_id not in self.active_sandboxes:
            raise ValueError(f"Sandbox {sandbox_id} not found")
        
        sandbox_info = self.active_sandboxes[sandbox_id]
        provider = sandbox_info["provider"]
        config = sandbox_info["config"]
        
        # Get solution for default command
        if not command:
            solution = self.registry.retrieve(sandbox_info["solution_id"])
            command = self._get_run_command(solution)
        
        # Update status
        sandbox_info["status"] = SandboxStatus.RUNNING
        
        # Execute with timeout
        timeout = config.get("timeout", 300)
        
        try:
            async for line in provider.execute(sandbox_id, command, timeout):
                yield line
        except Exception as e:
            sandbox_info["status"] = SandboxStatus.FAILED
            yield f"[error] Execution failed: {e}"
        else:
            sandbox_info["status"] = SandboxStatus.COMPLETED
    
    @state_checkpoint(
        state_type="sandbox_result",
        title="Sandbox Results",
        description="Capture final state after execution",
        data_captured=["exit_code", "stdout", "stderr", "metrics"],
        persistence="Registry metadata update"
    )
    async def get_results(self, sandbox_id: str) -> SandboxResult:
        """
        Get execution results from sandbox.
        
        Args:
            sandbox_id: Sandbox instance ID
            
        Returns:
            SandboxResult with status, output, metrics
        """
        
        if sandbox_id not in self.active_sandboxes:
            raise ValueError(f"Sandbox {sandbox_id} not found")
        
        sandbox_info = self.active_sandboxes[sandbox_id]
        provider = sandbox_info["provider"]
        
        # Get results from provider
        result = await provider.get_result(sandbox_id)
        
        # Add runner metadata
        result.metrics["runner"] = {
            "provider_used": provider.get_name(),
            "started": sandbox_info["started"].isoformat(),
            "config": sandbox_info["config"]
        }
        
        # Update Registry with test results
        await self._update_registry_results(
            sandbox_info["solution_id"],
            result
        )
        
        return result
    
    async def cleanup(self, sandbox_id: str) -> bool:
        """
        Clean up sandbox resources.
        
        Args:
            sandbox_id: Sandbox instance ID
            
        Returns:
            True if cleanup successful
        """
        
        if sandbox_id not in self.active_sandboxes:
            return False
        
        sandbox_info = self.active_sandboxes[sandbox_id]
        provider = sandbox_info["provider"]
        
        # Clean up via provider
        success = await provider.cleanup(sandbox_id)
        
        # Remove from tracking
        if success:
            del self.active_sandboxes[sandbox_id]
            logger.info(f"Cleaned up sandbox {sandbox_id}")
        else:
            logger.error(f"Failed to cleanup sandbox {sandbox_id}")
        
        return success
    
    async def cleanup_all(self) -> int:
        """
        Clean up all active sandboxes.
        
        Returns:
            Number of sandboxes cleaned
        """
        
        cleaned = 0
        sandbox_ids = list(self.active_sandboxes.keys())
        
        for sandbox_id in sandbox_ids:
            if await self.cleanup(sandbox_id):
                cleaned += 1
        
        logger.info(f"Cleaned up {cleaned} sandboxes")
        return cleaned
    
    def _extract_requirements(self, solution: Dict[str, Any]) -> Dict[str, Any]:
        """Extract sandbox requirements from solution metadata"""
        
        content = solution.get("content", {})
        
        return {
            "needs_network": content.get("requires_network", True),
            "needs_gpu": content.get("requires_gpu", False),
            "needs_persistence": content.get("requires_persistence", False),
            "platform": content.get("platform", "any"),
            "max_memory": content.get("memory_limit", "4g")
        }
    
    async def _prepare_solution_files(self, solution: Dict[str, Any]) -> str:
        """Prepare solution files for sandbox execution"""
        
        import tempfile
        import shutil
        
        # Create temp directory
        temp_dir = Path(tempfile.mkdtemp(prefix="ergon-solution-"))
        
        content = solution.get("content", {})
        
        # Write main solution file
        if "code" in content:
            main_file = temp_dir / content.get("main_file", "solution.py")
            main_file.write_text(content["code"])
        
        # Copy additional files if specified
        if "files" in content:
            for file_path, file_content in content["files"].items():
                file = temp_dir / file_path
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_text(file_content)
        
        # Write requirements if present
        if "requirements" in content:
            req_file = temp_dir / "requirements.txt"
            req_file.write_text("\n".join(content["requirements"]))
        
        return str(temp_dir)
    
    def _get_run_command(self, solution: Dict[str, Any]) -> List[str]:
        """Get run command from solution or use defaults"""
        
        content = solution.get("content", {})
        
        # Use specified command
        if "run_command" in content:
            return content["run_command"]
        
        # Detect by file type
        main_file = content.get("main_file", "solution.py")
        
        if main_file.endswith(".py"):
            return ["python", main_file]
        elif main_file.endswith(".js"):
            return ["node", main_file]
        elif main_file.endswith(".sh"):
            return ["bash", main_file]
        else:
            return ["python", main_file]  # Default to Python
    
    async def _update_registry_results(
        self,
        solution_id: str,
        result: SandboxResult
    ):
        """Update Registry with test results"""
        
        solution = self.registry.retrieve(solution_id)
        if not solution:
            return
        
        # Add test results to metadata
        if "test_results" not in solution:
            solution["test_results"] = []
        
        solution["test_results"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "status": result.status.value,
            "exit_code": result.exit_code,
            "execution_time": result.execution_time,
            "provider": result.metrics.get("provider"),
            "errors": result.errors
        })
        
        # Keep only last 10 results
        solution["test_results"] = solution["test_results"][-10:]
        
        # Update Registry
        self.registry.update(solution_id, solution)