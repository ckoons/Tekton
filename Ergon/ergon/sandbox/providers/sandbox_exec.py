"""
macOS sandbox-exec provider implementation.

Uses the built-in macOS sandbox-exec command to provide filesystem
isolation while allowing network access for LLM APIs.
"""

import os
import sys
import asyncio
import tempfile
import shutil
import uuid
from pathlib import Path
from typing import Dict, Any, List, AsyncIterator
import platform
import subprocess
from datetime import datetime
import logging

from ..base import SandboxProvider, SandboxResult, SandboxStatus

# Landmark imports with fallback
try:
    from landmarks import performance_boundary, danger_zone
except ImportError:
    def performance_boundary(**kwargs):
        def decorator(func):
            return func
        return decorator
    
    def danger_zone(**kwargs):
        def decorator(func):
            return func
        return decorator

logger = logging.getLogger(__name__)


class SandboxExecProvider(SandboxProvider):
    """
    macOS sandbox-exec based isolation provider.
    
    Provides filesystem isolation while allowing network access
    and system framework usage.
    """
    
    def __init__(self):
        self.sandboxes = {}  # Track active sandboxes
        self.profiles_dir = Path("/tmp/ergon-sandbox-profiles")
        self.profiles_dir.mkdir(exist_ok=True)
    
    async def is_available(self) -> bool:
        """Check if sandbox-exec is available (macOS only)"""
        if platform.system() != "Darwin":
            return False
        
        try:
            result = subprocess.run(
                ["which", "sandbox-exec"],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return sandbox-exec capabilities"""
        return {
            "platform": "darwin",
            "isolation": "filesystem",
            "network": True,
            "gpu": False,  # No GPU passthrough with sandbox-exec
            "persistent": False,
            "max_memory": "system",  # Uses system memory
            "max_cpu": "system"  # Uses system CPU
        }
    
    @performance_boundary(
        title="Sandbox Preparation",
        description="Create isolated environment with custom profile",
        sla="<500ms for directory setup and profile generation",
        optimization_notes="Pre-generate common profiles, reuse temp directories"
    )
    async def prepare(self, solution_id: str, solution_path: str, config: Dict[str, Any]) -> str:
        """Prepare sandbox environment with custom profile"""
        
        sandbox_id = str(uuid.uuid4())
        sandbox_dir = Path(f"/tmp/ergon-sandbox-{sandbox_id}")
        
        # Create directory structure
        sandbox_dir.mkdir(parents=True)
        (sandbox_dir / "solution").mkdir()
        (sandbox_dir / "workspace").mkdir()
        (sandbox_dir / "output").mkdir()
        
        # Copy solution files (read-only in sandbox)
        if Path(solution_path).exists():
            shutil.copytree(solution_path, sandbox_dir / "solution", dirs_exist_ok=True)
        
        # Generate sandbox profile
        profile_path = self._generate_profile(sandbox_id, sandbox_dir, config)
        
        # Store sandbox info
        self.sandboxes[sandbox_id] = {
            "id": sandbox_id,
            "solution_id": solution_id,
            "dir": sandbox_dir,
            "profile": profile_path,
            "status": SandboxStatus.READY,
            "created": datetime.utcnow(),
            "process": None,
            "stdout": [],
            "stderr": [],
            "exit_code": None
        }
        
        logger.info(f"Prepared sandbox {sandbox_id} for solution {solution_id}")
        return sandbox_id
    
    def _generate_profile(self, sandbox_id: str, sandbox_dir: Path, config: Dict[str, Any]) -> Path:
        """Generate sandbox-exec profile (.sb file)"""
        
        profile_path = self.profiles_dir / f"{sandbox_id}.sb"
        
        # Base profile with sensible defaults
        profile = f"""
; Ergon Sandbox Profile for {sandbox_id}
; Generated: {datetime.utcnow().isoformat()}
(version 1)

; Deny everything by default
(deny default)

; Allow network access (for LLM APIs, package downloads)
(allow network*)

; Allow process operations
(allow process-exec)
(allow process-fork)
(allow signal)
(allow sysctl-read)

; Allow mach operations (needed for Python/Node)
(allow mach-lookup)
(allow mach-register)

; Allow reading system files and frameworks
(allow file-read*
    (subpath "/System")
    (subpath "/Library")
    (subpath "/usr")
    (subpath "/bin")
    (subpath "/sbin")
    (subpath "/private/etc")
    (subpath "/private/var/select")
    (subpath "/dev/null")
    (subpath "/dev/zero")
    (subpath "/dev/random")
    (subpath "/dev/urandom"))

; Allow Homebrew installations (M1/M2 Macs)
(allow file-read* (subpath "/opt/homebrew"))

; Allow reading user's Python/Node installations
(allow file-read* 
    (regex "^/Users/[^/]+/\\.pyenv")
    (regex "^/Users/[^/]+/\\.nvm")
    (regex "^/Users/[^/]+/\\.npm")
    (regex "^/Users/[^/]+/Library/Python"))

; Solution files (read-only)
(allow file-read* (subpath "{sandbox_dir}/solution"))

; Workspace (read-write for solution work)
(allow file-read* file-write* 
    (subpath "{sandbox_dir}/workspace")
    (subpath "{sandbox_dir}/output"))

; Temp directories
(allow file-read* file-write* 
    (subpath "/tmp")
    (subpath "/var/tmp")
    (regex "^/private/tmp/"))

; Allow cache directories for package managers
(allow file-read* file-write*
    (regex "^/Users/[^/]+/Library/Caches/pip")
    (regex "^/Users/[^/]+/\\.cache")
    (regex "^/Users/[^/]+/\\.npm"))
"""
        
        # Add custom rules from config
        if custom_rules := config.get("sandbox_rules"):
            profile += f"\n; Custom rules\n{custom_rules}\n"
        
        profile_path.write_text(profile)
        return profile_path
    
    @danger_zone(
        title="Sandbox Command Execution",
        description="Execute untrusted code in sandbox",
        risk_level="medium",
        risks=["resource exhaustion", "network abuse", "infinite loops"],
        mitigation="Timeout enforcement, resource monitoring, kill on excess"
    )
    async def execute(self, sandbox_id: str, command: List[str], timeout: int = 300) -> AsyncIterator[str]:
        """Execute command in sandbox with streaming output"""
        
        if sandbox_id not in self.sandboxes:
            raise ValueError(f"Sandbox {sandbox_id} not found")
        
        sandbox = self.sandboxes[sandbox_id]
        sandbox["status"] = SandboxStatus.RUNNING
        sandbox["start_time"] = datetime.utcnow()
        
        # Build sandbox-exec command
        sandbox_cmd = [
            "sandbox-exec",
            "-f", str(sandbox["profile"]),
            *command
        ]
        
        # Set working directory to workspace
        cwd = sandbox["dir"] / "workspace"
        
        try:
            # Create async subprocess
            process = await asyncio.create_subprocess_exec(
                *sandbox_cmd,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**os.environ, "SANDBOX_ID": sandbox_id}
            )
            
            sandbox["process"] = process
            
            # Stream output with timeout
            try:
                async def read_stream(stream, output_list):
                    async for line in stream:
                        line_str = line.decode('utf-8', errors='replace').rstrip()
                        output_list.append(line_str)
                        yield line_str
                
                # Read both stdout and stderr
                tasks = []
                async for line in read_stream(process.stdout, sandbox["stdout"]):
                    yield f"[stdout] {line}"
                
                async for line in read_stream(process.stderr, sandbox["stderr"]):
                    yield f"[stderr] {line}"
                
                # Wait for completion with timeout
                await asyncio.wait_for(process.wait(), timeout=timeout)
                sandbox["exit_code"] = process.returncode
                
                if process.returncode == 0:
                    sandbox["status"] = SandboxStatus.COMPLETED
                else:
                    sandbox["status"] = SandboxStatus.FAILED
                    
            except asyncio.TimeoutError:
                # Kill process on timeout
                process.kill()
                await process.wait()
                sandbox["status"] = SandboxStatus.TIMEOUT
                yield "[error] Execution timeout exceeded"
                
        except Exception as e:
            sandbox["status"] = SandboxStatus.FAILED
            sandbox["errors"] = [str(e)]
            yield f"[error] Execution failed: {e}"
        
        finally:
            sandbox["end_time"] = datetime.utcnow()
    
    async def get_result(self, sandbox_id: str) -> SandboxResult:
        """Get execution result"""
        
        if sandbox_id not in self.sandboxes:
            raise ValueError(f"Sandbox {sandbox_id} not found")
        
        sandbox = self.sandboxes[sandbox_id]
        
        # Calculate execution time
        execution_time = None
        if "start_time" in sandbox and "end_time" in sandbox:
            execution_time = (sandbox["end_time"] - sandbox["start_time"]).total_seconds()
        
        return SandboxResult(
            sandbox_id=sandbox_id,
            solution_id=sandbox["solution_id"],
            status=sandbox["status"],
            exit_code=sandbox.get("exit_code"),
            execution_time=execution_time,
            stdout="\n".join(sandbox["stdout"]),
            stderr="\n".join(sandbox["stderr"]),
            metrics={
                "provider": "sandbox-exec",
                "platform": platform.system(),
                "platform_version": platform.version()
            },
            errors=sandbox.get("errors", [])
        )
    
    async def cleanup(self, sandbox_id: str) -> bool:
        """Clean up sandbox resources"""
        
        if sandbox_id not in self.sandboxes:
            return False
        
        sandbox = self.sandboxes[sandbox_id]
        
        try:
            # Kill process if still running
            if sandbox.get("process") and sandbox["process"].returncode is None:
                sandbox["process"].kill()
                await sandbox["process"].wait()
            
            # Remove sandbox directory
            if sandbox["dir"].exists():
                shutil.rmtree(sandbox["dir"])
            
            # Remove profile
            if sandbox["profile"].exists():
                sandbox["profile"].unlink()
            
            # Remove from tracking
            del self.sandboxes[sandbox_id]
            
            logger.info(f"Cleaned up sandbox {sandbox_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cleanup sandbox {sandbox_id}: {e}")
            return False