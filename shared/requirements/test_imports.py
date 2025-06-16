#!/usr/bin/env python3
"""
Test imports for all packages in shared requirements.
This ensures all packages are properly specified and can be imported.
"""

import sys
import importlib
import subprocess
from pathlib import Path

def test_package_import(package_name):
    """Try to import a package and return success status."""
    # Handle special cases where import name differs from package name
    import_map = {
        'python-dotenv': 'dotenv',
        'pydantic-settings': 'pydantic_settings',
        'python-multipart': 'multipart',
        'beautifulsoup4': 'bs4',
        'faiss-cpu': 'faiss',
        'sentence-transformers': 'sentence_transformers',
        'qdrant-client': 'qdrant_client',
        'scikit-learn': 'sklearn',
        'huggingface-hub': 'huggingface_hub',
        'psycopg2-binary': 'psycopg2',
        'python-decouple': 'decouple',
        'asyncio-throttle': 'asyncio_throttle',
        'prometheus-client': 'prometheus_client',
        'pytest-asyncio': 'pytest_asyncio',
        'pytest-cov': 'pytest_cov',
        'pytest-mock': 'pytest_mock',
        'sse-starlette': 'sse_starlette',
        'pydantic-ai': 'pydantic_ai',
        'langchain-community': 'langchain_community',
        'PyYAML': 'yaml',
    }
    
    import_name = import_map.get(package_name, package_name)
    
    try:
        importlib.import_module(import_name)
        return True, None
    except ImportError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def parse_requirements_file(file_path):
    """Parse requirements file and extract package names."""
    packages = []
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Skip comments, empty lines, and -r includes
            if not line or line.startswith('#') or line.startswith('-r'):
                continue
            
            # Extract package name (before any version specifiers)
            package = line.split('>=')[0].split('==')[0].split('<')[0].split('>')[0].strip()
            packages.append(package)
    
    return packages

def main():
    req_dir = Path(__file__).parent
    
    # Files to test (excluding README and dev dependencies for now)
    test_files = [
        'base.txt',
        'web.txt', 
        'ai.txt',
        'vector.txt',
        'database.txt',
        'data.txt',
        'utilities.txt'
    ]
    
    print("Testing imports for shared requirements...\n")
    
    all_failed = []
    
    for req_file in test_files:
        file_path = req_dir / req_file
        if not file_path.exists():
            print(f"❌ {req_file} not found")
            continue
            
        print(f"Testing {req_file}:")
        packages = parse_requirements_file(file_path)
        
        failed = []
        for package in packages:
            success, error = test_package_import(package)
            if success:
                print(f"  ✅ {package}")
            else:
                print(f"  ❌ {package}: {error}")
                failed.append((package, error))
        
        if failed:
            all_failed.extend([(req_file, pkg, err) for pkg, err in failed])
        print()
    
    if all_failed:
        print("\n❌ FAILED IMPORTS:")
        for req_file, package, error in all_failed:
            print(f"  {req_file}: {package} - {error}")
        return 1
    else:
        print("✅ All imports successful!")
        return 0

if __name__ == "__main__":
    sys.exit(main())