"""Comparator Tool - Identify discrepancies between code and browser"""
import asyncio
import logging
from typing import Dict, Any, List, Set, Tuple
from collections import defaultdict

from ..core.file_reader import ComponentReader
from ..tools.code_reader import CodeReader
from ..tools.browser_verifier import BrowserVerifier
from ..core.models import ToolResult, ToolStatus, DiscrepancyInfo, SemanticTagAnalysis

logger = logging.getLogger(__name__)


class Comparator:
    """Compare code (truth) vs browser (reality) to understand the full picture"""
    
    def __init__(self):
        """Initialize with code reader and browser verifier"""
        self.code_reader = CodeReader()
        self.browser_verifier = BrowserVerifier()
        logger.info("Comparator initialized")
    
    async def compare_component(self, component_name: str) -> ToolResult:
        """Full comparison of component between code and browser"""
        try:
            # 1. Get code data (truth)
            code_result = self.code_reader.list_semantic_tags(component_name)
            if code_result.status != ToolStatus.SUCCESS:
                return ToolResult(
                    tool_name="Comparator",
                    status=ToolStatus.ERROR,
                    component=component_name,
                    error=f"Failed to read code: {code_result.error}"
                )
            
            # 2. Get browser data (reality)
            browser_result = await self.browser_verifier.get_dom_semantic_tags(component_name)
            if browser_result.status != ToolStatus.SUCCESS:
                return ToolResult(
                    tool_name="Comparator",
                    status=ToolStatus.ERROR,
                    component=component_name,
                    error=f"Failed to check browser: {browser_result.error}"
                )
            
            # 3. Extract data
            code_tags = code_result.data['semantic_tags']
            browser_tags = browser_result.data['semantic_tags']
            
            # 4. Perform comparison
            comparison = self._compare_tags(code_tags, browser_tags)
            
            # 5. Categorize dynamic tags
            categorized = self._categorize_dynamic_tags(comparison['dom_only_tags'])
            
            # 6. Generate insights
            insights = self._generate_insights(comparison, categorized)
            
            # Build result
            data = {
                "comparison": comparison,
                "dynamic_tag_categories": categorized,
                "insights": insights,
                "summary": {
                    "code_tags": code_tags['total_count'],
                    "browser_tags": browser_tags['total_count'],
                    "static_tags_preserved": len(comparison['in_both']),
                    "dynamic_tags_added": len(comparison['dom_only_tags']),
                    "missing_from_dom": len(comparison['code_only_tags'])
                }
            }
            
            return ToolResult(
                tool_name="Comparator",
                status=ToolStatus.SUCCESS,
                component=component_name,
                data=data
            )
            
        except Exception as e:
            logger.error(f"Error comparing component {component_name}: {e}")
            return ToolResult(
                tool_name="Comparator",
                status=ToolStatus.ERROR,
                component=component_name,
                error=str(e)
            )
        finally:
            await self.browser_verifier.cleanup()
    
    async def diagnose_missing_tags(self, component_name: str) -> ToolResult:
        """Diagnose why specific tags might be missing from DOM"""
        try:
            comparison_result = await self.compare_component(component_name)
            if comparison_result.status != ToolStatus.SUCCESS:
                return comparison_result
            
            comparison = comparison_result.data['comparison']
            missing_tags = comparison['code_only_tags']
            
            if not missing_tags:
                return ToolResult(
                    tool_name="Comparator",
                    status=ToolStatus.SUCCESS,
                    component=component_name,
                    data={
                        "diagnosis": "All source tags are present in DOM",
                        "missing_count": 0
                    }
                )
            
            # Analyze missing tags
            diagnosis = {
                "missing_tags": missing_tags,
                "missing_count": len(missing_tags),
                "possible_causes": [],
                "recommendations": []
            }
            
            # Check patterns in missing tags
            if any('menu' in tag for tag in missing_tags):
                diagnosis["possible_causes"].append("Menu-related tags may require user interaction to appear")
                diagnosis["recommendations"].append("Try opening menus before checking")
            
            if any('panel' in tag for tag in missing_tags):
                diagnosis["possible_causes"].append("Panel tags may only appear when panels are active")
                diagnosis["recommendations"].append("Activate panels before verification")
            
            if any('state' in tag for tag in missing_tags):
                diagnosis["possible_causes"].append("State tags may depend on component state")
                diagnosis["recommendations"].append("Check component initialization")
            
            # General recommendations
            diagnosis["recommendations"].extend([
                "Check if MinimalLoader preserves all data-* attributes",
                "Verify component is fully loaded before checking",
                "Look for JavaScript errors in browser console"
            ])
            
            return ToolResult(
                tool_name="Comparator",
                status=ToolStatus.SUCCESS,
                component=component_name,
                data={"diagnosis": diagnosis}
            )
            
        except Exception as e:
            logger.error(f"Error diagnosing missing tags for {component_name}: {e}")
            return ToolResult(
                tool_name="Comparator",
                status=ToolStatus.ERROR,
                component=component_name,
                error=str(e)
            )
    
    async def suggest_fixes(self, component_name: str) -> ToolResult:
        """Suggest fixes based on comparison results"""
        try:
            comparison_result = await self.compare_component(component_name)
            if comparison_result.status != ToolStatus.SUCCESS:
                return comparison_result
            
            data = comparison_result.data
            suggestions = []
            
            # Check if all static tags made it
            if data['summary']['missing_from_dom'] == 0:
                suggestions.append({
                    "type": "success",
                    "message": "All static tags from source are present in DOM",
                    "action": "No fixes needed for static tags"
                })
            else:
                suggestions.append({
                    "type": "warning",
                    "message": f"{data['summary']['missing_from_dom']} static tags missing from DOM",
                    "action": "Check component loading process",
                    "details": data['comparison']['code_only_tags']
                })
            
            # Analyze dynamic tags
            categories = data['dynamic_tag_categories']
            
            if categories['navigation']:
                suggestions.append({
                    "type": "info",
                    "message": f"Found {len(categories['navigation'])} navigation-related dynamic tags",
                    "action": "These are expected for navigation functionality"
                })
            
            if categories['loading']:
                suggestions.append({
                    "type": "info",
                    "message": f"Found {len(categories['loading'])} loading-state dynamic tags",
                    "action": "These indicate proper loading state management"
                })
            
            if categories['state']:
                suggestions.append({
                    "type": "info",
                    "message": f"Found {len(categories['state'])} runtime state tags",
                    "action": "These track component state dynamically"
                })
            
            if categories['unknown']:
                suggestions.append({
                    "type": "warning",
                    "message": f"Found {len(categories['unknown'])} uncategorized dynamic tags",
                    "action": "Review these tags to understand their purpose",
                    "details": categories['unknown']
                })
            
            return ToolResult(
                tool_name="Comparator",
                status=ToolStatus.SUCCESS,
                component=component_name,
                data={"suggestions": suggestions}
            )
            
        except Exception as e:
            logger.error(f"Error suggesting fixes for {component_name}: {e}")
            return ToolResult(
                tool_name="Comparator",
                status=ToolStatus.ERROR,
                component=component_name,
                error=str(e)
            )
    
    def _compare_tags(self, code_tags: Dict[str, Any], browser_tags: Dict[str, Any]) -> Dict[str, Any]:
        """Compare tag sets between code and browser"""
        # Get all unique tag instances (tag_name:value pairs)
        code_instances = set()
        browser_instances = set()
        
        # Build instance sets
        for tag_name, values in code_tags['by_name'].items():
            for value_info in values:
                code_instances.add(f"{tag_name}:{value_info['value']}")
        
        for tag_name, values in browser_tags['by_name'].items():
            for value_info in values:
                browser_instances.add(f"{tag_name}:{value_info['value']}")
        
        # Get tag types only
        code_types = set(code_tags['summary'].keys())
        browser_types = set(browser_tags['found'])
        
        return {
            "code_only_tags": sorted(list(code_types - browser_types)),
            "dom_only_tags": sorted(list(browser_types - code_types)),
            "in_both": sorted(list(code_types & browser_types)),
            "code_only_instances": sorted(list(code_instances - browser_instances)),
            "dom_only_instances": sorted(list(browser_instances - code_instances)),
            "tag_count_comparison": {
                "code": code_tags['total_count'],
                "browser": browser_tags['total_count'],
                "difference": browser_tags['total_count'] - code_tags['total_count']
            }
        }
    
    def _categorize_dynamic_tags(self, dynamic_tags: List[str]) -> Dict[str, List[str]]:
        """Categorize dynamic tags by their likely purpose"""
        categories = {
            "navigation": [],
            "loading": [],
            "state": [],
            "list": [],
            "unknown": []
        }
        
        for tag in dynamic_tags:
            if 'nav' in tag or 'navigation' in tag:
                categories["navigation"].append(tag)
            elif 'loading' in tag or 'loader' in tag:
                categories["loading"].append(tag)
            elif 'state' in tag or 'status' in tag:
                categories["state"].append(tag)
            elif 'list' in tag:
                categories["list"].append(tag)
            else:
                categories["unknown"].append(tag)
        
        return categories
    
    def _generate_insights(self, comparison: Dict[str, Any], categories: Dict[str, List[str]]) -> List[str]:
        """Generate insights from the comparison"""
        insights = []
        
        # Overall health
        if comparison['tag_count_comparison']['difference'] > 0:
            insights.append(f"✓ Browser enriches component with {comparison['tag_count_comparison']['difference']} additional tags")
        elif comparison['tag_count_comparison']['difference'] < 0:
            insights.append(f"⚠️ Browser has {abs(comparison['tag_count_comparison']['difference'])} fewer tags than source")
        else:
            insights.append("✓ Perfect match between source and browser tag counts")
        
        # Static tag preservation
        if not comparison['code_only_tags']:
            insights.append("✓ All static tag types from source are preserved in DOM")
        else:
            insights.append(f"⚠️ {len(comparison['code_only_tags'])} tag types from source are missing in DOM")
        
        # Dynamic tag insights
        total_dynamic = sum(len(tags) for tags in categories.values())
        if total_dynamic > 0:
            insights.append(f"📊 System adds {total_dynamic} types of dynamic tags at runtime:")
            if categories['navigation']:
                insights.append(f"  • Navigation: {len(categories['navigation'])} types (nav-item, nav-target, etc.)")
            if categories['loading']:
                insights.append(f"  • Loading states: {len(categories['loading'])} types (loading indicators)")
            if categories['state']:
                insights.append(f"  • Runtime state: {len(categories['state'])} types (component state tracking)")
        
        # Component health assessment
        if not comparison['code_only_tags'] and categories['navigation'] and categories['loading']:
            insights.append("🎯 Component shows signs of healthy dynamic behavior")
        
        return insights