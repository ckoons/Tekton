"""
Docker container provider implementation.

Provides full container isolation for complex solutions that need
specific environments or can't run in sandbox-exec.
"""

import os
import asyncio
import tempfile
import shutil
import uuid
import json
from pathlib import Path
from typing import Dict, Any, List, AsyncIterator
import logging

try:
    import docker
    from docker.errors import DockerException, NotFound
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False
    DockerException = Exception
    NotFound = Exception

from ..base import SandboxProvider, SandboxResult, SandboxStatus

logger = logging.getLogger(__name__)


class DockerProvider(SandboxProvider):
    """
    Docker-based container isolation provider.
    
    Provides full isolation with configurable resource limits
    and network access.
    """
    
    def __init__(self):
        self.sandboxes = {}
        self.client = None
        if DOCKER_AVAILABLE:
            try:
                self.client = docker.from_env()
            except DockerException:
                logger.warning("Docker daemon not accessible")
    
    async def is_available(self) -> bool:
        """Check if Docker is available and running"""
        if not DOCKER_AVAILABLE:
            return False
        
        if not self.client:
            return False
        
        try:
            self.client.ping()
            return True
        except Exception:
            return False
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return Docker capabilities"""
        return {
            "platform": "any",
            "isolation": "full",
            "network": True,
            "gpu": True,  # Supports GPU where available
            "persistent": True,  # Can mount volumes
            "max_memory": "configurable",
            "max_cpu": "configurable"
        }
    
    async def prepare(self, solution_id: str, solution_path: str, config: Dict[str, Any]) -> str:
        """Prepare Docker container environment"""
        
        if not await self.is_available():
            raise RuntimeError("Docker is not available")
        
        sandbox_id = str(uuid.uuid4())
        
        # Prepare volume mounts
        sandbox_dir = Path(f"/tmp/ergon-docker-{sandbox_id}")
        sandbox_dir.mkdir(parents=True)
        (sandbox_dir / "solution").mkdir()
        (sandbox_dir / "workspace").mkdir()
        (sandbox_dir / "output").mkdir()
        
        # Copy solution files
        if Path(solution_path).exists():
            shutil.copytree(solution_path, sandbox_dir / "solution", dirs_exist_ok=True)
        
        # Determine base image
        image = config.get("docker_image", "python:3.11-slim")
        
        # Check if we need to pull the image
        try:
            self.client.images.get(image)
        except NotFound:
            logger.info(f"Pulling Docker image: {image}")
            self.client.images.pull(image)
        
        # Container configuration
        container_config = {
            "image": image,
            "name": f"ergon-sandbox-{sandbox_id[:8]}",
            "command": "sleep infinity",  # Keep container running
            "detach": True,
            "volumes": {
                str(sandbox_dir / "solution"): {"bind": "/solution", "mode": "ro"},
                str(sandbox_dir / "workspace"): {"bind": "/workspace", "mode": "rw"},
                str(sandbox_dir / "output"): {"bind": "/output", "mode": "rw"}
            },
            "working_dir": "/workspace",
            "environment": {
                "SANDBOX_ID": sandbox_id,
                "PYTHONUNBUFFERED": "1"
            },
            "mem_limit": config.get("memory_limit", "4g"),
            "nano_cpus": int(config.get("cpu_limit", 4) * 1e9),  # Convert to nanocpus
            "network_mode": config.get("network_mode", "bridge"),
            "auto_remove": False
        }
        
        # Add GPU support if requested and available
        if config.get("gpu_enabled") and config.get("gpu_count", 0) > 0:
            container_config["device_requests"] = [
                docker.types.DeviceRequest(
                    count=config.get("gpu_count", 1),
                    capabilities=[["gpu"]]
                )
            ]
        
        # Create and start container
        container = self.client.containers.run(**container_config)
        
        # Store sandbox info
        self.sandboxes[sandbox_id] = {
            "id": sandbox_id,
            "solution_id": solution_id,
            "container": container,
            "dir": sandbox_dir,
            "status": SandboxStatus.READY,
            "stdout": [],
            "stderr": [],
            "exit_code": None
        }
        
        logger.info(f"Prepared Docker sandbox {sandbox_id} for solution {solution_id}")
        return sandbox_id
    
    async def execute(self, sandbox_id: str, command: List[str], timeout: int = 300) -> AsyncIterator[str]:
        """Execute command in Docker container with streaming output"""
        
        if sandbox_id not in self.sandboxes:
            raise ValueError(f"Sandbox {sandbox_id} not found")
        
        sandbox = self.sandboxes[sandbox_id]
        container = sandbox["container"]
        sandbox["status"] = SandboxStatus.RUNNING
        
        try:
            # Execute command in container
            exec_result = container.exec_run(
                command,
                stdout=True,
                stderr=True,
                stream=True,
                demux=True,
                workdir="/workspace"
            )
            
            # Stream output
            timeout_task = asyncio.create_task(asyncio.sleep(timeout))
            
            for stdout_chunk, stderr_chunk in exec_result.output:
                if timeout_task.done():
                    container.kill()
                    sandbox["status"] = SandboxStatus.TIMEOUT
                    yield "[error] Execution timeout exceeded"
                    break
                
                if stdout_chunk:
                    lines = stdout_chunk.decode('utf-8', errors='replace').splitlines()
                    for line in lines:
                        sandbox["stdout"].append(line)
                        yield f"[stdout] {line}"
                
                if stderr_chunk:
                    lines = stderr_chunk.decode('utf-8', errors='replace').splitlines()
                    for line in lines:
                        sandbox["stderr"].append(line)
                        yield f"[stderr] {line}"
                
                # Small delay to prevent CPU spinning
                await asyncio.sleep(0.01)
            
            # Get exit code
            exec_info = container.exec_run(["echo", "$?"])
            try:
                sandbox["exit_code"] = int(exec_info.output.strip())
                if sandbox["exit_code"] == 0:
                    sandbox["status"] = SandboxStatus.COMPLETED
                else:
                    sandbox["status"] = SandboxStatus.FAILED
            except ValueError:
                sandbox["status"] = SandboxStatus.FAILED
            
            timeout_task.cancel()
            
        except Exception as e:
            sandbox["status"] = SandboxStatus.FAILED
            sandbox["errors"] = [str(e)]
            yield f"[error] Execution failed: {e}"
    
    async def get_result(self, sandbox_id: str) -> SandboxResult:
        """Get execution result"""
        
        if sandbox_id not in self.sandboxes:
            raise ValueError(f"Sandbox {sandbox_id} not found")
        
        sandbox = self.sandboxes[sandbox_id]
        container = sandbox["container"]
        
        # Get container stats
        metrics = {}
        try:
            stats = container.stats(stream=False)
            metrics = {
                "provider": "docker",
                "container_id": container.short_id,
                "image": container.image.tags[0] if container.image.tags else "unknown",
                "memory_usage": stats.get("memory_stats", {}).get("usage", 0),
                "cpu_percent": self._calculate_cpu_percent(stats)
            }
        except Exception as e:
            logger.warning(f"Failed to get container stats: {e}")
            metrics = {"provider": "docker", "stats_error": str(e)}
        
        return SandboxResult(
            sandbox_id=sandbox_id,
            solution_id=sandbox["solution_id"],
            status=sandbox["status"],
            exit_code=sandbox.get("exit_code"),
            execution_time=None,  # TODO: Track execution time
            stdout="\n".join(sandbox["stdout"]),
            stderr="\n".join(sandbox["stderr"]),
            metrics=metrics,
            errors=sandbox.get("errors", [])
        )
    
    def _calculate_cpu_percent(self, stats: Dict) -> float:
        """Calculate CPU usage percentage from Docker stats"""
        try:
            cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - \
                       stats["precpu_stats"]["cpu_usage"]["total_usage"]
            system_delta = stats["cpu_stats"]["system_cpu_usage"] - \
                          stats["precpu_stats"]["system_cpu_usage"]
            
            if system_delta > 0 and cpu_delta > 0:
                cpu_percent = (cpu_delta / system_delta) * 100.0
                return round(cpu_percent, 2)
        except (KeyError, ZeroDivisionError):
            pass
        return 0.0
    
    async def cleanup(self, sandbox_id: str) -> bool:
        """Clean up Docker container and resources"""
        
        if sandbox_id not in self.sandboxes:
            return False
        
        sandbox = self.sandboxes[sandbox_id]
        
        try:
            # Stop and remove container
            container = sandbox["container"]
            try:
                container.stop(timeout=5)
            except Exception:
                container.kill()
            
            container.remove(force=True)
            
            # Remove sandbox directory
            if sandbox["dir"].exists():
                shutil.rmtree(sandbox["dir"])
            
            # Remove from tracking
            del self.sandboxes[sandbox_id]
            
            logger.info(f"Cleaned up Docker sandbox {sandbox_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cleanup Docker sandbox {sandbox_id}: {e}")
            return False
    
    async def stop(self, sandbox_id: str) -> bool:
        """Stop a running container without removing it"""
        
        if sandbox_id not in self.sandboxes:
            return False
        
        try:
            container = self.sandboxes[sandbox_id]["container"]
            container.stop(timeout=5)
            self.sandboxes[sandbox_id]["status"] = SandboxStatus.COMPLETED
            return True
        except Exception as e:
            logger.error(f"Failed to stop container: {e}")
            return False