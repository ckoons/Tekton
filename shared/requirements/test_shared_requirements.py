#!/usr/bin/env python3
"""
Test that shared requirements can be resolved correctly.
This simulates what would happen when a component uses shared requirements.
"""

import subprocess
import tempfile
from pathlib import Path


def test_requirement_resolution(req_content: str, name: str):
    """Test if requirements can be resolved without conflicts."""
    print(f"\n🧪 Testing {name}...")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(req_content)
        req_file = f.name
    
    try:
        # Use uv pip compile to check resolution
        result = subprocess.run(
            ['uv', 'pip', 'compile', req_file],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Count resolved packages
            lines = result.stdout.strip().split('\n')
            packages = [l for l in lines if l and not l.startswith('#') and '==' in l]
            print(f"  ✅ Resolved successfully: {len(packages)} packages")
            return True
        else:
            print(f"  ❌ Resolution failed:")
            print(f"     {result.stderr}")
            return False
    finally:
        Path(req_file).unlink()


def main():
    print("Testing Shared Requirements Resolution")
    print("=" * 50)
    
    shared_req = Path(__file__).parent
    
    # Test individual shared requirements
    test_files = [
        'base.txt',
        'web.txt',
        'ai.txt',
        'vector.txt',
        'database.txt',
        'data.txt',
        'utilities.txt'
    ]
    
    results = {}
    for req_file in test_files:
        if (shared_req / req_file).exists():
            with open(shared_req / req_file) as f:
                content = f.read()
            results[req_file] = test_requirement_resolution(content, req_file)
    
    # Test combined requirements (simulating component usage)
    print("\n🧪 Testing combined requirements (simulating components)...")
    
    # Simulate Apollo (web + ai)
    apollo_req = f"-r {shared_req}/web.txt\n-r {shared_req}/ai.txt\ntekton-core>=0.1.0"
    results['Apollo simulation'] = test_requirement_resolution(apollo_req, "Apollo (web + ai)")
    
    # Simulate Engram (web + vector)
    engram_req = f"-r {shared_req}/web.txt\n-r {shared_req}/vector.txt\ntekton-core>=0.1.0"
    results['Engram simulation'] = test_requirement_resolution(engram_req, "Engram (web + vector)")
    
    # Simulate Ergon (web + database + data)
    ergon_req = f"-r {shared_req}/web.txt\n-r {shared_req}/database.txt\n-r {shared_req}/data.txt"
    results['Ergon simulation'] = test_requirement_resolution(ergon_req, "Ergon (web + db + data)")
    
    # Summary
    print("\n📊 Summary:")
    print("=" * 50)
    success = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"Successful resolutions: {success}/{total}")
    
    if success < total:
        print("\n❌ Failed resolutions:")
        for name, result in results.items():
            if not result:
                print(f"  - {name}")
        return 1
    else:
        print("\n✅ All requirements resolve successfully!")
        return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())