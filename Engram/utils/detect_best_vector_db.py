#!/usr/bin/env python
"""
Vector Database Detection Script for Engram

This script detects the available hardware and installed vector database libraries,
then recommends the optimal vector database backend for Engram.
"""

import os
import sys
import platform
import subprocess
import logging
from typing import Dict, Any, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("vector_db_detect")

def check_dependencies() -> Dict[str, bool]:
    """Check if vector database dependencies are available."""
    dependencies = {
        "faiss": False,
        "faiss_gpu": False,
        "lancedb": False,
        "pyarrow": False,
        "torch": False
    }
    
    # Check FAISS
    try:
        import faiss
        dependencies["faiss"] = True
        try:
            # Check for GPU support
            if faiss.get_num_gpus() > 0:
                dependencies["faiss_gpu"] = True
        except:
            pass
    except ImportError:
        pass
    
    # Check LanceDB
    try:
        import lancedb
        dependencies["lancedb"] = True
    except ImportError:
        pass
    
    # Check PyArrow
    try:
        import pyarrow
        dependencies["pyarrow"] = True
    except ImportError:
        pass
    
    # Check PyTorch
    try:
        import torch
        dependencies["torch"] = True
    except ImportError:
        pass
    
    return dependencies

def detect_hardware() -> Dict[str, Any]:
    """Detect hardware capabilities."""
    hardware = {
        "system": platform.system().lower(),
        "machine": platform.machine().lower(),
        "apple_silicon": False,
        "cuda_available": False,
        "metal_available": False,
        "num_cpus": os.cpu_count() or 1
    }
    
    # Check for Apple Silicon
    if hardware["system"] == "darwin" and hardware["machine"] in ["arm64", "aarch64"]:
        hardware["apple_silicon"] = True
        # Check for Metal support
        try:
            import torch
            if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                hardware["metal_available"] = True
        except:
            # Try a different approach if torch isn't available
            try:
                result = subprocess.run(["sysctl", "-n", "hw.optional.arm64"], 
                                     capture_output=True, text=True, check=False)
                if result.returncode == 0 and result.stdout.strip() == "1":
                    # Modern MacOS on Apple Silicon likely has Metal
                    hardware["metal_available"] = True
            except:
                pass
    
    # Check for CUDA
    try:
        import torch
        hardware["cuda_available"] = torch.cuda.is_available()
        if hardware["cuda_available"]:
            hardware["cuda_device"] = torch.cuda.get_device_name(0)
            hardware["cuda_version"] = torch.version.cuda
    except:
        # Try alternative CUDA detection
        try:
            result = subprocess.run(["nvidia-smi"], 
                                   capture_output=True, text=True, check=False)
            hardware["cuda_available"] = result.returncode == 0
        except:
            pass
    
    return hardware

def determine_best_db(dependencies: Dict[str, bool], hardware: Dict[str, Any]) -> Tuple[str, str]:
    """
    Determine the best vector database to use based on hardware and installed dependencies.
    
    Returns:
        Tuple of (database_name, reason)
    """
    # First check if any vector databases are available
    if not dependencies["faiss"] and not dependencies["lancedb"]:
        return "none", "No vector database libraries installed"
    
    # Decision tree for best database
    
    # Case 1: Apple Silicon with Metal
    if hardware["apple_silicon"] and hardware["metal_available"] and dependencies["lancedb"]:
        return "lancedb", "Optimal for Apple Silicon with Metal support"
    
    # Case 2: CUDA System with FAISS-GPU
    if hardware["cuda_available"] and dependencies["faiss_gpu"]:
        return "faiss", "Optimal for CUDA GPU acceleration"
    
    # Case 3: Apple Silicon without LanceDB
    if hardware["apple_silicon"] and dependencies["faiss"]:
        return "faiss", "Available on Apple Silicon (CPU only)"
    
    # Case 4: CUDA System with LanceDB but without FAISS-GPU
    if hardware["cuda_available"] and dependencies["lancedb"] and not dependencies["faiss_gpu"]:
        return "lancedb", "Better option with CUDA but without FAISS-GPU"
    
    # Case 5: LanceDB available
    if dependencies["lancedb"]:
        return "lancedb", "Available and generally good performance"
    
    # Case 6: FAISS available
    if dependencies["faiss"]:
        return "faiss", "Available for vector operations"
    
    # Fallback (should never reach here given earlier check)
    return "none", "No suitable vector database found"

def get_launcher_script(db_name: str, with_ollama: bool = False) -> str:
    """Get the appropriate launcher script based on the vector database and ollama preference."""
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    if db_name == "lancedb":
        if with_ollama:
            return os.path.join(root_dir, "engram_with_ollama_lancedb")
        else:
            return os.path.join(root_dir, "engram_with_lancedb")
    elif db_name == "faiss":
        if with_ollama:
            return os.path.join(root_dir, "engram_with_ollama_faiss")
        else:
            return os.path.join(root_dir, "engram_with_ollama")  # Default Ollama script uses FAISS
    else:
        # Fallback to standard launchers
        if with_ollama:
            return os.path.join(root_dir, "engram_with_ollama")
        else:
            return os.path.join(root_dir, "engram_with_claude")

def print_vector_db_status(dependencies: Dict[str, bool], hardware: Dict[str, Any], 
                          best_db: str, reason: str) -> None:
    """Print a summary of the vector database status."""
    print("\n==== Engram Vector Database Detection ====\n")
    
    # Hardware information
    print("🖥️  Hardware:")
    print(f"  • System: {hardware['system'].title()} on {hardware['machine']}")
    if hardware["apple_silicon"]:
        metal = "✅ Available" if hardware["metal_available"] else "❌ Not available"
        print(f"  • Apple Silicon: Yes (Metal: {metal})")
    if hardware["cuda_available"]:
        print(f"  • CUDA: Available")
        if "cuda_device" in hardware:
            print(f"  • GPU: {hardware['cuda_device']}")
    print(f"  • CPUs: {hardware['num_cpus']}")
    
    # Dependencies
    print("\n📦 Installed Libraries:")
    print(f"  • FAISS: {'✅ Yes' if dependencies['faiss'] else '❌ No'}")
    if dependencies["faiss"]:
        print(f"  • FAISS GPU: {'✅ Yes' if dependencies['faiss_gpu'] else '❌ No'}")
    print(f"  • LanceDB: {'✅ Yes' if dependencies['lancedb'] else '❌ No'}")
    print(f"  • PyArrow: {'✅ Yes' if dependencies['pyarrow'] else '❌ No'}")
    print(f"  • PyTorch: {'✅ Yes' if dependencies['torch'] else '❌ No'}")
    
    # Recommendation
    print("\n🏆 Recommendation:")
    if best_db == "none":
        print(f"  • No vector database available")
        print(f"  • Reason: {reason}")
        print(f"  • Engram will use file-based fallback mode")
    else:
        print(f"  • Best database: {best_db.upper()}")
        print(f"  • Reason: {reason}")
        
        # Launcher scripts
        print("\n🚀 Launcher Scripts:")
        print(f"  • With Claude: {os.path.basename(get_launcher_script(best_db, False))}")
        print(f"  • With Ollama: {os.path.basename(get_launcher_script(best_db, True))}")
    
    print("\n============================================\n")

def get_vector_db_info() -> Tuple[str, str, Dict[str, bool], Dict[str, Any]]:
    """Get all information about vector databases and return the best one."""
    dependencies = check_dependencies()
    hardware = detect_hardware()
    best_db, reason = determine_best_db(dependencies, hardware)
    return best_db, reason, dependencies, hardware

if __name__ == "__main__":
    # Process command-line arguments
    script_only = "--quiet" in sys.argv or "-q" in sys.argv
    ollama_mode = "--ollama" in sys.argv or "-o" in sys.argv
    
    # Detect the best vector database
    best_db, reason, dependencies, hardware = get_vector_db_info()
    
    # Show status if not in quiet mode
    if not script_only:
        print_vector_db_status(dependencies, hardware, best_db, reason)
    
    # Return just the script path if requested
    if script_only:
        print(get_launcher_script(best_db, ollama_mode))
    
    # Return success code for script to use
    sys.exit(0)