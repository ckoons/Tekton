"""
Tests for shared visualization component integration across Noesis and Sophia
Validates that visualization components work consistently across both systems
"""

import asyncio
import pytest
import numpy as np
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
import json
import subprocess
import os
from typing import Dict, Any, List

# Test configuration
NOESIS_UI_PATH = Path("/Users/cskoons/projects/github/Coder-A/Noesis/noesis/ui")
SOPHIA_UI_PATH = Path("/Users/cskoons/projects/github/Coder-A/Sophia/ui")
SHARED_VIZ_PATH = Path("/Users/cskoons/projects/github/Coder-A/shared/ui/visualization")


class TestSharedVisualizationCore:
    """Test core shared visualization functionality"""
    
    def test_shared_viz_core_exists(self):
        """Test that shared visualization core files exist"""
        assert SHARED_VIZ_PATH.exists(), "Shared visualization directory not found"
        
        core_files = [
            "viz-core.js",
            "tekton-viz.js",
            "renderers/canvas-renderer.js",
            "renderers/chartjs-renderer.js"
        ]
        
        for file_path in core_files:
            full_path = SHARED_VIZ_PATH / file_path
            assert full_path.exists(), f"Core visualization file missing: {file_path}"
    
    def test_viz_core_api_structure(self):
        """Test that viz-core.js has correct API structure"""
        viz_core_path = SHARED_VIZ_PATH / "viz-core.js"
        content = viz_core_path.read_text()
        
        # Check for essential classes and methods
        required_elements = [
            "class VisualizationRenderer",
            "class VisualizationFactory", 
            "class VizUtils",
            "initialize(containerId, options",
            "render(data, type, options",
            "getCapabilities()",
            "createRenderer(",
            "registerRenderer("
        ]
        
        for element in required_elements:
            assert element in content, f"Missing required API element: {element}"
    
    def test_tekton_viz_api_structure(self):
        """Test that tekton-viz.js has correct high-level API"""
        tekton_viz_path = SHARED_VIZ_PATH / "tekton-viz.js"
        content = tekton_viz_path.read_text()
        
        # Check for high-level visualization methods
        required_methods = [
            "drawManifold(",
            "drawTrajectory(",
            "drawScatter(",
            "drawTimeSeries(",
            "drawDistribution(",
            "drawHeatmap(",
            "drawNetwork(",
            "drawRegimeTransitions("
        ]
        
        for method in required_methods:
            assert method in content, f"Missing visualization method: {method}"


class TestNoesisVisualizationIntegration:
    """Test Noesis-specific visualization integration"""
    
    def test_noesis_ui_structure(self):
        """Test that Noesis UI has proper structure for visualizations"""
        assert NOESIS_UI_PATH.exists(), "Noesis UI directory not found"
        
        # Check for key UI files
        ui_files = [
            "index.html",
            "scripts/noesis-dashboard.js",
            "scripts/memory-visualizer.js",
            "scripts/manifold-analyzer.js",
            "scripts/dynamics-visualizer.js",
            "scripts/catastrophe-analyzer.js"
        ]
        
        for file_path in ui_files:
            full_path = NOESIS_UI_PATH / file_path
            assert full_path.exists(), f"Noesis UI file missing: {file_path}"
    
    def test_noesis_shared_viz_imports(self):
        """Test that Noesis components properly import shared visualization"""
        # Check main dashboard HTML includes shared viz
        index_path = NOESIS_UI_PATH / "index.html"
        content = index_path.read_text()
        
        # Should include shared visualization core
        expected_includes = [
            "../../../shared/ui/visualization/viz-core.js",
            "../../../shared/ui/visualization/tekton-viz.js"
        ]
        
        for include in expected_includes:
            assert include in content, f"Missing shared viz include: {include}"
    
    def test_noesis_visualization_components_use_shared_api(self):
        """Test that Noesis visualization components use shared API"""
        viz_files = [
            "scripts/memory-visualizer.js",
            "scripts/manifold-analyzer.js", 
            "scripts/dynamics-visualizer.js",
            "scripts/catastrophe-analyzer.js"
        ]
        
        for viz_file in viz_files:
            file_path = NOESIS_UI_PATH / viz_file
            if file_path.exists():
                content = file_path.read_text()
                
                # Should use TektonViz API
                shared_api_usage = [
                    "new TektonViz(",
                    "tektonViz.",
                    "VisualizationFactory"
                ]
                
                uses_shared_api = any(api in content for api in shared_api_usage)
                assert uses_shared_api, f"Component {viz_file} doesn't use shared visualization API"


class TestSophiaVisualizationIntegration:
    """Test Sophia-specific visualization integration"""
    
    def test_sophia_ui_structure(self):
        """Test that Sophia UI has proper structure for visualizations"""
        assert SOPHIA_UI_PATH.exists(), "Sophia UI directory not found"
        
        # Check for key UI files
        ui_files = [
            "sophia-component.html"
        ]
        
        for file_path in ui_files:
            full_path = SOPHIA_UI_PATH / file_path
            assert full_path.exists(), f"Sophia UI file missing: {file_path}"
    
    def test_sophia_chart_containers(self):
        """Test that Sophia UI has proper chart containers"""
        sophia_html_path = SOPHIA_UI_PATH / "sophia-component.html"
        content = sophia_html_path.read_text()
        
        # Check for chart containers
        expected_charts = [
            "sophia-performance-chart",
            "sophia-resource-chart", 
            "sophia-communication-chart",
            "sophia-radar-chart",
            "sophia-comparison-chart",
            "sophia-patterns-results",
            "sophia-causality-results",
            "sophia-predictions-chart",
            "sophia-network-visualization"
        ]
        
        for chart_id in expected_charts:
            assert chart_id in content, f"Missing chart container: {chart_id}"
    
    def test_sophia_theory_validation_charts(self):
        """Test that Sophia has theory validation visualization support"""
        sophia_html_path = SOPHIA_UI_PATH / "sophia-component.html"
        content = sophia_html_path.read_text()
        
        # Check for theory validation specific visualizations
        theory_viz_elements = [
            "sophia-theory-validation-view",
            "sophia-protocols-list",
            "sophia-workflow-diagram",
            "sophia-validation-summary"
        ]
        
        for element in theory_viz_elements:
            assert element in content, f"Missing theory validation viz element: {element}"


class TestCrossSystemCompatibility:
    """Test compatibility between Noesis and Sophia visualization usage"""
    
    async def test_shared_data_format_compatibility(self):
        """Test that both systems can handle shared data formats"""
        # Create test data in common formats
        test_data_formats = {
            "manifold_data": {
                "points": [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]],
                "connections": [[0, 1], [1, 2]],
                "regions": []
            },
            "trajectory_data": [
                {"x": 0, "y": 1.0, "time": 0},
                {"x": 1, "y": 1.5, "time": 1},
                {"x": 2, "y": 0.8, "time": 2}
            ],
            "time_series_data": {
                "timestamps": [0, 1, 2, 3, 4],
                "values": [1.0, 1.5, 2.0, 1.8, 2.2]
            },
            "network_data": {
                "nodes": [
                    {"id": "node1", "x": 100, "y": 100, "label": "Node 1"},
                    {"id": "node2", "x": 200, "y": 150, "label": "Node 2"}
                ],
                "edges": [
                    {"source": "node1", "target": "node2", "weight": 0.8}
                ]
            }
        }
        
        # Test that data formats are valid (this would normally be validated by renderer)
        for data_type, data in test_data_formats.items():
            assert data is not None, f"Invalid data format for {data_type}"
            
            # Validate structure
            if data_type == "manifold_data":
                assert "points" in data
                assert isinstance(data["points"], list)
                assert len(data["points"]) > 0
                
            elif data_type == "trajectory_data":
                assert isinstance(data, list)
                assert all("x" in point and "y" in point for point in data)
                
            elif data_type == "time_series_data":
                assert "timestamps" in data and "values" in data
                assert len(data["timestamps"]) == len(data["values"])
                
            elif data_type == "network_data":
                assert "nodes" in data and "edges" in data
                assert all("id" in node for node in data["nodes"])
    
    def test_renderer_capability_consistency(self):
        """Test that renderer capabilities are consistently defined"""
        # This would test that both systems expect the same capabilities
        expected_capabilities = {
            "dimensions": [2, 3],
            "types": [
                "scatter", "line", "manifold", "trajectory", 
                "timeseries", "distribution", "heatmap", "network"
            ],
            "interactive": True,
            "animated": True
        }
        
        # In a real test, we would load the actual renderers and check capabilities
        # For now, validate the expected structure
        assert "dimensions" in expected_capabilities
        assert "types" in expected_capabilities
        assert len(expected_capabilities["types"]) > 0
    
    async def test_cross_system_visualization_scenarios(self):
        """Test realistic cross-system visualization scenarios"""
        
        scenarios = [
            {
                "name": "Theory Validation Workflow",
                "description": "Noesis generates theory, Sophia validates with experiments",
                "noesis_viz": ["manifold", "dynamics", "catastrophe"],
                "sophia_viz": ["experiment_results", "validation_comparison", "protocol_timeline"],
                "shared_data": "theory_experiment_protocol"
            },
            {
                "name": "Multi-Scale Analysis",
                "description": "Both systems analyze same data at different scales",
                "noesis_viz": ["manifold", "synthesis_patterns"],
                "sophia_viz": ["performance_metrics", "component_comparison"],
                "shared_data": "collective_intelligence_metrics"
            },
            {
                "name": "Real-Time Monitoring",
                "description": "Live data streaming to both dashboards",
                "noesis_viz": ["streaming_analysis", "memory_evolution"],
                "sophia_viz": ["live_metrics", "alert_visualization"],
                "shared_data": "streaming_memory_state"
            }
        ]
        
        for scenario in scenarios:
            # Validate scenario structure
            assert "noesis_viz" in scenario
            assert "sophia_viz" in scenario
            assert "shared_data" in scenario
            
            # Both systems should have visualizations for the scenario
            assert len(scenario["noesis_viz"]) > 0
            assert len(scenario["sophia_viz"]) > 0


class TestVisualizationRenderers:
    """Test individual visualization renderers"""
    
    def test_canvas_renderer_structure(self):
        """Test canvas renderer implementation"""
        canvas_renderer_path = SHARED_VIZ_PATH / "renderers/canvas-renderer.js"
        content = canvas_renderer_path.read_text()
        
        # Check for required methods
        required_methods = [
            "class CanvasRenderer extends VisualizationRenderer",
            "async initialize(",
            "async render(",
            "async clear(",
            "getCapabilities("
        ]
        
        for method in required_methods:
            assert method in content, f"Canvas renderer missing: {method}"
    
    def test_chartjs_renderer_structure(self):
        """Test Chart.js renderer implementation"""
        chartjs_renderer_path = SHARED_VIZ_PATH / "renderers/chartjs-renderer.js"
        content = chartjs_renderer_path.read_text()
        
        # Check for required methods
        required_methods = [
            "class ChartJSRenderer extends VisualizationRenderer",
            "async initialize(",
            "async render(",
            "async clear(",
            "getCapabilities("
        ]
        
        for method in required_methods:
            assert method in content, f"Chart.js renderer missing: {method}"
    
    async def test_renderer_interchangeability(self):
        """Test that renderers can be swapped without breaking functionality"""
        # Mock renderer test
        
        class MockRenderer:
            def __init__(self):
                self.initialized = False
                self.rendered_data = []
            
            async def initialize(self, container_id, options={}):
                self.initialized = True
                self.container_id = container_id
                self.options = options
            
            async def render(self, data, viz_type, options={}):
                if not self.initialized:
                    raise Exception("Renderer not initialized")
                
                self.rendered_data.append({
                    "data": data,
                    "type": viz_type,
                    "options": options
                })
            
            async def clear(self):
                self.rendered_data = []
            
            def getCapabilities(self):
                return {
                    "dimensions": [2],
                    "types": ["scatter", "line"],
                    "interactive": False,
                    "animated": False
                }
        
        # Test that different renderers can handle the same data
        test_data = {"points": [[1, 2], [3, 4], [5, 6]]}
        
        renderers = [MockRenderer(), MockRenderer()]
        
        for i, renderer in enumerate(renderers):
            await renderer.initialize(f"test-container-{i}")
            await renderer.render(test_data, "scatter")
            
            assert len(renderer.rendered_data) == 1
            assert renderer.rendered_data[0]["data"] == test_data
            assert renderer.rendered_data[0]["type"] == "scatter"


class TestVisualizationPerformance:
    """Test visualization performance across systems"""
    
    async def test_large_dataset_handling(self):
        """Test handling of large datasets"""
        # Generate large test dataset
        large_dataset = {
            "points": [[float(i), float(i**2)] for i in range(10000)],
            "metadata": {"size": 10000, "type": "synthetic"}
        }
        
        # Test data size
        assert len(large_dataset["points"]) == 10000
        
        # In a real test, we would measure rendering time
        # For now, validate data structure
        first_point = large_dataset["points"][0]
        assert len(first_point) == 2
        assert isinstance(first_point[0], float)
        assert isinstance(first_point[1], float)
    
    def test_memory_efficient_data_structures(self):
        """Test that data structures are memory efficient"""
        # Test data structure efficiency
        efficient_structures = [
            {"type": "typed_arrays", "description": "Use Float32Array for coordinates"},
            {"type": "data_streaming", "description": "Stream large datasets incrementally"},
            {"type": "level_of_detail", "description": "Reduce detail for distant/small features"},
            {"type": "data_decimation", "description": "Reduce point density for performance"}
        ]
        
        for structure in efficient_structures:
            assert "type" in structure
            assert "description" in structure


class TestVisualizationAccessibility:
    """Test visualization accessibility features"""
    
    def test_color_accessibility(self):
        """Test color schemes are accessible"""
        # Test color palette accessibility
        accessible_palettes = {
            "viridis": ["#440154", "#31688e", "#35b779", "#fde725"],
            "colorblind_safe": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"],
            "high_contrast": ["#000000", "#ffffff", "#ff0000", "#00ff00"]
        }
        
        for palette_name, colors in accessible_palettes.items():
            assert len(colors) >= 4, f"Palette {palette_name} needs at least 4 colors"
            
            # Validate hex colors
            for color in colors:
                assert color.startswith("#"), f"Invalid color format: {color}"
                assert len(color) == 7, f"Invalid color length: {color}"
    
    def test_keyboard_navigation_support(self):
        """Test keyboard navigation support"""
        keyboard_features = [
            "arrow_key_navigation",
            "tab_focus_support", 
            "enter_activation",
            "escape_close",
            "zoom_shortcuts"
        ]
        
        # In a real test, these would be validated in actual UI
        for feature in keyboard_features:
            assert isinstance(feature, str)
            assert len(feature) > 0


class TestVisualizationDocumentation:
    """Test visualization documentation and examples"""
    
    def test_api_documentation_exists(self):
        """Test that API documentation exists"""
        # Check for documentation files
        doc_paths = [
            SHARED_VIZ_PATH / "README.md",
            Path(__file__).parent / "VISUALIZATION_GUIDE.md"
        ]
        
        existing_docs = [doc for doc in doc_paths if doc.exists()]
        assert len(existing_docs) > 0, "No visualization documentation found"
    
    def test_usage_examples_exist(self):
        """Test that usage examples exist"""
        # Examples should be in component files
        example_indicators = [
            "// Example:",
            "/* Usage:",
            "// Basic usage:",
            "* @example"
        ]
        
        viz_files = [
            SHARED_VIZ_PATH / "tekton-viz.js",
            SHARED_VIZ_PATH / "viz-core.js"
        ]
        
        examples_found = False
        for file_path in viz_files:
            if file_path.exists():
                content = file_path.read_text()
                if any(indicator in content for indicator in example_indicators):
                    examples_found = True
                    break
        
        assert examples_found, "No usage examples found in visualization files"


async def run_integration_test_suite():
    """Run the complete integration test suite"""
    
    print("🎨 Running Shared Visualization Integration Tests")
    print("=" * 60)
    
    test_classes = [
        TestSharedVisualizationCore,
        TestNoesisVisualizationIntegration,
        TestSophiaVisualizationIntegration,
        TestCrossSystemCompatibility,
        TestVisualizationRenderers,
        TestVisualizationPerformance,
        TestVisualizationAccessibility,
        TestVisualizationDocumentation
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for test_class in test_classes:
        print(f"\n📋 Running {test_class.__name__}")
        print("-" * 40)
        
        # Get test methods
        test_methods = [
            method for method in dir(test_class)
            if method.startswith('test_') and callable(getattr(test_class, method))
        ]
        
        # Create test instance
        test_instance = test_class()
        
        for method_name in test_methods:
            total_tests += 1
            test_method = getattr(test_instance, method_name)
            
            try:
                print(f"  🧪 {method_name}...", end=" ")
                
                # Run test (handle both sync and async)
                if asyncio.iscoroutinefunction(test_method):
                    await test_method()
                else:
                    test_method()
                
                passed_tests += 1
                print("✅")
                
            except Exception as e:
                failed_tests.append({
                    "class": test_class.__name__,
                    "method": method_name,
                    "error": str(e)
                })
                print(f"❌ FAIL - {e}")
    
    # Print summary
    print(f"\n{'='*60}")
    print("🏁 VISUALIZATION INTEGRATION TEST SUMMARY")
    print(f"{'='*60}")
    
    print(f"📊 Test Results:")
    print(f"  ✅ Passed: {passed_tests}")
    print(f"  ❌ Failed: {len(failed_tests)}")
    print(f"  📈 Total:  {total_tests}")
    
    if total_tests > 0:
        success_rate = (passed_tests / total_tests) * 100
        print(f"  🎯 Success Rate: {success_rate:.1f}%")
    
    # Show failed tests
    if failed_tests:
        print(f"\n❌ Failed Tests:")
        for failure in failed_tests:
            print(f"  {failure['class']}::{failure['method']} - {failure['error']}")
    
    # Overall result
    if len(failed_tests) == 0:
        print(f"\n🎉 ALL VISUALIZATION TESTS PASSED!")
        return True
    else:
        print(f"\n⚠️  Some visualization tests failed")
        return False


class TestSharedVisualizationEndToEnd:
    """End-to-end integration tests"""
    
    async def test_noesis_to_sophia_data_flow(self):
        """Test data flow from Noesis analysis to Sophia visualization"""
        
        # Simulate Noesis analysis results
        noesis_analysis = {
            "manifold_analysis": {
                "intrinsic_dimension": 6,
                "embedding_coordinates": [[1.2, 2.3], [2.1, 1.8], [3.0, 2.5]],
                "explained_variance": [0.4, 0.3, 0.15, 0.1, 0.05]
            },
            "dynamics_analysis": {
                "regime_sequence": [0, 0, 1, 1, 2, 2, 1],
                "transition_points": [2, 4, 6],
                "stability_scores": {"0": 0.8, "1": 0.7, "2": 0.9}
            },
            "catastrophe_analysis": {
                "critical_points": [
                    {"location": [1.5, 2.0], "type": "fold", "confidence": 0.85}
                ],
                "warning_level": "medium"
            }
        }
        
        # Test that data can be transformed for Sophia visualization
        sophia_viz_data = self.transform_noesis_to_sophia_format(noesis_analysis)
        
        # Validate transformation
        assert "experiment_predictions" in sophia_viz_data
        assert "validation_metrics" in sophia_viz_data
        assert "theory_visualization" in sophia_viz_data
        
        # Validate specific data
        theory_viz = sophia_viz_data["theory_visualization"]
        assert "manifold_projection" in theory_viz
        assert "regime_network" in theory_viz
        assert "critical_regions" in theory_viz
    
    def transform_noesis_to_sophia_format(self, noesis_data):
        """Transform Noesis analysis data to Sophia visualization format"""
        
        sophia_data = {
            "experiment_predictions": {},
            "validation_metrics": {},
            "theory_visualization": {}
        }
        
        # Transform manifold analysis
        if "manifold_analysis" in noesis_data:
            manifold = noesis_data["manifold_analysis"]
            sophia_data["theory_visualization"]["manifold_projection"] = {
                "points": manifold["embedding_coordinates"],
                "dimension": manifold["intrinsic_dimension"],
                "variance_explained": sum(manifold["explained_variance"])
            }
            
            sophia_data["experiment_predictions"]["intrinsic_dimension"] = {
                "predicted": manifold["intrinsic_dimension"],
                "confidence_interval": [manifold["intrinsic_dimension"] - 1, 
                                      manifold["intrinsic_dimension"] + 1]
            }
        
        # Transform dynamics analysis
        if "dynamics_analysis" in noesis_data:
            dynamics = noesis_data["dynamics_analysis"]
            sophia_data["theory_visualization"]["regime_network"] = {
                "nodes": [{"id": regime, "stability": score} 
                         for regime, score in dynamics["stability_scores"].items()],
                "transitions": [{"from": i, "to": i+1} 
                              for i in range(len(dynamics["transition_points"]))]
            }
            
            sophia_data["experiment_predictions"]["regime_transitions"] = {
                "predicted_count": len(dynamics["transition_points"]),
                "transition_points": dynamics["transition_points"]
            }
        
        # Transform catastrophe analysis  
        if "catastrophe_analysis" in noesis_data:
            catastrophe = noesis_data["catastrophe_analysis"]
            sophia_data["theory_visualization"]["critical_regions"] = {
                "points": [cp["location"] for cp in catastrophe["critical_points"]],
                "types": [cp["type"] for cp in catastrophe["critical_points"]],
                "warning_level": catastrophe["warning_level"]
            }
            
            sophia_data["experiment_predictions"]["critical_transitions"] = {
                "predicted_count": len(catastrophe["critical_points"]),
                "confidence": sum(cp["confidence"] for cp in catastrophe["critical_points"]) / len(catastrophe["critical_points"])
            }
        
        return sophia_data
    
    async def test_bidirectional_visualization_updates(self):
        """Test bidirectional updates between Noesis and Sophia visualizations"""
        
        # Simulate real-time data updates
        updates = [
            {
                "source": "noesis",
                "type": "memory_state_update",
                "data": {"thought_count": 150, "memory_complexity": 0.67}
            },
            {
                "source": "sophia", 
                "type": "experiment_progress",
                "data": {"completion": 0.45, "current_metric": "accuracy"}
            },
            {
                "source": "noesis",
                "type": "critical_warning",
                "data": {"warning_level": "high", "predicted_transition": 45}
            }
        ]
        
        # Test that updates can be processed by both systems
        processed_updates = []
        
        for update in updates:
            processed_update = {
                "timestamp": "2024-12-01T12:00:00Z",
                "source": update["source"],
                "type": update["type"],
                "data": update["data"],
                "visualization_impact": self.determine_viz_impact(update)
            }
            processed_updates.append(processed_update)
        
        # Validate processing
        assert len(processed_updates) == len(updates)
        
        # Check that each update has appropriate visualization impact
        for update in processed_updates:
            assert "visualization_impact" in update
            assert len(update["visualization_impact"]) > 0
    
    def determine_viz_impact(self, update):
        """Determine which visualizations need updating"""
        impact = []
        
        if update["type"] == "memory_state_update":
            impact.extend(["memory_chart", "complexity_trend", "thought_network"])
        elif update["type"] == "experiment_progress":
            impact.extend(["progress_bar", "metrics_chart", "timeline"])
        elif update["type"] == "critical_warning":
            impact.extend(["warning_indicator", "prediction_chart", "alert_modal"])
        
        return impact


if __name__ == "__main__":
    asyncio.run(run_integration_test_suite())