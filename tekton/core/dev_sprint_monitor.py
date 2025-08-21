"""
TektonCore Development Sprint Monitor

Monitors DAILY_LOG.md files for status changes and manages the Coder workflow:
- Building -> Assigned to Coder-X -> Ready for Merge -> Merged
- Branch management: sprint/coder-x/feature-name
- Task-level and Sprint-level status tracking
"""

import os
import asyncio
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

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

logger = setup_component_logging("tekton_core.dev_sprint_monitor")


class SprintStatus(str, Enum):
    """Development sprint status values"""
    REVIEW = "Review"                    # Human approval pending
    BUILDING = "Building"                # Available for assignment
    ASSIGNED_CODER_A = "Assigned to Coder-A"
    ASSIGNED_CODER_B = "Assigned to Coder-B" 
    ASSIGNED_CODER_C = "Assigned to Coder-C"
    READY_FOR_MERGE = "Ready for Merge"  # All tasks complete
    MERGED = "Merged"                    # Successfully integrated


class TaskStatus(str, Enum):
    """Individual task status values"""
    PENDING = "pending"                  # Not started
    IN_PROGRESS = "in_progress"          # Being worked on
    READY_FOR_MERGE = "ready for merge"  # Complete, ready to commit
    COMMITTED = "committed"              # Committed to branch
    REPAIR_MERGE_CONFLICT = "Repair Merge Conflict"  # Priority repair task


class CoderStatus(str, Enum):
    """Coder availability status"""
    FREE = "free"                        # Available for new assignment
    WORKING = "working"                  # Currently assigned to sprint
    REPAIRING = "repairing"              # Working on merge conflict repair


@state_checkpoint(
    title="Development Sprint State",
    state_type="file_based",
    description="Core sprint data model with task tracking and Coder assignments",
    rationale="File-based state management via DAILY_LOG.md for transparency and debuggability"
)
@dataclass
class DevSprint:
    """Development sprint data model"""
    name: str                            # Sprint name (e.g., "Planning_Team_Workflow_UI_Sprint")
    path: str                            # Full path to sprint directory
    status: SprintStatus                 # Current sprint status
    assigned_coder: Optional[str] = None # Which Coder is assigned (A, B, or C)
    branch_name: Optional[str] = None    # Git branch name
    tasks: List[Dict[str, Any]] = field(default_factory=list)  # Task list with status
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass 
class CoderAssignment:
    """Coder assignment tracking"""
    coder_id: str                        # A, B, or C
    status: CoderStatus                  # Current status
    assigned_sprint: Optional[str] = None  # Currently assigned sprint name
    branch_name: Optional[str] = None    # Current working branch
    last_activity: str = field(default_factory=lambda: datetime.now().isoformat())


@architecture_decision(
    title="File-Based Sprint Status Monitoring",
    description="Monitors DAILY_LOG.md files using filesystem watching for real-time status updates",
    rationale="Provides transparent, debuggable coordination without complex messaging systems",
    alternatives_considered=["Database polling", "Message queue", "Direct API calls"],
    impacts=["system_simplicity", "debugging_ease", "coordination_transparency"]
)
class DailyLogHandler(FileSystemEventHandler):
    """Handles filesystem events for DAILY_LOG.md files"""
    
    def __init__(self, monitor_callback):
        """Initialize handler with callback"""
        self.monitor_callback = monitor_callback
        super().__init__()
    
    def on_modified(self, event):
        """Handle file modification events"""
        if not event.is_directory and event.src_path.endswith('DAILY_LOG.md'):
            logger.info(f"DAILY_LOG.md modified: {event.src_path}")
            # Call monitor callback asynchronously
            asyncio.create_task(self.monitor_callback(event.src_path))


@integration_point(
    title="DAILY_LOG.md Parser Integration",
    target_component="filesystem",
    protocol="file_parsing",
    data_flow="DAILY_LOG.md → LogParser → DevSprint object",
    description="Parses DAILY_LOG.md files to extract sprint and task status information"
)
class DailyLogParser:
    """Parser for DAILY_LOG.md files"""
    
    @api_contract(
        title="Sprint Status Extraction API",
        endpoint="extract_sprint_status",
        method="STATIC",
        request_schema={"log_content": "str"},
        response_schema={"status": "SprintStatus", "tasks": "List[Dict]"},
        description="Extracts sprint status and task list from DAILY_LOG.md content"
    )
    @staticmethod
    def extract_sprint_status(log_content: str) -> Dict[str, Any]:
        """Extract sprint status and tasks from DAILY_LOG.md content"""
        
        # Look for sprint status patterns
        status_patterns = [
            r"##\s*Sprint Status:\s*(\w+(?:\s+\w+)*)",  # ## Sprint Status: Building
            r"Status:\s*(\w+(?:\s+\w+)*)",              # Status: Assigned to Coder-A
            r"Current Status:\s*(\w+(?:\s+\w+)*)"       # Current Status: Ready for Merge
        ]
        
        sprint_status = SprintStatus.BUILDING  # Default
        for pattern in status_patterns:
            match = re.search(pattern, log_content, re.IGNORECASE)
            if match:
                status_text = match.group(1).strip()
                # Map text to enum
                try:
                    if "coder-a" in status_text.lower():
                        sprint_status = SprintStatus.ASSIGNED_CODER_A
                    elif "coder-b" in status_text.lower():
                        sprint_status = SprintStatus.ASSIGNED_CODER_B  
                    elif "coder-c" in status_text.lower():
                        sprint_status = SprintStatus.ASSIGNED_CODER_C
                    elif "ready for merge" in status_text.lower():
                        sprint_status = SprintStatus.READY_FOR_MERGE
                    elif "merged" in status_text.lower():
                        sprint_status = SprintStatus.MERGED
                    elif "review" in status_text.lower():
                        sprint_status = SprintStatus.REVIEW
                    elif "building" in status_text.lower():
                        sprint_status = SprintStatus.BUILDING
                    break
                except ValueError:
                    logger.warning(f"Unknown status text: {status_text}")
        
        # Extract tasks - look for task list patterns
        tasks = []
        task_patterns = [
            r"(?:^|\n)\s*[-*]\s*([^:\n]+):\s*([^\n]+)",  # - Task name: status
            r"(?:^|\n)\s*\d+\.\s*([^:\n]+):\s*([^\n]+)", # 1. Task name: status
            r"(?:^|\n)\s*✅\s*([^:\n]+)",                 # ✅ Completed task
            r"(?:^|\n)\s*❌\s*([^:\n]+)",                 # ❌ Failed/pending task
        ]
        
        for pattern in task_patterns:
            matches = re.finditer(pattern, log_content, re.MULTILINE)
            for match in matches:
                task_name = match.group(1).strip()
                task_status = TaskStatus.PENDING
                
                if len(match.groups()) > 1:
                    status_text = match.group(2).strip().lower()
                    if "ready for merge" in status_text:
                        task_status = TaskStatus.READY_FOR_MERGE  
                    elif "committed" in status_text:
                        task_status = TaskStatus.COMMITTED
                    elif "in progress" in status_text or "working" in status_text:
                        task_status = TaskStatus.IN_PROGRESS
                    elif "repair" in status_text and "conflict" in status_text:
                        task_status = TaskStatus.REPAIR_MERGE_CONFLICT
                elif "✅" in pattern:
                    task_status = TaskStatus.COMMITTED
                
                tasks.append({
                    "name": task_name,
                    "status": task_status.value,
                    "updated_at": datetime.now().isoformat()
                })
        
        return {
            "status": sprint_status,
            "tasks": tasks,
            "assigned_coder": DailyLogParser._extract_assigned_coder(sprint_status),
            "branch_name": DailyLogParser._extract_branch_name(log_content)
        }
    
    @staticmethod
    def _extract_assigned_coder(status: SprintStatus) -> Optional[str]:
        """Extract coder ID from status"""
        if status == SprintStatus.ASSIGNED_CODER_A:
            return "A"
        elif status == SprintStatus.ASSIGNED_CODER_B:
            return "B"
        elif status == SprintStatus.ASSIGNED_CODER_C:
            return "C"
        return None
    
    @staticmethod
    def _extract_branch_name(log_content: str) -> Optional[str]:
        """Extract branch name from log content"""
        # Look for branch patterns
        branch_patterns = [
            r"branch[:\s]+([^\s\n]+)",
            r"sprint/coder-[abc]/([^\s\n]+)",
            r"git checkout -b\s+([^\s\n]+)"
        ]
        
        for pattern in branch_patterns:
            match = re.search(pattern, log_content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None


@architecture_decision(
    title="Development Sprint Monitoring Architecture",
    description="Provides real-time monitoring of development sprints through DAILY_LOG.md file watching",
    rationale="Enables automatic Coder assignment and branch management based on file-based status updates",
    alternatives_considered=["Database polling", "API-based status", "Message queue coordination"],
    impacts=["automation_capability", "response_time", "system_complexity", "debugging_ease"]
)
@performance_boundary(
    title="Sprint Monitor Performance",
    operation="file_system_watching",
    expected_load="~50 sprint directories",
    bottlenecks=["file I/O", "regex parsing", "concurrent file access"],
    optimization_notes="Uses efficient filesystem watching instead of polling",
    sla="<2s response time for file changes"
)
class DevSprintMonitor:
    """Monitors development sprints and manages Coder assignments"""
    
    def __init__(self, sprints_root: Optional[str] = None):
        """Initialize sprint monitor"""
        if sprints_root is None:
            # Default to MetaData/DevelopmentSprints/
            tekton_root = TektonEnviron.get("TEKTON_ROOT") or os.getcwd()
            sprints_root = os.path.join(tekton_root, "MetaData", "DevelopmentSprints")
        
        self.sprints_root = Path(sprints_root)
        self.sprints: Dict[str, DevSprint] = {}
        self.coders: Dict[str, CoderAssignment] = {
            "A": CoderAssignment(coder_id="A", status=CoderStatus.FREE),
            "B": CoderAssignment(coder_id="B", status=CoderStatus.FREE),
            "C": CoderAssignment(coder_id="C", status=CoderStatus.FREE)
        }
        
        # File system monitoring
        self.observer = Observer()
        self.handler = DailyLogHandler(self._on_daily_log_changed)
        
        # Task assignment queue
        self.assignment_queue: List[str] = []  # Sprint names waiting for assignment
        
        logger.info(f"DevSprintMonitor initialized, monitoring: {self.sprints_root}")
    
    @danger_zone(
        title="Concurrent Sprint Status Updates",
        risk_level="medium",
        description="Multiple DAILY_LOG.md files could be updated simultaneously",
        mitigation="File-level locking and async task queuing",
        monitoring="Log file modification timestamps and parsing errors"
    )
    async def start_monitoring(self):
        """Start monitoring DAILY_LOG.md files"""
        logger.info("Starting development sprint monitoring...")
        
        # Initial scan of existing sprints
        await self._scan_existing_sprints()
        
        # Start filesystem monitoring
        self.observer.schedule(self.handler, str(self.sprints_root), recursive=True)
        self.observer.start()
        
        logger.info(f"Monitoring {len(self.sprints)} development sprints")
    
    async def stop_monitoring(self):
        """Stop monitoring"""
        self.observer.stop()
        self.observer.join()
        logger.info("Stopped development sprint monitoring")
    
    async def _scan_existing_sprints(self):
        """Scan for existing development sprints"""
        if not self.sprints_root.exists():
            logger.warning(f"Sprints root directory does not exist: {self.sprints_root}")
            return
        
        # Look for directories ending in "_Sprint"
        for sprint_dir in self.sprints_root.iterdir():
            if sprint_dir.is_dir() and sprint_dir.name.endswith("_Sprint"):
                daily_log_path = sprint_dir / "DAILY_LOG.md"
                if daily_log_path.exists():
                    await self._process_daily_log(str(daily_log_path))
    
    async def _on_daily_log_changed(self, file_path: str):
        """Handle DAILY_LOG.md file changes"""
        logger.info(f"Processing DAILY_LOG.md change: {file_path}")
        await self._process_daily_log(file_path)
    
    @api_contract(
        title="Daily Log Processing API",
        endpoint="_process_daily_log",
        method="PRIVATE_ASYNC", 
        request_schema={"file_path": "str"},
        response_schema={"processed": "bool"},
        description="Processes DAILY_LOG.md file changes and updates sprint status"
    )
    async def _process_daily_log(self, file_path: str):
        """Process a DAILY_LOG.md file"""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract sprint information
            sprint_path = Path(file_path).parent
            sprint_name = sprint_path.name
            
            # Parse status and tasks
            parsed_data = DailyLogParser.extract_sprint_status(content)
            
            # Update or create sprint
            if sprint_name in self.sprints:
                sprint = self.sprints[sprint_name]
                old_status = sprint.status
                sprint.status = parsed_data["status"]
                sprint.tasks = parsed_data["tasks"]
                sprint.assigned_coder = parsed_data["assigned_coder"]
                sprint.branch_name = parsed_data["branch_name"]
                sprint.last_updated = datetime.now().isoformat()
                
                # Check for status changes
                if old_status != sprint.status:
                    await self._handle_status_change(sprint, old_status)
            else:
                # New sprint
                sprint = DevSprint(
                    name=sprint_name,
                    path=str(sprint_path),
                    status=parsed_data["status"],
                    assigned_coder=parsed_data["assigned_coder"],
                    branch_name=parsed_data["branch_name"],
                    tasks=parsed_data["tasks"]
                )
                self.sprints[sprint_name] = sprint
                logger.info(f"Discovered new sprint: {sprint_name} (status: {sprint.status})")
                
                # Handle initial status
                if sprint.status == SprintStatus.BUILDING:
                    await self._queue_for_assignment(sprint_name)
            
        except Exception as e:
            logger.error(f"Failed to process DAILY_LOG.md at {file_path}: {e}")
    
    async def _handle_status_change(self, sprint: DevSprint, old_status: SprintStatus):
        """Handle sprint status changes"""
        logger.info(f"Sprint {sprint.name} status changed: {old_status} -> {sprint.status}")
        
        # Handle transitions
        if old_status == SprintStatus.REVIEW and sprint.status == SprintStatus.BUILDING:
            # Sprint approved, queue for assignment
            await self._queue_for_assignment(sprint.name)
        
        elif sprint.status == SprintStatus.READY_FOR_MERGE:
            # Sprint ready for merge, free up the Coder
            if sprint.assigned_coder:
                await self._free_coder(sprint.assigned_coder)
        
        elif sprint.status == SprintStatus.MERGED:
            # Sprint completed, clean up
            if sprint.assigned_coder:
                await self._free_coder(sprint.assigned_coder) 
            # Branch should be deleted by merge process
    
    async def _queue_for_assignment(self, sprint_name: str):
        """Queue sprint for Coder assignment"""
        if sprint_name not in self.assignment_queue:
            self.assignment_queue.append(sprint_name)
            logger.info(f"Queued sprint for assignment: {sprint_name}")
            
            # Try to assign immediately
            await self._try_assign_next_sprint()
    
    @api_contract(
        title="Sprint Assignment API", 
        endpoint="_try_assign_next_sprint",
        method="PRIVATE_ASYNC",
        request_schema={},
        response_schema={"assigned": "bool", "coder": "Optional[str]"},
        description="Attempts to assign next queued sprint to an available Coder"
    )
    async def _try_assign_next_sprint(self):
        """Try to assign next sprint in queue to available Coder"""
        if not self.assignment_queue:
            return
        
        # Find free Coder (prioritize repairs)
        free_coder = None
        for coder_id, coder in self.coders.items():
            if coder.status == CoderStatus.FREE:
                free_coder = coder_id
                break
        
        if not free_coder:
            logger.info("No free Coders available for assignment")
            return
        
        # Assign next sprint
        sprint_name = self.assignment_queue.pop(0)
        if sprint_name not in self.sprints:
            logger.warning(f"Sprint not found for assignment: {sprint_name}")
            return
        
        sprint = self.sprints[sprint_name]
        await self._assign_sprint_to_coder(sprint, free_coder)
    
    async def _assign_sprint_to_coder(self, sprint: DevSprint, coder_id: str):
        """Assign sprint to specific Coder"""
        logger.info(f"Assigning sprint {sprint.name} to Coder-{coder_id}")
        
        # Update sprint
        sprint.assigned_coder = coder_id
        if coder_id == "A":
            sprint.status = SprintStatus.ASSIGNED_CODER_A
        elif coder_id == "B":
            sprint.status = SprintStatus.ASSIGNED_CODER_B
        elif coder_id == "C":
            sprint.status = SprintStatus.ASSIGNED_CODER_C
        
        # Generate branch name
        branch_name = f"sprint/coder-{coder_id.lower()}/{sprint.name.lower().replace('_', '-')}"
        sprint.branch_name = branch_name
        
        # Update Coder status
        coder = self.coders[coder_id]
        coder.status = CoderStatus.WORKING
        coder.assigned_sprint = sprint.name
        coder.branch_name = branch_name
        coder.last_activity = datetime.now().isoformat()
        
        # Update DAILY_LOG.md file
        await self._update_daily_log_status(sprint)
        
        logger.info(f"Sprint {sprint.name} assigned to Coder-{coder_id} on branch {branch_name}")
    
    async def _free_coder(self, coder_id: str):
        """Free up a Coder for new assignments"""
        if coder_id not in self.coders:
            return
        
        coder = self.coders[coder_id]
        logger.info(f"Freeing Coder-{coder_id} from sprint {coder.assigned_sprint}")
        
        coder.status = CoderStatus.FREE
        coder.assigned_sprint = None
        coder.branch_name = None
        coder.last_activity = datetime.now().isoformat()
        
        # Try to assign next sprint
        await self._try_assign_next_sprint()
    
    async def _update_daily_log_status(self, sprint: DevSprint):  
        """Update DAILY_LOG.md with new status"""
        daily_log_path = Path(sprint.path) / "DAILY_LOG.md"
        
        try:
            # Read current content
            with open(daily_log_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update status line
            status_text = sprint.status.value
            updated_content = re.sub(
                r"(##\s*Sprint Status:)\s*[^\n]*",
                f"\\1 {status_text}",
                content,
                flags=re.IGNORECASE
            )
            
            # Add assignment info if not present
            if sprint.assigned_coder and sprint.branch_name:
                assignment_info = f"\n**Assigned**: Coder-{sprint.assigned_coder}\n**Branch**: {sprint.branch_name}\n"
                if assignment_info not in updated_content:
                    # Insert after status line
                    updated_content = re.sub(
                        r"(##\s*Sprint Status:[^\n]*\n)",
                        f"\\1{assignment_info}",
                        updated_content,
                        flags=re.IGNORECASE
                    )
            
            # Write back to file
            with open(daily_log_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
                
            logger.info(f"Updated DAILY_LOG.md for sprint {sprint.name}")
            
        except Exception as e:
            logger.error(f"Failed to update DAILY_LOG.md for sprint {sprint.name}: {e}")
    
    # Public API methods
    
    def get_all_sprints(self) -> List[DevSprint]:
        """Get all monitored sprints"""
        return list(self.sprints.values())
    
    def get_sprints_by_status(self, status: SprintStatus) -> List[DevSprint]:
        """Get sprints filtered by status"""
        return [s for s in self.sprints.values() if s.status == status]
    
    def get_coder_status(self) -> Dict[str, CoderAssignment]:
        """Get status of all Coders"""
        return self.coders.copy()
    
    def get_assignment_queue(self) -> List[str]:
        """Get current assignment queue"""
        return self.assignment_queue.copy()
    
    async def force_assign_sprint(self, sprint_name: str, coder_id: str) -> bool:
        """Manually assign sprint to specific Coder"""
        if sprint_name not in self.sprints:
            return False
        
        if coder_id not in self.coders:
            return False
        
        if self.coders[coder_id].status != CoderStatus.FREE:
            return False
        
        sprint = self.sprints[sprint_name]
        await self._assign_sprint_to_coder(sprint, coder_id)
        
        # Remove from queue if present
        if sprint_name in self.assignment_queue:
            self.assignment_queue.remove(sprint_name)
        
        return True
    
    async def create_repair_task(self, sprint_name: str, conflict_details: str) -> bool:
        """Create priority repair task for merge conflicts"""
        if sprint_name not in self.sprints:
            return False
        
        sprint = self.sprints[sprint_name]
        
        # Add repair task to task list
        repair_task = {
            "name": "Repair Merge Conflict",
            "status": TaskStatus.REPAIR_MERGE_CONFLICT.value,
            "details": conflict_details,
            "priority": "high",
            "created_at": datetime.now().isoformat()
        }
        
        # Insert at beginning (highest priority)
        sprint.tasks.insert(0, repair_task)
        
        # Update status back to assigned
        if sprint.assigned_coder:
            if sprint.assigned_coder == "A":
                sprint.status = SprintStatus.ASSIGNED_CODER_A
            elif sprint.assigned_coder == "B":
                sprint.status = SprintStatus.ASSIGNED_CODER_B
            elif sprint.assigned_coder == "C":
                sprint.status = SprintStatus.ASSIGNED_CODER_C
            
            # Update Coder to repairing status
            self.coders[sprint.assigned_coder].status = CoderStatus.REPAIRING
        
        # Update DAILY_LOG.md
        await self._update_daily_log_status(sprint)
        
        logger.info(f"Created repair task for sprint {sprint_name}")
        return True