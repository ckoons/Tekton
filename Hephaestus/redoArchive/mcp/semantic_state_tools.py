"""
Semantic State Inspection Tools for Hephaestus UI DevTools - Phase 2

Tools for inspecting component state, discovering actions, and mapping relationships.
"""

from typing import Dict, Any, List, Optional, Set
from playwright.async_api import Page
import json

from .constants import ComponentNotFoundError
from .browser_manager import browser_manager
from shared.utils.logging_setup import setup_component_logging

logger = setup_component_logging("ui_semantic_state")


async def ui_inspect_state(
    component: str,
    include_children: bool = True,
    max_depth: int = 3,
    use_source: bool = True
) -> Dict[str, Any]:
    """
    Deep inspection of component state and semantic attributes
    
    Args:
        component: Component name or selector to inspect
        include_children: Whether to inspect child elements
        max_depth: Maximum depth for child inspection
        use_source: Whether to read from source files (True) or DOM (False)
        
    Returns:
        Detailed state information including all semantic attributes
    """
    await browser_manager.initialize()
    page = await browser_manager.get_page()
    
    result = {
        "component": component,
        "state_inspection": {},
        "semantic_coverage": {},
        "data_flows": [],
        "source": "file" if use_source else "dom"
    }
    
    try:
        # If use_source is True, read from the HTML file
        if use_source:
            import os
            from bs4 import BeautifulSoup
            
            # Build path to component HTML file
            component_path = f"/Users/cskoons/projects/github/Tekton/Hephaestus/ui/components/{component}/{component}-component.html"
            
            if not os.path.exists(component_path):
                result["error"] = f"Component file not found: {component_path}"
                return result
            
            # Read and parse the HTML file
            with open(component_path, 'r') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find the root component element
            root_element = soup.find(attrs={"data-tekton-component": component}) or \
                          soup.find(attrs={"data-tekton-area": component})
            
            if not root_element:
                result["error"] = f"No element with data-tekton-component='{component}' found in file"
                return result
            
            # Extract semantic attributes from the file
            component_state = {
                "tag": root_element.name,
                "semantic_attributes": {},
                "standard_attributes": {},
                "computed_state": {
                    "visible": True,  # Assume visible in source
                    "enabled": True,
                    "from_source": True
                },
                "children": []
            }
            
            # Get all data-tekton attributes
            for attr, value in root_element.attrs.items():
                if attr.startswith('data-tekton-'):
                    component_state["semantic_attributes"][attr.replace('data-tekton-', '')] = value
                elif attr in ['id', 'class', 'name', 'type']:
                    component_state["standard_attributes"][attr] = value
            
            # Find child elements with semantic tags
            if include_children:
                # Find all elements, then filter for semantic tags
                all_children = root_element.find_all()
                semantic_children = []
                for child in all_children:
                    if any(attr.startswith('data-tekton-') for attr in child.attrs.keys()):
                        semantic_children.append(child)
                
                for child in semantic_children[:20]:  # Limit to 20 children
                    child_state = {
                        "tag": child.name,
                        "semantic_attributes": {},
                        "text": child.get_text(strip=True)[:100] if child.get_text(strip=True) else ""
                    }
                    
                    for attr, value in child.attrs.items():
                        if attr.startswith('data-tekton-'):
                            child_state["semantic_attributes"][attr.replace('data-tekton-', '')] = value
                    
                    component_state["children"].append(child_state)
            
            result["state_inspection"] = component_state
            result["file_path"] = component_path
            
        else:
            # Try to find component by name first
            selectors = [
                f'[data-tekton-component="{component}"]',
                f'[data-tekton-area="{component}"]',
                f'#{component}-component',
                component  # Allow direct selector
            ]
            
            element = None
            for selector in selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        result["found_with_selector"] = selector
                        break
                except:
                    continue
            
            if not element:
                result["error"] = f"Component '{component}' not found"
                return result
            
            # Get component state
            component_state = await element.evaluate("""
            (el, maxDepth) => {
                function inspectElement(elem, depth = 0) {
                    if (depth > maxDepth) return null;
                    
                    const state = {
                        tag: elem.tagName.toLowerCase(),
                        semantic_attributes: {},
                        standard_attributes: {},
                        computed_state: {},
                        children: []
                    };
                    
                    // Get all attributes
                    for (const attr of elem.attributes) {
                        if (attr.name.startsWith('data-tekton-')) {
                            state.semantic_attributes[attr.name.replace('data-tekton-', '')] = attr.value;
                        } else if (['id', 'class', 'name', 'type', 'href', 'src'].includes(attr.name)) {
                            state.standard_attributes[attr.name] = attr.value;
                        }
                    }
                    
                    // Get computed state
                    state.computed_state = {
                        visible: elem.offsetWidth > 0 && elem.offsetHeight > 0,
                        enabled: !elem.disabled,
                        focus: elem === document.activeElement,
                        contentEditable: elem.contentEditable === 'true',
                        hasListeners: typeof elem.onclick === 'function' || elem.hasAttribute('onclick')
                    };
                    
                    // Get form state if applicable
                    if (elem.tagName === 'INPUT' || elem.tagName === 'SELECT' || elem.tagName === 'TEXTAREA') {
                        state.form_state = {
                            value: elem.value,
                            checked: elem.checked,
                            selected: elem.selected,
                            defaultValue: elem.defaultValue
                        };
                    }
                    
                    // Inspect children if requested
                    if (depth < maxDepth) {
                        const semanticChildren = elem.querySelectorAll('[data-tekton-component], [data-tekton-area], [data-tekton-action], [data-tekton-state]');
                        for (const child of semanticChildren) {
                            const childState = inspectElement(child, depth + 1);
                            if (childState) {
                                state.children.push(childState);
                            }
                        }
                    }
                    
                    return state;
                }
                
                return inspectElement(el, 0);
            }
            """, max_depth)
            
            result["state_inspection"] = component_state
        
        # Analyze semantic coverage (works for both sources)
        coverage = await analyze_semantic_coverage(result["state_inspection"])
        result["semantic_coverage"] = coverage
        
        # Detect data flows
        data_flows = await detect_data_flows(page, component)
        result["data_flows"] = data_flows
        
        # Get loading state if present
        loading_state = component_state["semantic_attributes"].get("loading-state")
        if loading_state:
            result["loading_info"] = {
                "state": loading_state,
                "component": component_state["semantic_attributes"].get("loading-component"),
                "started": component_state["semantic_attributes"].get("loading-started"),
                "error": component_state["semantic_attributes"].get("loading-error")
            }
        
        # Summary
        result["summary"] = {
            "total_semantic_attributes": len(component_state["semantic_attributes"]),
            "child_components": len(component_state["children"]),
            "has_actions": any(attr.startswith("action") or attr.startswith("trigger") 
                             for attr in component_state["semantic_attributes"]),
            "is_interactive": component_state["computed_state"]["hasListeners"] or 
                            component_state["tag"] in ["button", "a", "input", "select", "textarea"]
        }
        
    except Exception as e:
        result["error"] = str(e)
        logger.error(f"State inspection error: {e}")
    
    return result


async def ui_discover_actions(
    area: str = "hephaestus",
    include_handlers: bool = True
) -> Dict[str, Any]:
    """
    Discover all available actions and interactions in an area
    
    Args:
        area: UI area to analyze
        include_handlers: Whether to detect event handlers
        
    Returns:
        Comprehensive list of available actions and their triggers
    """
    await browser_manager.initialize()
    page = await browser_manager.get_page()
    
    result = {
        "area": area,
        "actions": [],
        "triggers": [],
        "forms": [],
        "navigation": [],
        "summary": {}
    }
    
    try:
        # Discover semantic actions
        action_elements = await page.query_selector_all('[data-tekton-action]')
        for element in action_elements:
            action_info = {
                "action": await element.get_attribute("data-tekton-action"),
                "element": {
                    "tag": await element.evaluate("el => el.tagName.toLowerCase()"),
                    "text": await element.text_content(),
                    "id": await element.get_attribute("id"),
                    "class": await element.get_attribute("class")
                },
                "enabled": await element.is_enabled(),
                "visible": await element.is_visible()
            }
            
            # Get related attributes
            for attr in ["target", "payload", "confirm", "validation"]:
                value = await element.get_attribute(f"data-tekton-{attr}")
                if value:
                    action_info[attr] = value
            
            if include_handlers:
                has_handlers = await element.evaluate("""
                    el => {
                        const handlers = [];
                        if (el.onclick) handlers.push('onclick');
                        if (el.onsubmit) handlers.push('onsubmit');
                        if (el.onchange) handlers.push('onchange');
                        // Check for addEventListener (limited detection)
                        if (el.hasAttribute('data-has-listeners')) handlers.push('custom');
                        return handlers;
                    }
                """)
                if has_handlers:
                    action_info["handlers"] = has_handlers
            
            result["actions"].append(action_info)
        
        # Discover triggers
        trigger_elements = await page.query_selector_all('[data-tekton-trigger]')
        for element in trigger_elements:
            trigger_info = {
                "trigger": await element.get_attribute("data-tekton-trigger"),
                "element": await element.evaluate("el => ({ tag: el.tagName.toLowerCase(), id: el.id })"),
                "event_type": await element.get_attribute("data-tekton-event") or "click"
            }
            result["triggers"].append(trigger_info)
        
        # Discover forms
        form_elements = await page.query_selector_all('form, [data-tekton-form]')
        for form in form_elements:
            form_info = {
                "name": await form.get_attribute("data-tekton-form") or await form.get_attribute("name"),
                "action": await form.get_attribute("action"),
                "method": await form.get_attribute("method") or "GET",
                "fields": []
            }
            
            # Get form fields
            fields = await form.query_selector_all('input, select, textarea')
            for field in fields[:10]:  # Limit to 10 fields
                field_info = {
                    "name": await field.get_attribute("name"),
                    "type": await field.get_attribute("type") or "text",
                    "required": await field.get_attribute("required") is not None,
                    "semantic_name": await field.get_attribute("data-tekton-input")
                }
                form_info["fields"].append(field_info)
            
            result["forms"].append(form_info)
        
        # Discover navigation
        nav_elements = await page.query_selector_all('[data-tekton-nav-item], [data-tekton-link]')
        for nav in nav_elements:
            nav_info = {
                "target": await nav.get_attribute("data-tekton-nav-target") or 
                         await nav.get_attribute("data-tekton-link"),
                "text": await nav.text_content(),
                "state": await nav.get_attribute("data-tekton-state") or "inactive",
                "type": "navigation" if await nav.get_attribute("data-tekton-nav-item") else "link"
            }
            result["navigation"].append(nav_info)
        
        # Create summary
        result["summary"] = {
            "total_actions": len(result["actions"]),
            "total_triggers": len(result["triggers"]),
            "total_forms": len(result["forms"]),
            "total_navigation": len(result["navigation"]),
            "action_types": list(set(a["action"] for a in result["actions"])),
            "trigger_types": list(set(t["trigger"] for t in result["triggers"]))
        }
        
        # Group actions by type
        action_groups = {}
        for action in result["actions"]:
            action_type = action["action"]
            if action_type not in action_groups:
                action_groups[action_type] = []
            action_groups[action_type].append(action)
        result["actions_by_type"] = action_groups
        
    except Exception as e:
        result["error"] = str(e)
        logger.error(f"Action discovery error: {e}")
    
    return result


async def ui_map_relationships(
    root_component: Optional[str] = None,
    max_levels: int = 3
) -> Dict[str, Any]:
    """
    Map component relationships and hierarchy
    
    Args:
        root_component: Starting component (None for full UI)
        max_levels: Maximum levels to traverse
        
    Returns:
        Component relationship map with parent-child relationships
    """
    await browser_manager.initialize()
    page = await browser_manager.get_page()
    
    result = {
        "root": root_component or "hephaestus",
        "hierarchy": {},
        "relationships": [],
        "component_map": {},
        "summary": {}
    }
    
    try:
        # Build component hierarchy
        hierarchy = await page.evaluate("""
            (rootComponent, maxLevels) => {
                const visited = new Set();
                const relationships = [];
                
                function findComponents(element, level = 0, parent = null) {
                    if (level > maxLevels) return null;
                    
                    const component = element.getAttribute('data-tekton-component') || 
                                    element.getAttribute('data-tekton-area');
                    
                    if (!component) {
                        // Look for children with components
                        const children = [];
                        for (const child of element.children) {
                            const childResult = findComponents(child, level, parent);
                            if (childResult) children.push(childResult);
                        }
                        return children.length > 0 ? { children } : null;
                    }
                    
                    // Skip if already visited
                    const id = component + '_' + level;
                    if (visited.has(id)) return null;
                    visited.add(id);
                    
                    // Record relationship
                    if (parent) {
                        relationships.push({
                            parent: parent,
                            child: component,
                            type: 'contains'
                        });
                    }
                    
                    const node = {
                        component: component,
                        type: element.getAttribute('data-tekton-type') || 'component',
                        attributes: {},
                        children: [],
                        metrics: {
                            depth: level,
                            childCount: 0
                        }
                    };
                    
                    // Get semantic attributes
                    for (const attr of element.attributes) {
                        if (attr.name.startsWith('data-tekton-')) {
                            node.attributes[attr.name.replace('data-tekton-', '')] = attr.value;
                        }
                    }
                    
                    // Find child components
                    const childElements = element.querySelectorAll('[data-tekton-component], [data-tekton-area]');
                    for (const child of childElements) {
                        if (child !== element && element.contains(child)) {
                            const childNode = findComponents(child, level + 1, component);
                            if (childNode && childNode.component) {
                                node.children.push(childNode);
                                node.metrics.childCount++;
                            }
                        }
                    }
                    
                    return node;
                }
                
                // Start from root or document
                let startElement;
                if (rootComponent) {
                    startElement = document.querySelector(`[data-tekton-component="${rootComponent}"], [data-tekton-area="${rootComponent}"]`);
                } else {
                    startElement = document.body;
                }
                
                const hierarchy = findComponents(startElement, 0);
                
                // Find cross-references (non-hierarchical relationships)
                const allComponents = document.querySelectorAll('[data-tekton-component], [data-tekton-area]');
                allComponents.forEach(comp => {
                    const component = comp.getAttribute('data-tekton-component') || 
                                   comp.getAttribute('data-tekton-area');
                    
                    // Check for references to other components
                    const target = comp.getAttribute('data-tekton-target');
                    const source = comp.getAttribute('data-tekton-source');
                    const triggers = comp.getAttribute('data-tekton-triggers');
                    
                    if (target) {
                        relationships.push({
                            source: component,
                            target: target,
                            type: 'targets'
                        });
                    }
                    if (source) {
                        relationships.push({
                            source: source,
                            target: component,
                            type: 'sources_from'
                        });
                    }
                    if (triggers) {
                        relationships.push({
                            source: component,
                            target: triggers,
                            type: 'triggers'
                        });
                    }
                });
                
                return { hierarchy, relationships };
            }
        """, root_component, max_levels)
        
        result["hierarchy"] = hierarchy["hierarchy"]
        result["relationships"] = hierarchy["relationships"]
        
        # Build flat component map
        component_map = {}
        
        def flatten_hierarchy(node, path=""):
            if not node:
                return
            
            if isinstance(node, dict) and "component" in node:
                comp_path = f"{path}/{node['component']}" if path else node["component"]
                component_map[node["component"]] = {
                    "path": comp_path,
                    "type": node.get("type", "component"),
                    "attributes": node.get("attributes", {}),
                    "child_count": node["metrics"]["childCount"],
                    "depth": node["metrics"]["depth"]
                }
                
                for child in node.get("children", []):
                    flatten_hierarchy(child, comp_path)
            elif isinstance(node, dict) and "children" in node:
                for child in node["children"]:
                    flatten_hierarchy(child, path)
        
        flatten_hierarchy(result["hierarchy"])
        result["component_map"] = component_map
        
        # Analyze relationships
        relationship_types = {}
        for rel in result["relationships"]:
            rel_type = rel["type"]
            if rel_type not in relationship_types:
                relationship_types[rel_type] = 0
            relationship_types[rel_type] += 1
        
        # Create summary
        result["summary"] = {
            "total_components": len(component_map),
            "max_depth": max(comp["depth"] for comp in component_map.values()) if component_map else 0,
            "relationship_types": relationship_types,
            "total_relationships": len(result["relationships"]),
            "root_components": [name for name, info in component_map.items() if info["depth"] == 0]
        }
        
        # Find isolated components (no relationships)
        all_components = set(component_map.keys())
        connected_components = set()
        for rel in result["relationships"]:
            if "parent" in rel:
                connected_components.add(rel["child"])
            if "source" in rel:
                connected_components.add(rel["source"])
                connected_components.add(rel["target"])
        
        isolated = all_components - connected_components
        if isolated:
            result["isolated_components"] = list(isolated)
        
    except Exception as e:
        result["error"] = str(e)
        logger.error(f"Relationship mapping error: {e}")
    
    return result


# Helper functions

async def analyze_semantic_coverage(component_state: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze semantic attribute coverage for a component"""
    coverage = {
        "categories": {
            "identity": False,
            "navigation": False,
            "state": False,
            "interaction": False,
            "layout": False,
            "data": False
        },
        "score": 0,
        "missing_recommended": []
    }
    
    attrs = component_state.get("semantic_attributes", {})
    
    # Check categories
    if any(attr in attrs for attr in ["id", "name", "component", "area"]):
        coverage["categories"]["identity"] = True
    
    if any(attr in attrs for attr in ["nav-item", "nav-target", "link"]):
        coverage["categories"]["navigation"] = True
        
    if any(attr in attrs for attr in ["state", "status", "loading-state"]):
        coverage["categories"]["state"] = True
        
    if any(attr in attrs for attr in ["action", "trigger", "form"]):
        coverage["categories"]["interaction"] = True
        
    if any(attr in attrs for attr in ["zone", "panel", "section"]):
        coverage["categories"]["layout"] = True
        
    if any(attr in attrs for attr in ["source", "target", "payload"]):
        coverage["categories"]["data"] = True
    
    # Calculate score
    covered = sum(1 for v in coverage["categories"].values() if v)
    coverage["score"] = covered / len(coverage["categories"])
    
    # Recommend missing attributes
    if not coverage["categories"]["identity"]:
        coverage["missing_recommended"].append("data-tekton-id or data-tekton-component")
    
    if component_state["tag"] in ["button", "a"] and not coverage["categories"]["interaction"]:
        coverage["missing_recommended"].append("data-tekton-action")
    
    return coverage


async def detect_data_flows(page: Page, component: str) -> List[Dict[str, Any]]:
    """Detect potential data flows for a component"""
    flows = []
    
    try:
        # Find elements that reference this component
        sources = await page.query_selector_all(f'[data-tekton-target="{component}"]')
        for source in sources:
            source_name = await source.get_attribute("data-tekton-component") or \
                         await source.get_attribute("data-tekton-area") or \
                         await source.get_attribute("id")
            flows.append({
                "type": "incoming",
                "source": source_name,
                "target": component,
                "mechanism": "target reference"
            })
        
        # Find elements this component targets
        element = await page.query_selector(f'[data-tekton-component="{component}"], [data-tekton-area="{component}"]')
        if element:
            target = await element.get_attribute("data-tekton-target")
            if target:
                flows.append({
                    "type": "outgoing",
                    "source": component,
                    "target": target,
                    "mechanism": "target reference"
                })
    except:
        pass
    
    return flows