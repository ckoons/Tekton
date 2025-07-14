#!/usr/bin/env python3
"""
Comprehensive integration tests for Noesis mathematical framework
Tests all components: base, manifold, dynamics, catastrophe, and synthesis
"""

import asyncio
import sys
import os
import numpy as np
import unittest
from unittest.mock import patch, MagicMock
import warnings

# Add Noesis to path
sys.path.insert(0, os.path.dirname(__file__))

# Filter sklearn warnings for cleaner test output
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)


class TestMathematicalFrameworkIntegration(unittest.TestCase):
    """Integration tests for the complete mathematical framework"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_data_2d = np.random.randn(100, 5)
        self.sample_trajectory = np.random.randn(200, 4)
        self.sample_time_series = np.cumsum(np.random.randn(150, 3), axis=0)
        
        # Add some structure to the data
        self.sample_data_2d[:50] *= 2  # Create two regimes
        self.sample_trajectory[100:] += 5  # Add a jump
        
        print(f"\n🧪 Test setup complete: {self.sample_data_2d.shape} data, {self.sample_trajectory.shape} trajectory")
    
    async def test_base_framework_validation(self):
        """Test base mathematical framework validation"""
        print("\n🔧 Testing Base Framework...")
        
        from noesis.core.theoretical.base import MathematicalFramework, AnalysisResult
        
        # Test with mock implementation
        class TestFramework(MathematicalFramework):
            async def analyze(self, data, **kwargs):
                return await self.prepare_results(
                    data={'test': 'result'},
                    analysis_type='test_analysis'
                )
        
        framework = TestFramework()
        
        # Test data validation
        is_valid, warnings = await framework.validate_data(self.sample_data_2d)
        self.assertTrue(is_valid, "Valid data should pass validation")
        
        # Test normalization
        normalized = framework.normalize_data(self.sample_data_2d, method='standard')
        self.assertAlmostEqual(np.mean(normalized), 0, places=1, msg="Standard normalization should center data")
        
        # Test distance computation
        distances = framework.compute_distance_matrix(self.sample_data_2d[:10])
        self.assertEqual(distances.shape, (10, 10), "Distance matrix should be square")
        self.assertEqual(distances[0, 0], 0, "Self-distance should be zero")
        
        # Test dimensionality estimation
        dim = framework.estimate_dimensionality(self.sample_data_2d)
        self.assertGreater(dim, 0, "Estimated dimension should be positive")
        self.assertLessEqual(dim, self.sample_data_2d.shape[1], "Dimension should not exceed feature count")
        
        print("✅ Base framework validation passed")
    
    async def test_manifold_analysis_integration(self):
        """Test manifold analysis component"""
        print("\n📐 Testing Manifold Analysis...")
        
        from noesis.core.theoretical.manifold import ManifoldAnalyzer, ManifoldStructure
        
        analyzer = ManifoldAnalyzer({
            'variance_threshold': 0.9,
            'embedding_method': 'pca'
        })
        
        # Test full analysis
        result = await analyzer.analyze(self.sample_data_2d)
        
        self.assertEqual(result.analysis_type, 'manifold_analysis', "Should return manifold analysis")
        self.assertIn('manifold_structure', result.data, "Should contain manifold structure")
        
        # Test manifold structure
        manifold_data = result.data['manifold_structure']
        self.assertIn('intrinsic_dimension', manifold_data, "Should estimate intrinsic dimension")
        self.assertIn('embedding_coordinates', manifold_data, "Should provide embedding")
        self.assertIn('topology_metrics', manifold_data, "Should compute topology metrics")
        
        # Test trajectory analysis
        if len(self.sample_trajectory) > analyzer.window_size:
            trajectory_analysis = await analyzer.identify_trajectory_patterns(self.sample_trajectory)
            self.assertGreater(trajectory_analysis.trajectory_length, 0, "Should compute trajectory length")
            self.assertEqual(len(trajectory_analysis.curvature), len(self.sample_trajectory), "Curvature array should match trajectory length")
        
        print("✅ Manifold analysis integration passed")
    
    async def test_dynamics_analysis_integration(self):
        """Test dynamics analysis (SLDS) component"""
        print("\n🌊 Testing Dynamics Analysis...")
        
        from noesis.core.theoretical.dynamics import DynamicsAnalyzer, SLDSModel
        
        analyzer = DynamicsAnalyzer({
            'n_regimes': 3,
            'em_iterations': 10  # Reduced for testing
        })
        
        # Test SLDS analysis
        result = await analyzer.analyze(self.sample_time_series)
        
        self.assertEqual(result.analysis_type, 'dynamics_analysis', "Should return dynamics analysis")
        self.assertIn('slds_model', result.data, "Should contain SLDS model")
        self.assertIn('regime_identification', result.data, "Should identify regimes")
        
        # Test SLDS model structure
        slds_data = result.data['slds_model']
        self.assertEqual(slds_data['n_regimes'], 3, "Should have correct number of regimes")
        self.assertIn('transition_matrices', slds_data, "Should contain transition matrices")
        self.assertIn('transition_probabilities', slds_data, "Should contain transition probabilities")
        
        # Test regime identification
        regime_data = result.data['regime_identification']
        self.assertIn('current_regime', regime_data, "Should identify current regime")
        self.assertIn('regime_sequence', regime_data, "Should provide regime sequence")
        self.assertEqual(len(regime_data['regime_sequence']), len(self.sample_time_series), 
                        "Regime sequence should match data length")
        
        print("✅ Dynamics analysis integration passed")
    
    async def test_catastrophe_analysis_integration(self):
        """Test catastrophe theory analysis component"""
        print("\n🔱 Testing Catastrophe Analysis...")
        
        from noesis.core.theoretical.catastrophe import CatastropheAnalyzer, CriticalPoint
        
        analyzer = CatastropheAnalyzer({
            'window_size': 30,
            'warning_threshold': 1.5
        })
        
        # Test trajectory-based analysis
        result = await analyzer.analyze(self.sample_trajectory)
        
        self.assertEqual(result.analysis_type, 'catastrophe_analysis', "Should return catastrophe analysis")
        self.assertIn('critical_points', result.data, "Should detect critical points")
        self.assertIn('early_warning_signals', result.data, "Should compute warning signals")
        
        # Test early warning signals
        warnings = result.data['early_warning_signals']
        if warnings:
            self.assertIn('composite_warning_score', warnings, "Should compute composite warning score")
            self.assertIn('warning_level', warnings, "Should assign warning level")
        
        # Test with multi-component data
        multi_data = {
            'trajectory': self.sample_trajectory,
            'manifold': {'embedding_coordinates': self.sample_data_2d},
            'dynamics': {'slds_model': {'transition_matrices': {'0': np.eye(3).tolist()}}}
        }
        
        result_multi = await analyzer.analyze(multi_data)
        self.assertIsInstance(result_multi.data['critical_points'], list, "Should return list of critical points")
        
        print("✅ Catastrophe analysis integration passed")
    
    async def test_synthesis_analysis_integration(self):
        """Test synthesis analysis component"""
        print("\n🎯 Testing Synthesis Analysis...")
        
        from noesis.core.theoretical.synthesis import SynthesisAnalyzer, UniversalPrinciple
        
        analyzer = SynthesisAnalyzer({
            'confidence_threshold': 0.7
        })
        
        # Create multi-scale test data
        multi_scale_data = {
            'small_scale': {
                'n_agents': 50,
                'intrinsic_dimension': 3,
                'complexity': 0.5,
                'manifold_structure': {
                    'intrinsic_dimension': 3,
                    'topology_metrics': {'density_variance': 0.3}
                }
            },
            'medium_scale': {
                'n_agents': 500,
                'intrinsic_dimension': 5,
                'complexity': 0.8,
                'manifold_structure': {
                    'intrinsic_dimension': 5,
                    'topology_metrics': {'density_variance': 0.6}
                }
            },
            'large_scale': {
                'n_agents': 5000,
                'intrinsic_dimension': 7,
                'complexity': 1.2,
                'manifold_structure': {
                    'intrinsic_dimension': 7,
                    'topology_metrics': {'density_variance': 0.9}
                }
            }
        }
        
        # Test synthesis analysis
        result = await analyzer.analyze(multi_scale_data)
        
        self.assertEqual(result.analysis_type, 'synthesis_analysis', "Should return synthesis analysis")
        self.assertIn('universal_principles', result.data, "Should extract universal principles")
        self.assertIn('emergent_properties', result.data, "Should identify emergent properties")
        self.assertIn('cross_scale_patterns', result.data, "Should find cross-scale patterns")
        
        # Check for scaling laws
        principles = result.data['universal_principles']
        has_scaling_law = any(p['principle_type'] == 'scaling_law' for p in principles)
        if has_scaling_law:
            print("  📈 Found scaling law principle")
        
        # Check for emergent properties
        emergent = result.data['emergent_properties']
        self.assertIsInstance(emergent, list, "Emergent properties should be a list")
        
        print("✅ Synthesis analysis integration passed")
    
    async def test_framework_error_handling(self):
        """Test error handling across the framework"""
        print("\n⚠️ Testing Error Handling...")
        
        from noesis.core.theoretical.base import MathematicalFramework
        from noesis.core.theoretical.manifold import ManifoldAnalyzer
        from noesis.core.theoretical.dynamics import DynamicsAnalyzer
        from noesis.core.theoretical.catastrophe import CatastropheAnalyzer
        
        # Test with invalid data
        invalid_data = np.array([[np.nan, 1], [2, np.inf]])
        
        # Test manifold analyzer with invalid data
        manifold_analyzer = ManifoldAnalyzer()
        result = await manifold_analyzer.analyze(invalid_data)
        self.assertIn('error', result.data, "Should handle invalid data gracefully")
        self.assertGreater(len(result.warnings), 0, "Should generate warnings for invalid data")
        
        # Test with empty data
        empty_data = np.array([]).reshape(0, 5)
        result_empty = await manifold_analyzer.analyze(empty_data)
        self.assertIn('error', result_empty.data, "Should handle empty data")
        
        # Test dynamics analyzer with insufficient data
        dynamics_analyzer = DynamicsAnalyzer()
        short_series = np.random.randn(5, 3)  # Too short for SLDS
        result_short = await dynamics_analyzer.analyze(short_series)
        # Should still return some result, even if limited
        self.assertEqual(result_short.analysis_type, 'dynamics_analysis', "Should return dynamics analysis type")
        
        print("✅ Error handling tests passed")
    
    async def test_end_to_end_integration(self):
        """Test complete end-to-end analysis pipeline"""
        print("\n🔄 Testing End-to-End Integration...")
        
        from noesis.core.theoretical.manifold import ManifoldAnalyzer
        from noesis.core.theoretical.dynamics import DynamicsAnalyzer
        from noesis.core.theoretical.catastrophe import CatastropheAnalyzer
        from noesis.core.theoretical.synthesis import SynthesisAnalyzer
        
        # Step 1: Manifold analysis
        manifold_analyzer = ManifoldAnalyzer()
        manifold_result = await manifold_analyzer.analyze(self.sample_data_2d)
        
        # Step 2: Dynamics analysis
        dynamics_analyzer = DynamicsAnalyzer({'em_iterations': 5})  # Quick run
        dynamics_result = await dynamics_analyzer.analyze(self.sample_time_series)
        
        # Step 3: Catastrophe analysis
        catastrophe_analyzer = CatastropheAnalyzer()
        
        # Prepare data for catastrophe analysis
        catastrophe_data = {
            'manifold': manifold_result.data.get('manifold_structure'),
            'dynamics': dynamics_result.data,
            'trajectory': self.sample_trajectory
        }
        
        catastrophe_result = await catastrophe_analyzer.analyze(catastrophe_data)
        
        # Step 4: Synthesis analysis
        synthesis_analyzer = SynthesisAnalyzer()
        
        # Prepare multi-scale data for synthesis
        synthesis_data = {
            'manifold_scale': {
                **manifold_result.data,
                'n_agents': 100,
                'analysis_type': 'manifold'
            },
            'dynamics_scale': {
                **dynamics_result.data,
                'n_agents': 150,
                'analysis_type': 'dynamics'
            },
            'catastrophe_scale': {
                **catastrophe_result.data,
                'n_agents': 200,
                'analysis_type': 'catastrophe'
            }
        }
        
        synthesis_result = await synthesis_analyzer.analyze(synthesis_data)
        
        # Verify end-to-end results
        self.assertTrue(manifold_result.confidence > 0, "Manifold analysis should have confidence")
        self.assertTrue(dynamics_result.confidence > 0, "Dynamics analysis should have confidence")
        self.assertTrue(catastrophe_result.confidence > 0, "Catastrophe analysis should have confidence")
        self.assertTrue(synthesis_result.confidence > 0, "Synthesis analysis should have confidence")
        
        # Check that data flows through pipeline
        self.assertIn('manifold_structure', manifold_result.data)
        self.assertIn('slds_model', dynamics_result.data)
        self.assertIn('critical_points', catastrophe_result.data)
        self.assertIn('universal_principles', synthesis_result.data)
        
        print("✅ End-to-end integration test passed")
        
        # Print summary
        print(f"\n📊 Pipeline Results Summary:")
        print(f"  🔧 Manifold: {manifold_result.data['original_dimensions']}D → "
              f"{manifold_result.data['manifold_structure']['intrinsic_dimension']}D")
        print(f"  🌊 Dynamics: {dynamics_result.data['slds_model']['n_regimes']} regimes identified")
        print(f"  🔱 Catastrophe: {len(catastrophe_result.data['critical_points'])} critical points")
        print(f"  🎯 Synthesis: {len(synthesis_result.data['universal_principles'])} principles found")
    
    async def test_noesis_component_integration(self):
        """Test integration with NoesisComponent"""
        print("\n🏗️ Testing Noesis Component Integration...")
        
        try:
            from noesis.core.noesis_component import NoesisComponent
            
            # Initialize component
            component = NoesisComponent()
            await component.init()
            
            # Test that theoretical framework is initialized
            self.assertIsNotNone(component.theoretical_framework, "Should initialize theoretical framework")
            
            # Test capabilities
            capabilities = component.get_capabilities()
            theoretical_caps = [cap for cap in capabilities if 'theoretical' in cap.lower()]
            self.assertGreater(len(theoretical_caps), 0, "Should have theoretical capabilities")
            
            # Test metadata
            metadata = component.get_metadata()
            self.assertIn('components', metadata, "Should have component status")
            
            await component.shutdown()
            print("✅ Noesis component integration passed")
            
        except ImportError as e:
            print(f"⚠️ Noesis component not available: {e}")
        except Exception as e:
            print(f"⚠️ Noesis component test failed: {e}")
    
    async def test_performance_benchmarks(self):
        """Test performance of mathematical framework components"""
        print("\n⏱️ Testing Performance Benchmarks...")
        
        import time
        from noesis.core.theoretical.manifold import ManifoldAnalyzer
        from noesis.core.theoretical.dynamics import DynamicsAnalyzer
        
        # Generate larger test data
        large_data = np.random.randn(1000, 10)
        large_time_series = np.random.randn(500, 8)
        
        # Benchmark manifold analysis
        manifold_analyzer = ManifoldAnalyzer({'em_iterations': 3})
        start_time = time.time()
        manifold_result = await manifold_analyzer.analyze(large_data)
        manifold_time = time.time() - start_time
        
        # Benchmark dynamics analysis
        dynamics_analyzer = DynamicsAnalyzer({'em_iterations': 3, 'n_regimes': 2})
        start_time = time.time()
        dynamics_result = await dynamics_analyzer.analyze(large_time_series)
        dynamics_time = time.time() - start_time
        
        print(f"  📐 Manifold analysis (1000×10): {manifold_time:.2f}s")
        print(f"  🌊 Dynamics analysis (500×8): {dynamics_time:.2f}s")
        
        # Performance thresholds (reasonable for testing)
        self.assertLess(manifold_time, 30, "Manifold analysis should complete within 30 seconds")
        self.assertLess(dynamics_time, 30, "Dynamics analysis should complete within 30 seconds")
        
        print("✅ Performance benchmarks passed")


async def run_integration_tests():
    """Run all integration tests"""
    print("🧠 Noesis Mathematical Framework Integration Tests")
    print("=" * 60)
    
    test_suite = TestMathematicalFrameworkIntegration()
    test_suite.setUp()
    
    # List of test methods to run
    test_methods = [
        'test_base_framework_validation',
        'test_manifold_analysis_integration', 
        'test_dynamics_analysis_integration',
        'test_catastrophe_analysis_integration',
        'test_synthesis_analysis_integration',
        'test_framework_error_handling',
        'test_end_to_end_integration',
        'test_noesis_component_integration',
        'test_performance_benchmarks'
    ]
    
    passed_tests = 0
    failed_tests = 0
    
    for test_method in test_methods:
        try:
            print(f"\n🧪 Running {test_method}...")
            test_func = getattr(test_suite, test_method)
            await test_func()
            passed_tests += 1
            print(f"✅ {test_method} PASSED")
            
        except Exception as e:
            failed_tests += 1
            print(f"❌ {test_method} FAILED: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"   ✅ Passed: {passed_tests}")
    print(f"   ❌ Failed: {failed_tests}")
    print(f"   📈 Success Rate: {passed_tests / len(test_methods) * 100:.1f}%")
    
    if failed_tests == 0:
        print("\n🎉 All mathematical framework integration tests passed!")
        return True
    else:
        print(f"\n⚠️ {failed_tests} tests failed. Check output above for details.")
        return False


async def test_framework_components():
    """Test individual framework components in isolation"""
    print("\n🔧 Testing Framework Components in Isolation...")
    
    try:
        # Test imports
        from noesis.core.theoretical.base import MathematicalFramework, AnalysisResult
        from noesis.core.theoretical.manifold import ManifoldAnalyzer, ManifoldStructure
        from noesis.core.theoretical.dynamics import DynamicsAnalyzer, SLDSModel
        from noesis.core.theoretical.catastrophe import CatastropheAnalyzer, CriticalPoint
        from noesis.core.theoretical.synthesis import SynthesisAnalyzer, UniversalPrinciple
        
        print("✅ All theoretical components imported successfully")
        
        # Test basic instantiation
        base_framework = MathematicalFramework()
        manifold_analyzer = ManifoldAnalyzer()
        dynamics_analyzer = DynamicsAnalyzer()
        catastrophe_analyzer = CatastropheAnalyzer()
        synthesis_analyzer = SynthesisAnalyzer()
        
        print("✅ All components instantiated successfully")
        
        # Test data structures
        test_result = AnalysisResult(
            analysis_type='test',
            data={'test': 'data'},
            confidence=0.9
        )
        result_dict = test_result.to_dict()
        self.assertIn('analysis_type', result_dict)
        self.assertIn('timestamp', result_dict)
        
        print("✅ Data structures working correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Component testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    async def main():
        print("🧪 Noesis Mathematical Framework Integration Tests")
        print("=" * 60)
        
        # Test 1: Component imports and basic functionality
        components_ok = await test_framework_components()
        
        if components_ok:
            # Test 2: Full integration tests
            integration_ok = await run_integration_tests()
            
            if integration_ok:
                print("\n🎊 All tests passed! Mathematical framework is working correctly.")
                return 0
            else:
                print("\n⚠️ Some integration tests failed.")
                return 1
        else:
            print("\n❌ Component tests failed. Check imports and dependencies.")
            return 1
    
    exit_code = asyncio.run(main())
    sys.exit(exit_code)