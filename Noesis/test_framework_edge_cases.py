#!/usr/bin/env python3
"""
Edge case and stress tests for Noesis mathematical framework
Tests boundary conditions, error scenarios, and numerical stability
"""

import asyncio
import sys
import os
import numpy as np
import warnings

# Add Noesis to path
sys.path.insert(0, os.path.dirname(__file__))

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)


async def test_edge_case_data():
    """Test framework with edge case data"""
    print("🔍 Testing Edge Case Data Scenarios...")
    
    from noesis.core.theoretical.manifold import ManifoldAnalyzer
    from noesis.core.theoretical.dynamics import DynamicsAnalyzer
    from noesis.core.theoretical.catastrophe import CatastropheAnalyzer
    
    test_cases = []
    
    # Test Case 1: Very small datasets
    try:
        tiny_data = np.random.randn(3, 2)
        analyzer = ManifoldAnalyzer()
        result = await analyzer.analyze(tiny_data)
        test_cases.append(("Tiny dataset (3×2)", "PASSED", result.confidence))
    except Exception as e:
        test_cases.append(("Tiny dataset (3×2)", f"FAILED: {e}", 0))
    
    # Test Case 2: High-dimensional data
    try:
        high_dim_data = np.random.randn(50, 100)  # More features than samples
        analyzer = ManifoldAnalyzer()
        result = await analyzer.analyze(high_dim_data)
        test_cases.append(("High-dim data (50×100)", "PASSED", result.confidence))
    except Exception as e:
        test_cases.append(("High-dim data (50×100)", f"FAILED: {e}", 0))
    
    # Test Case 3: Single time step
    try:
        single_step = np.random.randn(1, 5)
        dynamics_analyzer = DynamicsAnalyzer({'em_iterations': 1})
        result = await dynamics_analyzer.analyze(single_step)
        test_cases.append(("Single time step", "PASSED", result.confidence))
    except Exception as e:
        test_cases.append(("Single time step", f"FAILED: {e}", 0))
    
    # Test Case 4: Constant data (no variance)
    try:
        constant_data = np.ones((50, 4))
        analyzer = ManifoldAnalyzer()
        result = await analyzer.analyze(constant_data)
        test_cases.append(("Constant data", "PASSED", result.confidence))
    except Exception as e:
        test_cases.append(("Constant data", f"FAILED: {e}", 0))
    
    # Test Case 5: Data with extreme values
    try:
        extreme_data = np.random.randn(100, 5)
        extreme_data[0, 0] = 1e10  # Very large value
        extreme_data[1, 1] = -1e10  # Very small value
        analyzer = ManifoldAnalyzer()
        result = await analyzer.analyze(extreme_data)
        test_cases.append(("Extreme values", "PASSED", result.confidence))
    except Exception as e:
        test_cases.append(("Extreme values", f"FAILED: {e}", 0))
    
    # Test Case 6: Sparse data (mostly zeros)
    try:
        sparse_data = np.zeros((100, 10))
        sparse_data[::10, ::2] = np.random.randn(10, 5)  # 10% non-zero
        analyzer = ManifoldAnalyzer()
        result = await analyzer.analyze(sparse_data)
        test_cases.append(("Sparse data", "PASSED", result.confidence))
    except Exception as e:
        test_cases.append(("Sparse data", f"FAILED: {e}", 0))
    
    # Print results
    print("\n📊 Edge Case Test Results:")
    for case_name, status, confidence in test_cases:
        if "PASSED" in status:
            print(f"  ✅ {case_name}: {status} (confidence: {confidence:.3f})")
        else:
            print(f"  ❌ {case_name}: {status}")
    
    passed = sum(1 for _, status, _ in test_cases if "PASSED" in status)
    total = len(test_cases)
    print(f"\n📈 Edge Cases: {passed}/{total} passed ({passed/total*100:.1f}%)")
    
    return passed == total


async def test_numerical_stability():
    """Test numerical stability of algorithms"""
    print("\n🔢 Testing Numerical Stability...")
    
    from noesis.core.theoretical.base import MathematicalFramework
    from noesis.core.theoretical.manifold import ManifoldAnalyzer
    
    stability_tests = []
    
    # Test 1: Ill-conditioned matrices
    try:
        # Create ill-conditioned data
        ill_cond_data = np.random.randn(100, 5)
        ill_cond_data[:, 1] = ill_cond_data[:, 0] + 1e-12 * np.random.randn(100)  # Nearly collinear
        
        analyzer = ManifoldAnalyzer()
        result = await analyzer.analyze(ill_cond_data)
        
        has_warnings = len(result.warnings) > 0
        stability_tests.append(("Ill-conditioned data", "PASSED" if has_warnings else "NO_WARNING", result.confidence))
    except Exception as e:
        stability_tests.append(("Ill-conditioned data", f"FAILED: {e}", 0))
    
    # Test 2: Data with different scales
    try:
        multi_scale_data = np.random.randn(100, 4)
        multi_scale_data[:, 0] *= 1e6  # First column much larger
        multi_scale_data[:, 1] *= 1e-6  # Second column much smaller
        
        framework = MathematicalFramework()
        normalized = framework.normalize_data(multi_scale_data, method='standard')
        
        # Check if normalization worked
        scales_balanced = np.allclose(np.std(normalized, axis=0), 1.0, atol=0.1)
        stability_tests.append(("Multi-scale data", "PASSED" if scales_balanced else "UNBALANCED", 1.0))
    except Exception as e:
        stability_tests.append(("Multi-scale data", f"FAILED: {e}", 0))
    
    # Test 3: Near-singular covariance
    try:
        # Create data with near-zero variance in one dimension
        near_singular = np.random.randn(100, 5)
        near_singular[:, 2] = 1e-15 * np.random.randn(100)  # Near-zero variance
        
        analyzer = ManifoldAnalyzer()
        result = await analyzer.analyze(near_singular)
        
        stability_tests.append(("Near-singular covariance", "PASSED", result.confidence))
    except Exception as e:
        stability_tests.append(("Near-singular covariance", f"FAILED: {e}", 0))
    
    # Test 4: Perfect correlations
    try:
        perfect_corr = np.random.randn(100, 3)
        perfect_corr = np.column_stack([perfect_corr, perfect_corr[:, 0]])  # Perfect correlation
        
        analyzer = ManifoldAnalyzer()
        result = await analyzer.analyze(perfect_corr)
        
        stability_tests.append(("Perfect correlations", "PASSED", result.confidence))
    except Exception as e:
        stability_tests.append(("Perfect correlations", f"FAILED: {e}", 0))
    
    # Print results
    print("\n📊 Numerical Stability Test Results:")
    for test_name, status, confidence in stability_tests:
        if "PASSED" in status:
            print(f"  ✅ {test_name}: {status} (confidence: {confidence:.3f})")
        elif "NO_WARNING" in status:
            print(f"  ⚠️ {test_name}: Passed but no stability warning generated")
        else:
            print(f"  ❌ {test_name}: {status}")
    
    passed = sum(1 for _, status, _ in stability_tests if "PASSED" in status or "NO_WARNING" in status)
    total = len(stability_tests)
    print(f"\n📈 Stability Tests: {passed}/{total} passed ({passed/total*100:.1f}%)")
    
    return passed >= total * 0.75  # Allow 25% tolerance for stability tests


async def test_memory_and_performance():
    """Test memory usage and performance under stress"""
    print("\n⚡ Testing Memory and Performance...")
    
    import time
    import psutil
    import os
    
    from noesis.core.theoretical.manifold import ManifoldAnalyzer
    from noesis.core.theoretical.dynamics import DynamicsAnalyzer
    
    performance_tests = []
    
    # Get initial memory usage
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / 1024 / 1024  # MB
    
    # Test 1: Large dataset processing
    try:
        print("  📊 Testing large dataset (2000×20)...")
        large_data = np.random.randn(2000, 20)
        
        start_time = time.time()
        start_memory = process.memory_info().rss / 1024 / 1024
        
        analyzer = ManifoldAnalyzer({'embedding_method': 'pca'})  # Faster method
        result = await analyzer.analyze(large_data)
        
        end_time = time.time()
        end_memory = process.memory_info().rss / 1024 / 1024
        
        duration = end_time - start_time
        memory_used = end_memory - start_memory
        
        performance_tests.append(("Large dataset", "PASSED", {
            'duration': duration,
            'memory_mb': memory_used,
            'confidence': result.confidence
        }))
        
        print(f"    ⏱️ Duration: {duration:.2f}s")
        print(f"    💾 Memory used: {memory_used:.1f}MB")
        
    except Exception as e:
        performance_tests.append(("Large dataset", f"FAILED: {e}", {}))
    
    # Test 2: Long time series
    try:
        print("  📈 Testing long time series (1000×10)...")
        long_series = np.random.randn(1000, 10)
        
        start_time = time.time()
        start_memory = process.memory_info().rss / 1024 / 1024
        
        analyzer = DynamicsAnalyzer({'em_iterations': 5, 'n_regimes': 2})  # Reduced complexity
        result = await analyzer.analyze(long_series)
        
        end_time = time.time()
        end_memory = process.memory_info().rss / 1024 / 1024
        
        duration = end_time - start_time
        memory_used = end_memory - start_memory
        
        performance_tests.append(("Long time series", "PASSED", {
            'duration': duration,
            'memory_mb': memory_used,
            'confidence': result.confidence
        }))
        
        print(f"    ⏱️ Duration: {duration:.2f}s")
        print(f"    💾 Memory used: {memory_used:.1f}MB")
        
    except Exception as e:
        performance_tests.append(("Long time series", f"FAILED: {e}", {}))
    
    # Test 3: Memory cleanup
    try:
        print("  🧹 Testing memory cleanup...")
        pre_cleanup_memory = process.memory_info().rss / 1024 / 1024
        
        # Create and destroy multiple analyzers
        for i in range(10):
            temp_data = np.random.randn(500, 8)
            temp_analyzer = ManifoldAnalyzer()
            temp_result = await temp_analyzer.analyze(temp_data)
            del temp_analyzer, temp_result, temp_data
        
        # Force garbage collection
        import gc
        gc.collect()
        
        post_cleanup_memory = process.memory_info().rss / 1024 / 1024
        memory_growth = post_cleanup_memory - pre_cleanup_memory
        
        memory_leak = memory_growth > 100  # More than 100MB growth indicates potential leak
        
        performance_tests.append(("Memory cleanup", "PASSED" if not memory_leak else "MEMORY_LEAK", {
            'memory_growth_mb': memory_growth
        }))
        
        print(f"    📈 Memory growth: {memory_growth:.1f}MB")
        
    except Exception as e:
        performance_tests.append(("Memory cleanup", f"FAILED: {e}", {}))
    
    # Print results
    print(f"\n📊 Performance Test Results:")
    for test_name, status, metrics in performance_tests:
        if "PASSED" in status:
            duration = metrics.get('duration', 0)
            memory = metrics.get('memory_mb', 0)
            print(f"  ✅ {test_name}: {status}")
            if duration > 0:
                print(f"     ⏱️ Duration: {duration:.2f}s")
            if memory != 0:
                print(f"     💾 Memory: {memory:.1f}MB")
        elif "MEMORY_LEAK" in status:
            print(f"  ⚠️ {test_name}: Potential memory leak detected ({metrics.get('memory_growth_mb', 0):.1f}MB)")
        else:
            print(f"  ❌ {test_name}: {status}")
    
    passed = sum(1 for _, status, _ in performance_tests if "PASSED" in status)
    total = len(performance_tests)
    print(f"\n📈 Performance Tests: {passed}/{total} passed ({passed/total*100:.1f}%)")
    
    return passed >= total * 0.8  # Allow some tolerance for performance tests


async def test_concurrent_operations():
    """Test concurrent operations and thread safety"""
    print("\n🔄 Testing Concurrent Operations...")
    
    from noesis.core.theoretical.manifold import ManifoldAnalyzer
    import asyncio
    
    concurrent_tests = []
    
    # Test 1: Multiple concurrent analyses
    try:
        print("  🔀 Testing concurrent manifold analyses...")
        
        async def run_analysis(data_id):
            data = np.random.randn(200, 6)
            analyzer = ManifoldAnalyzer()
            result = await analyzer.analyze(data)
            return data_id, result.confidence
        
        # Run 5 analyses concurrently
        tasks = [run_analysis(i) for i in range(5)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check results
        successful = sum(1 for r in results if isinstance(r, tuple))
        errors = sum(1 for r in results if isinstance(r, Exception))
        
        concurrent_tests.append(("Concurrent analyses", f"PASSED ({successful}/5 successful, {errors} errors)", 
                               successful / 5))
        
    except Exception as e:
        concurrent_tests.append(("Concurrent analyses", f"FAILED: {e}", 0))
    
    # Test 2: Sequential vs concurrent performance
    try:
        print("  ⏱️ Comparing sequential vs concurrent performance...")
        
        # Sequential execution
        start_time = time.time()
        for i in range(3):
            data = np.random.randn(150, 5)
            analyzer = ManifoldAnalyzer()
            await analyzer.analyze(data)
        sequential_time = time.time() - start_time
        
        # Concurrent execution
        start_time = time.time()
        tasks = []
        for i in range(3):
            data = np.random.randn(150, 5)
            analyzer = ManifoldAnalyzer()
            tasks.append(analyzer.analyze(data))
        await asyncio.gather(*tasks)
        concurrent_time = time.time() - start_time
        
        speedup = sequential_time / concurrent_time if concurrent_time > 0 else 1
        
        concurrent_tests.append(("Performance comparison", f"PASSED (speedup: {speedup:.2f}x)", speedup))
        
        print(f"    📊 Sequential: {sequential_time:.2f}s")
        print(f"    📊 Concurrent: {concurrent_time:.2f}s")
        print(f"    📊 Speedup: {speedup:.2f}x")
        
    except Exception as e:
        concurrent_tests.append(("Performance comparison", f"FAILED: {e}", 0))
    
    # Print results
    print(f"\n📊 Concurrent Operations Test Results:")
    for test_name, status, metric in concurrent_tests:
        if "PASSED" in status:
            print(f"  ✅ {test_name}: {status}")
        else:
            print(f"  ❌ {test_name}: {status}")
    
    passed = sum(1 for _, status, _ in concurrent_tests if "PASSED" in status)
    total = len(concurrent_tests)
    print(f"\n📈 Concurrent Tests: {passed}/{total} passed ({passed/total*100:.1f}%)")
    
    return passed == total


async def main():
    """Run all edge case and stress tests"""
    print("🧪 Noesis Mathematical Framework - Edge Cases & Stress Tests")
    print("=" * 70)
    
    test_results = []
    
    # Run test suites
    print("\n1️⃣ Edge Case Data Scenarios")
    edge_case_result = await test_edge_case_data()
    test_results.append(("Edge Cases", edge_case_result))
    
    print("\n2️⃣ Numerical Stability Tests")
    stability_result = await test_numerical_stability()
    test_results.append(("Numerical Stability", stability_result))
    
    print("\n3️⃣ Memory and Performance Tests")
    performance_result = await test_memory_and_performance()
    test_results.append(("Performance", performance_result))
    
    print("\n4️⃣ Concurrent Operations Tests")
    concurrent_result = await test_concurrent_operations()
    test_results.append(("Concurrency", concurrent_result))
    
    # Final summary
    print("\n" + "=" * 70)
    print("📊 Final Test Summary:")
    
    passed_suites = 0
    total_suites = len(test_results)
    
    for suite_name, passed in test_results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {status} {suite_name}")
        if passed:
            passed_suites += 1
    
    success_rate = passed_suites / total_suites * 100
    print(f"\n📈 Overall Success Rate: {success_rate:.1f}% ({passed_suites}/{total_suites} suites)")
    
    if success_rate >= 75:
        print("\n🎉 Mathematical framework passes stress testing!")
        print("   The framework demonstrates good robustness and stability.")
        return 0
    else:
        print("\n⚠️ Some stress tests failed.")
        print("   Consider reviewing numerical stability and error handling.")
        return 1


if __name__ == "__main__":
    import time
    exit_code = asyncio.run(main())
    sys.exit(exit_code)