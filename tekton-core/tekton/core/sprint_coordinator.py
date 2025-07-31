"""
TektonCore Sprint Coordination System

Main coordination component that integrates all sprint management subsystems:
- DevSprintMonitor: Watches DAILY_LOG.md files
- BranchManager: Handles git branch operations
- SprintMergeCoordinator: Manages merge workflow
- Provides unified API for sprint workflow management
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from shared.utils.logging_setup import setup_component_logging

# Import shared environment
try:
    from shared.env import TektonEnviron
except ImportError:
    # Fallback if shared.env not available
    class TektonEnviron:
        @staticmethod
        def get(key, default=None):
            return os.environ.get(key, default)

# Import our components
from .dev_sprint_monitor import DevSprintMonitor, DevSprint, CoderAssignment
from .branch_manager import BranchManager, BranchInfo
from .sprint_merge_coordinator import SprintMergeCoordinator, SprintMergeRequest

# Import landmarks for architectural documentation
try:
    from landmarks import (
        architecture_decision,
        integration_point,
        api_contract,
        state_checkpoint
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

logger = setup_component_logging("tekton_core.sprint_coordinator")


@architecture_decision(
    title="Unified Sprint Coordination Architecture",
    description="Coordinates all sprint management components through single interface",
    rationale="Provides cohesive API while maintaining separation of concerns between monitoring, branching, and merging",
    alternatives_considered=["Direct component access", "Event-driven coordination", "Microservice architecture"],
    impacts=["api_simplicity", "component_coupling", "coordination_reliability"]
)
@integration_point(
    title="Sprint Component Integration Hub",
    target_component="multiple",
    protocol="direct_calls",
    data_flow="SprintCoordinator ↔ [DevSprintMonitor, BranchManager, SprintMergeCoordinator]",
    description="Central coordination point for all sprint management operations"
)
class SprintCoordinator:
    """Main coordination system for TektonCore sprint management"""
    
    def __init__(self, tekton_root: Optional[str] = None):
        """Initialize sprint coordinator"""
        if tekton_root is None:
            from shared.env import TektonEnviron
            tekton_root = TektonEnviron.get("TEKTON_ROOT") or os.getcwd()
        
        self.tekton_root = Path(tekton_root)
        
        # Initialize components
        self.sprint_monitor = DevSprintMonitor()
        self.branch_manager = BranchManager(tekton_root)
        self.merge_coordinator = SprintMergeCoordinator(
            branch_manager=self.branch_manager,
            sprint_monitor=self.sprint_monitor
        )
        
        # Set up cross-component references
        self.merge_coordinator.branch_manager = self.branch_manager
        self.merge_coordinator.sprint_monitor = self.sprint_monitor
        
        # Running state
        self.is_running = False
        
        logger.info("SprintCoordinator initialized with all components")
    
    async def start(self):
        """Start all sprint coordination services"""
        logger.info("Starting TektonCore sprint coordination...")
        
        # Start sprint monitoring
        await self.sprint_monitor.start_monitoring()
        
        # Set up event handlers
        await self._setup_event_handlers()
        
        self.is_running = True
        logger.info("Sprint coordination started successfully")
    
    async def stop(self):
        """Stop all sprint coordination services"""
        logger.info("Stopping TektonCore sprint coordination...")
        
        # Stop monitoring
        await self.sprint_monitor.stop_monitoring()
        
        self.is_running = False
        logger.info("Sprint coordination stopped")
    
    async def _setup_event_handlers(self):
        """Set up event handlers between components"""
        
        # Start background task to check for ready sprints
        asyncio.create_task(self._monitor_ready_for_merge())
    
    @api_contract(
        title="Ready-for-Merge Monitor API",
        endpoint="_monitor_ready_for_merge",
        method="PRIVATE_ASYNC",
        request_schema={},
        response_schema={},
        description="Background task that monitors sprints marked 'Ready for Merge' and initiates merge process"
    )
    async def _monitor_ready_for_merge(self):
        """Background task to monitor sprints ready for merge"""
        
        while self.is_running:
            try:
                # Check for sprints marked "Ready for Merge"
                ready_sprints = self.sprint_monitor.get_sprints_by_status("Ready for Merge")
                
                for sprint in ready_sprints:
                    if sprint.assigned_coder and sprint.branch_name:
                        # Check if already in merge queue
                        existing_request = None
                        for merge_request in self.merge_coordinator.get_merge_queue():
                            if merge_request.sprint_name == sprint.name:
                                existing_request = merge_request
                                break
                        
                        if not existing_request:
                            # Submit for merge
                            coder_repo_path = self.branch_manager.coder_repos.get(sprint.assigned_coder)
                            if coder_repo_path and coder_repo_path.exists():
                                await self.merge_coordinator.submit_sprint_merge(
                                    sprint_name=sprint.name,
                                    coder_id=sprint.assigned_coder,
                                    branch_name=sprint.branch_name,
                                    repo_path=str(coder_repo_path)
                                )
                                logger.info(f"Submitted sprint {sprint.name} for merge processing")
                
                # Sleep before next check
                await asyncio.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Error in ready-for-merge monitor: {e}")
                await asyncio.sleep(30)  # Wait longer on error
    
    # Public API Methods
    
    @api_contract(
        title="Sprint Status API",
        endpoint="get_sprint_status",
        method="SYNC",
        request_schema={"sprint_name": "Optional[str]"},
        response_schema={"sprints": "List[Dict]", "summary": "Dict"},
        description="Gets status of all sprints or specific sprint with detailed information"
    )
    def get_sprint_status(self, sprint_name: Optional[str] = None) -> Dict[str, Any]:
        """Get status of sprints"""
        
        if sprint_name:
            # Get specific sprint
            if sprint_name in self.sprint_monitor.sprints:
                sprint = self.sprint_monitor.sprints[sprint_name]
                
                # Get branch info if available
                branch_info = None
                if sprint.branch_name:
                    branch_info = self.branch_manager.branches.get(sprint.branch_name)
                
                # Get merge info if available
                merge_info = None
                for merge_request in self.merge_coordinator.get_merge_queue():
                    if merge_request.sprint_name == sprint_name:
                        merge_info = merge_request
                        break
                
                return {
                    "sprint": {
                        "name": sprint.name,
                        "status": sprint.status.value,
                        "assigned_coder": sprint.assigned_coder,
                        "branch_name": sprint.branch_name,
                        "tasks": sprint.tasks,
                        "last_updated": sprint.last_updated
                    },
                    "branch": branch_info.__dict__ if branch_info else None,
                    "merge": merge_info.__dict__ if merge_info else None
                }
            else:
                return {"error": f"Sprint not found: {sprint_name}"}
        
        else:
            # Get all sprints
            all_sprints = self.sprint_monitor.get_all_sprints()
            
            sprint_data = []
            for sprint in all_sprints:
                sprint_info = {
                    "name": sprint.name,
                    "status": sprint.status.value,
                    "assigned_coder": sprint.assigned_coder,
                    "branch_name": sprint.branch_name,
                    "task_count": len(sprint.tasks),
                    "last_updated": sprint.last_updated
                }
                
                # Add branch status if available
                if sprint.branch_name and sprint.branch_name in self.branch_manager.branches:
                    branch = self.branch_manager.branches[sprint.branch_name]
                    sprint_info["branch_status"] = branch.status.value
                    sprint_info["commit_count"] = branch.commit_count
                
                sprint_data.append(sprint_info)
            
            # Create summary
            status_counts = {}
            for sprint in all_sprints:
                status = sprint.status.value
                status_counts[status] = status_counts.get(status, 0) + 1
            
            return {
                "sprints": sprint_data,
                "summary": {
                    "total_sprints": len(all_sprints),
                    "status_counts": status_counts,
                    "assignment_queue_length": len(self.sprint_monitor.get_assignment_queue())
                }
            }
    
    def get_coder_status(self) -> Dict[str, Any]:
        """Get status of all Coders"""
        
        coder_assignments = self.sprint_monitor.get_coder_status()
        
        coder_data = {}
        for coder_id, assignment in coder_assignments.items():
            # Get repository status
            repo_status = asyncio.create_task(
                self.branch_manager.get_coder_repository_status(coder_id)
            )
            
            # Get active branches
            active_branches = self.branch_manager.get_branches_by_coder(coder_id)
            
            coder_data[f"Coder-{coder_id}"] = {
                "status": assignment.status.value,
                "assigned_sprint": assignment.assigned_sprint,
                "branch_name": assignment.branch_name,
                "last_activity": assignment.last_activity,
                "active_branches": len(active_branches),
                "branch_names": [b.name for b in active_branches]
            }
        
        return {
            "coders": coder_data,
            "assignment_queue": self.sprint_monitor.get_assignment_queue()
        }
    
    def get_merge_status(self) -> Dict[str, Any]:
        """Get merge coordination status"""
        # Fixed sprint_path -> path attribute issue
        logger.info("GET_MERGE_STATUS: Starting merge status check...")
        
        # Get all sprints from DevSprintMonitor
        all_sprints = self.sprint_monitor.get_all_sprints()
        logger.info(f"GET_MERGE_STATUS: Found {len(all_sprints)} total sprints")
        
        # Log each sprint for debugging
        for sprint in all_sprints:
            logger.info(f"GET_MERGE_STATUS: Sprint '{sprint.name}' has status '{sprint.status.value}'")
        
        # Find sprints that are Ready for Merge
        ready_for_merge = []
        for sprint in all_sprints:
            if sprint.status.value == "Ready for Merge":
                logger.info(f"GET_MERGE_STATUS: Found ready sprint: {sprint.name}")
                ready_for_merge.append({
                    "id": sprint.name.replace(" ", "_").replace("-", "_"),
                    "name": sprint.name,
                    "status": sprint.status.value,
                    "path": str(sprint.path),
                    "updated_at": sprint.last_updated,
                    "updated_by": getattr(sprint, 'updated_by', 'Unknown'),
                    "tasks": len(getattr(sprint, 'tasks', []))
                })
        
        logger.info(f"GET_MERGE_STATUS: Returning {len(ready_for_merge)} ready sprints")
        
        result = {
            "merges": ready_for_merge,
            "total_ready": len(ready_for_merge),
            "queue_length": len(ready_for_merge),
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"GET_MERGE_STATUS: Result: {result}")
        
        return result
    
    async def assign_sprint_to_coder(self, sprint_name: str, coder_id: str) -> bool:
        """Manually assign sprint to specific Coder"""
        
        success = await self.sprint_monitor.force_assign_sprint(sprint_name, coder_id)
        
        if success:
            # Create branch for the assignment
            sprint = self.sprint_monitor.sprints.get(sprint_name)
            if sprint and sprint.branch_name:
                try:
                    branch_info = await self.branch_manager.create_branch(
                        coder_id=coder_id,
                        sprint_name=sprint_name,
                        feature_name=sprint_name.lower().replace('_', '-')
                    )
                    logger.info(f"Created branch {branch_info.name} for manual assignment")
                except Exception as e:
                    logger.error(f"Failed to create branch for manual assignment: {e}")
        
        return success
    
    async def resolve_merge_conflict(self, merge_id: str, action: str, reason: str = "") -> bool:
        """Resolve merge conflict with human decision"""
        
        return await self.merge_coordinator.resolve_human_review(merge_id, action, reason)
    
    async def retry_failed_merge(self, merge_id: str) -> bool:
        """Retry a failed merge request"""
        
        return await self.merge_coordinator.retry_merge(merge_id)
    
    @state_checkpoint(
        title="Sprint Coordination State Summary",
        state_type="computed",
        description="Comprehensive state summary across all sprint coordination components",
        rationale="Provides unified view of system state for monitoring and debugging"
    )
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        
        return {
            "coordinator": {
                "running": self.is_running,
                "tekton_root": str(self.tekton_root)
            },
            "sprint_monitor": {
                "active_sprints": len(self.sprint_monitor.sprints),
                "assignment_queue": len(self.sprint_monitor.assignment_queue)
            },
            "branch_manager": {
                "active_branches": len(self.branch_manager.branches),
                "coder_repositories": list(self.branch_manager.coder_repos.keys())
            },
            "merge_coordinator": {
                "active_merges": len(self.merge_coordinator.merge_requests),
                "pending_human_review": len(self.merge_coordinator.get_pending_merges())
            },
            "timestamp": datetime.now().isoformat()
        }
    
    # Debugging and testing methods
    
    async def create_test_sprint(self, sprint_name: str, coder_id: str) -> bool:
        """Create a test sprint for development/testing"""
        
        try:
            # Create branch first
            branch_info = await self.branch_manager.create_branch(
                coder_id=coder_id,
                sprint_name=sprint_name,
                feature_name="test-feature"
            )
            
            # Simulate sprint assignment
            success = await self.sprint_monitor.force_assign_sprint(sprint_name, coder_id)
            
            if success:
                logger.info(f"Created test sprint {sprint_name} assigned to Coder-{coder_id}")
                return True
            else:
                logger.error(f"Failed to assign test sprint {sprint_name}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to create test sprint: {e}")
            return False
    
    async def perform_dry_run_merge(self, merge_id: str, merge_name: str) -> Dict[str, Any]:
        """Perform a dry-run merge to check for conflicts"""
        
        # Find the sprint
        sprint = None
        for sprint_name, s in self.sprint_monitor.sprints.items():
            if sprint_name == merge_name:
                sprint = s
                break
        
        if not sprint:
            return {
                "success": False,
                "error": f"Sprint {merge_name} not found"
            }
        
        # Get branch name
        branch_name = f"sprint/coder-{sprint.assigned_coder.lower()}/{merge_name.lower().replace('_', '-')}"
        
        # Perform dry-run
        success, result = await self.branch_manager.dry_run_merge(branch_name)
        
        if success:
            return {
                "success": True,
                "merge_id": merge_id,
                "merge_name": merge_name,
                **result
            }
        else:
            return {
                "success": False,
                "merge_id": merge_id,
                "merge_name": merge_name,
                "error": result.get("error", "Unknown error")
            }
    
    def get_debug_info(self) -> Dict[str, Any]:
        """Get detailed debug information"""
        
        return {
            "sprint_monitor": {
                "sprints": {name: sprint.__dict__ for name, sprint in self.sprint_monitor.sprints.items()},
                "coders": {cid: coder.__dict__ for cid, coder in self.sprint_monitor.coders.items()},
                "assignment_queue": self.sprint_monitor.assignment_queue
            },
            "branch_manager": {
                "branches": {name: branch.__dict__ for name, branch in self.branch_manager.branches.items()},
                "coder_repos": {cid: str(path) for cid, path in self.branch_manager.coder_repos.items()}
            },
            "merge_coordinator": {
                "merge_requests": {mid: mr.__dict__ for mid, mr in self.merge_coordinator.merge_requests.items()}
            }
        }