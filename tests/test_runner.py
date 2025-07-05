#!/usr/bin/env python3
"""
Test Runner for Tekton Tests
Discovers and runs tests from subdirectories
"""

import os
import sys
import time
import importlib.util
import asyncio
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional

class TestRunner:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results = {
            'passed': 0,
            'failed': 0,
            'errors': [],
            'test_times': {}
        }
    
    def discover_test_files(self, directory: Path) -> List[Path]:
        """Discover all test_*.py files in directory and subdirectories"""
        test_files = []
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.startswith('test_') and file.endswith('.py'):
                    test_files.append(Path(root) / file)
        
        return sorted(test_files)
    
    def load_test_module(self, test_file: Path):
        """Dynamically load a test module"""
        module_name = test_file.stem
        spec = importlib.util.spec_from_file_location(module_name, test_file)
        module = importlib.util.module_from_spec(spec)
        
        # Add test directory to sys.path temporarily
        test_dir = str(test_file.parent)
        if test_dir not in sys.path:
            sys.path.insert(0, test_dir)
        
        try:
            spec.loader.exec_module(module)
            return module
        finally:
            if test_dir in sys.path:
                sys.path.remove(test_dir)
    
    def find_test_functions(self, module) -> Dict[str, callable]:
        """Find all test functions in a module"""
        tests = {}
        
        for name in dir(module):
            if name.startswith('test_'):
                obj = getattr(module, name)
                if callable(obj):
                    tests[name] = obj
        
        return tests
    
    async def run_test_function(self, test_name: str, test_func: callable) -> Tuple[bool, str, float]:
        """Run a single test function"""
        start_time = time.time()
        
        try:
            # Check if it's an async function
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            elapsed = time.time() - start_time
            
            # Check result - tests should return True/False or None (assumed True)
            if result is False:
                return False, "Test returned False", elapsed
            else:
                return True, "Success", elapsed
                
        except Exception as e:
            elapsed = time.time() - start_time
            return False, str(e), elapsed
    
    async def run_test_file(self, test_file: Path) -> Dict[str, any]:
        """Run all tests in a file"""
        print(f"\n{'='*60}")
        print(f"Running tests from: {test_file}")
        print(f"{'='*60}")
        
        file_results = {
            'file': str(test_file),
            'passed': 0,
            'failed': 0,
            'tests': {}
        }
        
        try:
            # Load module
            module = self.load_test_module(test_file)
            
            # Check if module has custom test runner
            if hasattr(module, 'run_tests'):
                # Use module's own test runner
                print("Using module's custom test runner...")
                if asyncio.iscoroutinefunction(module.run_tests):
                    success = await module.run_tests()
                else:
                    success = module.run_tests()
                
                if success:
                    file_results['passed'] = 1
                    print("✓ Module tests passed")
                else:
                    file_results['failed'] = 1
                    print("✗ Module tests failed")
            else:
                # Find and run individual test functions
                tests = self.find_test_functions(module)
                
                if not tests:
                    print("No test functions found")
                    return file_results
                
                print(f"Found {len(tests)} test(s)")
                
                for test_name, test_func in tests.items():
                    success, message, elapsed = await self.run_test_function(test_name, test_func)
                    
                    if success:
                        file_results['passed'] += 1
                        self.results['passed'] += 1
                        print(f"✓ {test_name} ({elapsed:.2f}s)")
                    else:
                        file_results['failed'] += 1
                        self.results['failed'] += 1
                        self.results['errors'].append((str(test_file), test_name, message))
                        print(f"✗ {test_name} ({elapsed:.2f}s): {message}")
                    
                    file_results['tests'][test_name] = {
                        'success': success,
                        'message': message,
                        'elapsed': elapsed
                    }
                    self.results['test_times'][f"{test_file.stem}::{test_name}"] = elapsed
        
        except Exception as e:
            print(f"ERROR loading test file: {e}")
            file_results['failed'] = 1
            self.results['failed'] += 1
            self.results['errors'].append((str(test_file), "module_load", str(e)))
        
        return file_results
    
    async def run_tests(self, test_paths: List[Path]) -> bool:
        """Run all tests from given paths"""
        all_test_files = []
        
        # Discover test files
        for path in test_paths:
            if path.is_file() and path.suffix == '.py':
                all_test_files.append(path)
            elif path.is_dir():
                all_test_files.extend(self.discover_test_files(path))
        
        if not all_test_files:
            print("No test files found!")
            return False
        
        print(f"Discovered {len(all_test_files)} test file(s)")
        
        # Run tests from each file
        for test_file in all_test_files:
            await self.run_test_file(test_file)
        
        # Print summary
        self.print_summary()
        
        return self.results['failed'] == 0
    
    def print_summary(self):
        """Print test summary"""
        total = self.results['passed'] + self.results['failed']
        
        print(f"\n{'='*60}")
        print(f"Test Summary: {self.results['passed']}/{total} passed")
        print(f"{'='*60}")
        
        if self.results['errors']:
            print("\nFailed tests:")
            for file, test, error in self.results['errors']:
                print(f"  {file}::{test}")
                if self.verbose:
                    print(f"    Error: {error}")
        
        if self.results['test_times']:
            total_time = sum(self.results['test_times'].values())
            print(f"\nTotal test time: {total_time:.2f}s")
            
            if self.verbose:
                print("\nSlowest tests:")
                sorted_times = sorted(
                    self.results['test_times'].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]
                for test, elapsed in sorted_times:
                    print(f"  {test}: {elapsed:.2f}s")

async def main():
    parser = argparse.ArgumentParser(description='Run Tekton tests')
    parser.add_argument('paths', nargs='*', default=['.'],
                       help='Test files or directories (default: current directory)')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    parser.add_argument('-p', '--pattern', default='test_*.py',
                       help='Test file pattern (default: test_*.py)')
    
    args = parser.parse_args()
    
    # Convert paths to Path objects
    test_paths = []
    for path_str in args.paths:
        path = Path(path_str)
        if path.exists():
            test_paths.append(path)
        else:
            print(f"Warning: Path does not exist: {path}")
    
    if not test_paths:
        print("No valid test paths provided!")
        return 1
    
    # Create runner and run tests
    runner = TestRunner(verbose=args.verbose)
    success = await runner.run_tests(test_paths)
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(asyncio.run(main()))