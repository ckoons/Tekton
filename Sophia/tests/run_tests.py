#!/usr/bin/env python3
"""
Test runner for Sophia integration tests and monitoring
"""

import os
import sys
import argparse
import subprocess
import asyncio
from typing import List, Dict, Any
from datetime import datetime

# Add Sophia root to path
sophia_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if sophia_root not in sys.path:
    sys.path.insert(0, sophia_root)


class SophiaTestRunner:
    """Test runner for Sophia with monitoring and reporting"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = None
        self.end_time = None
    
    def run_unit_tests(self) -> Dict[str, Any]:
        """Run unit tests"""
        print("🧪 Running unit tests...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            "-m", "unit",
            "--tb=short",
            "-v"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=sophia_root)
        
        return {
            "status": "passed" if result.returncode == 0 else "failed",
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests"""
        print("🔗 Running integration tests...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            "-m", "integration",
            "--tb=short",
            "-v"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=sophia_root)
        
        return {
            "status": "passed" if result.returncode == 0 else "failed",
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    def run_api_tests(self) -> Dict[str, Any]:
        """Run API tests"""
        print("🌐 Running API tests...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            "-m", "api",
            "--tb=short",
            "-v"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=sophia_root)
        
        return {
            "status": "passed" if result.returncode == 0 else "failed",
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    def run_monitoring_tests(self) -> Dict[str, Any]:
        """Run monitoring and health check tests"""
        print("📊 Running monitoring tests...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            "-m", "monitoring",
            "--tb=short",
            "-v"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=sophia_root)
        
        return {
            "status": "passed" if result.returncode == 0 else "failed",
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    def run_e2e_tests(self) -> Dict[str, Any]:
        """Run end-to-end tests"""
        print("🎯 Running end-to-end tests...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            "-m", "e2e",
            "--tb=short",
            "-v"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=sophia_root)
        
        return {
            "status": "passed" if result.returncode == 0 else "failed",
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests"""
        print("🚀 Running all tests...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            "--tb=short",
            "-v",
            "--durations=10"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=sophia_root)
        
        return {
            "status": "passed" if result.returncode == 0 else "failed",
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests"""
        print("⚡ Running performance tests...")
        
        cmd = [
            sys.executable, "-m", "pytest",
            "-k", "performance",
            "--tb=short",
            "-v"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=sophia_root)
        
        return {
            "status": "passed" if result.returncode == 0 else "failed",
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    def check_system_health(self) -> Dict[str, Any]:
        """Check system health before running tests"""
        print("🏥 Checking system health...")
        
        health_checks = {
            "python_version": sys.version,
            "sophia_path": sophia_root,
            "dependencies": self._check_dependencies()
        }
        
        return health_checks
    
    def _check_dependencies(self) -> Dict[str, bool]:
        """Check if required dependencies are available"""
        dependencies = {}
        
        required_packages = [
            "pytest", "pytest-asyncio", "fastapi", "numpy", 
            "psutil", "httpx", "websockets"
        ]
        
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                dependencies[package] = True
            except ImportError:
                dependencies[package] = False
        
        return dependencies
    
    def generate_report(self) -> str:
        """Generate test report"""
        report = []
        report.append("="*60)
        report.append("SOPHIA TEST SUITE REPORT")
        report.append("="*60)
        report.append(f"Start time: {self.start_time}")
        report.append(f"End time: {self.end_time}")
        
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
            report.append(f"Total duration: {duration:.2f} seconds")
        
        report.append("")
        
        for test_type, result in self.test_results.items():
            status_emoji = "✅" if result["status"] == "passed" else "❌"
            report.append(f"{status_emoji} {test_type.upper()}: {result['status']}")
            
            if result["status"] == "failed":
                report.append(f"  Return code: {result['returncode']}")
                if result["stderr"]:
                    report.append(f"  Error: {result['stderr'][:200]}...")
        
        report.append("")
        report.append("="*60)
        
        return "\n".join(report)
    
    def run_test_suite(self, test_types: List[str] = None) -> bool:
        """Run specified test suite"""
        self.start_time = datetime.now()
        
        # Check system health first
        health = self.check_system_health()
        print(f"Python version: {health['python_version']}")
        print(f"Sophia path: {health['sophia_path']}")
        
        # Check dependencies
        missing_deps = [dep for dep, available in health['dependencies'].items() if not available]
        if missing_deps:
            print(f"⚠️  Missing dependencies: {', '.join(missing_deps)}")
            print("Please install missing dependencies with: pip install -r requirements.txt")
        
        # Default to all tests if none specified
        if not test_types:
            test_types = ["all"]
        
        # Run specified tests
        all_passed = True
        
        for test_type in test_types:
            if test_type == "unit":
                self.test_results["unit"] = self.run_unit_tests()
            elif test_type == "integration":
                self.test_results["integration"] = self.run_integration_tests()
            elif test_type == "api":
                self.test_results["api"] = self.run_api_tests()
            elif test_type == "monitoring":
                self.test_results["monitoring"] = self.run_monitoring_tests()
            elif test_type == "e2e":
                self.test_results["e2e"] = self.run_e2e_tests()
            elif test_type == "performance":
                self.test_results["performance"] = self.run_performance_tests()
            elif test_type == "all":
                self.test_results["all"] = self.run_all_tests()
            
            # Check if this test suite passed
            if test_type in self.test_results:
                if self.test_results[test_type]["status"] != "passed":
                    all_passed = False
        
        self.end_time = datetime.now()
        
        # Generate and print report
        report = self.generate_report()
        print("\n" + report)
        
        # Save report to file
        report_file = os.path.join(sophia_root, "test_report.txt")
        with open(report_file, "w") as f:
            f.write(report)
        
        print(f"\n📄 Full report saved to: {report_file}")
        
        return all_passed


def main():
    """Main entry point for test runner"""
    parser = argparse.ArgumentParser(description="Sophia Test Suite Runner")
    parser.add_argument(
        "--type", 
        choices=["unit", "integration", "api", "monitoring", "e2e", "performance", "all"],
        nargs="+",
        default=["all"],
        help="Type of tests to run"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--report", "-r",
        action="store_true",
        help="Generate detailed report"
    )
    
    args = parser.parse_args()
    
    runner = SophiaTestRunner()
    
    print("🧠 Sophia Test Suite Runner")
    print("=" * 50)
    
    success = runner.run_test_suite(args.type)
    
    if success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()