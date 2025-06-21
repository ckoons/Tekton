"""SafeTester Tool - Test changes without breaking production"""
import asyncio
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from copy import deepcopy

from ..core.browser import BrowserManager
from ..core.models import ToolResult, ToolStatus

logger = logging.getLogger(__name__)


class Change:
    """Represents a single change to test"""
    def __init__(self, change_type: str, selector: str, **kwargs):
        self.type = change_type  # 'text', 'attribute', 'style', 'class', 'element'
        self.selector = selector
        self.params = kwargs
        self.timestamp = datetime.now().isoformat()


class SafeTester:
    """Test changes without breaking production"""
    
    def __init__(self):
        """Initialize with browser manager"""
        self.browser = BrowserManager()
        self.change_history = []
        logger.info("SafeTester initialized")
    
    async def preview_change(self, component_name: str, changes: List[Dict[str, Any]]) -> ToolResult:
        """Preview changes without applying them"""
        try:
            # Navigate to component first
            nav_success = await self.browser.navigate_to_component(component_name)
            if not nav_success:
                return ToolResult(
                    tool_name="SafeTester",
                    status=ToolStatus.ERROR,
                    component=component_name,
                    error="Failed to navigate to component"
                )
            
            # Capture current state
            before_state = await self._capture_state(component_name)
            
            # Simulate changes to show what would happen
            preview_results = []
            
            for change in changes:
                change_obj = Change(
                    change_type=change.get("type", "unknown"),
                    selector=change.get("selector", ""),
                    **{k: v for k, v in change.items() if k not in ["type", "selector"]}
                )
                preview = await self._preview_single_change(change_obj)
                preview_results.append(preview)
            
            data = {
                "preview_mode": True,
                "changes": len(changes),
                "before_state": before_state,
                "preview_results": preview_results,
                "would_break": any(p.get("would_break", False) for p in preview_results)
            }
            
            warnings = []
            if data["would_break"]:
                warnings.append("Some changes would break the component")
            
            return ToolResult(
                tool_name="SafeTester",
                status=ToolStatus.SUCCESS,
                component=component_name,
                data=data,
                warnings=warnings
            )
            
        except Exception as e:
            logger.error(f"Error previewing changes: {e}")
            return ToolResult(
                tool_name="SafeTester",
                status=ToolStatus.ERROR,
                component=component_name,
                error=str(e)
            )
    
    async def test_in_sandbox(self, component_name: str, changes: List[Dict[str, Any]]) -> ToolResult:
        """Test changes in an isolated sandbox"""
        try:
            # Navigate to component
            nav_success = await self.browser.navigate_to_component(component_name)
            if not nav_success:
                return ToolResult(
                    tool_name="SafeTester",
                    status=ToolStatus.ERROR,
                    component=component_name,
                    error="Failed to navigate to component"
                )
            
            # Capture before state
            before_state = await self._capture_state(component_name)
            
            # Create sandbox by cloning component
            sandbox_created = await self._create_sandbox(component_name)
            if not sandbox_created:
                return ToolResult(
                    tool_name="SafeTester",
                    status=ToolStatus.ERROR,
                    component=component_name,
                    error="Failed to create sandbox"
                )
            
            # Apply changes in sandbox
            applied_changes = []
            failed_changes = []
            
            for change in changes:
                change_obj = Change(
                    change_type=change.get("type", "unknown"),
                    selector=change.get("selector", ""),
                    **{k: v for k, v in change.items() if k not in ["type", "selector"]}
                )
                result = await self._apply_change_in_sandbox(change_obj)
                
                if result["success"]:
                    applied_changes.append(result)
                else:
                    failed_changes.append(result)
            
            # Capture after state
            after_state = await self._capture_sandbox_state()
            
            # Validate changes
            validation = await self._validate_sandbox_changes(before_state, after_state)
            
            # Clean up sandbox
            await self._cleanup_sandbox()
            
            data = {
                "sandbox_mode": True,
                "changes_requested": len(changes),
                "changes_applied": len(applied_changes),
                "changes_failed": len(failed_changes),
                "before_state": before_state,
                "after_state": after_state,
                "applied_changes": applied_changes,
                "failed_changes": failed_changes,
                "validation": validation
            }
            
            status = ToolStatus.SUCCESS
            warnings = []
            
            if failed_changes:
                warnings.append(f"{len(failed_changes)} changes failed to apply")
                if not applied_changes:
                    status = ToolStatus.ERROR
            
            if not validation.get("safe", True):
                warnings.append("Changes may cause issues")
            
            return ToolResult(
                tool_name="SafeTester",
                status=status,
                component=component_name,
                data=data,
                warnings=warnings
            )
            
        except Exception as e:
            logger.error(f"Error testing in sandbox: {e}")
            return ToolResult(
                tool_name="SafeTester",
                status=ToolStatus.ERROR,
                component=component_name,
                error=str(e)
            )
    
    async def validate_change(self, component_name: str, changes: List[Dict[str, Any]]) -> ToolResult:
        """Validate if changes are safe to apply"""
        try:
            validations = []
            
            for change in changes:
                change_obj = Change(
                    change_type=change.get("type", "unknown"),
                    selector=change.get("selector", ""),
                    **{k: v for k, v in change.items() if k not in ["type", "selector"]}
                )
                validation = await self._validate_single_change(component_name, change_obj)
                validations.append(validation)
            
            # Overall safety assessment
            all_safe = all(v.get("safe", False) for v in validations)
            critical_issues = [v for v in validations if v.get("severity") == "critical"]
            
            data = {
                "changes_validated": len(changes),
                "all_safe": all_safe,
                "critical_issues": len(critical_issues),
                "validations": validations,
                "recommendation": self._get_recommendation(validations)
            }
            
            warnings = []
            if not all_safe:
                warnings.append("Some changes are not safe to apply")
            if critical_issues:
                warnings.append(f"{len(critical_issues)} critical issues found")
            
            return ToolResult(
                tool_name="SafeTester",
                status=ToolStatus.SUCCESS if all_safe else ToolStatus.WARNING,
                component=component_name,
                data=data,
                warnings=warnings
            )
            
        except Exception as e:
            logger.error(f"Error validating changes: {e}")
            return ToolResult(
                tool_name="SafeTester",
                status=ToolStatus.ERROR,
                component=component_name,
                error=str(e)
            )
    
    async def rollback_changes(self, component_name: str) -> ToolResult:
        """Rollback to previous state"""
        try:
            if not self.change_history:
                return ToolResult(
                    tool_name="SafeTester",
                    status=ToolStatus.WARNING,
                    component=component_name,
                    warnings=["No changes to rollback"],
                    data={"rolled_back": False}
                )
            
            # Get last change set
            last_changes = self.change_history[-1]
            
            # Reload component to original state
            nav_success = await self.browser.navigate_to_component(component_name)
            
            data = {
                "rolled_back": nav_success,
                "changes_reverted": len(last_changes) if nav_success else 0
            }
            
            if nav_success:
                self.change_history.pop()
            
            return ToolResult(
                tool_name="SafeTester",
                status=ToolStatus.SUCCESS if nav_success else ToolStatus.ERROR,
                component=component_name,
                data=data,
                error=None if nav_success else "Failed to reload component"
            )
            
        except Exception as e:
            logger.error(f"Error rolling back changes: {e}")
            return ToolResult(
                tool_name="SafeTester",
                status=ToolStatus.ERROR,
                component=component_name,
                error=str(e)
            )
    
    async def cleanup(self) -> None:
        """Clean up browser resources"""
        await self.browser.cleanup()
    
    # Helper methods
    async def _capture_state(self, component_name: str) -> Dict[str, Any]:
        """Capture current component state"""
        script = f"""
        () => {{
            const component = document.querySelector('[data-tekton-component="{component_name}"]');
            if (!component) return null;
            
            return {{
                html: component.outerHTML.substring(0, 1000),  // First 1000 chars
                elementCount: component.querySelectorAll('*').length,
                semanticTags: Array.from(component.attributes)
                    .filter(attr => attr.name.startsWith('data-tekton-')).length +
                    Array.from(component.querySelectorAll('*'))
                    .reduce((count, el) => count + Array.from(el.attributes)
                        .filter(attr => attr.name.startsWith('data-tekton-')).length, 0),
                textContent: component.textContent.substring(0, 500),
                classList: Array.from(component.classList),
                attributes: Object.fromEntries(
                    Array.from(component.attributes)
                        .filter(attr => attr.name.startsWith('data-tekton-'))
                        .map(attr => [attr.name, attr.value])
                )
            }};
        }}
        """
        return await self.browser.evaluate_script(script) or {}
    
    async def _preview_single_change(self, change: Change) -> Dict[str, Any]:
        """Preview what a single change would do"""
        preview = {
            "change_type": change.type,
            "selector": change.selector,
            "would_break": False,
            "impact": "low",
            "description": ""
        }
        
        # Check if selector exists
        exists_script = f"""
        () => {{
            const elements = document.querySelectorAll('{change.selector}');
            return elements.length;
        }}
        """
        element_count = await self.browser.evaluate_script(exists_script)
        
        if element_count == 0:
            preview["would_break"] = True
            preview["impact"] = "critical"
            preview["description"] = f"No elements match selector '{change.selector}'"
            return preview
        
        preview["elements_affected"] = element_count
        
        # Analyze change impact
        if change.type == "text":
            preview["description"] = f"Would change text content of {element_count} element(s)"
            preview["new_value"] = change.params.get("content", "")
            
        elif change.type == "attribute":
            attr_name = change.params.get("name", "")
            if attr_name.startswith("data-tekton-"):
                preview["impact"] = "medium"
                preview["description"] = f"Would modify semantic tag '{attr_name}'"
            else:
                preview["description"] = f"Would modify attribute '{attr_name}'"
            
        elif change.type == "style":
            preview["description"] = f"Would modify styles of {element_count} element(s)"
            preview["styles"] = change.params.get("styles", {})
            
        elif change.type == "class":
            action = change.params.get("action", "add")
            classes = change.params.get("classes", [])
            preview["description"] = f"Would {action} classes: {', '.join(classes)}"
            
        elif change.type == "element":
            action = change.params.get("action", "add")
            if action == "remove":
                preview["impact"] = "high"
                preview["would_break"] = element_count > 5  # Removing many elements is risky
            preview["description"] = f"Would {action} {element_count} element(s)"
        
        return preview
    
    async def _create_sandbox(self, component_name: str) -> bool:
        """Create a sandbox environment for testing"""
        # For now, we'll use a simple approach - clone the component
        script = f"""
        () => {{
            const component = document.querySelector('[data-tekton-component="{component_name}"]');
            if (!component) return false;
            
            // Create sandbox container
            const sandbox = document.createElement('div');
            sandbox.id = 'tekton-safetester-sandbox';
            sandbox.style.display = 'none';  // Hidden sandbox
            sandbox.setAttribute('data-sandbox', 'true');
            
            // Clone component
            const clone = component.cloneNode(true);
            clone.setAttribute('data-sandbox-component', 'true');
            sandbox.appendChild(clone);
            
            document.body.appendChild(sandbox);
            return true;
        }}
        """
        return await self.browser.evaluate_script(script)
    
    async def _apply_change_in_sandbox(self, change: Change) -> Dict[str, Any]:
        """Apply a change in the sandbox"""
        result = {
            "change": change.type,
            "selector": change.selector,
            "success": False,
            "error": None
        }
        
        # Modify selector to target sandbox
        sandbox_selector = f"#tekton-safetester-sandbox {change.selector}"
        
        try:
            if change.type == "text":
                script = f"""
                () => {{
                    const elements = document.querySelectorAll('{sandbox_selector}');
                    if (elements.length === 0) return false;
                    elements.forEach(el => el.textContent = '{change.params.get("content", "")}');
                    return true;
                }}
                """
                result["success"] = await self.browser.evaluate_script(script)
                
            elif change.type == "attribute":
                name = change.params.get("name", "")
                value = change.params.get("value", "")
                script = f"""
                () => {{
                    const elements = document.querySelectorAll('{sandbox_selector}');
                    if (elements.length === 0) return false;
                    elements.forEach(el => el.setAttribute('{name}', '{value}'));
                    return true;
                }}
                """
                result["success"] = await self.browser.evaluate_script(script)
                
            # Add more change types as needed
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    async def _capture_sandbox_state(self) -> Dict[str, Any]:
        """Capture sandbox state after changes"""
        script = """
        () => {
            const sandbox = document.querySelector('#tekton-safetester-sandbox');
            if (!sandbox) return null;
            
            const component = sandbox.querySelector('[data-sandbox-component]');
            if (!component) return null;
            
            return {
                html: component.outerHTML.substring(0, 1000),
                elementCount: component.querySelectorAll('*').length,
                semanticTags: Array.from(component.attributes)
                    .filter(attr => attr.name.startsWith('data-tekton-')).length +
                    Array.from(component.querySelectorAll('*'))
                    .reduce((count, el) => count + Array.from(el.attributes)
                        .filter(attr => attr.name.startsWith('data-tekton-')).length, 0),
                modified: true
            };
        }
        """
        return await self.browser.evaluate_script(script) or {}
    
    async def _validate_sandbox_changes(self, before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
        """Validate changes made in sandbox"""
        validation = {
            "safe": True,
            "issues": [],
            "metrics": {}
        }
        
        # Check element count change
        if before.get("elementCount") and after.get("elementCount"):
            diff = after["elementCount"] - before["elementCount"]
            validation["metrics"]["element_diff"] = diff
            if abs(diff) > 10:
                validation["issues"].append("Significant change in element count")
                validation["safe"] = False
        
        # Check semantic tag preservation
        if before.get("semanticTags") and after.get("semanticTags"):
            tag_diff = after["semanticTags"] - before["semanticTags"]
            validation["metrics"]["semantic_tag_diff"] = tag_diff
            if tag_diff < -5:
                validation["issues"].append("Lost semantic tags")
                validation["safe"] = False
        
        return validation
    
    async def _cleanup_sandbox(self) -> None:
        """Remove sandbox from DOM"""
        script = """
        () => {
            const sandbox = document.querySelector('#tekton-safetester-sandbox');
            if (sandbox) {
                sandbox.remove();
                return true;
            }
            return false;
        }
        """
        await self.browser.evaluate_script(script)
    
    async def _validate_single_change(self, component_name: str, change: Change) -> Dict[str, Any]:
        """Validate a single change"""
        validation = {
            "change_type": change.type,
            "selector": change.selector,
            "safe": True,
            "severity": "low",
            "issues": []
        }
        
        # Check selector safety
        if change.selector == "*" or change.selector == "body":
            validation["safe"] = False
            validation["severity"] = "critical"
            validation["issues"].append("Selector too broad - would affect entire page")
        
        # Check semantic tag modifications
        if change.type == "attribute" and change.params.get("name", "").startswith("data-tekton-"):
            validation["severity"] = "medium"
            validation["issues"].append("Modifying semantic tags - ensure compatibility")
        
        # Check element removal
        if change.type == "element" and change.params.get("action") == "remove":
            if "component" in change.selector or "workspace" in change.selector:
                validation["safe"] = False
                validation["severity"] = "critical"
                validation["issues"].append("Attempting to remove critical component elements")
        
        return validation
    
    def _get_recommendation(self, validations: List[Dict[str, Any]]) -> str:
        """Get overall recommendation based on validations"""
        if all(v.get("safe", False) for v in validations):
            return "All changes are safe to apply"
        
        critical = sum(1 for v in validations if v.get("severity") == "critical")
        if critical > 0:
            return f"DO NOT APPLY: {critical} critical issues found"
        
        medium = sum(1 for v in validations if v.get("severity") == "medium")
        if medium > 0:
            return f"REVIEW CAREFULLY: {medium} medium-severity issues found"
        
        return "PROCEED WITH CAUTION: Some minor issues found"