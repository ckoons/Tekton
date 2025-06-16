#!/usr/bin/env python3
"""
Find and test new versions of dependencies across Tekton components.

This utility helps maintain up-to-date dependencies by:
1. Checking for newer versions of installed packages
2. Creating test requirements files with updated versions
3. Allowing safe testing before committing updates
"""

import subprocess
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse
from datetime import datetime


def run_command(cmd: List[str]) -> Tuple[bool, str]:
    """Run a command and return success status and output."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)


def get_installed_packages() -> Dict[str, str]:
    """Get currently installed packages and versions."""
    success, output = run_command(["uv", "pip", "list", "--format", "json"])
    if not success:
        print(f"Error getting installed packages: {output}")
        return {}
    
    try:
        packages = json.loads(output)
        return {pkg["name"].lower(): pkg["version"] for pkg in packages}
    except json.JSONDecodeError:
        print("Error parsing package list")
        return {}


def check_newer_versions(package: str, current_version: str) -> Optional[str]:
    """Check if a newer version is available for a package."""
    success, output = run_command(["uv", "pip", "index", package])
    if not success:
        return None
    
    # Parse available versions from output
    # This is a simplified version - uv's actual output format may vary
    version_pattern = r"Available versions: (.+)"
    match = re.search(version_pattern, output)
    if match:
        versions = match.group(1).split(", ")
        # Simple comparison - in practice, use packaging.version
        latest = versions[-1] if versions else None
        if latest and latest > current_version:
            return latest
    
    return None


def parse_requirements_file(file_path: Path) -> List[Tuple[str, str, str]]:
    """Parse a requirements file and return package info."""
    requirements = []
    
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue
                
            # Skip -r includes
            if line.startswith("-r "):
                continue
            
            # Parse package lines
            # Handles: package>=1.0.0, package==1.0.0, package<2.0.0,>=1.0.0
            match = re.match(r"^([a-zA-Z0-9_-]+)([><=!]+.+?)(?:\s*#.*)?$", line)
            if match:
                package = match.group(1).lower()
                constraint = match.group(2)
                requirements.append((package, constraint, line))
    
    return requirements


def create_test_requirements(req_file: Path, updates: Dict[str, str]) -> Path:
    """Create a test requirements file with updated versions."""
    test_file = req_file.parent / f"{req_file.stem}_test_{datetime.now():%Y%m%d_%H%M%S}.txt"
    
    with open(req_file, "r") as f_in, open(test_file, "w") as f_out:
        for line in f_in:
            line_stripped = line.strip()
            
            # Copy comments and empty lines as-is
            if not line_stripped or line_stripped.startswith("#") or line_stripped.startswith("-r"):
                f_out.write(line)
                continue
            
            # Check if this line contains a package to update
            written = False
            for package, new_version in updates.items():
                if line_stripped.startswith(package):
                    # Replace with new version
                    f_out.write(f"{package}>={new_version}\n")
                    written = True
                    break
            
            if not written:
                f_out.write(line)
    
    return test_file


def find_updates_for_file(req_file: Path) -> Dict[str, Tuple[str, str]]:
    """Find available updates for packages in a requirements file."""
    updates = {}
    requirements = parse_requirements_file(req_file)
    installed = get_installed_packages()
    
    print(f"\nChecking {req_file.name}...")
    
    for package, constraint, full_line in requirements:
        current_version = installed.get(package)
        if not current_version:
            continue
            
        # Check for newer version
        newer = check_newer_versions(package, current_version)
        if newer:
            updates[package] = (current_version, newer)
            print(f"  {package}: {current_version} → {newer}")
    
    return updates


def main():
    parser = argparse.ArgumentParser(description="Find and test new dependency versions")
    parser.add_argument(
        "files", 
        nargs="*", 
        help="Requirements files to check (defaults to shared/requirements/*.txt)"
    )
    parser.add_argument(
        "--test", 
        action="store_true", 
        help="Create test requirements files with updates"
    )
    parser.add_argument(
        "--component", 
        help="Check a specific component's requirements"
    )
    
    args = parser.parse_args()
    
    # Determine which files to check
    req_files = []
    
    if args.files:
        req_files = [Path(f) for f in args.files]
    elif args.component:
        component_req = Path(args.component) / "requirements.txt"
        if component_req.exists():
            req_files = [component_req]
        else:
            print(f"Requirements file not found: {component_req}")
            return 1
    else:
        # Default to shared requirements
        shared_dir = Path(__file__).parent.parent / "requirements"
        req_files = list(shared_dir.glob("*.txt"))
        if not req_files:
            print(f"No requirements files found in {shared_dir}")
            return 1
    
    # Check each file for updates
    all_updates = {}
    for req_file in req_files:
        if not req_file.exists():
            print(f"File not found: {req_file}")
            continue
            
        updates = find_updates_for_file(req_file)
        if updates:
            all_updates[req_file] = updates
    
    # Summary
    if not all_updates:
        print("\nAll packages are up to date!")
        return 0
    
    print(f"\nFound updates for {sum(len(u) for u in all_updates.values())} packages")
    
    # Create test files if requested
    if args.test:
        print("\nCreating test requirements files...")
        for req_file, updates in all_updates.items():
            test_file = create_test_requirements(req_file, {
                pkg: new_ver for pkg, (old_ver, new_ver) in updates.items()
            })
            print(f"  Created: {test_file}")
        
        print("\nTo test updates:")
        print("  1. Create a virtual environment: uv venv test-env")
        print("  2. Install test requirements: uv pip install -r <test_file>")
        print("  3. Run tests: pytest")
        print("  4. If tests pass, update the original requirements file")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())