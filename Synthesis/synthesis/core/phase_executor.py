#!/usr/bin/env python3
"""
Phase Executor - Executes phases based on their dependencies.

This module handles the execution of phases, including parallelization,
error handling, and status updates.
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable

from synthesis.core.phase_models import PhaseStatus
from synthesis.core.phase_manager import PhaseManager

# Configure logging
logger = logging.getLogger("synthesis.core.phase_executor")


class PhaseExecutor:
    """
    Executes phases according to their dependencies.
    
    This class handles the execution of phases, ensuring they run in the
    correct order based on dependencies.
    """
    
    def __init__(self, phase_manager: PhaseManager):
        """
        Initialize the phase executor.
        
        Args:
            phase_manager: Phase manager to use
        """
        self.phase_manager = phase_manager
        self.phase_handlers: Dict[str, Callable] = {}
        self.executing = False
        self.max_parallel = 4
        self.execution_task = None
    
    def register_handler(self, phase_id: str, handler: Callable) -> bool:
        """
        Register a handler for a phase.
        
        Args:
            phase_id: Phase ID
            handler: Handler function
            
        Returns:
            Success status
        """
        if phase_id not in self.phase_manager.phases:
            logger.warning(f"Cannot register handler for unknown phase {phase_id}")
            return False
        
        self.phase_handlers[phase_id] = handler
        return True
    
    async def execute_phases(self, concurrency: int = 4) -> bool:
        """
        Execute all phases in dependency order.
        
        Args:
            concurrency: Maximum number of phases to execute in parallel
            
        Returns:
            Success status
        """
        if self.executing:
            logger.warning("Phase execution already in progress")
            return False
        
        self.executing = True
        self.max_parallel = concurrency
        
        try:
            # Start the execution task
            self.execution_task = asyncio.create_task(self._execute_phases_task())
            await self.execution_task
            
            # Check for critical failures
            if self.phase_manager.is_execution_failed():
                logger.error("Phase execution failed due to critical phase failures")
                return False
            
            return True
            
        except Exception as e:
            logger.exception(f"Error executing phases: {e}")
            return False
            
        finally:
            self.executing = False
            self.execution_task = None
    
    async def _execute_phases_task(self):
        """Execute phases in dependency order."""
        # Keep executing until all phases are completed or we have a critical failure
        while not self.phase_manager.all_phases_completed() and not self.phase_manager.is_execution_failed():
            # Get phases that are ready to execute
            ready_phases = self.phase_manager.get_ready_phases()
            
            if not ready_phases:
                # Check if we're stuck (no ready phases but not all completed)
                all_done = self.phase_manager.all_phases_completed()
                if not all_done:
                    logger.warning("No phases ready to execute, but not all phases are completed")
                    
                    # Check for dependency cycles
                    pending_phases = [
                        phase_id for phase_id, phase in self.phase_manager.phases.items()
                        if phase["status"] == PhaseStatus.PENDING
                    ]
                    
                    if pending_phases:
                        logger.error(f"Possible dependency cycle involving phases: {', '.join(pending_phases)}")
                        
                        # Skip phases with potential dependency issues
                        for phase_id in pending_phases:
                            self.phase_manager.update_phase_status(
                                phase_id=phase_id,
                                status=PhaseStatus.SKIPPED,
                                error="Skipped due to possible dependency cycle"
                            )
                    
                    break
                else:
                    # All phases completed
                    break
            
            # Limit concurrency
            executing_phases = [
                phase_id for phase_id, phase in self.phase_manager.phases.items()
                if phase["status"] == PhaseStatus.RUNNING
            ]
            
            available_slots = max(0, self.max_parallel - len(executing_phases))
            phases_to_execute = ready_phases[:available_slots]
            
            if not phases_to_execute:
                # Wait for running phases to complete
                await asyncio.sleep(0.1)
                continue
            
            # Start executing phases in parallel
            execution_tasks = []
            
            for phase_id in phases_to_execute:
                # Update status to running
                self.phase_manager.update_phase_status(
                    phase_id=phase_id,
                    status=PhaseStatus.RUNNING
                )
                
                # Create execution task
                task = asyncio.create_task(self._execute_phase(phase_id))
                execution_tasks.append(task)
            
            # Wait for all tasks to complete
            if execution_tasks:
                await asyncio.gather(*execution_tasks)
    
    async def _execute_phase(self, phase_id: str):
        """
        Execute a single phase.
        
        Args:
            phase_id: Phase ID to execute
        """
        if phase_id not in self.phase_handlers:
            logger.error(f"No handler registered for phase {phase_id}")
            self.phase_manager.update_phase_status(
                phase_id=phase_id,
                status=PhaseStatus.FAILED,
                error="No handler registered for phase"
            )
            return
        
        handler = self.phase_handlers[phase_id]
        phase = self.phase_manager.get_phase(phase_id)
        
        if not phase:
            logger.error(f"Phase {phase_id} not found")
            return
        
        try:
            # Execute the handler
            logger.info(f"Executing phase {phase_id}: {phase['name']}")
            result = await handler(phase)
            
            # Update phase status
            self.phase_manager.update_phase_status(
                phase_id=phase_id,
                status=PhaseStatus.COMPLETED,
                result=result
            )
            
            logger.info(f"Phase {phase_id} completed successfully")
            
        except Exception as e:
            logger.exception(f"Error executing phase {phase_id}: {e}")
            
            # Update phase status
            self.phase_manager.update_phase_status(
                phase_id=phase_id,
                status=PhaseStatus.FAILED,
                error=str(e)
            )
    
    async def cancel_execution(self) -> bool:
        """
        Cancel ongoing phase execution.
        
        Returns:
            Success status
        """
        if not self.executing or not self.execution_task:
            logger.warning("No phase execution in progress to cancel")
            return False
        
        try:
            # Cancel the execution task
            self.execution_task.cancel()
            
            # Update status of running phases
            for phase_id, phase in self.phase_manager.phases.items():
                if phase["status"] == PhaseStatus.RUNNING:
                    self.phase_manager.update_phase_status(
                        phase_id=phase_id,
                        status=PhaseStatus.FAILED,
                        error="Execution cancelled"
                    )
            
            logger.info("Phase execution cancelled")
            return True
            
        except Exception as e:
            logger.exception(f"Error cancelling phase execution: {e}")
            return False
            
        finally:
            self.executing = False
