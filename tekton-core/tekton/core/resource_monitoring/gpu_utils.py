#!/usr/bin/env python3
"""
GPU monitoring utilities.
"""

import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


def check_gpu_availability() -> bool:
    """
    Check if GPU monitoring is available.
    
    Returns:
        True if GPUs are available and can be monitored
    """
    try:
        import pynvml
        pynvml.nvmlInit()
        device_count = pynvml.nvmlDeviceGetCount()
        pynvml.nvmlShutdown()
        return device_count > 0
    except (ImportError, Exception):
        return False


def get_gpu_metrics() -> Optional[Dict[str, Dict[str, float]]]:
    """
    Collect GPU metrics if available.
    
    Returns:
        Dictionary of GPU metrics by device or None if not available
    """
    try:
        import pynvml
        pynvml.nvmlInit()
        device_count = pynvml.nvmlDeviceGetCount()
        
        gpu_metrics = {}
        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            memory = pynvml.nvmlDeviceGetMemoryInfo(handle)
            
            gpu_metrics[f"gpu{i}"] = {
                "utilization": util.gpu,
                "memory_used_percent": (memory.used / memory.total) * 100
            }
            
        pynvml.nvmlShutdown()
        return gpu_metrics
    except Exception as e:
        logger.warning(f"Failed to collect GPU metrics: {e}")
        return None


def get_gpu_info() -> List[Dict[str, Any]]:
    """
    Get detailed information about available GPUs.
    
    Returns:
        List of dictionaries with GPU information
    """
    try:
        import pynvml
        pynvml.nvmlInit()
        
        device_count = pynvml.nvmlDeviceGetCount()
        gpu_info = []
        
        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            name = pynvml.nvmlDeviceGetName(handle)
            memory = pynvml.nvmlDeviceGetMemoryInfo(handle)
            
            gpu_info.append({
                "name": name,
                "memory_total_gb": memory.total / (1024 ** 3)
            })
            
        pynvml.nvmlShutdown()
        return gpu_info
    except Exception as e:
        logger.warning(f"Failed to get GPU information: {e}")
        return []
