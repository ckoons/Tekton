"""BrowserVerifier Tool - Check what's actually in the browser DOM"""
import asyncio
import logging
from typing import Dict, Any, List, Optional

from ..core.browser import BrowserManager
from ..core.models import ToolResult, ToolStatus, SemanticTag, SemanticTagAnalysis

logger = logging.getLogger(__name__)


class BrowserVerifier:
    """Check what's actually in the browser DOM"""
    
    def __init__(self):
        """Initialize with browser manager"""
        self.browser = BrowserManager()
        logger.info("BrowserVerifier initialized")
    
    async def verify_component_loaded(self, component_name: str) -> ToolResult:
        """Check if component is loaded in DOM"""
        try:
            # Navigate to component
            success = await self.browser.navigate_to_component(component_name)
            
            if not success:
                return ToolResult(
                    tool_name="BrowserVerifier",
                    status=ToolStatus.ERROR,
                    component=component_name,
                    error="Failed to navigate to component",
                    data={"loaded": False}
                )
            
            # Check if component exists in DOM
            component_selector = f'[data-tekton-component="{component_name}"]'
            exists = await self.browser.wait_for_selector(component_selector, timeout=5000)
            
            data = {
                "loaded": exists,
                "url": await self.browser.get_current_url()
            }
            
            if exists:
                # Get component info
                script = f"""
                () => {{
                    const element = document.querySelector('[data-tekton-component="{component_name}"]');
                    if (!element) return null;
                    return {{
                        tagName: element.tagName.toLowerCase(),
                        id: element.id || null,
                        className: element.className || null,
                        hasChildren: element.children.length > 0
                    }};
                }}
                """
                component_info = await self.browser.evaluate_script(script)
                if component_info:
                    data["component_info"] = component_info
            
            return ToolResult(
                tool_name="BrowserVerifier",
                status=ToolStatus.SUCCESS if exists else ToolStatus.WARNING,
                component=component_name,
                data=data,
                warnings=[] if exists else ["Component not found in DOM"]
            )
            
        except Exception as e:
            logger.error(f"Error verifying component {component_name}: {e}")
            return ToolResult(
                tool_name="BrowserVerifier",
                status=ToolStatus.ERROR,
                component=component_name,
                error=str(e)
            )
    
    async def get_dom_semantic_tags(self, component_name: str) -> ToolResult:
        """Extract semantic tags from DOM for a component"""
        try:
            # First verify component is loaded
            verify_result = await self.verify_component_loaded(component_name)
            
            if verify_result.status == ToolStatus.ERROR:
                return verify_result
            
            if not verify_result.data.get("loaded", False):
                return ToolResult(
                    tool_name="BrowserVerifier",
                    status=ToolStatus.WARNING,
                    component=component_name,
                    data={"semantic_tags": None},
                    warnings=["Component not loaded in DOM"]
                )
            
            # Find all semantic tags in DOM
            dom_elements = await self.browser.find_elements_with_semantic_tags()
            
            # Create semantic tag analysis
            analysis = SemanticTagAnalysis(
                component_name=component_name,
                source="browser"
            )
            
            # Process DOM elements
            component_tags_found = False
            for element in dom_elements:
                # Check if this element belongs to the component
                if 'component' in element['attributes'] and element['attributes']['component'] == component_name:
                    component_tags_found = True
                
                # Add all semantic tags from this element
                for tag_name, tag_value in element['attributes'].items():
                    tag = SemanticTag(
                        name=tag_name,
                        value=tag_value,
                        element=element['tagName'],
                        attributes={
                            'id': element.get('id'),
                            'class': element.get('className')
                        }
                    )
                    analysis.add_tag(tag)
            
            # Build result
            data = {
                "semantic_tags": self._format_semantic_tags(analysis),
                "total_elements_with_tags": len(dom_elements),
                "component_specific_tags_found": component_tags_found
            }
            
            warnings = []
            if analysis.total_count == 0:
                warnings.append("No semantic tags found in DOM")
            elif not component_tags_found:
                warnings.append(f"No tags specifically for component '{component_name}' found")
            
            return ToolResult(
                tool_name="BrowserVerifier",
                status=ToolStatus.SUCCESS,
                component=component_name,
                data=data,
                warnings=warnings
            )
            
        except Exception as e:
            logger.error(f"Error getting DOM semantic tags for {component_name}: {e}")
            return ToolResult(
                tool_name="BrowserVerifier",
                status=ToolStatus.ERROR,
                component=component_name,
                error=str(e)
            )
    
    async def capture_dom_state(self, component_name: str) -> ToolResult:
        """Capture current DOM structure for component"""
        try:
            # Verify component is loaded
            verify_result = await self.verify_component_loaded(component_name)
            
            if verify_result.status == ToolStatus.ERROR:
                return verify_result
            
            if not verify_result.data.get("loaded", False):
                return ToolResult(
                    tool_name="BrowserVerifier",
                    status=ToolStatus.WARNING,
                    component=component_name,
                    data={"dom_structure": None},
                    warnings=["Component not loaded in DOM"]
                )
            
            # Get component DOM structure
            script = f"""
            () => {{
                const component = document.querySelector('[data-tekton-component="{component_name}"]');
                if (!component) return null;
                
                function getStructure(element, depth = 0, maxDepth = 3) {{
                    if (depth >= maxDepth) {{
                        return {{ tag: '...', truncated: true }};
                    }}
                    
                    const result = {{
                        tag: element.tagName.toLowerCase(),
                        attributes: {{}}
                    }};
                    
                    // Get semantic attributes
                    for (let i = 0; i < element.attributes.length; i++) {{
                        const attr = element.attributes[i];
                        if (attr.name.startsWith('data-tekton-')) {{
                            result.attributes[attr.name] = attr.value;
                        }}
                    }}
                    
                    // Add id and class if present
                    if (element.id) result.attributes.id = element.id;
                    if (element.className) result.attributes.class = element.className;
                    
                    // Get children (limited)
                    const children = [];
                    for (let i = 0; i < Math.min(element.children.length, 5); i++) {{
                        children.push(getStructure(element.children[i], depth + 1, maxDepth));
                    }}
                    
                    if (children.length > 0) {{
                        result.children = children;
                    }}
                    
                    return result;
                }}
                
                return getStructure(component);
            }}
            """
            
            dom_structure = await self.browser.evaluate_script(script)
            
            # Also get a count of all elements in the component
            count_script = f"""
            () => {{
                const component = document.querySelector('[data-tekton-component="{component_name}"]');
                if (!component) return 0;
                return component.querySelectorAll('*').length;
            }}
            """
            element_count = await self.browser.evaluate_script(count_script)
            
            data = {
                "dom_structure": dom_structure,
                "element_count": element_count,
                "captured": dom_structure is not None
            }
            
            return ToolResult(
                tool_name="BrowserVerifier",
                status=ToolStatus.SUCCESS,
                component=component_name,
                data=data
            )
            
        except Exception as e:
            logger.error(f"Error capturing DOM state for {component_name}: {e}")
            return ToolResult(
                tool_name="BrowserVerifier",
                status=ToolStatus.ERROR,
                component=component_name,
                error=str(e)
            )
    
    async def cleanup(self) -> None:
        """Clean up browser resources"""
        await self.browser.cleanup()
    
    def _format_semantic_tags(self, analysis: SemanticTagAnalysis) -> Dict[str, Any]:
        """Format semantic tag analysis for output"""
        # Group tags by name
        tags_by_name = {}
        for tag in analysis.tags:
            if tag.name not in tags_by_name:
                tags_by_name[tag.name] = []
            tags_by_name[tag.name].append({
                "value": tag.value,
                "element": tag.element,
                "full_name": tag.full_name
            })
        
        return {
            "total_count": analysis.total_count,
            "by_name": tags_by_name,
            "summary": analysis.tag_summary,
            "found": sorted(analysis.get_tag_names()),
            "count_by_type": {name: len(values) for name, values in analysis.tag_summary.items()}
        }