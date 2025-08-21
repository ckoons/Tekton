"""
TektonCore Merge Coordination System

Manages intelligent merge coordination for multi-AI development workflows.
"""

import os
import json
import asyncio
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

from shared.utils.logging_setup import setup_component_logging

logger = setup_component_logging("tekton_core.merge_coordinator")


class MergeState(str, Enum):
    """Merge request states"""
    PENDING = "pending"                # Branch ready, waiting for analysis
    ANALYZING = "analyzing"            # Performing dry-run analysis
    CLEAN = "clean"                    # No conflicts detected
    CONFLICTED = "conflicted"          # Conflicts require resolution
    RESOLVING = "resolving"            # Human resolution in progress
    MERGED = "merged"                  # Successfully merged
    REJECTED = "rejected"              # Merge rejected
    FAILED = "failed"                  # Merge failed due to error


class ConflictType(str, Enum):
    """Types of merge conflicts"""
    FILE_OVERLAP = "file_overlap"          # Same files modified
    API_CHANGES = "api_changes"            # Incompatible API modifications
    DATABASE_SCHEMA = "database_schema"     # Database schema conflicts
    CONFIGURATION = "configuration"        # Configuration conflicts
    LOGIC_CONTRADICTION = "logic_contradiction"  # Contradictory business logic
    PERFORMANCE_IMPACT = "performance_impact"    # Conflicting performance changes
    SECURITY_CONCERNS = "security_concerns"      # Security implementation conflicts


@dataclass
class ConflictDetail:
    """Detailed conflict information"""
    type: ConflictType
    files: List[str]
    description: str
    severity: str = "medium"  # low, medium, high, critical
    auto_resolvable: bool = False
    suggested_resolution: Optional[str] = None


@dataclass
class MergeOption:
    """Option for conflict resolution"""
    id: str
    ai_worker: str
    branch: str
    approach: str
    pros: List[str]
    cons: List[str]
    code_quality: str
    test_coverage: str
    files_changed: List[str]
    lines_added: int
    lines_removed: int


@dataclass
class MergeRequest:
    """Merge request data model"""
    id: str
    project_id: str
    task_id: str
    ai_worker: str
    branch: str
    target_branch: str = "main"
    state: MergeState = MergeState.PENDING
    conflicts: List[ConflictDetail] = None
    options: List[MergeOption] = None
    resolution_choice: Optional[str] = None
    created_at: str = None
    updated_at: str = None
    analyzed_at: Optional[str] = None
    resolved_at: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.conflicts is None:
            self.conflicts = []
        if self.options is None:
            self.options = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = self.created_at
        if self.metadata is None:
            self.metadata = {}


class GitOperations:
    """Git operations for merge analysis"""
    
    def __init__(self, repo_path: str):
        """Initialize git operations"""
        self.repo_path = Path(repo_path)
        
        if not self.repo_path.exists():
            raise ValueError(f"Repository path does not exist: {repo_path}")
    
    async def check_branch_exists(self, branch: str) -> bool:
        """Check if branch exists"""
        try:
            result = await self._run_git_command(["show-ref", "--verify", f"refs/heads/{branch}"])
            return result.returncode == 0
        except Exception:
            return False
    
    async def get_branch_status(self, branch: str) -> Dict[str, Any]:
        """Get detailed branch status"""
        if not await self.check_branch_exists(branch):
            return {"exists": False}
        
        try:
            # Get commit count ahead/behind main
            ahead_result = await self._run_git_command(["rev-list", "--count", f"main..{branch}"])
            behind_result = await self._run_git_command(["rev-list", "--count", f"{branch}..main"])
            
            # Get file changes
            files_result = await self._run_git_command(["diff", "--name-only", f"main...{branch}"])
            
            # Get commit info
            commit_result = await self._run_git_command(["log", "-1", "--format=%H|%s|%an|%at", branch])
            
            commits_ahead = int(ahead_result.stdout.strip()) if ahead_result.returncode == 0 else 0
            commits_behind = int(behind_result.stdout.strip()) if behind_result.returncode == 0 else 0
            files_changed = files_result.stdout.strip().split('\n') if files_result.stdout.strip() else []
            
            commit_info = {}
            if commit_result.returncode == 0:
                parts = commit_result.stdout.strip().split('|')
                if len(parts) == 4:
                    commit_info = {
                        "hash": parts[0],
                        "message": parts[1],
                        "author": parts[2],
                        "timestamp": int(parts[3])
                    }
            
            return {
                "exists": True,
                "commits_ahead": commits_ahead,
                "commits_behind": commits_behind,
                "files_changed": files_changed,
                "files_count": len(files_changed),
                "last_commit": commit_info
            }
        except Exception as e:
            logger.error(f"Failed to get branch status for {branch}: {e}")
            return {"exists": True, "error": str(e)}
    
    async def dry_run_merge(self, source_branch: str, target_branch: str = "main") -> Dict[str, Any]:
        """Perform dry-run merge analysis"""
        try:
            # First check if merge would succeed
            merge_result = await self._run_git_command([
                "merge-tree", 
                f"HEAD", 
                f"{source_branch}"
            ])
            
            # Check for conflicts in merge-tree output
            has_conflicts = False
            conflict_files = []
            
            if merge_result.stdout:
                # Parse merge-tree output for conflicts
                lines = merge_result.stdout.split('\n')
                for line in lines:
                    if line.startswith('<<<<<<<<') or 'conflict' in line.lower():
                        has_conflicts = True
                        break
            
            # Get detailed diff information
            diff_result = await self._run_git_command([
                "diff", 
                "--name-status", 
                f"{target_branch}...{source_branch}"
            ])
            
            changed_files = []
            if diff_result.stdout:
                for line in diff_result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            status = parts[0]
                            filename = parts[1]
                            changed_files.append({
                                "status": status,
                                "file": filename
                            })
            
            # Get line change statistics
            stat_result = await self._run_git_command([
                "diff", 
                "--stat", 
                f"{target_branch}...{source_branch}"
            ])
            
            lines_added = 0
            lines_removed = 0
            if stat_result.stdout:
                # Parse stat output for line counts
                lines = stat_result.stdout.split('\n')
                for line in lines:
                    if 'insertion' in line or 'deletion' in line:
                        parts = line.split(',')
                        for part in parts:
                            if 'insertion' in part:
                                try:
                                    lines_added = int(part.strip().split()[0])
                                except (ValueError, IndexError):
                                    pass
                            elif 'deletion' in part:
                                try:
                                    lines_removed = int(part.strip().split()[0])
                                except (ValueError, IndexError):
                                    pass
            
            return {
                "can_merge": not has_conflicts,
                "has_conflicts": has_conflicts,
                "conflict_files": conflict_files,
                "changed_files": changed_files,
                "files_count": len(changed_files),
                "lines_added": lines_added,
                "lines_removed": lines_removed,
                "merge_complexity": self._assess_merge_complexity(changed_files, lines_added, lines_removed)
            }
            
        except Exception as e:
            logger.error(f"Failed to perform dry-run merge for {source_branch}: {e}")
            return {
                "can_merge": False,
                "has_conflicts": True,
                "error": str(e)
            }
    
    def _assess_merge_complexity(self, changed_files: List[Dict], lines_added: int, lines_removed: int) -> str:
        """Assess merge complexity based on changes"""
        total_lines = lines_added + lines_removed
        file_count = len(changed_files)
        
        # Check for high-impact file types
        high_impact_files = [
            'package.json', 'requirements.txt', 'Cargo.toml',
            'schema.sql', 'migration', 'config'
        ]
        
        has_high_impact = any(
            any(pattern in f.get('file', '').lower() for pattern in high_impact_files)
            for f in changed_files
        )
        
        if total_lines > 500 or file_count > 20 or has_high_impact:
            return "high"
        elif total_lines > 100 or file_count > 5:
            return "medium"
        else:
            return "low"
    
    async def _run_git_command(self, args: List[str]) -> subprocess.CompletedProcess:
        """Run git command in repository directory"""
        cmd = ["git"] + args
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=self.repo_path,
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


class MergeCoordinator:
    """High-level merge coordination system"""
    
    def __init__(self, storage_path: Optional[str] = None):
        """Initialize merge coordinator"""
        if storage_path is None:
            home = Path.home()
            storage_path = home / ".tekton" / "merges"
        
        self.storage_path = Path(storage_path)
        self.queue_file = self.storage_path / "merge_queue.json"
        self.history_file = self.storage_path / "merge_history.json"
        
        # Ensure directories exist
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize queue if it doesn't exist
        if not self.queue_file.exists():
            self._create_empty_queue()
            
        logger.info(f"Merge coordinator initialized at {self.storage_path}")
    
    def _create_empty_queue(self):
        """Create empty merge queue"""
        queue_data = {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "queue": [],
            "stats": {
                "total_merges": 0,
                "successful_merges": 0,
                "failed_merges": 0,
                "auto_resolved": 0,
                "human_resolved": 0
            }
        }
        
        with open(self.queue_file, 'w') as f:
            json.dump(queue_data, f, indent=2)
    
    def _load_queue(self) -> Dict[str, Any]:
        """Load merge queue from file"""
        try:
            with open(self.queue_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load merge queue: {e}")
            self._create_empty_queue()
            return self._load_queue()
    
    def _save_queue(self, queue_data: Dict[str, Any]):
        """Save merge queue to file"""
        queue_data["updated_at"] = datetime.now().isoformat()
        
        with open(self.queue_file, 'w') as f:
            json.dump(queue_data, f, indent=2)
    
    async def submit_merge_request(self, project_id: str, task_id: str, ai_worker: str, branch: str, repo_path: str) -> MergeRequest:
        """Submit a new merge request"""
        merge_request = MergeRequest(
            id=f"merge_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{task_id[:8]}",
            project_id=project_id,
            task_id=task_id,
            ai_worker=ai_worker,
            branch=branch
        )
        
        # Add to queue
        queue_data = self._load_queue()
        queue_data["queue"].append(asdict(merge_request))
        self._save_queue(queue_data)
        
        # Start analysis
        await self._analyze_merge_request(merge_request, repo_path)
        
        logger.info(f"Submitted merge request for {ai_worker}/{branch}")
        return merge_request
    
    async def _analyze_merge_request(self, merge_request: MergeRequest, repo_path: str):
        """Analyze merge request for conflicts"""
        merge_request.state = MergeState.ANALYZING
        merge_request.analyzed_at = datetime.now().isoformat()
        
        try:
            git_ops = GitOperations(repo_path)
            
            # Get branch status
            branch_status = await git_ops.get_branch_status(merge_request.branch)
            
            if not branch_status.get("exists", False):
                merge_request.state = MergeState.FAILED
                merge_request.metadata["error"] = f"Branch {merge_request.branch} does not exist"
                self._update_merge_request(merge_request)
                return
            
            # Perform dry-run merge
            dry_run_result = await git_ops.dry_run_merge(merge_request.branch)
            
            if dry_run_result.get("can_merge", False):
                merge_request.state = MergeState.CLEAN
                merge_request.metadata.update({
                    "files_changed": dry_run_result.get("files_count", 0),
                    "lines_added": dry_run_result.get("lines_added", 0),
                    "lines_removed": dry_run_result.get("lines_removed", 0),
                    "complexity": dry_run_result.get("merge_complexity", "low")
                })
            else:
                merge_request.state = MergeState.CONFLICTED
                
                # Analyze conflicts
                conflicts = await self._analyze_conflicts(dry_run_result)
                merge_request.conflicts = conflicts
                
                # Create resolution options
                options = await self._create_resolution_options(merge_request, branch_status, dry_run_result)
                merge_request.options = options
            
            self._update_merge_request(merge_request)
            
        except Exception as e:
            logger.error(f"Failed to analyze merge request {merge_request.id}: {e}")
            merge_request.state = MergeState.FAILED
            merge_request.metadata["error"] = str(e)
            self._update_merge_request(merge_request)
    
    async def _analyze_conflicts(self, dry_run_result: Dict[str, Any]) -> List[ConflictDetail]:
        """Analyze conflicts from dry-run result"""
        conflicts = []
        
        changed_files = dry_run_result.get("changed_files", [])
        
        # Simple conflict detection based on file patterns
        for file_info in changed_files:
            filename = file_info.get("file", "")
            
            conflict_type = ConflictType.FILE_OVERLAP  # Default
            severity = "medium"
            
            # Determine conflict type based on file patterns
            if any(pattern in filename.lower() for pattern in ['api', 'endpoint', 'route']):
                conflict_type = ConflictType.API_CHANGES
                severity = "high"
            elif any(pattern in filename.lower() for pattern in ['schema', 'migration', 'model']):
                conflict_type = ConflictType.DATABASE_SCHEMA
                severity = "high"
            elif any(pattern in filename.lower() for pattern in ['config', 'settings', 'env']):
                conflict_type = ConflictType.CONFIGURATION
                severity = "medium"
            
            conflicts.append(ConflictDetail(
                type=conflict_type,
                files=[filename],
                description=f"Conflict in {filename}",
                severity=severity,
                auto_resolvable=False
            ))
        
        return conflicts
    
    async def _create_resolution_options(self, merge_request: MergeRequest, branch_status: Dict, dry_run_result: Dict) -> List[MergeOption]:
        """Create resolution options for conflicts"""
        options = []
        
        # Create option for the submitted branch
        option_a = MergeOption(
            id="option_a",
            ai_worker=merge_request.ai_worker,
            branch=merge_request.branch,
            approach=f"{merge_request.ai_worker}'s implementation",
            pros=["Original implementation", "Complete solution"],
            cons=["May conflict with other changes"],
            code_quality="Good",
            test_coverage="Unknown",
            files_changed=[f.get("file", "") for f in dry_run_result.get("changed_files", [])],
            lines_added=dry_run_result.get("lines_added", 0),
            lines_removed=dry_run_result.get("lines_removed", 0)
        )
        options.append(option_a)
        
        # Create option for main branch (reject changes)
        option_b = MergeOption(
            id="option_b",
            ai_worker="main",
            branch="main",
            approach="Keep current main branch implementation",
            pros=["Stable", "No conflicts"],
            cons=["Loses new functionality"],
            code_quality="Stable",
            test_coverage="Existing",
            files_changed=[],
            lines_added=0,
            lines_removed=0
        )
        options.append(option_b)
        
        return options
    
    def _update_merge_request(self, merge_request: MergeRequest):
        """Update merge request in queue"""
        merge_request.updated_at = datetime.now().isoformat()
        
        queue_data = self._load_queue()
        
        # Find and update the merge request
        for i, item in enumerate(queue_data["queue"]):
            if item["id"] == merge_request.id:
                queue_data["queue"][i] = asdict(merge_request)
                break
        
        self._save_queue(queue_data)
    
    async def get_merge_queue(self) -> List[MergeRequest]:
        """Get current merge queue"""
        queue_data = self._load_queue()
        merge_requests = []
        
        for item in queue_data["queue"]:
            # Convert back to MergeRequest object
            conflicts = [ConflictDetail(**c) for c in item.get("conflicts", [])]
            options = [MergeOption(**o) for o in item.get("options", [])]
            
            item["conflicts"] = conflicts
            item["options"] = options
            item["state"] = MergeState(item["state"])
            
            merge_requests.append(MergeRequest(**item))
        
        # Sort by priority and creation time
        merge_requests.sort(key=lambda mr: (
            0 if mr.state == MergeState.CLEAN else 1,  # Clean merges first
            mr.created_at
        ))
        
        return merge_requests
    
    async def resolve_conflict(self, merge_id: str, chosen_option: str, reason: str = None) -> bool:
        """Resolve merge conflict with chosen option"""
        queue_data = self._load_queue()
        
        for item in queue_data["queue"]:
            if item["id"] == merge_id:
                item["state"] = MergeState.RESOLVING.value
                item["resolution_choice"] = chosen_option
                item["resolved_at"] = datetime.now().isoformat()
                
                if reason:
                    item["metadata"]["resolution_reason"] = reason
                
                self._save_queue(queue_data)
                
                logger.info(f"Resolved merge conflict {merge_id} with option {chosen_option}")
                return True
        
        return False
    
    async def execute_merge(self, merge_id: str, repo_path: str) -> bool:
        """Execute approved merge"""
        # This would integrate with actual git operations
        # For MVP, we'll simulate the merge execution
        
        queue_data = self._load_queue()
        
        for item in queue_data["queue"]:
            if item["id"] == merge_id:
                if item["state"] in [MergeState.CLEAN.value, MergeState.RESOLVING.value]:
                    item["state"] = MergeState.MERGED.value
                    item["metadata"]["merged_at"] = datetime.now().isoformat()
                    
                    # Update stats
                    queue_data["stats"]["total_merges"] += 1
                    queue_data["stats"]["successful_merges"] += 1
                    
                    if item["state"] == MergeState.CLEAN.value:
                        queue_data["stats"]["auto_resolved"] += 1
                    else:
                        queue_data["stats"]["human_resolved"] += 1
                    
                    # Remove from queue (move to history)
                    queue_data["queue"] = [i for i in queue_data["queue"] if i["id"] != merge_id]
                    
                    self._save_queue(queue_data)
                    
                    logger.info(f"Executed merge {merge_id}")
                    return True
        
        return False
    
    async def get_merge_statistics(self) -> Dict[str, Any]:
        """Get merge coordination statistics"""
        queue_data = self._load_queue()
        queue = await self.get_merge_queue()
        
        state_counts = {}
        for state in MergeState:
            state_counts[state.value] = len([mr for mr in queue if mr.state == state])
        
        return {
            "queue_length": len(queue),
            "state_counts": state_counts,
            "statistics": queue_data.get("stats", {}),
            "clean_merges_pending": state_counts.get(MergeState.CLEAN.value, 0),
            "conflicts_pending": state_counts.get(MergeState.CONFLICTED.value, 0)
        }