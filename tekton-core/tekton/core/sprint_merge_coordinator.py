"""
TektonCore Sprint Merge Coordinator

Enhanced merge coordination system specifically for the Coder sprint workflow:
- Integrates with DevSprintMonitor for status updates
- Handles sprint-level merge operations
- Manages conflict resolution and repair tasks
- Coordinates between TektonCore and Coder instances
"""

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict, field
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

logger = setup_component_logging("tekton_core.sprint_merge_coordinator")


class SprintMergeState(str, Enum):
    """Sprint merge request states"""
    PENDING = "pending"                  # Sprint ready for merge, awaiting validation
    VALIDATING = "validating"            # Running tests and pre-merge validation
    CLEAN = "clean"                      # Ready to merge automatically
    CONFLICTED = "conflicted"            # Merge conflicts detected
    REPAIRING = "repairing"              # Coder working on conflict repair
    HUMAN_REVIEW = "human_review"        # Requires human intervention
    MERGING = "merging"                  # Merge operation in progress
    MERGED = "merged"                    # Successfully merged
    FAILED = "failed"                    # Merge failed


@state_checkpoint(
    title="Sprint Merge Request State",
    state_type="persistent",
    description="Merge request tracking for complete development sprints",
    rationale="Maintains merge coordination state across sprint completion and conflict resolution cycles"
)
@dataclass
class SprintMergeRequest:
    """Sprint-level merge request"""
    id: str                              # Unique merge request ID
    sprint_name: str                     # Associated development sprint
    coder_id: str                        # Assigned Coder (A, B, or C)
    branch_name: str                     # Git branch name
    repo_path: str                       # Repository path
    state: SprintMergeState              # Current merge state
    
    # Validation info
    tests_passing: Optional[bool] = None # Test validation results
    validation_output: str = ""          # Test/validation output
    
    # Conflict info
    conflict_files: List[str] = field(default_factory=list)  # Files with conflicts
    conflict_details: str = ""           # Detailed conflict information
    repair_attempts: int = 0             # Number of repair attempts
    
    # Timing
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    validated_at: Optional[str] = None   # When validation completed
    merged_at: Optional[str] = None      # When merge completed
    
    # Metadata
    commit_count: int = 0                # Number of commits in sprint
    files_changed: List[str] = field(default_factory=list)  # Modified files
    lines_added: int = 0                 # Lines of code added
    lines_removed: int = 0               # Lines of code removed
    metadata: Dict[str, Any] = field(default_factory=dict)


@architecture_decision(
    title="Sprint-Focused Merge Coordination",
    description="Coordinates merges at sprint level rather than individual commits",
    rationale="Aligns with sprint-based development workflow where entire feature sets are merged atomically",
    alternatives_considered=["Commit-level merging", "Task-level merging", "Continuous integration"],
    impacts=["merge_atomicity", "conflict_resolution", "feature_completeness"]
)
@integration_point(
    title="Sprint Monitor Integration",
    target_component="dev_sprint_monitor",
    protocol="direct_calls", 
    data_flow="SprintMergeCoordinator ↔ DevSprintMonitor ↔ DAILY_LOG.md",
    description="Coordinates with sprint monitoring for status updates and repair task creation"
)
class SprintMergeCoordinator:
    """Coordinates sprint-level merge operations"""
    
    def __init__(self, storage_path: Optional[str] = None, branch_manager=None, sprint_monitor=None):
        """Initialize sprint merge coordinator"""
        if storage_path is None:
            from shared.env import TektonEnviron
            tekton_root = TektonEnviron.get("TEKTON_ROOT") or os.getcwd()
            storage_path = os.path.join(tekton_root, ".tekton", "merges")
        
        self.storage_path = Path(storage_path)
        self.merge_queue_file = self.storage_path / "sprint_merge_queue.json"
        
        # Ensure directories exist
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize queue if it doesn't exist
        if not self.merge_queue_file.exists():
            self._create_empty_queue()
        
        # Component dependencies
        self.branch_manager = branch_manager
        self.sprint_monitor = sprint_monitor
        
        # Active merge requests
        self.merge_requests: Dict[str, SprintMergeRequest] = {}
        
        logger.info(f"SprintMergeCoordinator initialized at {self.storage_path}")
    
    def _create_empty_queue(self):
        """Create empty merge queue"""
        queue_data = {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "queue": [],
            "stats": {
                "total_sprints": 0,
                "successful_merges": 0,
                "failed_merges": 0,
                "conflicts_resolved": 0,
                "human_interventions": 0
            }
        }
        
        with open(self.merge_queue_file, 'w') as f:
            json.dump(queue_data, f, indent=2)
    
    def _load_queue(self) -> Dict[str, Any]:
        """Load merge queue from file"""
        try:
            with open(self.merge_queue_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load merge queue: {e}")
            self._create_empty_queue()
            return self._load_queue()
    
    def _save_queue(self, queue_data: Dict[str, Any]):
        """Save merge queue to file"""
        queue_data["updated_at"] = datetime.now().isoformat()
        
        with open(self.merge_queue_file, 'w') as f:
            json.dump(queue_data, f, indent=2)
    
    @api_contract(
        title="Sprint Merge Submission API",
        endpoint="submit_sprint_merge",
        method="ASYNC",
        request_schema={
            "sprint_name": "str",
            "coder_id": "str", 
            "branch_name": "str",
            "repo_path": "str"
        },
        response_schema={"merge_request": "SprintMergeRequest"},
        description="Submits completed sprint for merge validation and integration"
    )
    async def submit_sprint_merge(self, sprint_name: str, coder_id: str, branch_name: str, repo_path: str) -> SprintMergeRequest:
        """Submit sprint for merge processing"""
        
        merge_id = f"sprint_merge_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{coder_id}_{sprint_name[:8]}"
        
        merge_request = SprintMergeRequest(
            id=merge_id,
            sprint_name=sprint_name,
            coder_id=coder_id,
            branch_name=branch_name,
            repo_path=repo_path,
            state=SprintMergeState.PENDING
        )
        
        # Add to queue
        queue_data = self._load_queue()
        queue_data["queue"].append(asdict(merge_request))
        self._save_queue(queue_data)
        
        # Store in memory
        self.merge_requests[merge_id] = merge_request
        
        # Start validation process
        asyncio.create_task(self._process_merge_request(merge_request))
        
        logger.info(f"Submitted sprint merge request: {sprint_name} by Coder-{coder_id}")
        return merge_request
    
    @performance_boundary(
        title="Merge Validation Performance",
        operation="sprint_merge_validation",
        expected_load="~5 concurrent merge requests",
        bottlenecks=["test execution", "git operations", "file I/O"],
        optimization_notes="Parallel test execution and git operation batching",
        sla="<30s for merge validation"
    )
    async def _process_merge_request(self, merge_request: SprintMergeRequest):
        """Process sprint merge request"""
        
        try:
            # Update state to validating
            merge_request.state = SprintMergeState.VALIDATING
            merge_request.validated_at = datetime.now().isoformat()
            await self._update_merge_request(merge_request)
            
            # Step 1: Validate tests pass
            if self.branch_manager:
                tests_passed, test_output = await self.branch_manager.validate_branch_tests(merge_request.branch_name)
                merge_request.tests_passing = tests_passed
                merge_request.validation_output = test_output
            else:
                # Fallback validation
                tests_passed, test_output = await self._validate_tests_fallback(merge_request)
                merge_request.tests_passing = tests_passed
                merge_request.validation_output = test_output
            
            if not tests_passed:
                # Tests failed - create repair task
                merge_request.state = SprintMergeState.FAILED
                await self._create_repair_task(merge_request, f"Tests failing: {test_output}")
                await self._update_merge_request(merge_request)
                return
            
            # Step 2: Check for merge conflicts
            merge_success, merge_result = await self._attempt_merge(merge_request)
            
            if merge_success:
                # Clean merge
                merge_request.state = SprintMergeState.CLEAN
                await self._execute_clean_merge(merge_request)
            else:
                # Conflicts detected
                merge_request.state = SprintMergeState.CONFLICTED
                merge_request.conflict_details = merge_result
                await self._handle_merge_conflicts(merge_request)
            
            await self._update_merge_request(merge_request)
            
        except Exception as e:
            logger.error(f"Failed to process merge request {merge_request.id}: {e}")
            merge_request.state = SprintMergeState.FAILED
            merge_request.metadata["error"] = str(e)
            await self._update_merge_request(merge_request)
    
    async def _validate_tests_fallback(self, merge_request: SprintMergeRequest) -> Tuple[bool, str]:
        """Fallback test validation when BranchManager not available"""
        
        repo_path = Path(merge_request.repo_path)
        
        # Simple test command detection and execution
        test_commands = [
            (["npm", "test"], "package.json"),
            (["python", "-m", "pytest"], "pytest.ini"),
            (["cargo", "test"], "Cargo.toml"),
            (["make", "test"], "Makefile")
        ]
        
        for test_cmd, indicator_file in test_commands:
            if (repo_path / indicator_file).exists():
                try:
                    process = await asyncio.create_subprocess_exec(
                        *test_cmd,
                        cwd=repo_path,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    
                    stdout, stderr = await process.communicate()
                    output = stdout.decode() + stderr.decode()
                    
                    return process.returncode == 0, output
                    
                except Exception as e:
                    return False, f"Test execution failed: {e}"
        
        # No tests found
        return True, "No test suite detected, assuming pass"
    
    @danger_zone(
        title="Automated Merge Execution",
        risk_level="high",
        description="Automated merges can introduce breaking changes to main branch",
        mitigation="Comprehensive pre-merge validation, rollback capability, human oversight",
        monitoring="Merge success rates, post-merge build status, rollback frequency"
    )
    async def _attempt_merge(self, merge_request: SprintMergeRequest) -> Tuple[bool, str]:
        """Attempt merge and detect conflicts"""
        
        if self.branch_manager:
            # Use BranchManager for merge attempt
            success, result = await self.branch_manager.merge_branch(merge_request.branch_name)
            return success, result
        else:
            # Fallback merge attempt
            return await self._merge_fallback(merge_request)
    
    async def _merge_fallback(self, merge_request: SprintMergeRequest) -> Tuple[bool, str]:
        """Fallback merge attempt when BranchManager not available"""
        
        repo_path = Path(merge_request.repo_path)
        
        try:
            # Checkout main and pull latest
            process = await asyncio.create_subprocess_exec(
                "git", "checkout", "main",
                cwd=repo_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            
            process = await asyncio.create_subprocess_exec(
                "git", "pull", "origin", "main",
                cwd=repo_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            
            # Attempt merge
            process = await asyncio.create_subprocess_exec(
                "git", "merge", "--no-ff", merge_request.branch_name,
                cwd=repo_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            output = stdout.decode() + stderr.decode()
            
            if process.returncode == 0:
                return True, "Merge successful"
            else:
                # Abort merge to clean state
                await asyncio.create_subprocess_exec(
                    "git", "merge", "--abort",
                    cwd=repo_path,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                return False, f"Merge conflicts: {output}"
                
        except Exception as e:
            return False, f"Merge attempt failed: {e}"
    
    async def _execute_clean_merge(self, merge_request: SprintMergeRequest):
        """Execute clean merge (no conflicts)"""
        
        merge_request.state = SprintMergeState.MERGING
        
        try:
            # Execute actual merge
            if self.branch_manager:
                success, result = await self.branch_manager.merge_branch(merge_request.branch_name)
            else:
                success, result = await self._merge_fallback(merge_request)
            
            if success:
                merge_request.state = SprintMergeState.MERGED
                merge_request.merged_at = datetime.now().isoformat()
                
                # Update sprint status to Merged via sprint monitor
                if self.sprint_monitor:
                    await self._notify_sprint_merged(merge_request.sprint_name)
                
                # Update statistics
                queue_data = self._load_queue()
                queue_data["stats"]["successful_merges"] += 1
                self._save_queue(queue_data)
                
                logger.info(f"Successfully merged sprint {merge_request.sprint_name}")
            else:
                merge_request.state = SprintMergeState.FAILED
                merge_request.metadata["merge_error"] = result
                logger.error(f"Failed to execute clean merge for {merge_request.sprint_name}: {result}")
                
        except Exception as e:
            merge_request.state = SprintMergeState.FAILED
            merge_request.metadata["error"] = str(e)
            logger.error(f"Exception during clean merge execution: {e}")
    
    async def _handle_merge_conflicts(self, merge_request: SprintMergeRequest):
        """Handle merge conflicts"""
        
        merge_request.repair_attempts += 1
        
        if merge_request.repair_attempts > 3:
            # Too many repair attempts, escalate to human
            merge_request.state = SprintMergeState.HUMAN_REVIEW
            logger.warning(f"Sprint {merge_request.sprint_name} escalated to human review after {merge_request.repair_attempts} repair attempts")
            return
        
        # Create repair task
        await self._create_repair_task(merge_request, merge_request.conflict_details)
        merge_request.state = SprintMergeState.REPAIRING
        
        logger.info(f"Created repair task for sprint {merge_request.sprint_name} (attempt {merge_request.repair_attempts})")
    
    @integration_point(
        title="Sprint Repair Task Integration",
        target_component="dev_sprint_monitor",
        protocol="method_calls",
        data_flow="SprintMergeCoordinator → DevSprintMonitor → DAILY_LOG.md",
        description="Creates high-priority repair tasks when merge conflicts are detected"
    )
    async def _create_repair_task(self, merge_request: SprintMergeRequest, conflict_details: str):
        """Create repair task via sprint monitor"""
        
        if self.sprint_monitor:
            success = await self.sprint_monitor.create_repair_task(
                merge_request.sprint_name,
                conflict_details
            )
            
            if success:
                logger.info(f"Created repair task for sprint {merge_request.sprint_name}")
            else:
                logger.error(f"Failed to create repair task for sprint {merge_request.sprint_name}")
        else:
            logger.warning("Sprint monitor not available, cannot create repair task")
    
    async def _notify_sprint_merged(self, sprint_name: str):
        """Notify sprint monitor that sprint was successfully merged"""
        
        if self.sprint_monitor and sprint_name in self.sprint_monitor.sprints:
            sprint = self.sprint_monitor.sprints[sprint_name]
            sprint.status = "Merged"  # This should trigger DAILY_LOG.md update
            await self.sprint_monitor._update_daily_log_status(sprint)
    
    async def _update_merge_request(self, merge_request: SprintMergeRequest):
        """Update merge request in queue"""
        
        merge_request.updated_at = datetime.now().isoformat()
        
        # Update in-memory
        self.merge_requests[merge_request.id] = merge_request
        
        # Update persistent queue
        queue_data = self._load_queue()
        
        for i, item in enumerate(queue_data["queue"]):
            if item["id"] == merge_request.id:
                queue_data["queue"][i] = asdict(merge_request)
                break
        
        self._save_queue(queue_data)
    
    # Public API methods
    
    def get_merge_queue(self) -> List[SprintMergeRequest]:
        """Get current merge queue"""
        return list(self.merge_requests.values())
    
    def get_merge_request(self, merge_id: str) -> Optional[SprintMergeRequest]:
        """Get specific merge request"""
        return self.merge_requests.get(merge_id)
    
    def get_pending_merges(self) -> List[SprintMergeRequest]:
        """Get merges pending human review"""
        return [mr for mr in self.merge_requests.values() 
                if mr.state in [SprintMergeState.HUMAN_REVIEW, SprintMergeState.CONFLICTED]]
    
    async def retry_merge(self, merge_id: str) -> bool:
        """Retry failed merge request"""
        
        if merge_id not in self.merge_requests:
            return False
        
        merge_request = self.merge_requests[merge_id]
        
        # Reset state and retry
        merge_request.state = SprintMergeState.PENDING
        merge_request.repair_attempts = 0
        merge_request.conflict_files = []
        merge_request.conflict_details = ""
        
        # Restart processing
        asyncio.create_task(self._process_merge_request(merge_request))
        
        logger.info(f"Retrying merge request {merge_id}")
        return True
    
    async def resolve_human_review(self, merge_id: str, action: str, reason: str = "") -> bool:
        """Resolve merge request under human review"""
        
        if merge_id not in self.merge_requests:
            return False
        
        merge_request = self.merge_requests[merge_id]
        
        if action == "approve":
            # Force merge despite conflicts
            merge_request.state = SprintMergeState.MERGING
            await self._execute_clean_merge(merge_request)
        elif action == "reject":
            # Reject merge, send back to Coder
            merge_request.state = SprintMergeState.FAILED
            await self._create_repair_task(merge_request, f"Human review rejected: {reason}")
        elif action == "reset":
            # Reset branch to main for redo
            if self.branch_manager:
                await self.branch_manager.reset_branch_to_main(merge_request.branch_name)
            merge_request.state = SprintMergeState.FAILED
            await self._create_repair_task(merge_request, f"Branch reset requested: {reason}")
        
        await self._update_merge_request(merge_request)
        
        # Update stats
        queue_data = self._load_queue()
        queue_data["stats"]["human_interventions"] += 1
        self._save_queue(queue_data)
        
        logger.info(f"Resolved human review for {merge_id} with action: {action}")
        return True
    
    def get_merge_statistics(self) -> Dict[str, Any]:
        """Get merge coordination statistics"""
        
        queue_data = self._load_queue()
        
        # Count current states
        state_counts = {}
        for state in SprintMergeState:
            state_counts[state.value] = len([mr for mr in self.merge_requests.values() if mr.state == state])
        
        return {
            "queue_length": len(self.merge_requests),
            "state_counts": state_counts,
            "statistics": queue_data.get("stats", {}),
            "pending_human_review": len(self.get_pending_merges())
        }