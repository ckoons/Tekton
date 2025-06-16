#!/usr/bin/env python
"""
LanceDB Installation Script for Engram

This script installs and sets up LanceDB for use with Engram.
"""

import os
import sys
import subprocess
import logging
import platform
from pathlib import Path
from typing import Optional, List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("lancedb_install")

def check_python_version() -> bool:
    """Check if the Python version is compatible with LanceDB."""
    if sys.version_info >= (3, 8):
        logger.info(f"Python version {sys.version_info.major}.{sys.version_info.minor} is compatible")
        return True
    else:
        logger.error(f"Python version {sys.version_info.major}.{sys.version_info.minor} is not compatible. LanceDB requires Python 3.8+")
        return False

def detect_platform() -> Dict[str, Any]:
    """Detect the platform and its capabilities."""
    platform_info = {
        "system": platform.system().lower(),
        "machine": platform.machine().lower(),
        "apple_silicon": False,
        "cuda_available": False
    }
    
    # Check for Apple Silicon
    if platform_info["system"] == "darwin" and platform_info["machine"] in ["arm64", "aarch64"]:
        platform_info["apple_silicon"] = True
        logger.info("Detected Apple Silicon platform")
    
    # Check for CUDA
    try:
        result = subprocess.run(["nvcc", "--version"], 
                              capture_output=True, text=True, check=False)
        if result.returncode == 0:
            platform_info["cuda_available"] = True
            logger.info("CUDA is available")
    except:
        # Try nvidia-smi as alternative
        try:
            result = subprocess.run(["nvidia-smi"], 
                                  capture_output=True, text=True, check=False)
            if result.returncode == 0:
                platform_info["cuda_available"] = True
                logger.info("CUDA is available (detected via nvidia-smi)")
        except:
            logger.info("CUDA is not available")
    
    return platform_info

def check_dependencies() -> bool:
    """Check if required dependencies are available."""
    dependencies = {
        "pip": False,
        "numpy": False,
        "pyarrow": False,
        "lancedb": False
    }
    
    # Check pip
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      capture_output=True, check=False)
        dependencies["pip"] = True
    except:
        logger.error("pip is not available")
        return False
    
    # Check NumPy
    try:
        import numpy
        dependencies["numpy"] = True
        logger.info(f"NumPy version {numpy.__version__} is available")
    except ImportError:
        logger.warning("NumPy is not installed")
    
    # Check PyArrow
    try:
        import pyarrow
        dependencies["pyarrow"] = True
        logger.info(f"PyArrow version {pyarrow.__version__} is available")
    except ImportError:
        logger.warning("PyArrow is not installed")
    
    # Check LanceDB
    try:
        import lancedb
        dependencies["lancedb"] = True
        logger.info(f"LanceDB version {lancedb.__version__} is available")
    except ImportError:
        logger.warning("LanceDB is not installed")
    
    return dependencies["pip"]

def install_lancedb() -> bool:
    """Install LanceDB and its dependencies."""
    logger.info("Installing LanceDB and dependencies...")
    
    try:
        # Install required packages
        subprocess.run([sys.executable, "-m", "pip", "install", "pyarrow>=12.0.0", "numpy>=1.21.0"], 
                      check=True)
        subprocess.run([sys.executable, "-m", "pip", "install", "lancedb>=0.2.0"], 
                      check=True)
        
        # Verify installation
        try:
            import lancedb
            logger.info(f"Successfully installed LanceDB version {lancedb.__version__}")
            return True
        except ImportError:
            logger.error("Failed to import LanceDB after installation")
            return False
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install LanceDB: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during installation: {e}")
        return False

def setup_memory_directory(memory_dir: str) -> bool:
    """Set up the memory directory for LanceDB."""
    try:
        # Create directory if it doesn't exist
        os.makedirs(memory_dir, exist_ok=True)
        logger.info(f"Memory directory created: {memory_dir}")
        
        # Create a test database to verify permissions
        import lancedb
        db = lancedb.connect(memory_dir)
        if not db.table_names():
            # Create a test table
            import pyarrow as pa
            schema = pa.schema([
                pa.field("vector", pa.list_(pa.float32(), 5)),
                pa.field("text", pa.string())
            ])
            table = pa.Table.from_pydict(
                {
                    "vector": [[0.1, 0.2, 0.3, 0.4, 0.5]],
                    "text": ["Test entry"]
                },
                schema=schema
            )
            db.create_table("test", table)
            db.drop_table("test")
        
        logger.info("LanceDB database test successful")
        return True
    except Exception as e:
        logger.error(f"Failed to set up memory directory: {e}")
        return False

def main():
    """Main installation function."""
    print("\n--- LanceDB Setup for Engram ---\n")
    
    # Check Python version
    if not check_python_version():
        print("\n❌ Python version incompatible with LanceDB. Please use Python 3.8+")
        sys.exit(1)
    
    # Detect platform
    platform_info = detect_platform()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Failed to check dependencies. Please ensure pip is available.")
        sys.exit(1)
    
    # Install LanceDB
    print("\nInstalling LanceDB...")
    if install_lancedb():
        print("\n✅ LanceDB installation successful")
    else:
        print("\n❌ LanceDB installation failed")
        sys.exit(1)
    
    # Set up memory directory
    memory_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "memories", "lancedb")
    print(f"\nSetting up memory directory: {memory_dir}")
    if setup_memory_directory(memory_dir):
        print("\n✅ Memory directory setup successful")
    else:
        print("\n❌ Memory directory setup failed")
        sys.exit(1)
    
    print("\nLanceDB setup complete!")
    print("\nYou can now use LanceDB with Engram by:")
    print("1. Importing the adapter: from vector.lancedb.adapter import LanceDBAdapter")
    print("2. Creating an instance: adapter = LanceDBAdapter(client_id='your_client_id')")
    print("3. Using the adapter with Engram's memory system")

if __name__ == "__main__":
    main()