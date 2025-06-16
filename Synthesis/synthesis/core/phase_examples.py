#!/usr/bin/env python3
"""
Phase Examples - Example usage of the phase management system.

This module provides examples of how to use the phase management system,
including setting up phases, registering handlers, and executing phases.
"""

import asyncio
import logging

from synthesis.core.phase_manager import PhaseManager
from synthesis.core.phase_executor import PhaseExecutor


async def example():
    """Example usage of phase manager and executor."""
    # Create phase manager
    manager = PhaseManager()
    
    # Register phases
    manager.register_phase("setup", "Environment Setup", [], critical=True)
    manager.register_phase("build", "Build Components", ["setup"], critical=True)
    manager.register_phase("test", "Test Components", ["build"])
    manager.register_phase("package", "Package Solution", ["build"])
    manager.register_phase("deploy", "Deploy Solution", ["package", "test"], critical=True)
    manager.register_phase("validate", "Validate Deployment", ["deploy"])
    
    # Create phase executor
    executor = PhaseExecutor(manager)
    
    # Define phase handlers
    async def handle_setup(phase):
        print(f"Executing setup phase: {phase['name']}")
        await asyncio.sleep(1)
        return {"environment": "prepared"}
    
    async def handle_build(phase):
        print(f"Executing build phase: {phase['name']}")
        await asyncio.sleep(2)
        return {"components": ["component1", "component2"]}
    
    async def handle_test(phase):
        print(f"Executing test phase: {phase['name']}")
        await asyncio.sleep(1.5)
        return {"tests_passed": 42, "tests_failed": 0}
    
    async def handle_package(phase):
        print(f"Executing package phase: {phase['name']}")
        await asyncio.sleep(1)
        return {"package": "solution.zip"}
    
    async def handle_deploy(phase):
        print(f"Executing deploy phase: {phase['name']}")
        await asyncio.sleep(2)
        return {"deployment_id": "prod-123"}
    
    async def handle_validate(phase):
        print(f"Executing validate phase: {phase['name']}")
        await asyncio.sleep(1)
        return {"validation": "passed"}
    
    # Register handlers
    executor.register_handler("setup", handle_setup)
    executor.register_handler("build", handle_build)
    executor.register_handler("test", handle_test)
    executor.register_handler("package", handle_package)
    executor.register_handler("deploy", handle_deploy)
    executor.register_handler("validate", handle_validate)
    
    # Execute phases
    print("Starting phase execution")
    success = await executor.execute_phases(concurrency=2)
    
    print(f"Phase execution {'succeeded' if success else 'failed'}")
    
    # Print results
    for phase_id, phase in manager.get_all_phases().items():
        status = phase["status"]
        duration = (phase["completed_at"] - phase["started_at"]) if phase["completed_at"] and phase["started_at"] else None
        
        print(f"Phase {phase_id}: {status}, Duration: {duration:.2f}s" if duration else f"Phase {phase_id}: {status}")
        
        if phase["result"]:
            print(f"  Result: {phase['result']}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(example())
