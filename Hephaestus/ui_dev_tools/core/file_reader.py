"""File reading utilities for UI DevTools - The Source of Truth"""
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup, Tag
import logging

from .models import ComponentInfo, SemanticTag, SemanticTagAnalysis

logger = logging.getLogger(__name__)


class ComponentReader:
    """Read component source files - the source of truth"""
    
    def __init__(self, base_path: Optional[Path] = None):
        """Initialize with base path for components"""
        if base_path is None:
            # Default to ui/components relative to Hephaestus root
            hephaestus_root = Path(__file__).parent.parent.parent
            self.base_path = hephaestus_root / "ui" / "components"
        else:
            self.base_path = Path(base_path)
        
        logger.info(f"ComponentReader initialized with base path: {self.base_path}")
    
    def get_component_path(self, component_name: str) -> Path:
        """Get the path to a component's HTML file"""
        # Pattern: ui/components/{component_name}/{component_name}-component.html
        return self.base_path / component_name / f"{component_name}-component.html"
    
    def read_component(self, component_name: str) -> ComponentInfo:
        """Read a component's HTML file"""
        file_path = self.get_component_path(component_name)
        
        try:
            if not file_path.exists():
                logger.warning(f"Component file not found: {file_path}")
                return ComponentInfo(
                    name=component_name,
                    file_path=str(file_path),
                    exists=False,
                    error=f"Component file not found: {file_path}"
                )
            
            content = file_path.read_text(encoding='utf-8')
            logger.info(f"Successfully read component {component_name} ({len(content)} bytes)")
            
            return ComponentInfo(
                name=component_name,
                file_path=str(file_path),
                exists=True,
                content=content
            )
            
        except Exception as e:
            logger.error(f"Error reading component {component_name}: {e}")
            return ComponentInfo(
                name=component_name,
                file_path=str(file_path),
                exists=file_path.exists(),
                error=str(e)
            )
    
    def extract_semantic_tags(self, html_content: str) -> SemanticTagAnalysis:
        """Extract all data-tekton-* attributes from HTML content"""
        analysis = SemanticTagAnalysis(
            component_name="",  # Will be set by caller
            source="code"
        )
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find all elements - NO LAMBDAS!
            for element in soup.find_all():
                # Skip if not a Tag (could be NavigableString, etc)
                if not isinstance(element, Tag):
                    continue
                
                # Check each attribute explicitly
                for attr_name, attr_value in element.attrs.items():
                    if attr_name.startswith('data-tekton-'):
                        # Extract the semantic tag name (remove data-tekton- prefix)
                        tag_name = attr_name[12:]  # len('data-tekton-') = 12
                        
                        # Create semantic tag object
                        tag = SemanticTag(
                            name=tag_name,
                            value=str(attr_value),
                            element=element.name,
                            attributes={k: v for k, v in element.attrs.items() if k != attr_name}
                        )
                        
                        analysis.add_tag(tag)
                        logger.debug(f"Found semantic tag: {tag.full_name}='{tag.value}' on <{tag.element}>")
            
            logger.info(f"Extracted {analysis.total_count} semantic tags from HTML")
            return analysis
            
        except Exception as e:
            logger.error(f"Error extracting semantic tags: {e}")
            return analysis
    
    def analyze_component(self, component_name: str) -> Tuple[ComponentInfo, Optional[SemanticTagAnalysis]]:
        """Read component and analyze its semantic tags"""
        component_info = self.read_component(component_name)
        
        if not component_info.exists or not component_info.content:
            return component_info, None
        
        analysis = self.extract_semantic_tags(component_info.content)
        analysis.component_name = component_name
        
        return component_info, analysis
    
    def list_available_components(self) -> List[str]:
        """List all available components in the base path"""
        components = []
        
        try:
            if not self.base_path.exists():
                logger.warning(f"Base path does not exist: {self.base_path}")
                return components
            
            # Look for directories that contain component HTML files
            for item in self.base_path.iterdir():
                if item.is_dir():
                    # Check if it has a component HTML file
                    component_file = item / f"{item.name}-component.html"
                    if component_file.exists():
                        components.append(item.name)
                        logger.debug(f"Found component: {item.name}")
            
            logger.info(f"Found {len(components)} components")
            return sorted(components)
            
        except Exception as e:
            logger.error(f"Error listing components: {e}")
            return components