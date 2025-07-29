"""
Workflow Engine for Harmonia.

This module provides the core workflow execution engine,
including task scheduling, dependency resolution, and execution context management.
"""

import logging
import asyncio
import time
import copy
import json
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Union, Callable
from uuid import UUID, uuid4

from harmonia.models.workflow import (
    WorkflowDefinition,
    TaskDefinition,
    WorkflowExecution,
    TaskExecution,
    TaskStatus,
    WorkflowStatus,
    RetryPolicy
)
from harmonia.models.execution import (
    EventType,
    ExecutionEvent,
    Checkpoint,
    ExecutionMetrics,
    ExecutionHistory,
    ExecutionSummary
)
from harmonia.core.state import StateManager
from harmonia.core.expressions import evaluate_expression, substitute_parameters, evaluate_condition
from harmonia.core.component import ComponentRegistry

# Import landmarks with fallback
try:
    from landmarks import (
        architecture_decision,
        performance_boundary,
        integration_point,
        danger_zone,
        state_checkpoint
    )
except ImportError:
    # Define no-op decorators when landmarks not available
    def architecture_decision(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def performance_boundary(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def integration_point(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def danger_zone(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator
    
    def state_checkpoint(**kwargs):
        def decorator(func_or_class):
            return func_or_class
        return decorator

# Configure logger
logger = logging.getLogger(__name__)


@architecture_decision(
    title="Workflow Engine Architecture",
    description="Core orchestration engine that transforms Metis tasks into executable CI workflows",
    rationale="Provides visual workflow design, component routing, and real-time execution monitoring",
    alternatives_considered=["Static configuration", "Script-based orchestration", "External workflow tools"],
    impacts=["task_execution", "component_coordination", "error_handling"],
    decided_by="Casey",
    decision_date="2025-01-29"
)
class WorkflowEngine:
    """
    Core workflow execution engine.
    
    This class is responsible for executing workflows, managing their state,
    resolving dependencies, and coordinating task execution across components.
    """
    
    def __init__(
        self,
        state_manager: Optional[StateManager] = None,
        component_registry: Optional[ComponentRegistry] = None,
        max_concurrent_tasks: int = 10,
        default_retry_policy: Optional[RetryPolicy] = None,
        event_handlers: Optional[Dict[EventType, List[Callable]]] = None
    ):
        """
        Initialize the workflow engine.
        
        Args:
            state_manager: State manager for persisting workflow state
            component_registry: Registry of component adapters
            max_concurrent_tasks: Maximum number of concurrent tasks to execute
            default_retry_policy: Default retry policy for tasks
            event_handlers: Event handlers for workflow events
        """
        self.state_manager = state_manager or StateManager()
        self.component_registry = component_registry or ComponentRegistry()
        self.max_concurrent_tasks = max_concurrent_tasks
        
        # Default retry policy if not specified
        self.default_retry_policy = default_retry_policy or RetryPolicy(
            max_retries=3,
            initial_delay=1.0,
            max_delay=60.0,
            backoff_multiplier=2.0
        )
        
        # Event handlers
        self.event_handlers = event_handlers or {event_type: [] for event_type in EventType}
        
        # Active executions and tasks
        self.active_executions: Dict[UUID, WorkflowExecution] = {}
        self.execution_tasks: Dict[UUID, Dict[str, asyncio.Task]] = {}
        self.execution_semaphores: Dict[UUID, asyncio.Semaphore] = {}
        
        # Execution histories
        self.execution_histories: Dict[UUID, ExecutionHistory] = {}
        
        logger.info("Workflow engine initialized")
    
    @integration_point(
        title="Workflow Execution Entry Point",
        description="Main entry point for executing workflows from Metis task definitions",
        target_component="ComponentRegistry, StateManager",
        protocol="internal_api",
        data_flow="WorkflowDefinition → TaskExecution → Component routing → Results",
        integration_date="2025-01-29"
    )
    async def execute_workflow(
        self,
        workflow_def: WorkflowDefinition,
        input_data: Optional[Dict[str, Any]] = None,
        execution_id: Optional[UUID] = None,
        metadata: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> WorkflowExecution:
        """
        Execute a workflow with the given input.
        
        Args:
            workflow_def: Workflow definition to execute
            input_data: Input data for the workflow
            execution_id: Optional execution ID (generated if not provided)
            metadata: Optional metadata for the execution
            context: Optional context for the execution
            
        Returns:
            Workflow execution object
        """
        # Generate execution ID if not provided
        if execution_id is None:
            execution_id = uuid4()
        
        # Create execution object
        execution = WorkflowExecution(
            id=execution_id,
            workflow_id=workflow_def.id,
            status=WorkflowStatus.PENDING,
            input=input_data or {},
            metadata=metadata or {},
            task_executions={}
        )
        
        # Create execution history
        execution_history = ExecutionHistory(execution_id=execution_id)
        self.execution_histories[execution_id] = execution_history
        
        # Add to active executions
        self.active_executions[execution_id] = execution
        
        # Create semaphore for controlling concurrent tasks
        self.execution_semaphores[execution_id] = asyncio.Semaphore(self.max_concurrent_tasks)
        
        # Initialize task executions
        for task_id, task_def in workflow_def.tasks.items():
            task_execution = TaskExecution(
                task_id=task_id,
                status=TaskStatus.PENDING
            )
            execution.task_executions[task_id] = task_execution
        
        # Save initial state
        await self.state_manager.save_workflow_execution(execution)
        
        # Start execution in background
        execution_task = asyncio.create_task(
            self._execute_workflow(workflow_def, execution, context or {})
        )
        self.execution_tasks[execution_id] = {"main": execution_task}
        
        # Fire workflow started event
        await self._fire_event(EventType.WORKFLOW_STARTED, execution_id, details={
            "workflow_id": str(workflow_def.id),
            "workflow_name": workflow_def.name
        })
        
        logger.info(f"Started workflow execution {execution_id} for workflow {workflow_def.name}")
        return execution
    
    async def _execute_workflow(
        self,
        workflow_def: WorkflowDefinition,
        execution: WorkflowExecution,
        context: Dict[str, Any]
    ) -> None:
        """
        Execute a workflow.
        
        Args:
            workflow_def: Workflow definition to execute
            execution: Workflow execution object
            context: Context for the execution
        """
        try:
            # Update status to running
            execution.status = WorkflowStatus.RUNNING
            execution.start_time = datetime.now()
            await self.state_manager.save_workflow_execution(execution)
            
            # Build execution context
            execution_context = {
                "workflow": {
                    "id": str(workflow_def.id),
                    "name": workflow_def.name
                },
                "execution": {
                    "id": str(execution.id),
                    "start_time": execution.start_time.isoformat()
                },
                "input": execution.input,
                "tasks": {},
                **context
            }
            
            # Find root tasks (no dependencies)
            root_tasks = self._get_root_tasks(workflow_def)
            if not root_tasks:
                raise ValueError(f"Workflow {workflow_def.name} has no root tasks")
            
            # Create a dependency graph
            dependency_graph = self._build_dependency_graph(workflow_def)
            
            # Create a reverse dependency graph (who depends on me)
            reverse_graph = self._build_reverse_dependency_graph(dependency_graph)
            
            # Track completed and failed tasks
            completed_tasks: Set[str] = set()
            failed_tasks: Set[str] = set()
            
            # Create task tracking sets
            pending_tasks: Set[str] = set(workflow_def.tasks.keys())
            ready_tasks: Set[str] = set(task.id for task in root_tasks)
            active_tasks: Set[str] = set()
            
            # Create an event to signal when all tasks are done
            all_tasks_done = asyncio.Event()
            
            # Create checkpoint task
            checkpoint_task = asyncio.create_task(
                self._periodic_checkpoint(execution.id, workflow_def, execution)
            )
            self.execution_tasks[execution.id]["checkpoint"] = checkpoint_task
            
            # Process tasks until all are done
            while pending_tasks and not execution.status == WorkflowStatus.CANCELED:
                # Check if we have completed all tasks
                if not pending_tasks:
                    break
                
                # Process ready tasks
                ready_task_list = list(ready_tasks)
                for task_id in ready_task_list:
                    if task_id in active_tasks or task_id not in pending_tasks:
                        continue
                    
                    # Check if dependencies are satisfied
                    dependencies = dependency_graph.get(task_id, set())
                    if not all(dep in completed_tasks for dep in dependencies):
                        continue
                    
                    # Check if any required dependency failed
                    if any(dep in failed_tasks for dep in dependencies):
                        # Mark this task as skipped due to failed dependency
                        await self._skip_task(
                            workflow_def, execution, task_id,
                            f"Skipped due to failed dependency: {dependencies & failed_tasks}"
                        )
                        pending_tasks.remove(task_id)
                        active_tasks.discard(task_id)
                        ready_tasks.discard(task_id)
                        
                        # Update dependents
                        self._update_dependents(
                            task_id, TaskStatus.SKIPPED, reverse_graph,
                            ready_tasks, pending_tasks, active_tasks,
                            completed_tasks, failed_tasks
                        )
                        continue
                    
                    # Check any conditions for the task
                    task_def = workflow_def.tasks[task_id]
                    if "condition" in task_def.metadata:
                        condition = task_def.metadata["condition"]
                        condition_result = evaluate_condition(condition, execution_context)
                        if not condition_result:
                            # Skip this task as condition is not met
                            await self._skip_task(
                                workflow_def, execution, task_id,
                                "Skipped due to condition not met"
                            )
                            pending_tasks.remove(task_id)
                            active_tasks.discard(task_id)
                            ready_tasks.discard(task_id)
                            
                            # Update dependents
                            self._update_dependents(
                                task_id, TaskStatus.SKIPPED, reverse_graph,
                                ready_tasks, pending_tasks, active_tasks,
                                completed_tasks, failed_tasks
                            )
                            continue
                    
                    # Start task execution in a background task
                    task_execution_task = asyncio.create_task(
                        self._execute_task(
                            workflow_def, execution, task_id, execution_context,
                            on_task_done=lambda t_id, status: self._on_task_done(
                                t_id, status, workflow_def, execution, execution_context,
                                pending_tasks, ready_tasks, active_tasks,
                                completed_tasks, failed_tasks, reverse_graph, all_tasks_done
                            )
                        )
                    )
                    self.execution_tasks[execution.id][task_id] = task_execution_task
                    
                    # Update task sets
                    pending_tasks.remove(task_id)
                    ready_tasks.discard(task_id)
                    active_tasks.add(task_id)
                
                # Wait for a task to complete or a short timeout
                try:
                    # Wait for a task to complete or a short timeout
                    await asyncio.wait_for(all_tasks_done.wait(), timeout=0.1)
                    all_tasks_done.clear()
                except asyncio.TimeoutError:
                    # Continue processing tasks
                    pass
            
            # Cancel checkpoint task
            if not checkpoint_task.done():
                checkpoint_task.cancel()
                try:
                    await checkpoint_task
                except asyncio.CancelledError:
                    pass
            
            # Check final status
            if execution.status == WorkflowStatus.CANCELED:
                logger.info(f"Workflow execution {execution.id} was canceled")
            elif failed_tasks:
                execution.status = WorkflowStatus.FAILED
                execution.error = f"Failed tasks: {', '.join(failed_tasks)}"
                await self._fire_event(EventType.WORKFLOW_FAILED, execution.id, details={
                    "failed_tasks": list(failed_tasks)
                })
            else:
                execution.status = WorkflowStatus.COMPLETED
                await self._fire_event(EventType.WORKFLOW_COMPLETED, execution.id)
            
            # Set end time and save final state
            execution.end_time = datetime.now()
            await self.state_manager.save_workflow_execution(execution)
            
            # Generate and save execution metrics
            metrics = self._generate_execution_metrics(execution)
            history = self.execution_histories.get(execution.id)
            if history:
                history.metrics = metrics
                await self.state_manager.save_execution_history(history)
            
            logger.info(
                f"Workflow execution {execution.id} completed with status {execution.status.value}"
            )
        
        except asyncio.CancelledError:
            # Handle cancellation
            execution.status = WorkflowStatus.CANCELED
            execution.end_time = datetime.now()
            await self.state_manager.save_workflow_execution(execution)
            
            await self._fire_event(EventType.WORKFLOW_CANCELED, execution.id)
            logger.info(f"Workflow execution {execution.id} was canceled")
        
        except Exception as e:
            # Handle unexpected errors
            execution.status = WorkflowStatus.FAILED
            execution.error = f"Workflow execution error: {str(e)}"
            execution.end_time = datetime.now()
            await self.state_manager.save_workflow_execution(execution)
            
            await self._fire_event(
                EventType.ERROR_OCCURRED,
                execution.id,
                details={"error": str(e), "traceback": traceback.format_exc()}
            )
            
            logger.error(f"Error executing workflow {execution.id}: {e}", exc_info=True)
        
        finally:
            # Clean up execution resources
            self.execution_semaphores.pop(execution.id, None)
            for task in self.execution_tasks.get(execution.id, {}).values():
                if not task.done():
                    task.cancel()
    
    @performance_boundary(
        title="Task Execution Pipeline",
        description="Executes individual tasks with retry logic and component routing",
        sla="<5s for task routing and initialization",
        optimization_notes="Semaphore limits concurrent tasks to prevent overload",
        measured_impact="Enables parallel task execution while maintaining system stability"
    )
    @danger_zone(
        title="Component Task Execution",
        description="Routes tasks to external components with error handling",
        risk_level="medium",
        risks=["component_failures", "timeout_errors", "retry_exhaustion"],
        mitigation="Retry policy with exponential backoff, error isolation",
        review_required=True
    )
    async def _execute_task(
        self,
        workflow_def: WorkflowDefinition,
        execution: WorkflowExecution,
        task_id: str,
        execution_context: Dict[str, Any],
        on_task_done: Callable[[str, TaskStatus], None]
    ) -> None:
        """
        Execute a single task within a workflow.
        
        Args:
            workflow_def: Workflow definition
            execution: Workflow execution
            task_id: ID of the task to execute
            execution_context: Execution context
            on_task_done: Callback for when task is done
        """
        task_def = workflow_def.tasks[task_id]
        task_execution = execution.task_executions[task_id]
        
        # Get retry policy for this task
        retry_policy = task_def.retry_policy or self.default_retry_policy
        
        # Update task status to running
        task_execution.status = TaskStatus.RUNNING
        task_execution.start_time = datetime.now()
        await self.state_manager.save_workflow_execution(execution)
        
        await self._fire_event(
            EventType.TASK_STARTED,
            execution.id,
            task_id=task_id,
            details={"task_name": task_def.name}
        )
        
        logger.info(f"Executing task {task_id} ({task_def.name}) in workflow {execution.id}")
        
        # Acquire semaphore to limit concurrent tasks
        semaphore = self.execution_semaphores.get(execution.id)
        if semaphore:
            await semaphore.acquire()
        
        try:
            # Resolve input parameters
            resolved_input = self._resolve_task_input(task_def, execution_context)
            task_execution.input = resolved_input
            
            # Get task component and action
            component_name = task_def.component
            action_name = task_def.action
            
            # Execute retry logic
            retry_count = 0
            last_error = None
            
            while retry_count <= retry_policy.max_retries:
                if retry_count > 0:
                    # Calculate delay with exponential backoff
                    delay = min(
                        retry_policy.max_delay,
                        retry_policy.initial_delay * (retry_policy.backoff_multiplier ** (retry_count - 1))
                    )
                    
                    # Add jitter to delay
                    jitter = 0.1  # 10% jitter
                    delay = delay * (1 + jitter * (2 * (uuid4().int % 100) / 100 - 1))
                    
                    logger.info(
                        f"Retrying task {task_id} ({retry_count}/{retry_policy.max_retries}) "
                        f"after {delay:.2f}s delay"
                    )
                    
                    await self._fire_event(
                        EventType.RETRY_ATTEMPTED,
                        execution.id,
                        task_id=task_id,
                        details={
                            "retry_count": retry_count,
                            "max_retries": retry_policy.max_retries,
                            "delay": delay,
                            "error": str(last_error) if last_error else None
                        }
                    )
                    
                    # Wait before retry
                    await asyncio.sleep(delay)
                
                try:
                    # Execute task on component
                    if component_name in self.component_registry.components:
                        component = self.component_registry.get_component(component_name)
                        result = await component.execute_action(action_name, resolved_input)
                    else:
                        # Mock execution for testing
                        logger.warning(f"Component {component_name} not found, using mock execution")
                        result = {
                            "status": "success",
                            "message": f"Mock execution of {action_name} on {component_name}",
                            "task_id": task_id,
                            "timestamp": datetime.now().isoformat()
                        }
                        await asyncio.sleep(0.5)  # Simulate execution time
                    
                    # Store task result
                    task_execution.output = result
                    
                    # Update task status to completed
                    task_execution.status = TaskStatus.COMPLETED
                    task_execution.end_time = datetime.now()
                    await self.state_manager.save_workflow_execution(execution)
                    
                    # Update execution context with task result
                    execution_context["tasks"][task_id] = result
                    
                    await self._fire_event(
                        EventType.TASK_COMPLETED,
                        execution.id,
                        task_id=task_id,
                        details={"duration": (task_execution.end_time - task_execution.start_time).total_seconds()}
                    )
                    
                    logger.info(f"Task {task_id} ({task_def.name}) completed successfully")
                    
                    # Call the completion callback
                    on_task_done(task_id, TaskStatus.COMPLETED)
                    return
                
                except Exception as e:
                    last_error = e
                    retry_count += 1
                    task_execution.retries = retry_count
                    
                    # Check if we should retry
                    if retry_count <= retry_policy.max_retries:
                        # Save current state for debugging
                        await self.state_manager.save_workflow_execution(execution)
                        continue
                    
                    # No more retries, mark as failed
                    task_execution.status = TaskStatus.FAILED
                    task_execution.end_time = datetime.now()
                    task_execution.error = str(e)
                    await self.state_manager.save_workflow_execution(execution)
                    
                    await self._fire_event(
                        EventType.TASK_FAILED,
                        execution.id,
                        task_id=task_id,
                        details={"error": str(e), "retries": retry_count}
                    )
                    
                    logger.error(f"Task {task_id} ({task_def.name}) failed after {retry_count} retries: {e}")
                    
                    # Call the completion callback
                    on_task_done(task_id, TaskStatus.FAILED)
                    return
        
        finally:
            # Release semaphore
            if semaphore:
                semaphore.release()
    
    def _on_task_done(
        self,
        task_id: str,
        status: TaskStatus,
        workflow_def: WorkflowDefinition,
        execution: WorkflowExecution,
        execution_context: Dict[str, Any],
        pending_tasks: Set[str],
        ready_tasks: Set[str],
        active_tasks: Set[str],
        completed_tasks: Set[str],
        failed_tasks: Set[str],
        reverse_graph: Dict[str, Set[str]],
        all_tasks_done: asyncio.Event
    ) -> None:
        """
        Handle task completion.
        
        Args:
            task_id: ID of the completed task
            status: Final status of the task
            workflow_def: Workflow definition
            execution: Workflow execution
            execution_context: Execution context
            pending_tasks: Set of pending tasks
            ready_tasks: Set of ready tasks
            active_tasks: Set of active tasks
            completed_tasks: Set of completed tasks
            failed_tasks: Set of failed tasks
            reverse_graph: Reverse dependency graph
            all_tasks_done: Event to signal when all tasks are done
        """
        # Update task sets
        active_tasks.discard(task_id)
        
        if status == TaskStatus.COMPLETED:
            completed_tasks.add(task_id)
        else:
            failed_tasks.add(task_id)
        
        # Update task's dependents
        self._update_dependents(
            task_id, status, reverse_graph,
            ready_tasks, pending_tasks, active_tasks,
            completed_tasks, failed_tasks
        )
        
        # Signal that a task has completed
        all_tasks_done.set()
    
    def _update_dependents(
        self,
        task_id: str,
        status: TaskStatus,
        reverse_graph: Dict[str, Set[str]],
        ready_tasks: Set[str],
        pending_tasks: Set[str],
        active_tasks: Set[str],
        completed_tasks: Set[str],
        failed_tasks: Set[str]
    ) -> None:
        """
        Update the status of tasks that depend on the completed task.
        
        Args:
            task_id: ID of the completed task
            status: Status of the completed task
            reverse_graph: Reverse dependency graph
            ready_tasks: Set of ready tasks
            pending_tasks: Set of pending tasks
            active_tasks: Set of active tasks
            completed_tasks: Set of completed tasks
            failed_tasks: Set of failed tasks
        """
        dependents = reverse_graph.get(task_id, set())
        for dependent in dependents:
            if dependent not in pending_tasks:
                continue
            
            # Check if all dependencies are satisfied
            if all(
                dep in completed_tasks or dep in failed_tasks
                for dep in reverse_graph.get(dependent, set())
            ):
                ready_tasks.add(dependent)
    
    async def _skip_task(
        self,
        workflow_def: WorkflowDefinition,
        execution: WorkflowExecution,
        task_id: str,
        reason: str
    ) -> None:
        """
        Skip a task that can't be executed.
        
        Args:
            workflow_def: Workflow definition
            execution: Workflow execution
            task_id: ID of the task to skip
            reason: Reason for skipping the task
        """
        task_def = workflow_def.tasks[task_id]
        task_execution = execution.task_executions[task_id]
        
        # Update task status to skipped
        task_execution.status = TaskStatus.SKIPPED
        task_execution.error = reason
        await self.state_manager.save_workflow_execution(execution)
        
        await self._fire_event(
            EventType.TASK_SKIPPED,
            execution.id,
            task_id=task_id,
            details={"reason": reason}
        )
        
        logger.info(f"Skipped task {task_id} ({task_def.name}): {reason}")
    
    def _resolve_task_input(
        self,
        task_def: TaskDefinition,
        execution_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Resolve input expressions to actual values.
        
        Args:
            task_def: Task definition
            execution_context: Execution context
            
        Returns:
            Resolved input values
        """
        if not task_def.input:
            return {}
        
        # Make a deep copy to avoid modifying the original
        input_copy = copy.deepcopy(task_def.input)
        
        # Process all expressions in the input
        resolved_input = substitute_parameters(input_copy, {}, {}, execution_context.get("tasks"), execution_context)
        
        return resolved_input
    
    def _get_root_tasks(self, workflow_def: WorkflowDefinition) -> List[TaskDefinition]:
        """
        Get tasks with no dependencies (roots of the workflow).
        
        Args:
            workflow_def: Workflow definition
            
        Returns:
            List of root tasks
        """
        return [
            task for task in workflow_def.tasks.values()
            if not task.depends_on
        ]
    
    def _build_dependency_graph(self, workflow_def: WorkflowDefinition) -> Dict[str, Set[str]]:
        """
        Build a dependency graph for the workflow.
        
        Args:
            workflow_def: Workflow definition
            
        Returns:
            Dictionary mapping task IDs to sets of dependent task IDs
        """
        graph: Dict[str, Set[str]] = {}
        
        for task_id, task in workflow_def.tasks.items():
            graph[task_id] = set(task.depends_on)
        
        return graph
    
    def _build_reverse_dependency_graph(self, dependency_graph: Dict[str, Set[str]]) -> Dict[str, Set[str]]:
        """
        Build a reverse dependency graph (who depends on me).
        
        Args:
            dependency_graph: Forward dependency graph
            
        Returns:
            Dictionary mapping task IDs to sets of tasks that depend on them
        """
        reverse_graph: Dict[str, Set[str]] = {task_id: set() for task_id in dependency_graph}
        
        for task_id, dependencies in dependency_graph.items():
            for dep in dependencies:
                reverse_graph.setdefault(dep, set()).add(task_id)
        
        return reverse_graph
    
    async def _periodic_checkpoint(
        self,
        execution_id: UUID,
        workflow_def: WorkflowDefinition,
        execution: WorkflowExecution,
        interval: int = 60
    ) -> None:
        """
        Periodically create checkpoints of the workflow execution.
        
        Args:
            execution_id: Execution ID
            workflow_def: Workflow definition
            execution: Workflow execution
            interval: Checkpoint interval in seconds
        """
        try:
            while execution.status == WorkflowStatus.RUNNING:
                # Wait for the interval
                await asyncio.sleep(interval)
                
                # Create checkpoint if workflow is still running
                if execution.status == WorkflowStatus.RUNNING:
                    await self.create_checkpoint(execution_id)
        
        except asyncio.CancelledError:
            # Task was cancelled, no need to do anything
            pass
        
        except Exception as e:
            logger.error(f"Error in checkpoint task for execution {execution_id}: {e}")
    
    async def create_checkpoint(self, execution_id: UUID) -> Optional[Checkpoint]:
        """
        Create a checkpoint of the current workflow state.
        
        Args:
            execution_id: Execution ID
            
        Returns:
            Created checkpoint if successful
        """
        execution = self.active_executions.get(execution_id)
        if not execution:
            logger.error(f"Cannot create checkpoint: Execution {execution_id} not found")
            return None
        
        # Create checkpoint with current state
        checkpoint = Checkpoint(
            execution_id=execution_id,
            workflow_status=execution.status,
            task_statuses={
                task_id: task.status
                for task_id, task in execution.task_executions.items()
            },
            completed_tasks=[
                task_id for task_id, task in execution.task_executions.items()
                if task.status == TaskStatus.COMPLETED
            ],
            state_data={
                "input": execution.input,
                "output": execution.output,
                "metadata": execution.metadata,
                "task_results": {
                    task_id: task.output
                    for task_id, task in execution.task_executions.items()
                    if task.output
                }
            }
        )
        
        # Save checkpoint to state manager
        await self.state_manager.save_checkpoint(checkpoint)
        
        # Add to execution history
        history = self.execution_histories.get(execution_id)
        if history:
            history.add_checkpoint(checkpoint)
            await self.state_manager.save_execution_history(history)
        
        await self._fire_event(
            EventType.CHECKPOINT_CREATED,
            execution_id,
            details={"checkpoint_id": str(checkpoint.id)}
        )
        
        logger.info(f"Created checkpoint for execution {execution_id}")
        return checkpoint
    
    async def restore_from_checkpoint(
        self,
        checkpoint_id: UUID,
        new_execution_id: Optional[UUID] = None
    ) -> Optional[UUID]:
        """
        Restore a workflow execution from a checkpoint.
        
        Args:
            checkpoint_id: ID of the checkpoint to restore from
            new_execution_id: Optional ID for the new execution
            
        Returns:
            ID of the new execution if successful
        """
        # Load checkpoint
        checkpoint = await self.state_manager.load_checkpoint(checkpoint_id)
        if not checkpoint:
            logger.error(f"Cannot restore: Checkpoint {checkpoint_id} not found")
            return None
        
        # Load original execution
        original_execution = await self.state_manager.load_workflow_execution(checkpoint.execution_id)
        if not original_execution:
            logger.error(f"Cannot restore: Original execution {checkpoint.execution_id} not found")
            return None
        
        # Load workflow definition
        workflow_def = await self.state_manager.load_workflow_definition(original_execution.workflow_id)
        if not workflow_def:
            logger.error(f"Cannot restore: Workflow {original_execution.workflow_id} not found")
            return None
        
        # Generate new execution ID if not provided
        if new_execution_id is None:
            new_execution_id = uuid4()
        
        # Create new execution
        new_execution = WorkflowExecution(
            id=new_execution_id,
            workflow_id=original_execution.workflow_id,
            status=WorkflowStatus.PENDING,
            input=original_execution.input,
            task_executions={},
            metadata={
                **original_execution.metadata,
                "restored_from": str(checkpoint_id),
                "original_execution_id": str(original_execution.id)
            }
        )
        
        # Initialize task executions based on checkpoint
        for task_id, task_def in workflow_def.tasks.items():
            status = checkpoint.task_statuses.get(task_id, TaskStatus.PENDING)
            
            # If task was completed in checkpoint, copy its output
            output = {}
            if task_id in checkpoint.completed_tasks:
                output = checkpoint.state_data.get("task_results", {}).get(task_id, {})
            
            task_execution = TaskExecution(
                task_id=task_id,
                status=status,
                output=output
            )
            
            new_execution.task_executions[task_id] = task_execution
        
        # Save new execution
        await self.state_manager.save_workflow_execution(new_execution)
        
        # Execute workflow from checkpoint state
        await self.execute_workflow(
            workflow_def,
            original_execution.input,
            new_execution_id,
            new_execution.metadata,
            {"restored_from_checkpoint": True, "checkpoint_data": checkpoint.state_data}
        )
        
        logger.info(
            f"Restored execution {new_execution_id} from checkpoint {checkpoint_id} "
            f"of execution {checkpoint.execution_id}"
        )
        return new_execution_id
    
    async def pause_workflow(self, execution_id: UUID) -> bool:
        """
        Pause a running workflow.
        
        Args:
            execution_id: ID of the workflow execution to pause
            
        Returns:
            True if successfully paused
        """
        execution = self.active_executions.get(execution_id)
        if not execution:
            logger.error(f"Cannot pause: Execution {execution_id} not found")
            return False
        
        if execution.status != WorkflowStatus.RUNNING:
            logger.warning(f"Cannot pause: Execution {execution_id} is not running")
            return False
        
        # Create a checkpoint before pausing
        await self.create_checkpoint(execution_id)
        
        # Update status to paused
        execution.status = WorkflowStatus.PAUSED
        await self.state_manager.save_workflow_execution(execution)
        
        await self._fire_event(EventType.WORKFLOW_PAUSED, execution_id)
        
        logger.info(f"Paused workflow execution {execution_id}")
        return True
    
    async def resume_workflow(self, execution_id: UUID) -> bool:
        """
        Resume a paused workflow.
        
        Args:
            execution_id: ID of the workflow execution to resume
            
        Returns:
            True if successfully resumed
        """
        execution = self.active_executions.get(execution_id)
        if not execution:
            logger.error(f"Cannot resume: Execution {execution_id} not found")
            return False
        
        if execution.status != WorkflowStatus.PAUSED:
            logger.warning(f"Cannot resume: Execution {execution_id} is not paused")
            return False
        
        # Update status to running
        execution.status = WorkflowStatus.RUNNING
        await self.state_manager.save_workflow_execution(execution)
        
        await self._fire_event(EventType.WORKFLOW_RESUMED, execution_id)
        
        logger.info(f"Resumed workflow execution {execution_id}")
        return True
    
    async def cancel_workflow(self, execution_id: UUID) -> bool:
        """
        Cancel a running workflow.
        
        Args:
            execution_id: ID of the workflow execution to cancel
            
        Returns:
            True if successfully canceled
        """
        execution = self.active_executions.get(execution_id)
        if not execution:
            logger.error(f"Cannot cancel: Execution {execution_id} not found")
            return False
        
        if execution.status not in (WorkflowStatus.RUNNING, WorkflowStatus.PENDING, WorkflowStatus.PAUSED):
            logger.warning(f"Cannot cancel: Execution {execution_id} is not running, pending, or paused")
            return False
        
        # Create a checkpoint before canceling
        if execution.status == WorkflowStatus.RUNNING:
            await self.create_checkpoint(execution_id)
        
        # Update status to canceled
        execution.status = WorkflowStatus.CANCELED
        execution.end_time = datetime.now()
        await self.state_manager.save_workflow_execution(execution)
        
        # Cancel all running tasks
        task_dict = self.execution_tasks.get(execution_id, {})
        for task_id, task in task_dict.items():
            if not task.done():
                task.cancel()
                logger.debug(f"Canceled task {task_id} for execution {execution_id}")
        
        # Fire event
        await self._fire_event(EventType.WORKFLOW_CANCELED, execution_id)
        
        logger.info(f"Canceled workflow execution {execution_id}")
        return True
    
    async def get_workflow_status(self, execution_id: UUID) -> Optional[ExecutionSummary]:
        """
        Get the status of a workflow execution.
        
        Args:
            execution_id: ID of the workflow execution
            
        Returns:
            Execution summary if found
        """
        # Try to get from active executions first
        execution = self.active_executions.get(execution_id)
        if not execution:
            # Try to load from state manager
            execution = await self.state_manager.load_workflow_execution(execution_id)
            
        if not execution:
            logger.error(f"Execution {execution_id} not found")
            return None
        
        # Get workflow definition
        workflow_def = await self.state_manager.load_workflow_definition(execution.workflow_id)
        if not workflow_def:
            logger.error(f"Workflow {execution.workflow_id} not found")
            return None
        
        # Calculate durations
        duration = None
        if execution.start_time:
            if execution.end_time:
                duration = execution.end_time - execution.start_time
            else:
                duration = datetime.now() - execution.start_time
        
        # Count tasks by status
        completed_count = 0
        failed_count = 0
        for task_execution in execution.task_executions.values():
            if task_execution.status == TaskStatus.COMPLETED:
                completed_count += 1
            elif task_execution.status == TaskStatus.FAILED:
                failed_count += 1
        
        # Create summary
        summary = ExecutionSummary(
            id=execution.id,
            workflow_id=execution.workflow_id,
            workflow_name=workflow_def.name,
            status=execution.status,
            start_time=execution.start_time,
            end_time=execution.end_time,
            duration=duration,
            task_count=len(execution.task_executions),
            completed_tasks=completed_count,
            failed_tasks=failed_count,
            has_error=execution.error is not None,
            error_message=execution.error
        )
        
        return summary
    
    def _generate_execution_metrics(self, execution: WorkflowExecution) -> ExecutionMetrics:
        """
        Generate metrics for a workflow execution.
        
        Args:
            execution: Workflow execution
            
        Returns:
            Execution metrics
        """
        # Calculate total duration
        if execution.start_time and execution.end_time:
            total_duration = execution.end_time - execution.start_time
        else:
            total_duration = timedelta(seconds=0)
        
        # Calculate per-task durations
        task_durations = {}
        task_wait_times = {}
        for task_id, task in execution.task_executions.items():
            if task.start_time and task.end_time:
                task_durations[task_id] = task.end_time - task.start_time
            else:
                task_durations[task_id] = timedelta(seconds=0)
            
            # TODO: Calculate wait times based on dependencies
            task_wait_times[task_id] = timedelta(seconds=0)
        
        # Collect retry counts
        retry_counts = {
            task_id: task.retries
            for task_id, task in execution.task_executions.items()
        }
        
        # Count errors
        error_counts = {
            task_id: 1 if task.error else 0
            for task_id, task in execution.task_executions.items()
        }
        
        # Calculate average task duration
        if task_durations:
            total_task_duration = sum(
                (d.total_seconds() for d in task_durations.values()),
                0.0
            )
            average_task_duration = total_task_duration / len(task_durations)
        else:
            average_task_duration = 0.0
        
        # Count checkpoints
        history = self.execution_histories.get(execution.id)
        checkpoint_count = len(history.checkpoints) if history else 0
        
        # Create metrics
        metrics = ExecutionMetrics(
            execution_id=execution.id,
            total_duration=total_duration,
            task_durations=task_durations,
            task_wait_times=task_wait_times,
            retry_counts=retry_counts,
            error_counts=error_counts,
            checkpoint_count=checkpoint_count,
            average_task_duration=average_task_duration
        )
        
        return metrics
    
    async def _fire_event(
        self,
        event_type: EventType,
        execution_id: UUID,
        task_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        message: Optional[str] = None
    ) -> None:
        """
        Fire a workflow execution event.
        
        Args:
            event_type: Type of event
            execution_id: Execution ID
            task_id: Optional task ID
            details: Optional event details
            message: Optional human-readable message
        """
        # Create event
        event = ExecutionEvent(
            execution_id=execution_id,
            event_type=event_type,
            task_id=task_id,
            details=details or {},
            message=message
        )
        
        # Add to execution history
        history = self.execution_histories.get(execution_id)
        if history:
            history.add_event(event)
        
        # Call event handlers
        handlers = self.event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"Error in event handler for {event_type}: {e}")
    
    def register_event_handler(
        self,
        event_type: EventType,
        handler: Callable[[ExecutionEvent], None]
    ) -> None:
        """
        Register a handler for workflow events.
        
        Args:
            event_type: Type of event to handle
            handler: Event handler function
        """
        self.event_handlers.setdefault(event_type, []).append(handler)
    
    def unregister_event_handler(
        self,
        event_type: EventType,
        handler: Callable[[ExecutionEvent], None]
    ) -> None:
        """
        Unregister a handler for workflow events.
        
        Args:
            event_type: Type of event
            handler: Event handler function
        """
        if event_type in self.event_handlers:
            self.event_handlers[event_type] = [
                h for h in self.event_handlers[event_type] if h != handler
            ]