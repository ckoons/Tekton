"""
Example AI model spawning functionality for Rhetor.
Shows how to spawn and manage child AI processes.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

from .process_manager import get_process_manager, ManagedProcess

logger = logging.getLogger(__name__)


class AIModelSpawner:
    """
    Handles spawning of various AI model processes.
    Each model runs as a separate process in Rhetor's process group.
    """
    
    def __init__(self):
        self.process_manager = get_process_manager()
        self.model_configs = {
            "llama": {
                "command": ["ollama", "run", "llama2"],
                "env": {"OLLAMA_HOST": "0.0.0.0:11435"}
            },
            "codellama": {
                "command": ["ollama", "run", "codellama"],
                "env": {"OLLAMA_HOST": "0.0.0.0:11436"}
            },
            "whisper": {
                "command": ["python", "-m", "whisper_server", "--port", "8100"],
                "env": {}
            },
            "stable-diffusion": {
                "command": ["python", "-m", "sd_server", "--port", "8101"],
                "env": {"CUDA_VISIBLE_DEVICES": "0"}
            }
        }
    
    def spawn_model(self, model_type: str, custom_config: Optional[Dict] = None) -> ManagedProcess:
        """
        Spawn a specific AI model as a child process.
        
        Args:
            model_type: Type of model to spawn (llama, codellama, etc.)
            custom_config: Optional custom configuration
            
        Returns:
            ManagedProcess instance
        """
        if model_type not in self.model_configs:
            raise ValueError(f"Unknown model type: {model_type}")
        
        config = self.model_configs[model_type].copy()
        if custom_config:
            config.update(custom_config)
        
        # Add Rhetor-specific environment
        env = config.get("env", {})
        env["RHETOR_PARENT"] = str(os.getpid())
        env["RHETOR_MODEL_TYPE"] = model_type
        
        return self.process_manager.spawn_model(
            name=f"{model_type}_model",
            command=config["command"],
            env=env,
            metadata={"model_type": model_type}
        )
    
    def spawn_model_pool(self, model_type: str, count: int = 3) -> List[ManagedProcess]:
        """
        Spawn a pool of identical models for load balancing.
        
        Args:
            model_type: Type of model to spawn
            count: Number of instances
            
        Returns:
            List of ManagedProcess instances
        """
        processes = []
        base_port = 8200
        
        for i in range(count):
            # Customize each instance
            custom_config = {
                "command": self.model_configs[model_type]["command"].copy(),
                "env": self.model_configs[model_type]["env"].copy()
            }
            
            # Adjust port for each instance
            if "--port" in custom_config["command"]:
                port_idx = custom_config["command"].index("--port")
                custom_config["command"][port_idx + 1] = str(base_port + i)
            
            # Add instance identifier
            custom_config["env"]["INSTANCE_ID"] = str(i)
            
            process = self.process_manager.spawn_model(
                name=f"{model_type}_pool_{i}",
                command=custom_config["command"],
                env=custom_config["env"],
                metadata={
                    "model_type": model_type,
                    "pool_instance": i,
                    "port": base_port + i
                }
            )
            processes.append(process)
            
            logger.info(f"Spawned {model_type} instance {i} on port {base_port + i}")
        
        return processes
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get status of all spawned models"""
        stats = self.process_manager.get_process_stats()
        
        # Group by model type
        by_type = {}
        for proc_info in stats['processes']:
            # Extract model type from name
            name_parts = proc_info['name'].split('_')
            if name_parts:
                model_type = name_parts[0]
                if model_type not in by_type:
                    by_type[model_type] = []
                by_type[model_type].append(proc_info)
        
        return {
            "total_models": stats['active_count'],
            "by_type": by_type,
            "system_stats": {
                "total_cpu_percent": sum(p['cpu_percent'] for p in stats['processes']),
                "total_memory_mb": sum(p['memory_mb'] for p in stats['processes'])
            }
        }


# Example usage in Rhetor API
def example_endpoint():
    """Example of how Rhetor would spawn models in response to requests"""
    spawner = AIModelSpawner()
    
    # Spawn a single model
    llama_process = spawner.spawn_model("llama")
    logger.info(f"Spawned Llama with PID: {llama_process.process.pid}")
    
    # Spawn a pool for load balancing
    codellama_pool = spawner.spawn_model_pool("codellama", count=3)
    logger.info(f"Spawned {len(codellama_pool)} CodeLlama instances")
    
    # Check status
    status = spawner.get_model_status()
    logger.info(f"Model status: {status}")
    
    return status