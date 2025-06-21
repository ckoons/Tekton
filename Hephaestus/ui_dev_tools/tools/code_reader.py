"""CodeReader Tool - Read component source files (the truth)"""
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from ..core.file_reader import ComponentReader
from ..core.models import ToolResult, ToolStatus, SemanticTagAnalysis

logger = logging.getLogger(__name__)


class CodeReader:
    """Read and understand component source files (the truth)"""
    
    def __init__(self, base_path: Optional[Path] = None):
        """Initialize with optional base path"""
        self.reader = ComponentReader(base_path)
        logger.info("CodeReader initialized")
    
    def read_component(self, component_name: str) -> ToolResult:
        """Read component HTML/CSS/JS and return structured data"""
        try:
            # Read component and analyze semantic tags
            component_info, analysis = self.reader.analyze_component(component_name)
            
            if not component_info.exists:
                return ToolResult(
                    tool_name="CodeReader",
                    status=ToolStatus.ERROR,
                    component=component_name,
                    error=component_info.error,
                    data={
                        "file_path": component_info.file_path,
                        "exists": False
                    }
                )
            
            # Build result data
            data = {
                "file_path": component_info.file_path,
                "exists": True,
                "content_size": len(component_info.content),
                "semantic_tags": self._format_semantic_tags(analysis) if analysis else None
            }
            
            # Add warnings if needed
            warnings = []
            if analysis and analysis.total_count == 0:
                warnings.append("No semantic tags found in component")
            
            return ToolResult(
                tool_name="CodeReader",
                status=ToolStatus.SUCCESS,
                component=component_name,
                data=data,
                warnings=warnings
            )
            
        except Exception as e:
            logger.error(f"Error reading component {component_name}: {e}")
            return ToolResult(
                tool_name="CodeReader",
                status=ToolStatus.ERROR,
                component=component_name,
                error=str(e)
            )
    
    def list_semantic_tags(self, component_name: str) -> ToolResult:
        """Extract and list all data-tekton-* attributes from a component"""
        try:
            component_info, analysis = self.reader.analyze_component(component_name)
            
            if not component_info.exists:
                return ToolResult(
                    tool_name="CodeReader",
                    status=ToolStatus.ERROR,
                    component=component_name,
                    error=component_info.error
                )
            
            if not analysis:
                return ToolResult(
                    tool_name="CodeReader",
                    status=ToolStatus.WARNING,
                    component=component_name,
                    warnings=["Could not analyze semantic tags"],
                    data={"semantic_tags": None}
                )
            
            # Format the semantic tags data
            data = {
                "semantic_tags": self._format_semantic_tags(analysis),
                "summary": {
                    "total_tags": analysis.total_count,
                    "unique_tag_types": len(analysis.get_tag_names()),
                    "tag_types": sorted(analysis.get_tag_names())
                }
            }
            
            return ToolResult(
                tool_name="CodeReader",
                status=ToolStatus.SUCCESS,
                component=component_name,
                data=data
            )
            
        except Exception as e:
            logger.error(f"Error listing semantic tags for {component_name}: {e}")
            return ToolResult(
                tool_name="CodeReader",
                status=ToolStatus.ERROR,
                component=component_name,
                error=str(e)
            )
    
    def get_component_structure(self, component_name: str) -> ToolResult:
        """Parse and return component HTML structure"""
        try:
            from bs4 import BeautifulSoup
            
            component_info = self.reader.read_component(component_name)
            
            if not component_info.exists:
                return ToolResult(
                    tool_name="CodeReader",
                    status=ToolStatus.ERROR,
                    component=component_name,
                    error=component_info.error
                )
            
            # Parse HTML structure
            soup = BeautifulSoup(component_info.content, 'html.parser')
            
            # Find the main component element
            component_element = soup.find(attrs={'data-tekton-component': component_name})
            
            if not component_element:
                # Try to find any element with data-tekton attributes
                for element in soup.find_all():
                    if any(attr.startswith('data-tekton-') for attr in element.attrs):
                        component_element = element
                        break
            
            structure = self._parse_element_structure(component_element if component_element else soup)
            
            data = {
                "structure": structure,
                "has_component_root": component_element is not None,
                "file_path": component_info.file_path
            }
            
            return ToolResult(
                tool_name="CodeReader",
                status=ToolStatus.SUCCESS,
                component=component_name,
                data=data
            )
            
        except Exception as e:
            logger.error(f"Error getting component structure for {component_name}: {e}")
            return ToolResult(
                tool_name="CodeReader",
                status=ToolStatus.ERROR,
                component=component_name,
                error=str(e)
            )
    
    def list_components(self) -> ToolResult:
        """List all available components"""
        try:
            components = self.reader.list_available_components()
            
            data = {
                "components": components,
                "count": len(components),
                "base_path": str(self.reader.base_path)
            }
            
            return ToolResult(
                tool_name="CodeReader",
                status=ToolStatus.SUCCESS,
                data=data
            )
            
        except Exception as e:
            logger.error(f"Error listing components: {e}")
            return ToolResult(
                tool_name="CodeReader",
                status=ToolStatus.ERROR,
                error=str(e)
            )
    
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
            "summary": analysis.tag_summary
        }
    
    def _parse_element_structure(self, element, max_depth: int = 3, current_depth: int = 0) -> Dict[str, Any]:
        """Parse element structure recursively (limited depth)"""
        if current_depth >= max_depth:
            return {"tag": "...", "truncated": True}
        
        from bs4 import NavigableString, Tag
        
        if isinstance(element, NavigableString):
            return {"text": str(element).strip()}
        
        if not isinstance(element, Tag):
            return {"type": str(type(element).__name__)}
        
        result = {
            "tag": element.name,
            "attributes": {}
        }
        
        # Extract semantic attributes
        for attr, value in element.attrs.items():
            if attr.startswith('data-tekton-'):
                result["attributes"][attr] = value
        
        # Add ID and class if present
        if element.get('id'):
            result["attributes"]["id"] = element.get('id')
        if element.get('class'):
            result["attributes"]["class"] = ' '.join(element.get('class'))
        
        # Get children (limited)
        children = []
        child_count = 0
        for child in element.children:
            if isinstance(child, Tag) and child_count < 5:  # Limit children
                children.append(self._parse_element_structure(child, max_depth, current_depth + 1))
                child_count += 1
            elif isinstance(child, NavigableString) and child.strip():
                text = child.strip()
                if text and len(text) < 50:  # Only short text
                    children.append({"text": text})
        
        if children:
            result["children"] = children
        
        return result