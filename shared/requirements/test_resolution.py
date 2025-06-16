#!/usr/bin/env python3
"""
Test requirements resolution for the new shared structure.
Tests both individual files and component combinations.
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def check_resolution(req_files: List[Path], name: str) -> Tuple[bool, str, int]:
    """Check if requirements can be resolved using uv."""
    cmd = ['uv', 'pip', 'compile'] + [str(f) for f in req_files]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # Count packages
            lines = result.stdout.strip().split('\n')
            packages = [l for l in lines if l and not l.startswith('#') and '==' in l]
            return True, f"✅ {len(packages)} packages", len(packages)
        else:
            # Extract key error
            error = result.stderr.strip()
            if "not found in the package registry" in error:
                # Extract package name
                import re
                match = re.search(r'Because (\S+) was not found', error)
                if match:
                    return False, f"❌ Package not found: {match.group(1)}", 0
            elif "your requirements are unsatisfiable" in error:
                return False, f"❌ Version conflict: {error.split(':')[-1].strip()}", 0
            else:
                return False, f"❌ Resolution failed", 0
    except Exception as e:
        return False, f"❌ Error: {str(e)}", 0


def main():
    req_dir = Path(__file__).parent
    
    print("Testing Shared Requirements Resolution")
    print("=" * 60)
    
    # Test individual files
    print("\n📦 Individual Requirements Files:")
    individual_tests = [
        ('base.txt', [req_dir / 'base.txt']),
        ('web.txt', [req_dir / 'web.txt']),
        ('ai.txt', [req_dir / 'ai.txt']),
        ('vector.txt', [req_dir / 'vector.txt']),
        ('database.txt', [req_dir / 'database.txt']),
        ('data.txt', [req_dir / 'data.txt']),
        ('utilities.txt', [req_dir / 'utilities.txt']),
        ('dev.txt', [req_dir / 'dev.txt']),
    ]
    
    results = {}
    for name, files in individual_tests:
        if all(f.exists() for f in files):
            success, msg, count = check_resolution(files, name)
            results[name] = (success, count)
            print(f"  {name:<15} {msg}")
    
    # Test component combinations
    print("\n🔧 Component Simulations:")
    component_tests = [
        ('Apollo (web+ai)', [req_dir / 'web.txt', req_dir / 'ai.txt']),
        ('Engram (web+vector)', [req_dir / 'web.txt', req_dir / 'vector.txt']),
        ('Ergon (web+db+data)', [req_dir / 'web.txt', req_dir / 'database.txt', req_dir / 'data.txt']),
        ('Hermes (web+vector+db)', [req_dir / 'web.txt', req_dir / 'vector.txt', req_dir / 'database.txt']),
        ('Dev Environment', [req_dir / 'web.txt', req_dir / 'dev.txt']),
    ]
    
    for name, files in component_tests:
        if all(f.exists() for f in files):
            success, msg, count = check_resolution(files, name)
            results[name] = (success, count)
            print(f"  {name:<25} {msg}")
    
    # Summary
    print("\n📊 Summary:")
    print("=" * 60)
    
    success_count = sum(1 for s, _ in results.values() if s)
    total_count = len(results)
    total_packages = sum(c for _, c in results.values())
    
    print(f"Successful resolutions: {success_count}/{total_count}")
    print(f"Total unique packages across all: ~{total_packages // len(results)} average")
    
    if success_count < total_count:
        print("\n❌ Failed resolutions:")
        for name, (success, _) in results.items():
            if not success:
                print(f"  - {name}")
        return 1
    else:
        print("\n✅ All requirements resolve successfully!")
        print("\n💡 Next steps:")
        print("  1. Create virtual environments: python shared/utils/setup-venvs.py")
        print("  2. Update component requirements to use shared files")
        print("  3. Test with tekton-launch --launch-all")
        return 0


if __name__ == "__main__":
    sys.exit(main())