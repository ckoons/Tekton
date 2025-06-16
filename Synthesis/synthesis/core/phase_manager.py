#!/usr/bin/env python3
"""
Phase Manager - Manages execution phases within Synthesis.

This module handles the lifecycle of execution phases, including
scheduling, monitoring, and coordination.
"""

import logging
import time
from typing import Dict, List, Any, Optional, Set, Callable

from synthesis.core.phase_models import PhaseStatus

# Configure logging
logger = logging.getLogger("synthesis.core.phase_manager")


class PhaseManager:
    """
    Manages execution phases and their dependencies.
    
    This class handles the sequencing, parallelization, and monitoring
    of execution phases based on their dependencies.
    """
    
    def __init__(self):
        """Initialize the phase manager."""
        self.phases: Dict[str, Dict[str, Any]] = {}
        self.callbacks: Dict[str, List[Callable]] = {}
    
    def register_phase(self, 
                     phase_id: str, 
                     name: str, 
                     dependencies: Optional[List[str]] = None,
                     critical: bool = False,
                     metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Register a phase with the manager.
        
        Args:
            phase_id: Unique identifier for the phase
            name: Human-readable name for the phase
            dependencies: List of phase IDs that must complete before this phase
            critical: Whether failure of this phase should stop execution
            metadata: Additional metadata for the phase
            
        Returns:
            Success status
        """
        if phase_id in self.phases:
            logger.warning(f"Phase {phase_id} already registered, updating")
        
        self.phases[phase_id] = {
            "id": phase_id,
            "name": name,
            "dependencies": dependencies or [],
            "status": PhaseStatus.PENDING,
            "critical": critical,
            "metadata": metadata or {},
            "started_at": None,
            "completed_at": None,
            "error": None,
            "result": None
        }
        
        logger.info(f"Registered phase {phase_id}: {name}")
        return True
    
    def register_callback(self, phase_id: str, callback: Callable) -> bool:
        """
        Register a callback for phase status changes.
        
        Args:
            phase_id: Phase ID
            callback: Callback function
            
        Returns:
            Success status
        """
        if phase_id not in self.phases:
            logger.warning(f"Cannot register callback for unknown phase {phase_id}")
            return False
        
        if phase_id not in self.callbacks:
            self.callbacks[phase_id] = []
        
        self.callbacks[phase_id].append(callback)
        return True
    
    def get_phase(self, phase_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a phase by ID.
        
        Args:
            phase_id: Phase ID
            
        Returns:
            Phase data or None if not found
        """
        return self.phases.get(phase_id)
    
    def get_all_phases(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all phases.
        
        Returns:
            Dictionary of all phases
        """
        return self.phases
    
    def get_dependency_graph(self) -> Dict[str, Set[str]]:
        """
        Get the dependency graph for all phases.
        
        Returns:
            Dictionary mapping phase IDs to sets of dependency phase IDs
        """
        graph = {}
        
        for phase_id, phase in self.phases.items():
            graph[phase_id] = set(phase["dependencies"])
        
        return graph
    
    def get_readiness_graph(self) -> Dict[str, Set[str]]:
        """
        Get the readiness graph (inverse of dependency graph).
        
        Returns:
            Dictionary mapping phase IDs to sets of phases that depend on them
        """
        graph = {phase_id: set() for phase_id in self.phases}
        
        for phase_id, phase in self.phases.items():
            for dependency in phase["dependencies"]:
                if dependency in graph:
                    graph[dependency].add(phase_id)
        
        return graph
    
    def get_ready_phases(self) -> List[str]:
        """
        Get phases that are ready to execute.
        
        Returns:
            List of phase IDs that are ready to execute
        """
        ready_phases = []
        
        for phase_id, phase in self.phases.items():
            # Skip phases that are not pending
            if phase["status"] != PhaseStatus.PENDING:
                continue
            
            # Check if all dependencies are completed
            dependencies_met = True
            for dependency in phase["dependencies"]:
                if dependency not in self.phases:
                    logger.warning(f"Phase {phase_id} depends on unknown phase {dependency}")
                    dependencies_met = False
                    break
                    
                dep_phase = self.phases[dependency]
                if dep_phase["status"] != PhaseStatus.COMPLETED:
                    dependencies_met = False
                    break
            
            if dependencies_met:
                ready_phases.append(phase_id)
        
        return ready_phases
    
    def update_phase_status(self, 
                          phase_id: str, 
                          status: PhaseStatus,
                          result: Optional[Dict[str, Any]] = None,
                          error: Optional[str] = None) -> bool:
        """
        Update the status of a phase.
        
        Args:
            phase_id: Phase ID
            status: New status
            result: Optional result data for the phase
            error: Optional error message
            
        Returns:
            Success status
        """
        if phase_id not in self.phases:
            logger.warning(f"Cannot update status of unknown phase {phase_id}")
            return False
        
        phase = self.phases[phase_id]
        old_status = phase["status"]
        phase["status"] = status
        
        # Update timing information
        if status == PhaseStatus.RUNNING and not phase["started_at"]:
            phase["started_at"] = time.time()
        elif status in [PhaseStatus.COMPLETED, PhaseStatus.FAILED, PhaseStatus.SKIPPED] and not phase["completed_at"]:
            phase["completed_at"] = time.time()
        
        # Update result and error
        if result is not None:
            phase["result"] = result
        
        if error is not None:
            phase["error"] = error
        
        # Log status change
        logger.info(f"Phase {phase_id} status changed: {old_status} -> {status}")
        
        # Call callbacks
        self._notify_callbacks(phase_id, old_status, status)
        
        return True
    
    def _notify_callbacks(self, phase_id: str, old_status: PhaseStatus, new_status: PhaseStatus):
        """Notify callbacks of phase status changes."""
        if phase_id not in self.callbacks:
            return
        
        for callback in self.callbacks[phase_id]:
            try:
                callback(phase_id, old_status, new_status, self.phases[phase_id])
            except Exception as e:
                logger.error(f"Error in phase callback for {phase_id}: {e}")
    
    def all_phases_completed(self) -> bool:
        """
        Check if all phases are completed.
        
        Returns:
            True if all phases are completed
        """
        return all(
            phase["status"] in [PhaseStatus.COMPLETED, PhaseStatus.SKIPPED, PhaseStatus.FAILED]
            for phase in self.phases.values()
        )
    
    def get_failed_phases(self) -> List[str]:
        """
        Get a list of failed phases.
        
        Returns:
            List of failed phase IDs
        """
        return [
            phase_id for phase_id, phase in self.phases.items()
            if phase["status"] == PhaseStatus.FAILED
        ]
    
    def get_critical_failures(self) -> List[str]:
        """
        Get a list of critical phases that failed.
        
        Returns:
            List of failed critical phase IDs
        """
        return [
            phase_id for phase_id, phase in self.phases.items()
            if phase["status"] == PhaseStatus.FAILED and phase["critical"]
        ]
    
    def is_execution_failed(self) -> bool:
        """
        Check if the execution has failed due to critical phase failures.
        
        Returns:
            True if execution has failed
        """
        return len(self.get_critical_failures()) > 0
    
    def reset(self):
        """Reset all phase statuses to pending."""
        for phase in self.phases.values():
            phase["status"] = PhaseStatus.PENDING
            phase["started_at"] = None
            phase["completed_at"] = None
            phase["error"] = None
            phase["result"] = None
        
        logger.info("Reset all phases to pending status")
