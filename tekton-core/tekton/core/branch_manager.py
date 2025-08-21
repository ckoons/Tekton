"""
TektonCore Branch Management System

Manages git branch lifecycle for Coder workflow:
- Create branches: sprint/coder-x/feature-name
- Monitor branch status and progress
- Handle merge operations and cleanup
- Coordinate with multiple Coder directories (../Coder-A, ../Coder-B, ../Coder-C)
"""

import os
import asyncio
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum

from shared.utils.logging_setup import setup_component_logging

# Import shared environment
try:
    from shared.env import TektonEnviron
except ImportError:
    # Fallback if shared.env not available
    class TektonEnviron:
        @staticmethod
        def get(key, default=None):
            return TektonEnviron.get(key, default)

# Import landmarks for architectural documentation
try:
    from landmarks import (
        architecture_decision,
        integration_point,
        api_contract,
        state_checkpoint,
        performance_boundary,
        danger_zone
    )
except ImportError:
    # Landmarks not available, define no-op decorators
    def architecture_decision(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def integration_point(**kwargs):
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
    
    def performance_boundary(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def danger_zone(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator

logger = setup_component_logging("tekton_core.branch_manager")


class BranchStatus(str, Enum):
    """Branch status values"""
    ACTIVE = "active"                    # Branch exists and is being worked on
    READY_FOR_MERGE = "ready_for_merge"  # All tests pass, ready for integration
    MERGING = "merging"                  # Merge operation in progress
    MERGED = "merged"                    # Successfully merged and deleted
    CONFLICT = "conflict"                # Merge conflicts detected
    FAILED = "failed"                    # Branch operation failed


@state_checkpoint(
    title="Branch Tracking State",
    state_type="transient",
    description="Runtime state tracking for git branches across Coder directories",
    rationale="Maintains branch status and metadata for coordination between TektonCore and Coder instances"  
)
@dataclass
class BranchInfo:
    """Branch information and status"""
    name: str                            # Full branch name (sprint/coder-a/feature-name)
    coder_id: str                        # A, B, or C
    sprint_name: str                     # Associated sprint name
    repo_path: str                       # Path to git repository
    status: BranchStatus                 # Current branch status
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_activity: str = field(default_factory=lambda: datetime.now().isoformat())
    commit_count: int = 0                # Number of commits on branch
    files_changed: List[str] = field(default_factory=list)  # Files modified
    tests_passing: Optional[bool] = None # Test status
    merge_conflicts: List[str] = field(default_factory=list)  # Conflicting files
    metadata: Dict[str, Any] = field(default_factory=dict)


@architecture_decision(
    title="Multi-Coder Repository Architecture", 
    description="Manages git branches across multiple Coder directories (../Coder-A, ../Coder-B, ../Coder-C)",
    rationale="Each Coder works in isolated environment with own git clone, enables parallel development",
    alternatives_considered=["Single shared repository", "Git worktrees", "Separate repositories"],
    impacts=["development_isolation", "merge_complexity", "resource_usage"]
)
@integration_point(
    title="Git CLI Integration",
    target_component="git",
    protocol="subprocess",
    data_flow="BranchManager → git commands → repository state",
    description="Manages git operations across multiple repository clones"
)
class BranchManager:
    """Manages git branches for Coder workflow"""
    
    def __init__(self, tekton_root: Optional[str] = None):
        """Initialize branch manager"""
        if tekton_root is None:
            from shared.env import TektonEnviron
            tekton_root = TektonEnviron.get("TEKTON_ROOT") or os.getcwd()
        
        self.tekton_root = Path(tekton_root)
        self.parent_dir = self.tekton_root.parent
        
        # Coder repository paths
        self.coder_repos = {
            "A": self.parent_dir / "Coder-A",
            "B": self.parent_dir / "Coder-B", 
            "C": self.parent_dir / "Coder-C"
        }
        
        # Track active branches
        self.branches: Dict[str, BranchInfo] = {}
        
        logger.info(f"BranchManager initialized, managing repositories: {list(self.coder_repos.keys())}")
    
    @api_contract(
        title="Branch Creation API",
        endpoint="create_branch",
        method="ASYNC",
        request_schema={
            "coder_id": "str",
            "sprint_name": "str", 
            "feature_name": "str"
        },
        response_schema={"branch_info": "BranchInfo", "success": "bool"},
        description="Creates new git branch for Coder sprint work"
    )
    async def create_branch(self, coder_id: str, sprint_name: str, feature_name: Optional[str] = None) -> BranchInfo:
        """Create new branch for Coder sprint work"""
        
        if coder_id not in self.coder_repos:
            raise ValueError(f"Invalid coder_id: {coder_id}")
        
        repo_path = self.coder_repos[coder_id]
        if not repo_path.exists():
            raise ValueError(f"Coder repository does not exist: {repo_path}")
        
        # Generate branch name
        if not feature_name:
            feature_name = sprint_name.lower().replace('_', '-')
        
        branch_name = f"sprint/coder-{coder_id.lower()}/{feature_name}"
        
        logger.info(f"Creating branch {branch_name} in {repo_path}")
        
        try:
            # Ensure we're on main and up to date
            await self._run_git_command(repo_path, ["checkout", "main"])
            await self._run_git_command(repo_path, ["pull", "origin", "main"])
            
            # Create and checkout new branch
            result = await self._run_git_command(repo_path, ["checkout", "-b", branch_name])
            
            if result.returncode != 0:
                logger.error(f"Failed to create branch {branch_name}: {result.stderr}")
                raise RuntimeError(f"Git branch creation failed: {result.stderr}")
            
            # Create branch info
            branch_info = BranchInfo(
                name=branch_name,
                coder_id=coder_id,
                sprint_name=sprint_name,
                repo_path=str(repo_path),
                status=BranchStatus.ACTIVE
            )
            
            self.branches[branch_name] = branch_info
            
            logger.info(f"Successfully created branch {branch_name}")
            return branch_info
            
        except Exception as e:
            logger.error(f"Failed to create branch {branch_name}: {e}")
            raise
    
    @performance_boundary(
        title="Branch Status Check Performance",
        operation="git_status_check",
        expected_load="~10 active branches",
        bottlenecks=["git command execution", "file system I/O"],
        optimization_notes="Batches multiple git operations for efficiency",
        sla="<5s for branch status check"
    )
    async def get_branch_status(self, branch_name: str) -> Optional[BranchInfo]:
        """Get detailed status of a branch"""
        
        if branch_name not in self.branches:
            return None
        
        branch_info = self.branches[branch_name]
        repo_path = Path(branch_info.repo_path)
        
        try:
            # Check if branch still exists
            result = await self._run_git_command(repo_path, ["show-ref", "--verify", f"refs/heads/{branch_name}"])
            
            if result.returncode != 0:
                # Branch doesn't exist, update status
                branch_info.status = BranchStatus.FAILED
                return branch_info
            
            # Get commit count ahead of main
            result = await self._run_git_command(repo_path, ["rev-list", "--count", f"main..{branch_name}"])
            if result.returncode == 0:
                branch_info.commit_count = int(result.stdout.strip())
            
            # Get files changed
            result = await self._run_git_command(repo_path, ["diff", "--name-only", f"main...{branch_name}"])
            if result.returncode == 0:
                branch_info.files_changed = [f.strip() for f in result.stdout.split('\n') if f.strip()]
            
            # Check for uncommitted changes
            result = await self._run_git_command(repo_path, ["status", "--porcelain"])
            has_uncommitted = bool(result.stdout.strip())
            
            # Update last activity
            branch_info.last_activity = datetime.now().isoformat()
            branch_info.metadata.update({
                "has_uncommitted_changes": has_uncommitted,
                "last_checked": datetime.now().isoformat()
            })
            
            return branch_info
            
        except Exception as e:
            logger.error(f"Failed to get branch status for {branch_name}: {e}")
            branch_info.status = BranchStatus.FAILED
            return branch_info
    
    @api_contract(
        title="Branch Test Validation API",
        endpoint="validate_branch_tests",
        method="ASYNC",
        request_schema={"branch_name": "str"},
        response_schema={"tests_passing": "bool", "test_output": "str"},
        description="Validates that all tests pass on the branch before merge eligibility"
    )
    async def validate_branch_tests(self, branch_name: str) -> Tuple[bool, str]:
        """Validate that tests pass on branch"""
        
        if branch_name not in self.branches:
            return False, "Branch not found"
        
        branch_info = self.branches[branch_name]
        repo_path = Path(branch_info.repo_path)
        
        try:
            # Checkout the branch
            await self._run_git_command(repo_path, ["checkout", branch_name])
            
            # Pull latest from main to ensure up to date
            await self._run_git_command(repo_path, ["pull", "origin", "main"])
            
            # Run tests - look for common test commands
            test_commands = [
                ["npm", "test"],
                ["python", "-m", "pytest"],
                ["cargo", "test"],
                ["make", "test"],
                ["./test.sh"]
            ]
            
            test_output = ""
            tests_passed = False
            
            for test_cmd in test_commands:
                # Check if test command exists
                if await self._command_exists(test_cmd[0]):
                    logger.info(f"Running tests with: {' '.join(test_cmd)}")
                    
                    result = await self._run_command(repo_path, test_cmd)
                    test_output = result.stdout + result.stderr
                    
                    if result.returncode == 0:
                        tests_passed = True
                        logger.info(f"Tests passed for branch {branch_name}")
                        break
                    else:
                        logger.warning(f"Tests failed for branch {branch_name}: {test_output}")
            
            # Update branch info
            branch_info.tests_passing = tests_passed
            branch_info.metadata["last_test_run"] = datetime.now().isoformat()
            branch_info.metadata["test_output"] = test_output
            
            if tests_passed:
                branch_info.status = BranchStatus.READY_FOR_MERGE
            
            return tests_passed, test_output
            
        except Exception as e:
            logger.error(f"Failed to validate tests for branch {branch_name}: {e}")
            return False, str(e)
    
    @danger_zone(
        title="Git Merge Operations",
        risk_level="high",
        description="Merge operations can fail and leave repository in inconsistent state",
        mitigation="Pre-merge validation, atomic operations, rollback capability",
        monitoring="Merge success rates, conflict frequency, rollback occurrences"
    )
    async def dry_run_merge(self, branch_name: str, target_branch: str = "main") -> Tuple[bool, Dict[str, Any]]:
        """Perform dry-run merge to check for conflicts without committing"""
        
        if branch_name not in self.branches:
            return False, {"error": "Branch not found"}
        
        branch_info = self.branches[branch_name]
        repo_path = Path(branch_info.repo_path)
        
        logger.info(f"Performing dry-run merge of {branch_name} to {target_branch}")
        
        try:
            # Save current branch
            current_branch_result = await self._run_git_command(repo_path, ["rev-parse", "--abbrev-ref", "HEAD"])
            current_branch = current_branch_result.stdout.strip()
            
            # Checkout target branch and update
            await self._run_git_command(repo_path, ["checkout", target_branch])
            await self._run_git_command(repo_path, ["pull", "origin", target_branch])
            
            # Attempt merge with --no-commit flag
            result = await self._run_git_command(repo_path, ["merge", "--no-commit", "--no-ff", branch_name])
            
            conflicts = []
            can_merge = False
            
            if result.returncode == 0:
                # No conflicts
                can_merge = True
                logger.info(f"Dry-run merge successful - no conflicts for {branch_name}")
            else:
                # Get conflict details
                conflict_result = await self._run_git_command(repo_path, ["diff", "--name-only", "--diff-filter=U"])
                conflict_files = [f.strip() for f in conflict_result.stdout.split('\n') if f.strip()]
                
                for file in conflict_files:
                    # Get more details about the conflict
                    diff_result = await self._run_git_command(repo_path, ["diff", file])
                    conflicts.append({
                        "file": file,
                        "type": "content",
                        "description": f"Both branches modified {file}"
                    })
                
                logger.warning(f"Dry-run merge found {len(conflicts)} conflicts for {branch_name}")
            
            # Always abort the merge
            await self._run_git_command(repo_path, ["merge", "--abort"])
            
            # Return to original branch
            await self._run_git_command(repo_path, ["checkout", current_branch])
            
            return True, {
                "can_merge": can_merge,
                "conflicts": conflicts,
                "branch_name": branch_name,
                "target_branch": target_branch
            }
            
        except Exception as e:
            logger.error(f"Error during dry-run merge: {e}")
            # Try to clean up
            try:
                await self._run_git_command(repo_path, ["merge", "--abort"])
                await self._run_git_command(repo_path, ["checkout", current_branch])
            except:
                pass
            return False, {"error": str(e)}
    
    async def merge_branch(self, branch_name: str, target_branch: str = "main") -> Tuple[bool, str]:
        """Merge branch to target branch"""
        
        if branch_name not in self.branches:
            return False, "Branch not found"
        
        branch_info = self.branches[branch_name]
        repo_path = Path(branch_info.repo_path)
        
        logger.info(f"Attempting to merge {branch_name} to {target_branch}")
        
        try:
            # Update status
            branch_info.status = BranchStatus.MERGING
            
            # Checkout target branch and update
            await self._run_git_command(repo_path, ["checkout", target_branch])
            await self._run_git_command(repo_path, ["pull", "origin", target_branch])
            
            # Attempt merge
            result = await self._run_git_command(repo_path, ["merge", "--no-ff", branch_name])
            
            if result.returncode == 0:
                # Merge successful
                logger.info(f"Successfully merged {branch_name} to {target_branch}")
                
                # Push merged changes
                push_result = await self._run_git_command(repo_path, ["push", "origin", target_branch])
                
                if push_result.returncode == 0:
                    # Delete branch locally and remotely
                    await self._run_git_command(repo_path, ["branch", "-d", branch_name])
                    await self._run_git_command(repo_path, ["push", "origin", "--delete", branch_name])
                    
                    # Update status
                    branch_info.status = BranchStatus.MERGED
                    branch_info.metadata["merged_at"] = datetime.now().isoformat()
                    
                    return True, "Merge completed successfully"
                else:
                    logger.error(f"Failed to push merge: {push_result.stderr}")
                    return False, f"Merge succeeded but push failed: {push_result.stderr}"
            else:
                # Merge failed - likely conflicts
                logger.warning(f"Merge conflicts detected for {branch_name}: {result.stderr}")
                
                # Get conflict files
                conflict_result = await self._run_git_command(repo_path, ["diff", "--name-only", "--diff-filter=U"])
                conflict_files = [f.strip() for f in conflict_result.stdout.split('\n') if f.strip()]
                
                # Abort merge to clean state
                await self._run_git_command(repo_path, ["merge", "--abort"])
                
                # Update branch info
                branch_info.status = BranchStatus.CONFLICT
                branch_info.merge_conflicts = conflict_files
                branch_info.metadata["conflict_detected_at"] = datetime.now().isoformat()
                
                return False, f"Merge conflicts in files: {', '.join(conflict_files)}"
                
        except Exception as e:
            logger.error(f"Failed to merge branch {branch_name}: {e}")
            
            # Try to abort merge if it was in progress
            try:
                await self._run_git_command(repo_path, ["merge", "--abort"])
            except:
                pass
            
            branch_info.status = BranchStatus.FAILED
            return False, str(e)
    
    async def delete_branch(self, branch_name: str) -> bool:
        """Delete branch (for cleanup or reset)"""
        
        if branch_name not in self.branches:
            return False
        
        branch_info = self.branches[branch_name]
        repo_path = Path(branch_info.repo_path)
        
        try:
            # Checkout main first
            await self._run_git_command(repo_path, ["checkout", "main"])
            
            # Delete branch locally
            result = await self._run_git_command(repo_path, ["branch", "-D", branch_name])  # Force delete
            
            # Delete remotely if exists
            await self._run_git_command(repo_path, ["push", "origin", "--delete", branch_name])
            
            # Remove from tracking
            del self.branches[branch_name]
            
            logger.info(f"Deleted branch {branch_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete branch {branch_name}: {e}")
            return False
    
    async def reset_branch_to_main(self, branch_name: str) -> bool:
        """Reset branch to main (for redo scenarios)"""
        
        if branch_name not in self.branches:
            return False
        
        branch_info = self.branches[branch_name]
        repo_path = Path(branch_info.repo_path)
        
        try:
            # Checkout the branch
            await self._run_git_command(repo_path, ["checkout", branch_name])
            
            # Reset to main
            await self._run_git_command(repo_path, ["reset", "--hard", "origin/main"])
            
            # Force push to reset remote branch
            result = await self._run_git_command(repo_path, ["push", "--force", "origin", branch_name])
            
            if result.returncode == 0:
                # Reset branch info
                branch_info.status = BranchStatus.ACTIVE
                branch_info.commit_count = 0
                branch_info.files_changed = []
                branch_info.tests_passing = None
                branch_info.merge_conflicts = []
                branch_info.last_activity = datetime.now().isoformat()
                branch_info.metadata["reset_at"] = datetime.now().isoformat()
                
                logger.info(f"Reset branch {branch_name} to main")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to reset branch {branch_name}: {e}")
            return False
    
    # Utility methods
    
    async def _run_git_command(self, repo_path: Path, args: List[str]) -> subprocess.CompletedProcess:
        """Run git command in repository directory"""
        return await self._run_command(repo_path, ["git"] + args)
    
    async def _run_command(self, repo_path: Path, cmd: List[str]) -> subprocess.CompletedProcess:
        """Run command in repository directory"""
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=repo_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=process.returncode,
            stdout=stdout.decode('utf-8') if stdout else "",
            stderr=stderr.decode('utf-8') if stderr else ""
        )
    
    async def _command_exists(self, command: str) -> bool:
        """Check if command exists in PATH"""
        try:
            result = await asyncio.create_subprocess_exec(
                "which", command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.communicate()
            return result.returncode == 0
        except:
            return False
    
    # Public API methods
    
    def get_all_branches(self) -> List[BranchInfo]:
        """Get all tracked branches"""
        return list(self.branches.values())
    
    def get_branches_by_coder(self, coder_id: str) -> List[BranchInfo]:
        """Get branches for specific Coder"""
        return [b for b in self.branches.values() if b.coder_id == coder_id]
    
    def get_branches_by_status(self, status: BranchStatus) -> List[BranchInfo]:
        """Get branches filtered by status"""
        return [b for b in self.branches.values() if b.status == status]
    
    async def get_coder_repository_status(self, coder_id: str) -> Dict[str, Any]:
        """Get overall repository status for a Coder"""
        
        if coder_id not in self.coder_repos:
            return {"error": f"Invalid coder_id: {coder_id}"}
        
        repo_path = self.coder_repos[coder_id]
        
        if not repo_path.exists():
            return {"error": f"Repository does not exist: {repo_path}"}
        
        try:
            # Get current branch
            result = await self._run_git_command(repo_path, ["branch", "--show-current"])
            current_branch = result.stdout.strip()
            
            # Get status
            result = await self._run_git_command(repo_path, ["status", "--porcelain"])
            has_changes = bool(result.stdout.strip())
            
            # Get recent commits
            result = await self._run_git_command(repo_path, ["log", "--oneline", "-5"])
            recent_commits = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            return {
                "coder_id": coder_id,
                "repo_path": str(repo_path),
                "current_branch": current_branch,
                "has_uncommitted_changes": has_changes,
                "recent_commits": recent_commits,
                "active_branches": len(self.get_branches_by_coder(coder_id)),
                "status": "healthy"
            }
            
        except Exception as e:
            logger.error(f"Failed to get repository status for Coder-{coder_id}: {e}")
            return {"error": str(e)}