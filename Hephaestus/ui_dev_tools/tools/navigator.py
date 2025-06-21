"""Navigator Tool - Navigate to components reliably"""
import asyncio
import logging
from typing import Dict, Any, Optional, List

from ..core.browser import BrowserManager
from ..core.file_reader import ComponentReader
from ..core.models import ToolResult, ToolStatus

logger = logging.getLogger(__name__)


class Navigator:
    """Navigate to components reliably"""
    
    def __init__(self):
        """Initialize with browser manager and component reader"""
        self.browser = BrowserManager()
        self.reader = ComponentReader()
        logger.info("Navigator initialized")
    
    async def navigate_to_component(self, component_name: str, wait_for_ready: bool = True) -> ToolResult:
        """Navigate to a component with verification"""
        try:
            # First check if component exists in code
            component_info = self.reader.read_component(component_name)
            
            if not component_info.exists:
                return ToolResult(
                    tool_name="Navigator",
                    status=ToolStatus.ERROR,
                    component=component_name,
                    error=f"Component '{component_name}' not found in codebase",
                    data={"component_exists": False}
                )
            
            # Navigate to the component
            logger.info(f"Navigating to component: {component_name}")
            success = await self.browser.navigate_to_component(component_name)
            
            if not success:
                return ToolResult(
                    tool_name="Navigator",
                    status=ToolStatus.ERROR,
                    component=component_name,
                    error="Failed to navigate to component",
                    data={
                        "component_exists": True,
                        "navigation_success": False
                    }
                )
            
            # Wait for component to be ready if requested
            if wait_for_ready:
                ready = await self.wait_for_ready(component_name)
                if not ready:
                    return ToolResult(
                        tool_name="Navigator",
                        status=ToolStatus.WARNING,
                        component=component_name,
                        warnings=["Component loaded but may not be fully ready"],
                        data={
                            "component_exists": True,
                            "navigation_success": True,
                            "component_ready": False
                        }
                    )
            
            # Get current state
            current_url = await self.browser.get_current_url()
            component_loaded = await self._check_component_loaded(component_name)
            
            data = {
                "component_exists": True,
                "navigation_success": True,
                "component_ready": component_loaded,
                "current_url": current_url,
                "load_method": await self._get_load_method()
            }
            
            return ToolResult(
                tool_name="Navigator",
                status=ToolStatus.SUCCESS,
                component=component_name,
                data=data
            )
            
        except Exception as e:
            logger.error(f"Error navigating to component {component_name}: {e}")
            return ToolResult(
                tool_name="Navigator",
                status=ToolStatus.ERROR,
                component=component_name,
                error=str(e)
            )
    
    async def wait_for_ready(self, component_name: str, timeout: int = 10000) -> bool:
        """Wait for component to be fully loaded and ready"""
        try:
            logger.info(f"Waiting for component {component_name} to be ready...")
            
            # Wait strategies
            strategies = [
                # Strategy 1: Check for component element
                self._wait_for_component_element,
                # Strategy 2: Check for semantic tags
                self._wait_for_semantic_tags,
                # Strategy 3: Check for no loading indicators
                self._wait_for_no_loading
            ]
            
            start_time = asyncio.get_event_loop().time()
            
            while (asyncio.get_event_loop().time() - start_time) * 1000 < timeout:
                all_ready = True
                
                for strategy in strategies:
                    if not await strategy(component_name):
                        all_ready = False
                        break
                
                if all_ready:
                    logger.info(f"Component {component_name} is ready")
                    return True
                
                # Wait a bit before checking again
                await asyncio.sleep(0.5)
            
            logger.warning(f"Timeout waiting for component {component_name} to be ready")
            return False
            
        except Exception as e:
            logger.error(f"Error waiting for component ready: {e}")
            return False
    
    async def get_current_component(self) -> ToolResult:
        """Get the currently loaded component"""
        try:
            # Check all available components
            available_components = self.reader.list_available_components()
            
            current_component = None
            loaded_components = []
            
            # Check which components are currently in DOM
            for component in available_components:
                if await self._check_component_loaded(component):
                    loaded_components.append(component)
                    # The "current" is likely the one with the main workspace
                    if await self._is_main_component(component):
                        current_component = component
            
            # If no main component found but some are loaded, pick the first
            if not current_component and loaded_components:
                current_component = loaded_components[0]
            
            data = {
                "current_component": current_component,
                "loaded_components": loaded_components,
                "current_url": await self.browser.get_current_url()
            }
            
            if current_component:
                return ToolResult(
                    tool_name="Navigator",
                    status=ToolStatus.SUCCESS,
                    data=data
                )
            else:
                return ToolResult(
                    tool_name="Navigator",
                    status=ToolStatus.WARNING,
                    data=data,
                    warnings=["No component currently loaded"]
                )
                
        except Exception as e:
            logger.error(f"Error getting current component: {e}")
            return ToolResult(
                tool_name="Navigator",
                status=ToolStatus.ERROR,
                error=str(e)
            )
    
    async def list_navigable_components(self) -> ToolResult:
        """List all components that can be navigated to"""
        try:
            # Get components from codebase
            available_components = self.reader.list_available_components()
            
            # Check navigation UI for accessible components
            nav_components = await self._get_navigation_components()
            
            data = {
                "available_in_code": available_components,
                "available_in_nav": nav_components,
                "total_components": len(available_components)
            }
            
            # Identify any discrepancies
            code_set = set(available_components)
            nav_set = set(nav_components)
            
            if code_set != nav_set:
                data["discrepancies"] = {
                    "in_code_only": sorted(list(code_set - nav_set)),
                    "in_nav_only": sorted(list(nav_set - code_set))
                }
            
            return ToolResult(
                tool_name="Navigator",
                status=ToolStatus.SUCCESS,
                data=data
            )
            
        except Exception as e:
            logger.error(f"Error listing navigable components: {e}")
            return ToolResult(
                tool_name="Navigator",
                status=ToolStatus.ERROR,
                error=str(e)
            )
    
    async def cleanup(self) -> None:
        """Clean up browser resources"""
        await self.browser.cleanup()
    
    # Helper methods
    async def _check_component_loaded(self, component_name: str) -> bool:
        """Check if a component is loaded in DOM"""
        script = f"""
        () => {{
            const component = document.querySelector('[data-tekton-component="{component_name}"]');
            return component !== null;
        }}
        """
        return await self.browser.evaluate_script(script)
    
    async def _wait_for_component_element(self, component_name: str) -> bool:
        """Wait strategy: Check for component element"""
        return await self.browser.wait_for_selector(
            f'[data-tekton-component="{component_name}"]',
            timeout=100  # Quick check
        )
    
    async def _wait_for_semantic_tags(self, component_name: str) -> bool:
        """Wait strategy: Check for semantic tags"""
        script = f"""
        () => {{
            const component = document.querySelector('[data-tekton-component="{component_name}"]');
            if (!component) return false;
            
            // Check if component has expected semantic tags
            const semanticAttrs = Array.from(component.attributes)
                .filter(attr => attr.name.startsWith('data-tekton-'))
                .length;
            
            return semanticAttrs > 2;  // Should have more than just component tag
        }}
        """
        return await self.browser.evaluate_script(script)
    
    async def _wait_for_no_loading(self, component_name: str) -> bool:
        """Wait strategy: Check for no loading indicators"""
        script = """
        () => {
            // Check for any loading indicators
            const loadingElements = document.querySelectorAll(
                '[data-tekton-loading-state="true"], ' +
                '[data-tekton-loading="true"], ' +
                '.loading, .spinner'
            );
            return loadingElements.length === 0;
        }
        """
        return await self.browser.evaluate_script(script)
    
    async def _is_main_component(self, component_name: str) -> bool:
        """Check if this is the main active component"""
        script = f"""
        () => {{
            const component = document.querySelector('[data-tekton-component="{component_name}"]');
            if (!component) return false;
            
            // Check if it's in the main workspace area
            const isWorkspace = component.getAttribute('data-tekton-type') === 'component-workspace';
            const isVisible = component.offsetParent !== null;
            
            return isWorkspace && isVisible;
        }}
        """
        return await self.browser.evaluate_script(script)
    
    async def _get_navigation_components(self) -> List[str]:
        """Get components available in navigation UI"""
        script = """
        () => {
            // Look for navigation items
            const navItems = document.querySelectorAll('[data-tekton-nav-item]');
            const components = new Set();
            
            navItems.forEach(item => {
                const target = item.getAttribute('data-tekton-nav-target');
                if (target) {
                    components.add(target);
                }
            });
            
            return Array.from(components);
        }
        """
        try:
            return await self.browser.evaluate_script(script) or []
        except:
            return []
    
    async def _get_load_method(self) -> str:
        """Determine which load method was used"""
        script = """
        () => {
            if (window.MinimalLoader) return 'MinimalLoader';
            if (window.loadComponent) return 'loadComponent';
            return 'hash_navigation';
        }
        """
        return await self.browser.evaluate_script(script)