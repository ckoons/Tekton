"""
Advanced Task Coordination for A2A Protocol v0.2.1

Provides sophisticated task coordination patterns including dependencies,
workflows, parallel execution, and conditional logic.
"""

from typing import Dict, List, Optional, Set, Any, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4
import asyncio

from tekton.models.base import TektonBaseModel
from .task import Task, TaskState, TaskPriority, TaskManager
from .errors import TaskNotFoundError, InvalidRequestError


class DependencyType(str, Enum):
    """Types of task dependencies"""
    FINISH_TO_START = "finish_to_start"  # B starts after A finishes
    START_TO_START = "start_to_start"    # B starts after A starts
    FINISH_TO_FINISH = "finish_to_finish" # B finishes after A finishes
    START_TO_FINISH = "start_to_finish"  # B finishes after A starts


class CoordinationPattern(str, Enum):
    """Task coordination patterns"""
    SEQUENTIAL = "sequential"      # Tasks run one after another
    PARALLEL = "parallel"         # Tasks run simultaneously
    PIPELINE = "pipeline"         # Output of one task feeds into next
    FANOUT = "fanout"            # One task triggers multiple tasks
    FANIN = "fanin"              # Multiple tasks merge into one
    CONDITIONAL = "conditional"   # Tasks run based on conditions
    LOOP = "loop"                # Tasks repeat based on conditions


@dataclass
class TaskDependency:
    """Represents a dependency between tasks"""
    predecessor_id: str
    successor_id: str
    dependency_type: DependencyType = DependencyType.FINISH_TO_START
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_satisfied(self, tasks: Dict[str, Task]) -> bool:
        """Check if dependency is satisfied"""
        predecessor = tasks.get(self.predecessor_id)
        if not predecessor:
            return False
            
        if self.dependency_type == DependencyType.FINISH_TO_START:
            return predecessor.state in [TaskState.COMPLETED]
        elif self.dependency_type == DependencyType.START_TO_START:
            return predecessor.state in [TaskState.RUNNING, TaskState.COMPLETED]
        elif self.dependency_type == DependencyType.FINISH_TO_FINISH:
            # Special handling needed - successor can run but not complete
            return True
        elif self.dependency_type == DependencyType.START_TO_FINISH:
            return predecessor.state in [TaskState.RUNNING, TaskState.COMPLETED]
            
        return False


@dataclass
class ConditionalRule:
    """Rule for conditional task execution"""
    condition: str  # Expression to evaluate
    true_task_id: Optional[str] = None
    false_task_id: Optional[str] = None
    context_variables: Dict[str, Any] = field(default_factory=dict)
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate the condition"""
        # Simple evaluation - in production would use safe expression evaluator
        # For now, support basic comparisons
        try:
            # Merge contexts
            eval_context = {**self.context_variables, **context}
            
            # Very basic evaluation (should use proper expression parser)
            if "==" in self.condition:
                left, right = self.condition.split("==")
                return str(eval_context.get(left.strip())) == right.strip().strip("'\"")
            elif ">" in self.condition:
                left, right = self.condition.split(">")
                return float(eval_context.get(left.strip(), 0)) > float(right.strip())
            elif "<" in self.condition:
                left, right = self.condition.split("<")
                return float(eval_context.get(left.strip(), 0)) < float(right.strip())
            else:
                # Default to checking truthiness of variable
                return bool(eval_context.get(self.condition))
        except:
            return False


class TaskWorkflow(TektonBaseModel):
    """Represents a workflow of coordinated tasks"""
    
    id: str
    name: str
    description: Optional[str] = None
    created_by: str
    created_at: datetime
    
    # Workflow components
    tasks: Dict[str, str] = {}  # workflow_task_id -> actual_task_id
    dependencies: List[TaskDependency] = []
    conditional_rules: Dict[str, ConditionalRule] = {}
    
    # Workflow settings
    pattern: CoordinationPattern = CoordinationPattern.SEQUENTIAL
    max_parallel: Optional[int] = None  # For parallel execution
    retry_failed: bool = False
    timeout_seconds: Optional[int] = None
    
    # Workflow state
    state: TaskState = TaskState.PENDING
    context: Dict[str, Any] = {}  # Shared context between tasks
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    @classmethod
    def create(
        cls,
        name: str,
        created_by: str,
        pattern: CoordinationPattern = CoordinationPattern.SEQUENTIAL,
        **kwargs
    ) -> 'TaskWorkflow':
        """Create a new workflow"""
        return cls(
            id=f"workflow-{uuid4().hex[:12]}",
            name=name,
            created_by=created_by,
            created_at=datetime.now(timezone.utc),
            pattern=pattern,
            **kwargs
        )
    
    def add_task(self, workflow_task_id: str, actual_task_id: str) -> None:
        """Add a task to the workflow"""
        self.tasks[workflow_task_id] = actual_task_id
    
    def add_dependency(
        self,
        predecessor_id: str,
        successor_id: str,
        dependency_type: DependencyType = DependencyType.FINISH_TO_START
    ) -> None:
        """Add a dependency between tasks"""
        dep = TaskDependency(
            predecessor_id=predecessor_id,
            successor_id=successor_id,
            dependency_type=dependency_type
        )
        self.dependencies.append(dep)
    
    def add_conditional_rule(
        self,
        rule_id: str,
        condition: str,
        true_task_id: Optional[str] = None,
        false_task_id: Optional[str] = None
    ) -> None:
        """Add a conditional execution rule"""
        rule = ConditionalRule(
            condition=condition,
            true_task_id=true_task_id,
            false_task_id=false_task_id
        )
        self.conditional_rules[rule_id] = rule
    
    def get_ready_tasks(self, task_states: Dict[str, Task]) -> List[str]:
        """Get tasks that are ready to execute"""
        ready = []
        
        for workflow_task_id, actual_task_id in self.tasks.items():
            task = task_states.get(actual_task_id)
            
            # Skip if task doesn't exist or already started
            if not task or task.state != TaskState.PENDING:
                continue
                
            # Check dependencies
            dependencies_satisfied = True
            for dep in self.dependencies:
                if dep.successor_id == actual_task_id:
                    if not dep.is_satisfied(task_states):
                        dependencies_satisfied = False
                        break
            
            if dependencies_satisfied:
                ready.append(actual_task_id)
        
        return ready
    
    def is_complete(self, task_states: Dict[str, Task]) -> bool:
        """Check if workflow is complete"""
        for actual_task_id in self.tasks.values():
            task = task_states.get(actual_task_id)
            if not task or not task.is_terminal():
                return False
        return True
    
    def get_next_tasks(self, completed_task_id: str) -> List[str]:
        """Get tasks that should run after a specific task completes"""
        next_tasks = []
        
        for dep in self.dependencies:
            if dep.predecessor_id == completed_task_id:
                next_tasks.append(dep.successor_id)
        
        return next_tasks


class TaskCoordinator:
    """Coordinates complex task execution patterns"""
    
    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager
        self.workflows: Dict[str, TaskWorkflow] = {}
        self._running_workflows: Set[str] = set()
        self._workflow_tasks: Dict[str, str] = {}  # task_id -> workflow_id
        self._lock = asyncio.Lock()
        
        # Register for task events
        self.task_manager.add_event_callback(self._handle_task_event)
    
    async def create_workflow(
        self,
        name: str,
        created_by: str,
        pattern: CoordinationPattern = CoordinationPattern.SEQUENTIAL,
        **kwargs
    ) -> TaskWorkflow:
        """Create a new workflow"""
        async with self._lock:
            workflow = TaskWorkflow.create(
                name=name,
                created_by=created_by,
                pattern=pattern,
                **kwargs
            )
            self.workflows[workflow.id] = workflow
            return workflow
    
    async def create_sequential_workflow(
        self,
        name: str,
        created_by: str,
        task_definitions: List[Dict[str, Any]]
    ) -> TaskWorkflow:
        """Create a workflow where tasks run sequentially"""
        workflow = await self.create_workflow(
            name=name,
            created_by=created_by,
            pattern=CoordinationPattern.SEQUENTIAL
        )
        
        previous_task_id = None
        for i, task_def in enumerate(task_definitions):
            # Create task
            task = self.task_manager.create_task(
                name=task_def.get("name", f"Task {i+1}"),
                created_by=created_by,
                description=task_def.get("description"),
                input_data=task_def.get("input_data"),
                priority=TaskPriority(task_def.get("priority", "normal"))
            )
            
            # Add to workflow
            workflow_task_id = f"step-{i+1}"
            workflow.add_task(workflow_task_id, task.id)
            self._workflow_tasks[task.id] = workflow.id
            
            # Add dependency on previous task
            if previous_task_id:
                workflow.add_dependency(
                    previous_task_id,
                    task.id,
                    DependencyType.FINISH_TO_START
                )
            
            previous_task_id = task.id
        
        return workflow
    
    async def create_parallel_workflow(
        self,
        name: str,
        created_by: str,
        task_definitions: List[Dict[str, Any]],
        max_parallel: Optional[int] = None
    ) -> TaskWorkflow:
        """Create a workflow where tasks run in parallel"""
        workflow = await self.create_workflow(
            name=name,
            created_by=created_by,
            pattern=CoordinationPattern.PARALLEL,
            max_parallel=max_parallel
        )
        
        for i, task_def in enumerate(task_definitions):
            # Create task
            task = self.task_manager.create_task(
                name=task_def.get("name", f"Task {i+1}"),
                created_by=created_by,
                description=task_def.get("description"),
                input_data=task_def.get("input_data"),
                priority=TaskPriority(task_def.get("priority", "normal"))
            )
            
            # Add to workflow
            workflow_task_id = f"parallel-{i+1}"
            workflow.add_task(workflow_task_id, task.id)
            self._workflow_tasks[task.id] = workflow.id
        
        return workflow
    
    async def create_pipeline_workflow(
        self,
        name: str,
        created_by: str,
        task_definitions: List[Dict[str, Any]]
    ) -> TaskWorkflow:
        """Create a pipeline where output of one task feeds into next"""
        workflow = await self.create_workflow(
            name=name,
            created_by=created_by,
            pattern=CoordinationPattern.PIPELINE
        )
        
        previous_task_id = None
        for i, task_def in enumerate(task_definitions):
            # Create task
            task = self.task_manager.create_task(
                name=task_def.get("name", f"Stage {i+1}"),
                created_by=created_by,
                description=task_def.get("description"),
                input_data=task_def.get("input_data"),
                priority=TaskPriority(task_def.get("priority", "normal"))
            )
            
            # Add to workflow
            workflow_task_id = f"stage-{i+1}"
            workflow.add_task(workflow_task_id, task.id)
            self._workflow_tasks[task.id] = workflow.id
            
            # Add dependency and data flow
            if previous_task_id:
                workflow.add_dependency(
                    previous_task_id,
                    task.id,
                    DependencyType.FINISH_TO_START
                )
                # Mark that this task should receive output from previous
                task.metadata["pipeline_input_from"] = previous_task_id
            
            previous_task_id = task.id
        
        return workflow
    
    async def create_fanout_workflow(
        self,
        name: str,
        created_by: str,
        source_task_def: Dict[str, Any],
        target_task_defs: List[Dict[str, Any]]
    ) -> TaskWorkflow:
        """Create a fan-out workflow where one task triggers multiple"""
        workflow = await self.create_workflow(
            name=name,
            created_by=created_by,
            pattern=CoordinationPattern.FANOUT
        )
        
        # Create source task
        source_task = self.task_manager.create_task(
            name=source_task_def.get("name", "Source Task"),
            created_by=created_by,
            description=source_task_def.get("description"),
            input_data=source_task_def.get("input_data"),
            priority=TaskPriority(source_task_def.get("priority", "normal"))
        )
        
        workflow.add_task("source", source_task.id)
        self._workflow_tasks[source_task.id] = workflow.id
        
        # Create target tasks
        for i, task_def in enumerate(target_task_defs):
            task = self.task_manager.create_task(
                name=task_def.get("name", f"Target {i+1}"),
                created_by=created_by,
                description=task_def.get("description"),
                input_data=task_def.get("input_data"),
                priority=TaskPriority(task_def.get("priority", "normal"))
            )
            
            workflow_task_id = f"target-{i+1}"
            workflow.add_task(workflow_task_id, task.id)
            self._workflow_tasks[task.id] = workflow.id
            
            # Add dependency from source
            workflow.add_dependency(
                source_task.id,
                task.id,
                DependencyType.FINISH_TO_START
            )
        
        return workflow
    
    async def start_workflow(self, workflow_id: str) -> None:
        """Start executing a workflow"""
        async with self._lock:
            workflow = self.workflows.get(workflow_id)
            if not workflow:
                raise InvalidRequestError(f"Workflow {workflow_id} not found")
            
            if workflow.state != TaskState.PENDING:
                raise InvalidRequestError(f"Workflow already started")
            
            workflow.state = TaskState.RUNNING
            workflow.started_at = datetime.now(timezone.utc)
            self._running_workflows.add(workflow_id)
            
            # Start initial tasks
            await self._execute_ready_tasks(workflow)
    
    async def _execute_ready_tasks(self, workflow: TaskWorkflow) -> None:
        """Execute tasks that are ready to run"""
        # Get current task states
        task_states = {}
        for task_id in workflow.tasks.values():
            try:
                task_states[task_id] = self.task_manager.get_task(task_id)
            except TaskNotFoundError:
                pass
        
        # Get ready tasks
        ready_tasks = workflow.get_ready_tasks(task_states)
        
        # Apply parallel execution limits
        if workflow.max_parallel and len(ready_tasks) > workflow.max_parallel:
            ready_tasks = ready_tasks[:workflow.max_parallel]
        
        # Start ready tasks
        for task_id in ready_tasks:
            task = task_states.get(task_id)
            if task and task.state == TaskState.PENDING:
                # Handle pipeline input
                if workflow.pattern == CoordinationPattern.PIPELINE:
                    input_from = task.metadata.get("pipeline_input_from")
                    if input_from:
                        source_task = task_states.get(input_from)
                        if source_task and source_task.output_data:
                            task.input_data = source_task.output_data
                
                # Start the task
                self.task_manager.update_task_state(task_id, TaskState.RUNNING)
    
    def _handle_task_event(
        self,
        event_type: str,
        task: Task,
        message: Optional[str] = None,
        data: Optional[Any] = None
    ) -> None:
        """Handle task events for workflow coordination"""
        # Check if task is part of a workflow
        workflow_id = self._workflow_tasks.get(task.id)
        if not workflow_id or workflow_id not in self._running_workflows:
            return
        
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return
        
        # Handle task completion
        if event_type == "task.state_changed" and task.state == TaskState.COMPLETED:
            # Schedule next tasks
            asyncio.create_task(self._handle_task_completion(workflow, task))
        
        # Handle task failure
        elif event_type == "task.state_changed" and task.state == TaskState.FAILED:
            if not workflow.retry_failed:
                # Fail the workflow
                asyncio.create_task(self._fail_workflow(workflow, f"Task {task.id} failed"))
    
    async def _handle_task_completion(self, workflow: TaskWorkflow, completed_task: Task) -> None:
        """Handle when a task in a workflow completes"""
        async with self._lock:
            # Update workflow context with task output
            if completed_task.output_data:
                workflow.context[f"task_{completed_task.id}_output"] = completed_task.output_data
            
            # Check conditional rules
            for rule_id, rule in workflow.conditional_rules.items():
                if rule.evaluate(workflow.context):
                    if rule.true_task_id:
                        # Enable conditional task
                        pass  # Would need to implement conditional task enabling
                else:
                    if rule.false_task_id:
                        # Enable alternative task
                        pass
            
            # Execute next ready tasks
            await self._execute_ready_tasks(workflow)
            
            # Check if workflow is complete
            task_states = {}
            for task_id in workflow.tasks.values():
                try:
                    task_states[task_id] = self.task_manager.get_task(task_id)
                except TaskNotFoundError:
                    pass
            
            if workflow.is_complete(task_states):
                await self._complete_workflow(workflow)
    
    async def _complete_workflow(self, workflow: TaskWorkflow) -> None:
        """Mark workflow as completed"""
        workflow.state = TaskState.COMPLETED
        workflow.completed_at = datetime.now(timezone.utc)
        self._running_workflows.discard(workflow.id)
    
    async def _fail_workflow(self, workflow: TaskWorkflow, reason: str) -> None:
        """Mark workflow as failed"""
        async with self._lock:
            workflow.state = TaskState.FAILED
            workflow.completed_at = datetime.now(timezone.utc)
            self._running_workflows.discard(workflow.id)
            
            # Cancel remaining pending tasks
            for task_id in workflow.tasks.values():
                try:
                    task = self.task_manager.get_task(task_id)
                    if task.state == TaskState.PENDING:
                        self.task_manager.cancel_task(task_id, f"Workflow failed: {reason}")
                except TaskNotFoundError:
                    pass
    
    async def get_workflow(self, workflow_id: str) -> Optional[TaskWorkflow]:
        """Get workflow details"""
        return self.workflows.get(workflow_id)
    
    async def list_workflows(
        self,
        created_by: Optional[str] = None,
        state: Optional[TaskState] = None
    ) -> List[TaskWorkflow]:
        """List workflows with optional filters"""
        workflows = list(self.workflows.values())
        
        if created_by:
            workflows = [w for w in workflows if w.created_by == created_by]
        
        if state:
            workflows = [w for w in workflows if w.state == state]
        
        return workflows
    
    async def cancel_workflow(self, workflow_id: str, reason: Optional[str] = None) -> None:
        """Cancel a running workflow"""
        async with self._lock:
            workflow = self.workflows.get(workflow_id)
            if not workflow:
                raise InvalidRequestError(f"Workflow {workflow_id} not found")
            
            if workflow.state != TaskState.RUNNING:
                raise InvalidRequestError("Can only cancel running workflows")
            
            workflow.state = TaskState.CANCELLED
            workflow.completed_at = datetime.now(timezone.utc)
            self._running_workflows.discard(workflow_id)
            
            # Cancel all pending/running tasks
            for task_id in workflow.tasks.values():
                try:
                    task = self.task_manager.get_task(task_id)
                    if task.state in [TaskState.PENDING, TaskState.RUNNING]:
                        self.task_manager.cancel_task(
                            task_id, 
                            reason or "Workflow cancelled"
                        )
                except TaskNotFoundError:
                    pass