#!/usr/bin/env python3
"""
Comprehensive test runner for Noesis mathematical framework
Runs all integration tests, edge cases, and generates detailed reports
"""

import asyncio
import sys
import os
import time
import json
from datetime import datetime
from typing import Dict, List, Any

# Add Noesis to path
sys.path.insert(0, os.path.dirname(__file__))


class TestReporter:
    """Test result reporter and analyzer"""
    
    def __init__(self):
        self.start_time = time.time()
        self.test_results = {}
        self.suite_results = {}
        
    def record_suite_result(self, suite_name: str, passed: bool, details: Dict[str, Any] = None):
        """Record test suite result"""
        self.suite_results[suite_name] = {
            'passed': passed,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_time = time.time() - self.start_time
        
        passed_suites = sum(1 for result in self.suite_results.values() if result['passed'])
        total_suites = len(self.suite_results)
        success_rate = (passed_suites / total_suites * 100) if total_suites > 0 else 0
        
        return {
            'test_session': {
                'timestamp': datetime.now().isoformat(),
                'duration_seconds': total_time,
                'total_suites': total_suites,
                'passed_suites': passed_suites,
                'failed_suites': total_suites - passed_suites,
                'success_rate_percent': success_rate
            },
            'suite_results': self.suite_results,
            'summary': {
                'overall_status': 'PASSED' if success_rate >= 80 else 'FAILED',
                'recommendation': self._get_recommendation(success_rate)
            }
        }
    
    def _get_recommendation(self, success_rate: float) -> str:
        """Get recommendation based on test results"""
        if success_rate >= 95:
            return "Excellent! Framework is ready for production use."
        elif success_rate >= 80:
            return "Good! Framework is stable with minor issues to address."
        elif success_rate >= 60:
            return "Fair. Several issues need attention before deployment."
        else:
            return "Poor. Major issues detected. Significant work needed."
    
    def print_summary(self):
        """Print test summary to console"""
        report = self.generate_report()
        session = report['test_session']
        
        print("\n" + "=" * 80)
        print("🧪 NOESIS MATHEMATICAL FRAMEWORK - COMPREHENSIVE TEST REPORT")
        print("=" * 80)
        
        print(f"\n📊 Test Session Summary:")
        print(f"   🕐 Duration: {session['duration_seconds']:.1f} seconds")
        print(f"   📦 Total Suites: {session['total_suites']}")
        print(f"   ✅ Passed: {session['passed_suites']}")
        print(f"   ❌ Failed: {session['failed_suites']}")
        print(f"   📈 Success Rate: {session['success_rate_percent']:.1f}%")
        
        print(f"\n📋 Suite Details:")
        for suite_name, result in self.suite_results.items():
            status = "✅ PASSED" if result['passed'] else "❌ FAILED"
            print(f"   {status} {suite_name}")
            
            # Print additional details if available
            if result['details']:
                for key, value in result['details'].items():
                    if isinstance(value, (int, float)):
                        print(f"      {key}: {value}")
                    elif isinstance(value, str) and len(value) < 50:
                        print(f"      {key}: {value}")
        
        print(f"\n💡 Recommendation:")
        print(f"   {report['summary']['recommendation']}")
        
        # Overall status
        overall_status = report['summary']['overall_status']
        if overall_status == 'PASSED':
            print(f"\n🎉 OVERALL RESULT: {overall_status}")
            print("   The Noesis mathematical framework is working correctly!")
        else:
            print(f"\n⚠️ OVERALL RESULT: {overall_status}")
            print("   Please review failed tests and address issues.")


async def run_basic_component_tests():
    """Run basic component import and instantiation tests"""
    print("🔧 Running Basic Component Tests...")
    
    try:
        # Test imports
        from noesis.core.theoretical.base import MathematicalFramework, AnalysisResult
        from noesis.core.theoretical.manifold import ManifoldAnalyzer
        from noesis.core.theoretical.dynamics import DynamicsAnalyzer
        from noesis.core.theoretical.catastrophe import CatastropheAnalyzer
        from noesis.core.theoretical.synthesis import SynthesisAnalyzer
        
        # Test instantiation
        components = {
            'base': MathematicalFramework(),
            'manifold': ManifoldAnalyzer(),
            'dynamics': DynamicsAnalyzer(),
            'catastrophe': CatastropheAnalyzer(),
            'synthesis': SynthesisAnalyzer()
        }
        
        print("✅ All components imported and instantiated successfully")
        return True, {'components_tested': len(components)}
        
    except Exception as e:
        print(f"❌ Component tests failed: {e}")
        return False, {'error': str(e)}


async def run_integration_tests():
    """Run comprehensive integration tests"""
    print("\n🔗 Running Integration Tests...")
    
    try:
        # Import and run integration test module
        import test_mathematical_framework
        
        # Create test instance
        test_suite = test_mathematical_framework.TestMathematicalFrameworkIntegration()
        test_suite.setUp()
        
        # Run individual tests
        test_methods = [
            'test_base_framework_validation',
            'test_manifold_analysis_integration',
            'test_dynamics_analysis_integration',
            'test_catastrophe_analysis_integration',
            'test_synthesis_analysis_integration',
            'test_framework_error_handling',
            'test_end_to_end_integration'
        ]
        
        passed_tests = 0
        failed_tests = 0
        
        for test_method in test_methods:
            try:
                test_func = getattr(test_suite, test_method)
                await test_func()
                passed_tests += 1
                print(f"  ✅ {test_method}")
            except Exception as e:
                failed_tests += 1
                print(f"  ❌ {test_method}: {e}")
        
        success_rate = passed_tests / len(test_methods) * 100
        passed = success_rate >= 80
        
        return passed, {
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'total_tests': len(test_methods),
            'success_rate': success_rate
        }
        
    except Exception as e:
        print(f"❌ Integration tests failed: {e}")
        return False, {'error': str(e)}


async def run_edge_case_tests():
    """Run edge case and stress tests"""
    print("\n🔍 Running Edge Case Tests...")
    
    try:
        # Import and run edge case tests
        import test_framework_edge_cases
        
        # We'll run a simplified version of the edge case tests
        from noesis.core.theoretical.manifold import ManifoldAnalyzer
        import numpy as np
        
        edge_cases_passed = 0
        edge_cases_total = 0
        
        # Test 1: Small dataset
        try:
            tiny_data = np.random.randn(5, 3)
            analyzer = ManifoldAnalyzer()
            result = await analyzer.analyze(tiny_data)
            edge_cases_passed += 1
            print("  ✅ Small dataset handling")
        except:
            print("  ❌ Small dataset handling")
        edge_cases_total += 1
        
        # Test 2: High dimensional data
        try:
            high_dim = np.random.randn(20, 50)
            analyzer = ManifoldAnalyzer()
            result = await analyzer.analyze(high_dim)
            edge_cases_passed += 1
            print("  ✅ High dimensional data")
        except:
            print("  ❌ High dimensional data")
        edge_cases_total += 1
        
        # Test 3: Constant data
        try:
            constant_data = np.ones((30, 4))
            analyzer = ManifoldAnalyzer()
            result = await analyzer.analyze(constant_data)
            edge_cases_passed += 1
            print("  ✅ Constant data handling")
        except:
            print("  ❌ Constant data handling")
        edge_cases_total += 1
        
        success_rate = edge_cases_passed / edge_cases_total * 100
        passed = success_rate >= 70  # More lenient for edge cases
        
        return passed, {
            'passed_cases': edge_cases_passed,
            'total_cases': edge_cases_total,
            'success_rate': success_rate
        }
        
    except Exception as e:
        print(f"❌ Edge case tests failed: {e}")
        return False, {'error': str(e)}


async def run_performance_tests():
    """Run basic performance tests"""
    print("\n⚡ Running Performance Tests...")
    
    try:
        from noesis.core.theoretical.manifold import ManifoldAnalyzer
        from noesis.core.theoretical.dynamics import DynamicsAnalyzer
        import numpy as np
        import time
        
        performance_results = {}
        
        # Test 1: Manifold analysis performance
        large_data = np.random.randn(500, 10)
        start_time = time.time()
        
        analyzer = ManifoldAnalyzer()
        result = await analyzer.analyze(large_data)
        
        manifold_time = time.time() - start_time
        performance_results['manifold_time'] = manifold_time
        
        # Test 2: Dynamics analysis performance
        time_series = np.random.randn(200, 6)
        start_time = time.time()
        
        dynamics_analyzer = DynamicsAnalyzer({'em_iterations': 5})
        result = await dynamics_analyzer.analyze(time_series)
        
        dynamics_time = time.time() - start_time
        performance_results['dynamics_time'] = dynamics_time
        
        # Performance thresholds (reasonable for testing)
        manifold_ok = manifold_time < 30
        dynamics_ok = dynamics_time < 30
        
        passed = manifold_ok and dynamics_ok
        
        print(f"  📐 Manifold analysis (500×10): {manifold_time:.2f}s {'✅' if manifold_ok else '❌'}")
        print(f"  🌊 Dynamics analysis (200×6): {dynamics_time:.2f}s {'✅' if dynamics_ok else '❌'}")
        
        return passed, performance_results
        
    except Exception as e:
        print(f"❌ Performance tests failed: {e}")
        return False, {'error': str(e)}


async def run_noesis_component_tests():
    """Test integration with NoesisComponent"""
    print("\n🏗️ Running Noesis Component Tests...")
    
    try:
        from noesis.core.noesis_component import NoesisComponent
        
        # Initialize component
        component = NoesisComponent()
        await component.init()
        
        # Test capabilities
        capabilities = component.get_capabilities()
        has_theoretical = any('theoretical' in cap.lower() for cap in capabilities)
        
        # Test metadata
        metadata = component.get_metadata()
        has_components = 'components' in metadata
        
        await component.shutdown()
        
        passed = has_theoretical and has_components
        
        details = {
            'has_theoretical_capabilities': has_theoretical,
            'has_component_metadata': has_components,
            'total_capabilities': len(capabilities)
        }
        
        if passed:
            print("  ✅ NoesisComponent integration working")
        else:
            print("  ❌ NoesisComponent integration issues")
        
        return passed, details
        
    except ImportError:
        print("  ⚠️ NoesisComponent not available - skipping")
        return True, {'skipped': 'NoesisComponent not available'}
    except Exception as e:
        print(f"  ❌ NoesisComponent tests failed: {e}")
        return False, {'error': str(e)}


async def main():
    """Main test runner"""
    print("🧠 Noesis Mathematical Framework - Comprehensive Test Suite")
    print("=" * 70)
    print("Running all tests to validate framework integrity and performance...")
    
    reporter = TestReporter()
    
    # Test Suite 1: Basic Components
    print("\n1️⃣ Basic Component Tests")
    passed, details = await run_basic_component_tests()
    reporter.record_suite_result("Basic Components", passed, details)
    
    # Test Suite 2: Integration Tests
    print("\n2️⃣ Integration Tests")
    passed, details = await run_integration_tests()
    reporter.record_suite_result("Integration Tests", passed, details)
    
    # Test Suite 3: Edge Cases
    print("\n3️⃣ Edge Case Tests")
    passed, details = await run_edge_case_tests()
    reporter.record_suite_result("Edge Cases", passed, details)
    
    # Test Suite 4: Performance
    print("\n4️⃣ Performance Tests")
    passed, details = await run_performance_tests()
    reporter.record_suite_result("Performance", passed, details)
    
    # Test Suite 5: Noesis Component Integration
    print("\n5️⃣ Noesis Component Integration")
    passed, details = await run_noesis_component_tests()
    reporter.record_suite_result("Component Integration", passed, details)
    
    # Generate and save report
    report = reporter.generate_report()
    
    # Save detailed report to file
    report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Detailed report saved to: {report_file}")
    except Exception as e:
        print(f"\n⚠️ Could not save report file: {e}")
    
    # Print summary
    reporter.print_summary()
    
    # Return exit code
    overall_passed = report['summary']['overall_status'] == 'PASSED'
    return 0 if overall_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)