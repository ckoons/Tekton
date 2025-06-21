"""
Analyze Tools Module for Hephaestus UI DevTools

This module contains functions for analyzing UI structure, detecting frameworks,
assessing complexity, and providing recommendations.
"""

from typing import Dict, Any
from bs4 import BeautifulSoup

from .constants import HEPHAESTUS_URL, UI_COMPONENTS, ComponentNotFoundError
from .browser_manager import browser_manager
from .navigation_tools import find_component_element


async def ui_analyze(
    area: str = "hephaestus",
    deep_scan: bool = False
) -> Dict[str, Any]:
    """
    Analyze UI structure and patterns
    
    Args:
        area: UI area to analyze
        deep_scan: Whether to perform deep analysis
    
    Returns:
        Analysis of UI structure, patterns, and recommendations
    """
    await browser_manager.initialize()
    page = await browser_manager.get_page()
    
    result = {
        "area": area,
        "ui_url": HEPHAESTUS_URL,
        "analysis": {}
    }
    
    # Get HTML for the area
    if area == "hephaestus":
        html = await page.content()
    else:
        try:
            element = await find_component_element(page, area)
            html = await element.inner_html()
        except ComponentNotFoundError as e:
            result["error"] = str(e)
            return result
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Analyze structure
    structure_analysis = {
        "total_elements": len(soup.find_all()),
        "forms": len(soup.find_all("form")),
        "inputs": len(soup.find_all(["input", "textarea", "select"])),
        "buttons": len(soup.find_all(["button", "input[type='button']", "input[type='submit']"])),
        "links": len(soup.find_all("a")),
        "images": len(soup.find_all("img")),
        "tables": len(soup.find_all("table")),
        "divs": len(soup.find_all("div")),
        "sections": len(soup.find_all(["section", "article", "aside", "nav", "header", "footer"]))
    }
    result["analysis"]["structure"] = structure_analysis
    
    # Detect frameworks and libraries
    framework_detection = {
        "react": False,
        "vue": False,
        "angular": False,
        "jquery": False,
        "bootstrap": False,
        "tailwind": False
    }
    
    # Check for framework indicators
    scripts = soup.find_all("script")
    for script in scripts:
        src = script.get("src", "")
        text = script.string or ""
        
        if "react" in src.lower() or "React" in text:
            framework_detection["react"] = True
        if "vue" in src.lower() or "Vue" in text:
            framework_detection["vue"] = True
        if "angular" in src.lower() or "angular" in text:
            framework_detection["angular"] = True
        if "jquery" in src.lower() or "$(" in text or "jQuery" in text:
            framework_detection["jquery"] = True
    
    result["analysis"]["frameworks"] = framework_detection
    
    # Component-specific insights
    if area != "hephaestus":
        component_info = {
            "area_name": area,
            "description": UI_COMPONENTS[area]["description"],
            "suggested_selectors": UI_COMPONENTS[area]["selectors"],
            "found": True
        }
        result["analysis"]["component_info"] = component_info
    
    # Complexity assessment
    complexity_score = 0
    complexity_factors = []
    
    if any(framework_detection.values()):
        complexity_score += 10
        complexity_factors.append("Frameworks detected")
    
    if structure_analysis["total_elements"] > 1000:
        complexity_score += 2
        complexity_factors.append(f"Large DOM ({structure_analysis['total_elements']} elements)")
    
    result["analysis"]["complexity"] = {
        "score": complexity_score,
        "level": "high" if complexity_score >= 10 else "medium" if complexity_score >= 5 else "low",
        "factors": complexity_factors
    }
    
    # Recommendations
    recommendations = []
    
    if any(framework_detection.values()):
        recommendations.append({
            "type": "warning",
            "message": "Frameworks detected. Avoid adding more complexity.",
            "frameworks": [k for k, v in framework_detection.items() if v]
        })
    
    recommendations.append({
        "type": "info",
        "message": f"Working in '{area}' area. Use selectors like: {', '.join(UI_COMPONENTS.get(area, {}).get('selectors', [])[:2])}"
    })
    
    result["recommendations"] = recommendations
    
    return result