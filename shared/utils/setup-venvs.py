#!/usr/bin/env python3
"""
Set up shared virtual environments for Tekton components.
This creates 5 shared venvs instead of 15+ individual ones.
"""

import subprocess
import sys
import os
from pathlib import Path
import argparse
from typing import List, Dict, Tuple
import json


class VenvManager:
    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or Path.home() / "venvs"
        self.tekton_root = Path(__file__).parent.parent.parent
        self.shared_req = self.tekton_root / "shared" / "requirements"
        
        # Define virtual environments and their requirements
        self.venv_configs = {
            "tekton-core": {
                "description": "Core web framework components",
                "size": "~500MB",
                "components": ["Apollo", "Telos", "Terma", "Harmonia", "Prometheus"],
                "requirements": [
                    f"-r {self.shared_req}/web.txt",
                    "tekton-core>=0.1.0",
                    "tekton-llm-client>=1.0.0",
                    "fastmcp>=1.0.0",
                ]
            },
            "tekton-ai": {
                "description": "AI/LLM integration components",
                "size": "~1GB",
                "components": ["Budget", "Rhetor", "Synthesis"],
                "requirements": [
                    f"-r {self.shared_req}/web.txt",
                    f"-r {self.shared_req}/ai.txt",
                    "tekton-core>=0.1.0",
                    "tekton-llm-client>=1.0.0",
                ]
            },
            "tekton-ml": {
                "description": "Machine learning and vector components",
                "size": "~6GB",
                "components": ["Engram", "Hermes", "Sophia", "Athena"],
                "requirements": [
                    f"-r {self.shared_req}/web.txt",
                    f"-r {self.shared_req}/vector.txt",
                    "tekton-core>=0.1.0",
                ]
            },
            "tekton-data": {
                "description": "Database and data processing components",
                "size": "~2GB", 
                "components": ["Ergon", "Metis", "Harmonia"],
                "requirements": [
                    f"-r {self.shared_req}/web.txt",
                    f"-r {self.shared_req}/database.txt",
                    f"-r {self.shared_req}/data.txt",
                    "tekton-core>=0.1.0",
                ]
            },
            "tekton-dev": {
                "description": "Development and testing environment",
                "size": "~3GB",
                "components": ["Development", "Testing", "Linting"],
                "requirements": [
                    f"-r {self.shared_req}/web.txt",
                    f"-r {self.shared_req}/dev.txt",
                    f"-r {self.shared_req}/ai.txt",
                ]
            }
        }
    
    def run_command(self, cmd: List[str], cwd: Path = None) -> Tuple[bool, str]:
        """Run a command and return success status and output."""
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True,
                cwd=cwd
            )
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)
    
    def create_venv(self, name: str, force: bool = False, skip_install: bool = False) -> bool:
        """Create a single virtual environment."""
        venv_path = self.base_dir / name
        
        # Check if already exists
        if venv_path.exists() and not force:
            print(f"  ⚠️  {name} already exists (use --force to recreate)")
            return True
        
        # Remove if forcing
        if venv_path.exists() and force:
            print(f"  🗑️  Removing existing {name}")
            import shutil
            shutil.rmtree(venv_path)
        
        # Create venv
        print(f"  📦 Creating {name}...")
        success, output = self.run_command(["uv", "venv", str(venv_path)])
        if not success:
            print(f"  ❌ Failed to create {name}: {output}")
            return False
        
        if skip_install:
            print(f"  ⏭️  Skipping package installation")
            print(f"  ✅ {name} created successfully (no packages installed)")
            return True
        
        # Install requirements
        config = self.venv_configs[name]
        req_file = venv_path / "requirements.txt"
        
        # Write requirements to temp file
        with open(req_file, "w") as f:
            for req in config["requirements"]:
                f.write(f"{req}\n")
        
        print(f"  📥 Installing packages for {name}...")
        pip_cmd = [
            str(venv_path / "bin" / "pip"),
            "install",
            "-r",
            str(req_file)
        ]
        
        success, output = self.run_command(pip_cmd)
        if not success:
            print(f"  ❌ Failed to install packages: {output}")
            return False
        
        print(f"  ✅ {name} created successfully")
        return True
    
    def create_activation_script(self) -> None:
        """Create a helper script for easy venv activation."""
        script_path = self.base_dir / "activate-tekton.sh"
        
        script_content = """#!/bin/bash
# Tekton virtual environment activation helper

case "$1" in
    core)
        source ~/venvs/tekton-core/bin/activate
        echo "Activated tekton-core environment"
        ;;
    ai)
        source ~/venvs/tekton-ai/bin/activate
        echo "Activated tekton-ai environment"
        ;;
    ml)
        source ~/venvs/tekton-ml/bin/activate
        echo "Activated tekton-ml environment"
        ;;
    data)
        source ~/venvs/tekton-data/bin/activate
        echo "Activated tekton-data environment"
        ;;
    dev)
        source ~/venvs/tekton-dev/bin/activate
        echo "Activated tekton-dev environment"
        ;;
    *)
        echo "Usage: source activate-tekton.sh [core|ai|ml|data|dev]"
        echo ""
        echo "Environments:"
        echo "  core - Web framework components"
        echo "  ai   - AI/LLM integration components"
        echo "  ml   - Machine learning and vector components"
        echo "  data - Database and data processing"
        echo "  dev  - Development and testing"
        ;;
esac
"""
        
        with open(script_path, "w") as f:
            f.write(script_content)
        
        os.chmod(script_path, 0o755)
        print(f"\n✅ Created activation helper: {script_path}")
        print("   Usage: source ~/venvs/activate-tekton.sh [core|ai|ml|data|dev]")
    
    def show_summary(self) -> None:
        """Show summary of virtual environments."""
        print("\n📊 Virtual Environment Summary:")
        print("=" * 60)
        
        for name, config in self.venv_configs.items():
            print(f"\n{name}:")
            print(f"  Description: {config['description']}")
            print(f"  Size: {config['size']}")
            print(f"  Components: {', '.join(config['components'])}")
            
            venv_path = self.base_dir / name
            if venv_path.exists():
                print(f"  Status: ✅ Exists at {venv_path}")
            else:
                print(f"  Status: ❌ Not created")
    
    def create_component_mapping(self) -> None:
        """Create a JSON mapping of components to venvs."""
        mapping = {}
        
        # Reverse map from venv configs
        for venv_name, config in self.venv_configs.items():
            for component in config["components"]:
                mapping[component.lower()] = venv_name
        
        # Add special cases
        mapping.update({
            "athena": "tekton-ml",
            "codex": "tekton-core",  # Will be updated later
            "terma": "tekton-core",
            "llmadapter": "tekton-ai",  # Deprecated but included
        })
        
        # Save mapping
        mapping_file = self.tekton_root / "shared" / "utils" / "venv-mapping.json"
        with open(mapping_file, "w") as f:
            json.dump(mapping, f, indent=2)
        
        print(f"\n✅ Created component mapping: {mapping_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Set up shared virtual environments for Tekton"
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        help="Base directory for venvs (default: ~/venvs)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force recreate existing environments"
    )
    parser.add_argument(
        "--env",
        choices=["core", "ai", "ml", "data", "dev", "all"],
        default="all",
        help="Which environment(s) to create"
    )
    parser.add_argument(
        "--skip-install",
        action="store_true",
        help="Create venvs but skip package installation"
    )
    
    args = parser.parse_args()
    
    manager = VenvManager(base_dir=args.base_dir)
    
    # Ensure base directory exists
    manager.base_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🚀 Setting up Tekton virtual environments in {manager.base_dir}")
    print("=" * 60)
    
    # Determine which venvs to create
    if args.env == "all":
        venvs_to_create = list(manager.venv_configs.keys())
    else:
        env_map = {
            "core": "tekton-core",
            "ai": "tekton-ai",
            "ml": "tekton-ml",
            "data": "tekton-data",
            "dev": "tekton-dev"
        }
        venvs_to_create = [env_map[args.env]]
    
    # Create venvs
    success_count = 0
    for venv_name in venvs_to_create:
        print(f"\n🔧 Processing {venv_name}...")
        if manager.create_venv(venv_name, force=args.force, skip_install=args.skip_install):
            success_count += 1
    
    # Create helper files
    if success_count > 0:
        manager.create_activation_script()
        manager.create_component_mapping()
    
    # Show summary
    manager.show_summary()
    
    print(f"\n✅ Created {success_count}/{len(venvs_to_create)} environments")
    
    if success_count < len(venvs_to_create):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())