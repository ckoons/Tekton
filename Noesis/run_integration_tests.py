#!/usr/bin/env python3
"""
Test runner for Noesis-Sophia integration tests
Runs comprehensive end-to-end workflow validation
"""

import sys
import asyncio
import time
import traceback
from pathlib import Path
from typing import Dict, List, Any
import importlib.util

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class IntegrationTestRunner:
    """Runs integration tests with detailed reporting"""
    
    def __init__(self):
        self.test_results = []
        self.start_time = time.time()
        
    async def run_test_module(self, module_path: str, test_class_names: List[str] = None) -> Dict[str, Any]:
        """Run tests from a specific module"""
        print(f"\n{'='*60}")
        print(f"Running tests from: {module_path}")
        print(f"{'='*60}")
        
        module_results = {
            "module": module_path,
            "tests": [],
            "success_count": 0,
            "failure_count": 0,
            "error_count": 0,
            "total_time": 0
        }
        
        try:
            # Import the test module
            spec = importlib.util.spec_from_file_location("test_module", module_path)
            test_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(test_module)
            
            # Get test classes
            test_classes = []
            if test_class_names:
                for class_name in test_class_names:
                    if hasattr(test_module, class_name):
                        test_classes.append(getattr(test_module, class_name))
            else:
                # Find all test classes
                for attr_name in dir(test_module):
                    attr = getattr(test_module, attr_name)
                    if (isinstance(attr, type) and 
                        attr_name.startswith('Test') and 
                        attr != type):
                        test_classes.append(attr)
            
            # Run tests from each class
            for test_class in test_classes:
                class_results = await self.run_test_class(test_class)
                module_results["tests"].extend(class_results["tests"])
                module_results["success_count"] += class_results["success_count"]
                module_results["failure_count"] += class_results["failure_count"]
                module_results["error_count"] += class_results["error_count"]
                module_results["total_time"] += class_results["total_time"]
        
        except Exception as e:
            print(f"❌ Failed to run module {module_path}: {e}")
            traceback.print_exc()
            module_results["error_count"] += 1
        
        return module_results
    
    async def run_test_class(self, test_class) -> Dict[str, Any]:
        """Run all test methods in a test class"""
        print(f"\n📋 Running {test_class.__name__}")
        print("-" * 40)
        
        class_results = {
            "class": test_class.__name__,
            "tests": [],
            "success_count": 0,
            "failure_count": 0,
            "error_count": 0,
            "total_time": 0
        }
        
        # Get test methods
        test_methods = [
            method for method in dir(test_class)
            if method.startswith('test_') and callable(getattr(test_class, method))
        ]
        
        # Create test instance
        test_instance = test_class()
        
        # Set up fixtures if available
        await self.setup_fixtures(test_instance)
        
        # Run each test method
        for method_name in test_methods:
            test_result = await self.run_test_method(test_instance, method_name)
            class_results["tests"].append(test_result)
            
            if test_result["status"] == "success":
                class_results["success_count"] += 1
            elif test_result["status"] == "failure":
                class_results["failure_count"] += 1
            else:
                class_results["error_count"] += 1
            
            class_results["total_time"] += test_result["duration"]
        
        return class_results
    
    async def setup_fixtures(self, test_instance):
        """Set up test fixtures"""
        fixture_methods = [
            method for method in dir(test_instance)
            if method.startswith('setup_') or hasattr(getattr(test_instance, method), '_pytest_fixture')
        ]
        
        for fixture_method in fixture_methods:
            try:
                method = getattr(test_instance, fixture_method)
                if asyncio.iscoroutinefunction(method):
                    await method()
                else:
                    method()
            except Exception as e:
                print(f"⚠️ Fixture setup failed for {fixture_method}: {e}")
    
    async def run_test_method(self, test_instance, method_name: str) -> Dict[str, Any]:
        """Run a single test method"""
        start_time = time.time()
        test_result = {
            "name": method_name,
            "status": "unknown",
            "duration": 0,
            "error": None,
            "output": []
        }
        
        try:
            print(f"  🧪 {method_name}...", end=" ")
            
            # Get the test method
            test_method = getattr(test_instance, method_name)
            
            # Run the test
            if asyncio.iscoroutinefunction(test_method):
                result = await test_method()
            else:
                result = test_method()
            
            test_result["status"] = "success"
            print("✅")
            
            # Store any return value
            if result is not None:
                test_result["output"].append(f"Returned: {result}")
                
        except AssertionError as e:
            test_result["status"] = "failure"
            test_result["error"] = str(e)
            print(f"❌ FAIL")
            print(f"    {e}")
            
        except Exception as e:
            test_result["status"] = "error"
            test_result["error"] = str(e)
            print(f"💥 ERROR")
            print(f"    {e}")
            # Print full traceback for errors
            traceback.print_exc()
        
        test_result["duration"] = time.time() - start_time
        return test_result
    
    def print_summary(self, all_results: List[Dict[str, Any]]):
        """Print test execution summary"""
        total_time = time.time() - self.start_time
        
        total_success = sum(r["success_count"] for r in all_results)
        total_failure = sum(r["failure_count"] for r in all_results)
        total_error = sum(r["error_count"] for r in all_results)
        total_tests = total_success + total_failure + total_error
        
        print(f"\n{'='*60}")
        print("🏁 INTEGRATION TEST SUMMARY")
        print(f"{'='*60}")
        
        print(f"📊 Test Results:")
        print(f"  ✅ Passed: {total_success}")
        print(f"  ❌ Failed: {total_failure}")
        print(f"  💥 Errors: {total_error}")
        print(f"  📈 Total:  {total_tests}")
        
        if total_tests > 0:
            success_rate = (total_success / total_tests) * 100
            print(f"  🎯 Success Rate: {success_rate:.1f}%")
        
        print(f"\n⏱️ Execution Time: {total_time:.2f} seconds")
        
        # Module breakdown
        print(f"\n📋 Module Breakdown:")
        for result in all_results:
            module_name = Path(result["module"]).stem
            print(f"  {module_name}: {result['success_count']}/{result['success_count'] + result['failure_count'] + result['error_count']} passed")
        
        # Failed tests
        if total_failure > 0 or total_error > 0:
            print(f"\n❌ Failed/Error Tests:")
            for module_result in all_results:
                for test_result in module_result["tests"]:
                    if test_result["status"] in ["failure", "error"]:
                        print(f"  {module_result['module']}::{test_result['name']} - {test_result['status'].upper()}")
                        if test_result["error"]:
                            print(f"    {test_result['error']}")
        
        # Overall result
        if total_failure == 0 and total_error == 0:
            print(f"\n🎉 ALL TESTS PASSED!")
            return True
        else:
            print(f"\n⚠️  Some tests failed or had errors")
            return False


async def main():
    """Main test execution"""
    print("🚀 Starting Noesis-Sophia Integration Tests")
    print("=" * 60)
    
    runner = IntegrationTestRunner()
    
    # Define test modules and classes to run
    test_configs = [
        {
            "module": "test_noesis_sophia_integration.py",
            "classes": ["TestNoesisSophiaIntegration", "TestNoesisAnalysisToSophiaIntegration", "TestExperimentResultValidation"]
        },
        {
            "module": "test_theory_experiment_protocols.py", 
            "classes": ["TestSophiaAPIEndpoints", "TestProtocolLifecycle", "TestErrorHandlingAndEdgeCases"]
        },
        {
            "module": "test_end_to_end_workflows.py",
            "classes": ["TestCompleteWorkflows", "TestWorkflowIntegration"]
        }
    ]
    
    all_results = []
    
    # Run each test module
    for test_config in test_configs:
        module_path = project_root / test_config["module"]
        
        if module_path.exists():
            result = await runner.run_test_module(
                str(module_path), 
                test_config.get("classes")
            )
            all_results.append(result)
        else:
            print(f"⚠️ Test module not found: {module_path}")
    
    # Print final summary
    success = runner.print_summary(all_results)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


async def run_specific_workflow_tests():
    """Run specific high-level workflow tests only"""
    print("🎯 Running Key Workflow Tests")
    print("=" * 40)
    
    runner = IntegrationTestRunner()
    
    # Import the workflow test module
    try:
        from test_end_to_end_workflows import TestCompleteWorkflows
        
        # Create test instance
        test_instance = TestCompleteWorkflows()
        
        # Run key workflow tests
        key_tests = [
            "test_discovery_to_validation_workflow",
            "test_real_time_monitoring_to_intervention_workflow",  
            "test_multi_scale_synthesis_to_scaling_experiments",
            "test_iterative_theory_refinement_workflow"
        ]
        
        results = []
        for test_name in key_tests:
            if hasattr(test_instance, test_name):
                print(f"\n🔬 Running {test_name}")
                result = await runner.run_test_method(test_instance, test_name)
                results.append(result)
                
                if result["status"] == "success":
                    print(f"✅ Workflow completed successfully")
                else:
                    print(f"❌ Workflow failed: {result['error']}")
            else:
                print(f"⚠️ Test method {test_name} not found")
        
        # Summary
        successes = sum(1 for r in results if r["status"] == "success")
        total = len(results)
        
        print(f"\n{'='*40}")
        print(f"🏁 Workflow Test Summary: {successes}/{total} passed")
        
        if successes == total:
            print("🎉 All key workflows validated!")
        else:
            print("⚠️ Some workflows need attention")
            
        return successes == total
        
    except ImportError as e:
        print(f"❌ Could not import workflow tests: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Noesis-Sophia integration tests")
    parser.add_argument("--workflows-only", action="store_true", 
                       help="Run only key workflow tests")
    parser.add_argument("--module", type=str,
                       help="Run tests from specific module only")
    
    args = parser.parse_args()
    
    if args.workflows_only:
        asyncio.run(run_specific_workflow_tests())
    else:
        asyncio.run(main())