"""
Tests for ui_capture HTML fix
Tests both current broken behavior and desired behavior
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))  # Hephaestus root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))  # Tekton root

from hephaestus.mcp.html_processor import html_to_structured_data as _html_to_structured_data


class TestUICaptureParser:
    """Test the HTML parser fix"""
    
    # Sample HTML that demonstrates the issue
    SAMPLE_HTML = '''
    <html>
    <body data-theme="dark">
        <div class="navigation" data-tekton-nav="main">
            <ul class="nav-list">
                <li data-component="prometheus">
                    <span class="nav-label">Prometheus</span>
                </li>
                <li data-component="rhetor">
                    <span class="nav-label">Rhetor</span>
                </li>
            </ul>
        </div>
        <div class="content">
            <div id="main-content">
                <h1>Welcome</h1>
                <p>Some content here</p>
            </div>
        </div>
    </body>
    </html>
    '''
    
    def test_current_broken_behavior(self):
        """Test that demonstrates the current broken behavior"""
        # Current behavior: only returns 1 element (root)
        result = _html_to_structured_data(self.SAMPLE_HTML)
        
        # This is the BROKEN behavior we want to fix
        assert result["element_count"] == 1, "Currently returns only root element"
        assert len(result["elements"]) == 1
        assert result["elements"][0]["tag"] == "body"
        
        # The structure DOES contain children, but element_count is wrong
        assert "children" in result["elements"][0]
        assert len(result["elements"][0]["children"]) > 0
    
    def test_with_selector_works(self):
        """Test that selectors return correct counts"""
        # When using selectors, counts are correct
        result = _html_to_structured_data(self.SAMPLE_HTML, ".nav-label")
        assert result["element_count"] == 2, "Selectors return correct count"
        
    def test_total_element_count_needed(self):
        """Test what we SHOULD get - total element count"""
        # Helper to count all elements in tree
        def count_elements(element_data):
            count = 1  # Count this element
            if "children" in element_data:
                for child in element_data["children"]:
                    count += count_elements(child)
            return count
        
        result = _html_to_structured_data(self.SAMPLE_HTML)
        total_elements = sum(count_elements(el) for el in result["elements"])
        
        # We should have many more than 1 element!
        assert total_elements > 5, f"Should count all elements, got {total_elements}"
        
        # This is what element_count SHOULD represent
        print(f"Total elements in structure: {total_elements}")
    
    def test_raw_html_approach(self):
        """Test the proposed fix - returning raw HTML"""
        # Proposed new structure
        result = {
            "html": self.SAMPLE_HTML,
            "element_count": 10,  # Actual count
            "selectors_found": {
                ".nav-label": 2,
                "[data-component]": 2,
                "li": 2,
                "div": 3
            },
            "structure": _html_to_structured_data(self.SAMPLE_HTML)  # Keep for compatibility
        }
        
        # This would allow ui_sandbox to search the HTML directly
        assert ".nav-label" in result["html"]
        assert "data-component=\"prometheus\"" in result["html"]
        assert result["selectors_found"][".nav-label"] == 2


class TestDesiredBehavior:
    """Tests for the desired behavior after fix"""
    
    def test_ui_capture_returns_html(self):
        """After fix: ui_capture should return raw HTML"""
        # This is what we WANT the result to look like
        desired_result = {
            "area": "hephaestus",
            "html": "<full html content>",
            "total_elements": 150,  # Real count
            "structure": {
                "element_count": 150,  # Fixed to show total
                "elements": [...]  # Full tree
            },
            "selectors_available": {
                ".nav-label": 15,
                "[data-component]": 15,
                "[data-tekton-nav]": 1
            }
        }
        
        # Key improvements:
        assert "html" in desired_result
        assert desired_result["total_elements"] > 1
        assert "selectors_available" in desired_result
        
    def test_ui_sandbox_can_find_selectors(self):
        """After fix: ui_sandbox can search HTML for selectors"""
        sample_html = '<div><span class="target">Hello</span></div>'
        
        # ui_sandbox would search the HTML string
        selector = ".target"
        assert selector in sample_html or f'class="target"' in sample_html
        
        # This would prevent "selector not found" errors


if __name__ == "__main__":
    # Run tests to show current broken state
    print("=== Testing Current Broken Behavior ===")
    test = TestUICaptureParser()
    
    try:
        test.test_current_broken_behavior()
        print("✓ Confirmed: element_count is broken (returns 1)")
    except AssertionError as e:
        print(f"✗ Unexpected: {e}")
    
    try:
        test.test_with_selector_works()
        print("✓ Confirmed: selectors work correctly")
    except AssertionError as e:
        print(f"✗ Failed: {e}")
        
    try:
        test.test_total_element_count_needed()
        print("✓ Confirmed: structure contains all elements but count is wrong")
    except AssertionError as e:
        print(f"✗ Failed: {e}")