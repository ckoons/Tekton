"""
HTML Processing Module for Hephaestus UI DevTools

This module contains all HTML parsing, analysis and processing functions
used by the UI DevTools to work with component HTML content.
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from bs4 import BeautifulSoup, Tag, NavigableString
from playwright.async_api import Page

from .constants import DANGEROUS_PATTERNS


def detect_dangerous_patterns(content: str) -> List[str]:
    """Detect dangerous patterns in content"""
    detected = []
    
    for category, patterns in DANGEROUS_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE):
                detected.append(f"{category}: {pattern}")
    
    return detected


def extract_element_info(element: Tag) -> Dict[str, Any]:
    """Extract relevant information from a BeautifulSoup element"""
    info = {
        "tag": element.name,
        "id": element.get("id"),
        "classes": element.get("class", []),
        "attributes": {}
    }
    
    # Extract relevant attributes
    for attr in ["href", "src", "alt", "title", "placeholder", "value", "type", "name", "data-component"]:
        if element.get(attr):
            info["attributes"][attr] = element.get(attr)
    
    # Extract text content
    text = element.get_text(strip=True)
    if text and len(text) < 200:
        info["text"] = text
    elif text:
        info["text"] = text[:200] + "..."
    
    return info


def suggest_similar_selectors(html: str, failed_selector: str, max_suggestions: int = 5) -> List[str]:
    """Suggest similar selectors when one fails to match"""
    soup = BeautifulSoup(html, 'html.parser')
    suggestions = []
    
    # Parse the failed selector to understand what was being looked for
    selector_lower = failed_selector.lower()
    
    # Extract key parts from the selector
    # Check if it's looking for an ID
    if failed_selector.startswith("#"):
        target_id = failed_selector[1:]
        # Find IDs that contain similar words
        for element in soup.find_all(id=True):
            elem_id = element.get("id", "")
            if target_id.lower() in elem_id.lower() or elem_id.lower() in target_id.lower():
                suggestions.append(f"#{elem_id}")
    
    # Check if it's looking for a class
    elif failed_selector.startswith("."):
        target_class = failed_selector[1:]
        # Find classes that contain similar words
        seen_classes = set()
        for element in soup.find_all(class_=True):
            for cls in element.get("class", []):
                if cls in seen_classes:
                    continue
                if target_class.lower() in cls.lower() or cls.lower() in target_class.lower():
                    suggestions.append(f".{cls}")
                    seen_classes.add(cls)
    
    # Check for data attributes
    elif "[data-" in failed_selector:
        # Extract data attribute name
        match = re.search(r'\[data-([^=\]]+)', failed_selector)
        if match:
            data_attr = f"data-{match.group(1)}"
            # Find all elements with data attributes
            for element in soup.find_all():
                for attr, value in element.attrs.items():
                    if attr.startswith("data-") and (data_attr in attr or attr in data_attr):
                        if value:
                            suggestions.append(f'[{attr}="{value}"]')
                        else:
                            suggestions.append(f'[{attr}]')
    
    # For any selector, also look for elements with similar text content or structure
    # Extract meaningful words from the selector
    words = re.findall(r'[a-zA-Z]+', failed_selector.lower())
    if words:
        # Look for elements containing these words in class, id, or data attributes
        for word in words:
            if len(word) > 2:  # Skip very short words
                # Check classes
                for element in soup.find_all(class_=re.compile(word, re.I)):
                    for cls in element.get("class", []):
                        if word in cls.lower():
                            suggestions.append(f".{cls}")
                
                # Check IDs
                for element in soup.find_all(id=re.compile(word, re.I)):
                    suggestions.append(f"#{element.get('id')}")
                
                # Check data attributes
                for element in soup.find_all():
                    for attr, value in element.attrs.items():
                        if attr.startswith("data-") and word in attr.lower():
                            if value:
                                suggestions.append(f'[{attr}="{value}"]')
    
    # Remove duplicates while preserving order
    seen = set()
    unique_suggestions = []
    for s in suggestions:
        if s not in seen and s != failed_selector:
            seen.add(s)
            unique_suggestions.append(s)
    
    # If we have very few suggestions, add some generic ones based on the area
    if len(unique_suggestions) < 3:
        # Add common structural selectors
        for element in soup.find_all(['header', 'nav', 'main', 'footer', 'section', 'article', 'div']):
            if element.get('class'):
                for cls in element.get('class'):
                    if cls not in seen:
                        unique_suggestions.append(f".{cls}")
                        seen.add(cls)
            if element.get('id'):
                id_sel = f"#{element.get('id')}"
                if id_sel not in seen:
                    unique_suggestions.append(id_sel)
                    seen.add(id_sel)
        
        # Also look for any data-tekton attributes as fallback
        def has_data_tekton_attrs(attrs):
            """Check if element has any data-tekton attributes"""
            if not attrs:
                return False
            return any(k.startswith('data-tekton') for k in attrs.keys())
        
        for element in soup.find_all(attrs=has_data_tekton_attrs):
            for attr, value in element.attrs.items():
                if attr.startswith('data-tekton') and value:
                    attr_sel = f'[{attr}="{value}"]'
                    if attr_sel not in seen and len(unique_suggestions) < max_suggestions:
                        unique_suggestions.append(attr_sel)
                        seen.add(attr_sel)
    
    return unique_suggestions[:max_suggestions]


def count_elements_in_tree(element_data: Dict[str, Any]) -> int:
    """Recursively count all elements in a tree structure"""
    count = 1  # Count this element
    if "children" in element_data:
        for child in element_data["children"]:
            count += count_elements_in_tree(child)
    return count


def html_to_structured_data(html: str, selector: Optional[str] = None, max_depth: int = 3) -> Dict[str, Any]:
    """Convert HTML to structured data representation with proper DOM traversal"""
    soup = BeautifulSoup(html, 'html.parser')
    
    # If selector provided, find matching elements
    if selector:
        try:
            # Use CSS select for better selector support
            elements = soup.select(selector)
        except:
            # Fallback for simple selectors
            if selector.startswith("#"):
                element = soup.find(id=selector[1:])
                elements = [element] if element else []
            elif selector.startswith("."):
                elements = soup.find_all(class_=selector[1:])
            else:
                elements = soup.find_all(selector)
        
        # If no elements found, provide helpful suggestions
        if not elements:
            suggestions = suggest_similar_selectors(html, selector)
            return {
                "element_count": 0,
                "elements": [],
                "selector_not_found": True,
                "failed_selector": selector,
                "suggestions": suggestions,
                "suggestion_message": f"No matches for '{selector}'. Try: " + ", ".join(suggestions) if suggestions else f"No matches for '{selector}'. No similar selectors found."
            }
    else:
        # Get the root element (body or document)
        root = soup.body if soup.body else soup
        elements = [root]
    
    def extract_element_tree(element: Tag, depth: int = 0) -> Dict[str, Any]:
        """Recursively extract element information"""
        if not isinstance(element, Tag) or depth > max_depth:
            return None
            
        info = {
            "tag": element.name,
            "id": element.get("id"),
            "classes": element.get("class", []),
            "attributes": {}
        }
        
        # Extract data attributes and other relevant attributes
        for attr_name, attr_value in element.attrs.items():
            if attr_name.startswith("data-") or attr_name in ["href", "src", "alt", "title", "placeholder", "value", "type", "name"]:
                info["attributes"][attr_name] = attr_value
        
        # Get direct text content (not from children)
        direct_text = "".join([str(s) for s in element.children if isinstance(s, NavigableString)]).strip()
        if direct_text:
            info["text"] = direct_text[:100] + "..." if len(direct_text) > 100 else direct_text
        
        # Process children
        child_elements = [child for child in element.children if isinstance(child, Tag)]
        if child_elements and depth < max_depth:
            info["children"] = []
            for child in child_elements[:10]:  # Limit to 10 children per level
                child_info = extract_element_tree(child, depth + 1)
                if child_info:
                    info["children"].append(child_info)
        else:
            info["child_count"] = len(child_elements)
        
        return info
    
    # Build the structured result
    result = {
        "element_count": len(elements),  # This is the count of root elements
        "elements": []
    }
    
    for element in elements:
        if isinstance(element, Tag):
            el_tree = extract_element_tree(element)
            if el_tree:
                result["elements"].append(el_tree)
    
    # Calculate the TOTAL element count when no selector is provided
    if not selector and result["elements"]:
        total_count = sum(count_elements_in_tree(el) for el in result["elements"])
        result["total_element_count"] = total_count
        # For backward compatibility, update element_count to show the real total
        result["element_count"] = total_count
        result["root_element_count"] = len(elements)  # Preserve original count as well
    
    return result


async def analyze_dynamic_content(page: Page, area: str, html: str) -> Dict[str, Any]:
    """
    Phase 1: Analyze content for dynamic loading patterns and provide intelligent routing
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    analysis = {
        "content_type": "static",  # static|dynamic|hybrid
        "confidence": 0.0,
        "dynamic_areas": [],
        "devtools_suitable": [],
        "file_editing_recommended": [],
        "recommendation": "devtools",  # devtools|file_editing|hybrid
        "reasoning": ""
    }
    
    # Detect dynamic content indicators
    dynamic_indicators = {
        "javascript_loading": 0,
        "empty_containers": 0,
        "component_scripts": 0,
        "async_content": 0
    }
    
    # Check for JavaScript-loaded content
    scripts = soup.find_all("script")
    for script in scripts:
        src = script.get("src", "")
        content = script.string or ""
        
        # Component-specific scripts indicate dynamic loading
        if area in src or f"{area}-component" in src:
            dynamic_indicators["component_scripts"] += 1
        
        # Look for loading patterns in script content
        if any(keyword in content for keyword in ["innerHTML", "appendChild", "createElement", "fetch"]):
            dynamic_indicators["javascript_loading"] += 1
    
    # Check for empty containers that should have content
    empty_containers = soup.find_all(attrs={"data-tekton-area": True})
    for container in empty_containers:
        if not container.get_text(strip=True) and len(container.find_all()) < 3:
            dynamic_indicators["empty_containers"] += 1
            
            # Identify specific dynamic area
            tekton_area = container.get("data-tekton-area")
            if tekton_area:
                analysis["dynamic_areas"].append({
                    "selector": f'[data-tekton-area="{tekton_area}"]',
                    "reason": "Empty container with semantic tags - likely JavaScript populated",
                    "file_location": f"{tekton_area}-component.html"
                })
    
    # Check for loading indicators
    def has_loading_class(class_attr):
        """Check if element has loading or spinner class"""
        if not class_attr:
            return False
        class_str = ' '.join(class_attr) if isinstance(class_attr, list) else str(class_attr)
        return "loading" in class_str or "spinner" in class_str
    
    loading_elements = soup.find_all(class_=has_loading_class)
    if loading_elements:
        dynamic_indicators["async_content"] += len(loading_elements)
    
    # Score dynamic content (higher score = more dynamic)
    dynamic_score = sum(dynamic_indicators.values())
    
    # Determine content type based on score
    if dynamic_score == 0:
        analysis["content_type"] = "static"
        analysis["confidence"] = 0.9
        analysis["recommendation"] = "devtools"
        analysis["reasoning"] = "Content appears to be static HTML - DevTools will work perfectly"
    elif dynamic_score <= 2:
        analysis["content_type"] = "hybrid"
        analysis["confidence"] = 0.7
        analysis["recommendation"] = "devtools"
        analysis["reasoning"] = "Some dynamic content detected but DevTools should still be effective"
    else:
        analysis["content_type"] = "dynamic"
        analysis["confidence"] = 0.8
        analysis["recommendation"] = "file_editing"
        analysis["reasoning"] = f"High dynamic content score ({dynamic_score}) - recommend editing component files directly"
    
    # Build specific recommendations
    # Find elements suitable for DevTools manipulation
    interactive_elements = soup.find_all(['button', 'input', 'select', 'textarea', 'a'])
    for elem in interactive_elements[:5]:  # Limit to avoid too much output
        if elem.get_text(strip=True) or elem.get("placeholder"):
            analysis["devtools_suitable"].append({
                "selector": _get_best_selector(elem),
                "type": elem.name,
                "description": elem.get_text(strip=True)[:50] or elem.get("placeholder", "")
            })
    
    # Identify static text elements that can be modified
    def is_suitable_text(text):
        """Check if text is suitable for modification (not too short or too long)"""
        if not text:
            return False
        stripped = text.strip()
        return len(stripped) > 10 and len(stripped) < 100
    
    text_elements = soup.find_all(text=is_suitable_text)
    for text_elem in text_elements[:5]:
        parent = text_elem.parent
        if parent and parent.name not in ['script', 'style']:
            analysis["devtools_suitable"].append({
                "selector": _get_best_selector(parent),
                "type": "text",
                "description": text_elem.strip()[:50]
            })
    
    # For file editing recommendations, identify component structure
    if analysis["content_type"] in ["dynamic", "hybrid"]:
        # Look for component markers
        component_divs = soup.find_all(attrs={"data-component": True})
        for comp in component_divs:
            comp_name = comp.get("data-component")
            if comp_name:
                analysis["file_editing_recommended"].append({
                    "file": f"ui/components/{comp_name}/{comp_name}-component.html",
                    "reason": "Component HTML template file",
                    "selector": f'[data-component="{comp_name}"]'
                })
        
        # Add JavaScript file recommendations if heavy dynamic content
        if dynamic_indicators["component_scripts"] > 0:
            analysis["file_editing_recommended"].append({
                "file": f"ui/scripts/{area}/{area}-component.js",
                "reason": "Component JavaScript logic",
                "indicators": f"{dynamic_indicators['component_scripts']} component scripts detected"
            })
    
    return analysis


def _get_best_selector(element: Tag) -> str:
    """Get the most specific selector for an element"""
    # Prefer ID
    if element.get("id"):
        return f"#{element.get('id')}"
    
    # Then data-tekton attributes
    for attr, value in element.attrs.items():
        if attr.startswith("data-tekton") and value:
            return f'[{attr}="{value}"]'
    
    # Then specific classes
    classes = element.get("class", [])
    if classes:
        # Prefer semantic classes
        for cls in classes:
            if any(keyword in cls for keyword in ["nav", "header", "content", "footer", "title", "button", "input"]):
                return f".{cls}"
        # Fall back to first class
        return f".{classes[0]}"
    
    # Finally, tag with context
    parent = element.parent
    if parent and parent.get("id"):
        return f"#{parent.get('id')} > {element.name}"
    elif parent and parent.get("class"):
        return f".{parent.get('class')[0]} > {element.name}"
    
    return element.name