#!/usr/bin/env python3
"""
Resource Monitor Example Script

This script demonstrates the resource monitoring capabilities of Tekton.
It creates a resource monitor and a health dashboard, then registers
components for monitoring.
"""

import os
import sys
import time
import asyncio
import random
import multiprocessing
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))

from tekton.core.resource_monitor import ResourceMonitor, ResourceConfig
from tekton.core.monitoring.dashboard import HealthDashboard, ComponentHealth, HealthStatus, ComponentState


def cpu_intensive_task(duration=60):
    """Task to simulate CPU intensive operations."""
    print(f"Starting CPU intensive task for {duration} seconds")
    end_time = time.time() + duration
    while time.time() < end_time:
        # Compute heavy calculation
        [i**2 for i in range(10000)]
        time.sleep(0.001)  # Small pause to not freeze the system


def memory_intensive_task(size_mb=500, duration=60):
    """Task to simulate memory intensive operations."""
    print(f"Starting memory intensive task ({size_mb}MB) for {duration} seconds")
    # Allocate memory (1MB = 1024*1024 bytes)
    size_bytes = size_mb * 1024 * 1024
    data = bytearray(size_bytes)
    
    # Hold the memory for the duration
    end_time = time.time() + duration
    while time.time() < end_time:
        # Touch the memory occasionally to ensure it's not paged out
        data[random.randint(0, size_bytes-1)] = random.randint(0, 255)
        time.sleep(1)


async def simulate_component_activity(resource_monitor, dashboard):
    """Simulate various component activities to demonstrate resource monitoring."""
    print("Simulating component activities...")
    
    # Create and register components
    components = [
        {"id": "data-processor", "name": "Data Processor", "type": "service"},
        {"id": "model-trainer", "name": "Model Trainer", "type": "worker"},
        {"id": "api-gateway", "name": "API Gateway", "type": "service"}
    ]
    
    # Add components to dashboard
    for comp in components:
        component = ComponentHealth(
            component_id=comp["id"],
            component_name=comp["name"],
            component_type=comp["type"],
            status=HealthStatus.HEALTHY,
            state=ComponentState.READY.value,
            last_heartbeat=time.time(),
            metrics={},
            dependencies=[]
        )
        dashboard.system_health.add_component(component)
    
    # Start some resource-intensive processes
    processes = []
    
    try:
        # Simulate each component with its own process
        
        # Data processor - moderate CPU usage
        data_proc = multiprocessing.Process(
            target=cpu_intensive_task,
            args=(120,)  # 2 minutes duration
        )
        data_proc.start()
        processes.append(data_proc)
        resource_monitor.register_component("data-processor", [data_proc.pid])
        
        # Wait to stagger resource usage
        await asyncio.sleep(5)
        
        # Model trainer - high CPU and memory usage
        model_trainer = multiprocessing.Process(
            target=memory_intensive_task,
            args=(200, 120)  # 200MB for 2 minutes
        )
        model_trainer.start()
        processes.append(model_trainer)
        resource_monitor.register_component("model-trainer", [model_trainer.pid])
        
        # Keep running and updating status
        iteration = 0
        while any(p.is_alive() for p in processes):
            # Update component status in health dashboard
            for comp_id in ["data-processor", "model-trainer", "api-gateway"]:
                if comp_id in dashboard.component_status:
                    # Get current metrics from resource monitor
                    metrics = resource_monitor.get_current_metrics()
                    if comp_id in metrics.component_metrics:
                        comp_metrics = metrics.component_metrics[comp_id]
                        
                        # Decide status based on CPU usage
                        cpu_pct = comp_metrics.get("cpu_percent", 0)
                        if cpu_pct > 80:
                            status = HealthStatus.DEGRADED
                            state = ComponentState.DEGRADED.value
                        else:
                            status = HealthStatus.HEALTHY
                            state = ComponentState.READY.value
                            
                        # Update component in dashboard
                        comp = dashboard.system_health.get_component(comp_id)
                        if comp:
                            comp.update_status(
                                status=status,
                                state=state,
                                last_heartbeat=time.time(),
                                metrics=comp_metrics
                            )
            
            # Occasionally trigger metrics issues for alert testing
            if iteration % 10 == 0:
                # API Gateway occasionally has issues
                api_comp = dashboard.system_health.get_component("api-gateway")
                if api_comp:
                    api_comp.update_status(
                        status=HealthStatus.DEGRADED,
                        state=ComponentState.DEGRADED.value,
                        last_heartbeat=time.time(),
                        metrics={
                            "cpu_percent": 85.0,
                            "memory_percent": 65.0,
                            "error_rate": 0.08,
                            "request_latency": 800
                        }
                    )
            
            iteration += 1
            await asyncio.sleep(3)
    
    finally:
        # Clean up processes
        for p in processes:
            if p.is_alive():
                p.terminate()
                p.join()


async def main():
    """Main function to demonstrate resource monitoring."""
    print("Starting Resource Monitor Example")
    
    # Create resource monitor with custom configuration
    config = ResourceConfig(
        cpu_threshold=ResourceThreshold(60.0, 80.0),  # Lower thresholds for demo
        memory_threshold=ResourceThreshold(50.0, 75.0),
        check_interval_seconds=2.0,
        alert_cooldown_seconds=30.0,  # Shorter cooldown for demo
        retention_hours=1
    )
    
    resource_monitor = ResourceMonitor(config=config)
    
    # Create alert handler
    def alert_handler(resource_name, level, value, threshold):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level} ALERT: {resource_name} at {value:.1f}% (threshold: {threshold:.1f}%)")
    
    resource_monitor.add_alert_handler(alert_handler)
    
    # Create health dashboard
    dashboard = HealthDashboard(update_interval=2.0)
    
    # Start monitoring
    print("Starting resource monitoring")
    resource_monitor.start()
    
    # Start dashboard
    print("Starting dashboard")
    await dashboard.start()
    
    try:
        # Display system info
        system_info = resource_monitor.get_system_info()
        print("\nSystem Information:")
        print(f"  Platform: {system_info['platform']}")
        print(f"  CPU: {system_info.get('cpu_model', 'Unknown')}")
        print(f"  CPU Cores: {system_info['physical_cpu_count']} physical / {system_info['cpu_count']} logical")
        print(f"  Memory: {system_info['memory_total_gb']:.1f} GB")
        
        # Print dashboard URL
        print("\nDashboard available at: http://localhost:8080")
        print("Press Ctrl+C to stop the example")
        
        # Simulate component activity
        await simulate_component_activity(resource_monitor, dashboard)
        
        # Keep running for a while
        print("\nExample completed. Dashboard will remain active for 30 more seconds.")
        await asyncio.sleep(30)
        
    except KeyboardInterrupt:
        print("\nExample interrupted by user")
    finally:
        # Stop monitoring and dashboard
        resource_monitor.stop()
        await dashboard.stop()
        print("Example finished")


if __name__ == "__main__":
    # Add import for ResourceThreshold in main scope
    from tekton.core.resource_monitor import ResourceThreshold
    
    # Run the example
    asyncio.run(main())