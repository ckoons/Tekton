#!/usr/bin/env python3
"""
System information utilities for resource monitoring.
"""

import platform
import psutil
from datetime import datetime
from typing import Dict, Any, List

from .gpu_utils import get_gpu_info, check_gpu_availability


def get_system_info() -> Dict[str, Any]:
    """
    Get general system information including hardware details.
    
    Returns:
        Dictionary of system information
    """
    info = {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "hostname": platform.node(),
        "architecture": platform.machine(),
        "cpu_count": psutil.cpu_count(logical=True),
        "physical_cpu_count": psutil.cpu_count(logical=False),
        "memory_total_gb": psutil.virtual_memory().total / (1024 ** 3),
        "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat()
    }
    
    try:
        import cpuinfo
        cpu_info = cpuinfo.get_cpu_info()
        info["cpu_model"] = cpu_info.get("brand_raw", "Unknown")
    except ImportError:
        info["cpu_model"] = "Unknown (py-cpuinfo not installed)"
        
    if check_gpu_availability():
        info["gpus"] = get_gpu_info()
            
    return info
