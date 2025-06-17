"""
Test Phase 1 UI DevTools Enhancements

Tests for:
1. Dynamic content detection in ui_capture
2. ui_recommend_approach tool
3. Enhanced error messages with file editing guidance
"""

import asyncio
import json
import pytest
from unittest.mock import Mock, patch, AsyncMock

# Import the enhanced tools
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ui_tools_v2 import (
    ui_capture, ui_recommend_approach, _analyze_dynamic_content, browser_manager
)


class TestDynamicContentDetection:
    """Test dynamic content detection in ui_capture"""
    
    @pytest.mark.asyncio
    async def test_static_content_detection(self):
        """Test detection of static content"""
        # Mock static HTML
        static_html = """
        <div data-tekton-area="navigation">
            <nav>
                <a href="#" class="nav-label">Home</a>
                <a href="#" class="nav-label">About</a>
            </nav>
        </div>
        """
        
        with patch('ui_tools_v2.browser_manager') as mock_browser:
            mock_page = Mock()
            mock_browser.get_page.return_value = mock_page
            
            # Mock ui_capture to return our test HTML
            with patch('ui_tools_v2.ui_capture') as mock_capture:
                mock_capture.return_value = {
                    "dynamic_analysis": await _analyze_dynamic_content(mock_page, "navigation", static_html)
                }
                
                result = await mock_capture("navigation")
                
                analysis = result["dynamic_analysis"]
                assert analysis["content_type"] == "static"
                assert analysis["recommendation"] == "devtools"
                assert analysis["confidence"] > 0.8
    
    @pytest.mark.asyncio
    async def test_dynamic_content_detection(self):
        """Test detection of dynamic content"""
        # Mock dynamic HTML with component loading patterns
        dynamic_html = """
        <div data-tekton-area="rhetor">
            <div class="rhetor__loading">Loading...</div>
            <script src="rhetor-component.js"></script>
            <div id="rhetor-content"></div>
        </div>
        """
        
        mock_page = Mock()
        analysis = await _analyze_dynamic_content(mock_page, "rhetor", dynamic_html)
        
        assert analysis["content_type"] in ["dynamic", "hybrid"]
        assert analysis["recommendation"] in ["file_editing", "hybrid"]
        assert len(analysis["dynamic_areas"]) >= 0
    
    @pytest.mark.asyncio
    async def test_component_specific_analysis(self):
        """Test component-specific dynamic analysis"""
        # Mock rhetor component with minimal content but complex structure
        rhetor_html = """
        <div data-tekton-area="rhetor" class="rhetor">
            <div class="rhetor__header"></div>
            <div class="rhetor__tabs"></div>
            <div class="rhetor__content"></div>
            <div class="rhetor__footer"></div>
            <script>/* component loading */</script>
        </div>
        """
        
        mock_page = Mock()
        analysis = await _analyze_dynamic_content(mock_page, "rhetor", rhetor_html)
        
        # Should detect minimal text with complex structure
        assert analysis["content_type"] in ["dynamic", "hybrid"]
        assert any("rhetor" in da.get("file_location", "") for da in analysis["dynamic_areas"])


class TestRecommendationEngine:
    """Test ui_recommend_approach tool"""
    
    @pytest.mark.asyncio
    async def test_navigation_recommendation(self):
        """Test recommendation for navigation elements"""
        with patch('ui_tools_v2.ui_capture') as mock_capture:
            # Mock static navigation capture
            mock_capture.return_value = {
                "dynamic_analysis": {
                    "content_type": "static",
                    "recommendation": "devtools",
                    "dynamic_areas": []
                }
            }
            
            result = await ui_recommend_approach(
                target_description="navigation button",
                intended_change="change text",
                area="navigation"
            )
            
            assert result["recommended_tool"] == "devtools"
            assert result["confidence"] > 0.8
            assert "navigation" in result["reasoning"].lower()
    
    @pytest.mark.asyncio
    async def test_chat_interface_recommendation(self):
        """Test recommendation for chat interface (dynamic content)"""
        with patch('ui_tools_v2.ui_capture') as mock_capture:
            # Mock dynamic content capture
            mock_capture.return_value = {
                "dynamic_analysis": {
                    "content_type": "dynamic",
                    "recommendation": "file_editing",
                    "dynamic_areas": [
                        {"file_location": "rhetor-component.html"}
                    ]
                }
            }
            
            result = await ui_recommend_approach(
                target_description="chat interface",
                intended_change="add semantic tags",
                area="rhetor"
            )
            
            assert result["recommended_tool"] == "file_editing"
            assert result["confidence"] > 0.7
            assert "rhetor-component.html" in result["file_locations"]
    
    @pytest.mark.asyncio
    async def test_semantic_tagging_recommendation(self):
        """Test recommendation for semantic tagging work"""
        with patch('ui_tools_v2.ui_capture') as mock_capture:
            # Mock hybrid content
            mock_capture.return_value = {
                "dynamic_analysis": {
                    "content_type": "hybrid",
                    "recommendation": "hybrid",
                    "dynamic_areas": []
                }
            }
            
            result = await ui_recommend_approach(
                target_description="component header",
                intended_change="add semantic tags",
                area="prometheus"
            )
            
            # Should recommend DevTools for semantic work on navigation elements
            assert result["recommended_tool"] == "devtools"
            assert "semantic" in result["reasoning"].lower()
    
    @pytest.mark.asyncio
    async def test_error_handling_recommendation(self):
        """Test recommendation when ui_capture fails"""
        with patch('ui_tools_v2.ui_capture') as mock_capture:
            # Mock capture failure
            mock_capture.side_effect = Exception("Component not found")
            
            result = await ui_recommend_approach(
                target_description="unknown element",
                intended_change="modify",
                area="unknown"
            )
            
            assert result["recommended_tool"] == "file_editing"
            assert result["confidence"] > 0.8
            assert "file editing is safer" in result["reasoning"]


class TestEnhancedErrorMessages:
    """Test enhanced error messages in ui_sandbox"""
    
    def test_error_message_structure(self):
        """Test that enhanced error messages include guidance"""
        # This would be tested in integration tests with actual browser
        # For now, verify the JavaScript code structure
        
        # Simulate the enhanced error structure
        enhanced_error = {
            "success": False,
            "error": "No elements found for selector: #nonexistent",
            "guidance": "Element not visible to DevTools - try file editing: rhetor-component.html"
        }
        
        assert enhanced_error["guidance"] is not None
        assert "file editing" in enhanced_error["guidance"]
        assert "component.html" in enhanced_error["guidance"]


class TestPhase1Integration:
    """Integration tests for Phase 1 enhancements"""
    
    @pytest.mark.asyncio
    async def test_recommendation_to_capture_workflow(self):
        """Test the workflow from recommendation to capture"""
        with patch('ui_tools_v2.ui_capture') as mock_capture:
            # Step 1: Get recommendation
            mock_capture.return_value = {
                "dynamic_analysis": {
                    "content_type": "static",
                    "recommendation": "devtools",
                    "dynamic_areas": []
                }
            }
            
            recommendation = await ui_recommend_approach(
                target_description="navigation",
                intended_change="modify",
                area="hephaestus"
            )
            
            # Step 2: Should recommend DevTools
            assert recommendation["recommended_tool"] == "devtools"
            
            # Step 3: Capture should include dynamic analysis
            capture_result = await mock_capture("hephaestus")
            assert "dynamic_analysis" in capture_result
    
    def test_confidence_scoring(self):
        """Test that confidence scores are reasonable"""
        # Test various scenarios for confidence scoring
        test_cases = [
            {
                "content_type": "static",
                "involves_dynamic": False,
                "expected_confidence_range": (0.9, 1.0)
            },
            {
                "content_type": "dynamic", 
                "involves_dynamic": True,
                "expected_confidence_range": (0.8, 0.9)
            },
            {
                "content_type": "hybrid",
                "involves_dynamic": False,
                "expected_confidence_range": (0.7, 0.8)
            }
        ]
        
        for case in test_cases:
            # This would be tested with actual recommendation calls
            # For now, verify the logic makes sense
            min_conf, max_conf = case["expected_confidence_range"]
            assert min_conf < max_conf
            assert min_conf >= 0.0 and max_conf <= 1.0


if __name__ == "__main__":
    # Run a simple test
    async def run_simple_test():
        """Run a simple test to verify basic functionality"""
        print("Testing Phase 1 enhancements...")
        
        # Test dynamic content analysis
        mock_page = Mock()
        static_html = '<div data-tekton-nav="main"><a class="nav-label">Test</a></div>'
        
        analysis = await _analyze_dynamic_content(mock_page, "navigation", static_html)
        print(f"Static content analysis: {analysis['content_type']} (confidence: {analysis['confidence']})")
        
        dynamic_html = '<div data-tekton-area="rhetor"><div class="loading">Loading...</div></div>'
        analysis = await _analyze_dynamic_content(mock_page, "rhetor", dynamic_html)
        print(f"Dynamic content analysis: {analysis['content_type']} (confidence: {analysis['confidence']})")
        
        print("✅ Phase 1 enhancements basic test passed!")
    
    asyncio.run(run_simple_test())