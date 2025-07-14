#!/usr/bin/env python3
"""
Quick validation script to ensure test files can be imported and run
Tests the test infrastructure before running full test suite
"""

import sys
import os

# Add Noesis to path
sys.path.insert(0, os.path.dirname(__file__))


def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        # Test core theoretical framework imports
        from noesis.core.theoretical.base import MathematicalFramework, AnalysisResult
        from noesis.core.theoretical.manifold import ManifoldAnalyzer, ManifoldStructure
        from noesis.core.theoretical.dynamics import DynamicsAnalyzer, SLDSModel
        from noesis.core.theoretical.catastrophe import CatastropheAnalyzer, CriticalPoint
        from noesis.core.theoretical.synthesis import SynthesisAnalyzer, UniversalPrinciple
        
        print("  ✅ Core theoretical framework modules")
        
        # Test numpy and scipy
        import numpy as np
        import scipy
        print("  ✅ NumPy and SciPy")
        
        # Test sklearn
        from sklearn.decomposition import PCA
        from sklearn.manifold import TSNE
        from sklearn.cluster import KMeans
        print("  ✅ Scikit-learn")
        
        # Test test modules
        import test_mathematical_framework
        import test_framework_edge_cases
        print("  ✅ Test modules")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return False


def test_basic_functionality():
    """Test basic functionality of framework components"""
    print("\n🧪 Testing basic functionality...")
    
    try:
        import numpy as np
        from noesis.core.theoretical.base import MathematicalFramework
        
        # Test basic framework
        framework = MathematicalFramework()
        
        # Create test data
        test_data = np.random.randn(50, 5)
        
        # Test validation
        is_valid, warnings = framework.validate_data(test_data)
        if not is_valid:
            print(f"  ❌ Data validation failed: {warnings}")
            return False
        
        print("  ✅ Data validation")
        
        # Test normalization
        normalized = framework.normalize_data(test_data)
        if normalized.shape != test_data.shape:
            print("  ❌ Normalization failed")
            return False
        
        print("  ✅ Data normalization")
        
        # Test distance computation
        distances = framework.compute_distance_matrix(test_data[:10])
        if distances.shape != (10, 10):
            print("  ❌ Distance computation failed")
            return False
        
        print("  ✅ Distance computation")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Basic functionality test failed: {e}")
        return False


def test_async_operations():
    """Test that async operations work correctly"""
    print("\n⏲️ Testing async operations...")
    
    try:
        import asyncio
        import numpy as np
        from noesis.core.theoretical.manifold import ManifoldAnalyzer
        
        async def test_async():
            # Create test data
            test_data = np.random.randn(30, 4)
            
            # Test async analysis
            analyzer = ManifoldAnalyzer()
            result = await analyzer.analyze(test_data)
            
            # Check result structure
            if result.analysis_type != 'manifold_analysis':
                return False
            
            if 'manifold_structure' not in result.data:
                return False
            
            return True
        
        # Run async test
        success = asyncio.run(test_async())
        
        if success:
            print("  ✅ Async operations")
            return True
        else:
            print("  ❌ Async operations failed")
            return False
        
    except Exception as e:
        print(f"  ❌ Async test failed: {e}")
        return False


def test_data_structures():
    """Test that data structures work correctly"""
    print("\n📊 Testing data structures...")
    
    try:
        from noesis.core.theoretical.base import AnalysisResult
        from noesis.core.theoretical.manifold import ManifoldStructure
        from noesis.core.theoretical.dynamics import SLDSModel
        from noesis.core.theoretical.catastrophe import CriticalPoint
        from noesis.core.theoretical.synthesis import UniversalPrinciple
        import numpy as np
        from datetime import datetime
        
        # Test AnalysisResult
        result = AnalysisResult(
            analysis_type='test',
            data={'test': 'data'},
            confidence=0.8
        )
        result_dict = result.to_dict()
        
        required_fields = ['analysis_type', 'timestamp', 'data', 'confidence']
        if not all(field in result_dict for field in required_fields):
            print("  ❌ AnalysisResult missing required fields")
            return False
        
        print("  ✅ AnalysisResult structure")
        
        # Test ManifoldStructure
        manifold = ManifoldStructure(
            intrinsic_dimension=3,
            principal_components=np.random.randn(3, 5),
            explained_variance=np.array([0.5, 0.3, 0.2]),
            embedding_coordinates=np.random.randn(20, 3)
        )
        manifold_dict = manifold.to_dict()
        
        if 'intrinsic_dimension' not in manifold_dict:
            print("  ❌ ManifoldStructure serialization failed")
            return False
        
        print("  ✅ ManifoldStructure")
        
        # Test CriticalPoint
        critical_point = CriticalPoint(
            location=np.array([1.0, 2.0]),
            transition_type='fold',
            stability_change={'variance': 0.5},
            warning_signals=['high_variance'],
            control_parameters={},
            confidence=0.7
        )
        cp_dict = critical_point.to_dict()
        
        if 'transition_type' not in cp_dict:
            print("  ❌ CriticalPoint serialization failed")
            return False
        
        print("  ✅ CriticalPoint")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Data structures test failed: {e}")
        return False


def main():
    """Run all validation tests"""
    print("🔧 Noesis Mathematical Framework - Test Validation")
    print("=" * 55)
    print("Validating test infrastructure before running full test suite...")
    
    tests = [
        ("Imports", test_imports),
        ("Basic Functionality", test_basic_functionality),
        ("Async Operations", test_async_operations),
        ("Data Structures", test_data_structures)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed_tests += 1
                print(f"✅ {test_name} validation PASSED")
            else:
                print(f"❌ {test_name} validation FAILED")
        except Exception as e:
            print(f"❌ {test_name} validation ERROR: {e}")
    
    # Summary
    print("\n" + "=" * 55)
    print("📊 Validation Summary:")
    print(f"   ✅ Passed: {passed_tests}/{total_tests}")
    print(f"   📈 Success Rate: {passed_tests/total_tests*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 All validations passed! Test infrastructure is ready.")
        print("   You can now run the full test suite with:")
        print("   python run_all_tests.py")
        return 0
    else:
        print(f"\n⚠️ {total_tests - passed_tests} validation(s) failed.")
        print("   Please fix issues before running the full test suite.")
        print("\n💡 Common fixes:")
        print("   - Install missing dependencies: pip install numpy scipy scikit-learn")
        print("   - Check that all Noesis modules are in the correct location")
        print("   - Verify Python version compatibility (3.8+)")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)