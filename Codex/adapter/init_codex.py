import os
import sys
import logging
import asyncio
import subprocess
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("codex_init")

async def initialize_codex():
    """
    Initialize Codex for integration with Tekton.
    
    This function:
    1. Registers Codex with Hermes
    2. Creates necessary UI components
    3. Ensures .gitignore is properly configured
    
    Returns:
        bool: Whether initialization was successful
    """
    try:
        # Get current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        codex_dir = os.path.dirname(current_dir)
        
        # Register with Hermes
        logger.info("Registering Codex with Hermes...")
        register_script = os.path.join(current_dir, "register_with_hermes.py")
        
        result = subprocess.run([sys.executable, register_script], check=True)
        if result.returncode != 0:
            logger.error("Failed to register Codex with Hermes")
            return False
        
        logger.info("Successfully registered Codex with Hermes")
        
        # Update .gitignore
        gitignore_path = os.path.join(codex_dir, ".gitignore")
        if os.path.exists(gitignore_path):
            with open(gitignore_path, "r") as f:
                content = f.read()
            
            # Check if Aider entries are already present
            if ".aider*" not in content:
                logger.info("Updating .gitignore with Aider entries")
                with open(gitignore_path, "a") as f:
                    f.write("\n\n# Aider-specific files\n.aider*\naider.conf.yml\n")
        
        # Create UI directories if needed
        ui_dir = os.path.join(codex_dir, "ui")
        os.makedirs(ui_dir, exist_ok=True)
        
        # Copy component template to Hephaestus static directory
        hephaestus_dir = os.path.join(os.path.dirname(codex_dir), "Hephaestus")
        component_dir = os.path.join(hephaestus_dir, "hephaestus", "ui", "static", "component")
        
        if os.path.exists(component_dir):
            template_source = os.path.join(ui_dir, "component_template.html")
            template_dest = os.path.join(component_dir, "codex.html")
            
            # Copy only if source exists and is newer than destination
            if os.path.exists(template_source) and (
                not os.path.exists(template_dest) or 
                os.path.getmtime(template_source) > os.path.getmtime(template_dest)
            ):
                logger.info(f"Copying component template to {template_dest}")
                with open(template_source, "r") as src:
                    with open(template_dest, "w") as dst:
                        dst.write(src.read())
        
        logger.info("Codex initialization completed successfully")
        return True
    
    except Exception as e:
        logger.error(f"Error initializing Codex: {e}")
        return False

async def main():
    """
    Main entry point for initialization.
    """
    success = await initialize_codex()
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)