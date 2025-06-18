"""
Sandbox Tools Module for Hephaestus UI DevTools

This module contains functions for testing UI changes in a sandboxed environment,
allowing preview and validation before applying changes.
"""

from typing import Dict, List, Any

from .browser_manager import browser_manager
from .html_processor import detect_dangerous_patterns, html_to_structured_data


async def ui_sandbox(
    area: str,
    changes: List[Dict[str, Any]],
    preview: bool = True
) -> Dict[str, Any]:
    """
    Test UI changes in a sandboxed environment
    
    Args:
        area: UI area to modify (use 'hephaestus' for general changes)
        changes: List of changes to apply
        preview: Whether to preview changes without applying
    
    Returns:
        Result of sandbox testing including validation
    """
    await browser_manager.initialize()
    page = await browser_manager.get_page()
    
    result = {
        "area": area,
        "changes": changes,
        "preview": preview,
        "validations": []
    }
    
    # Validate changes for dangerous patterns
    for i, change in enumerate(changes):
        change_content = change.get("content", "")
        detected = detect_dangerous_patterns(change_content)
        
        if detected:
            result["validations"].append({
                "change_index": i,
                "status": "rejected",
                "reason": "Dangerous patterns detected",
                "patterns": detected
            })
            
            result["applied"] = False
            result["error"] = "Changes rejected due to framework/complexity detection"
            return result
    
    # Create snapshot
    original_html = await page.content()
    result["original_snapshot"] = html_to_structured_data(original_html)
    
    # Apply changes
    sandbox_results = []
    
    for i, change in enumerate(changes):
        change_type = change.get("type", "html")
        selector = change.get("selector")
        content = change.get("content", "")
        action = change.get("action", "replace")
        
        try:
            if change_type in ["html", "text"]:
                # Escape content and selector properly
                escaped_content = content.replace('\\', '\\\\').replace('`', '\\`').replace('${', '\\${')
                escaped_selector = selector.replace('\\', '\\\\').replace("'", "\\'")
                
                js_code = f"""
                (function() {{
                    const elements = document.querySelectorAll('{escaped_selector}');
                    if (elements.length === 0) {{
                        // Enhanced error message with file editing guidance
                        return {{ 
                            success: false, 
                            error: 'No elements found for selector: {escaped_selector}',
                            guidance: 'Element not visible to DevTools - try file editing: {area}-component.html'
                        }};
                    }}
                    
                    elements.forEach(el => {{
                        const content = `{escaped_content}`;
                        
                        switch('{action}') {{
                            case 'replace':
                                {f'el.textContent = content;' if change_type == 'text' else 'el.innerHTML = content;'}
                                break;
                            case 'append':
                                {f'el.textContent += content;' if change_type == 'text' else 'el.innerHTML += content;'}
                                break;
                            case 'prepend':
                                {f'el.textContent = content + el.textContent;' if change_type == 'text' else 'el.innerHTML = content + el.innerHTML;'}
                                break;
                            case 'after':
                                el.insertAdjacentHTML('afterend', {'`<span>${content}</span>`' if change_type == 'text' else 'content'});
                                break;
                            case 'before':
                                el.insertAdjacentHTML('beforebegin', {'`<span>${content}</span>`' if change_type == 'text' else 'content'});
                                break;
                        }}
                    }});
                    
                    return {{ success: true, count: elements.length }};
                }})();
                """
                
                result_js = await page.evaluate(js_code)
                sandbox_results.append({
                    "change_index": i,
                    "success": result_js.get("success", False),
                    "elements_modified": result_js.get("count", 0),
                    "error": result_js.get("error"),
                    "guidance": result_js.get("guidance")  # Phase 1: Enhanced error guidance
                })
            
            elif change_type == "css":
                # Support both full CSS rules and single property changes
                if "property" in change and "value" in change:
                    # Single property format
                    css_rule = f"{selector} {{ {change['property']}: {change['value']}; }}"
                else:
                    # Full CSS content
                    css_rule = content
                
                await page.add_style_tag(content=css_rule)
                sandbox_results.append({
                    "change_index": i,
                    "success": True,
                    "type": "css_injected",
                    "css": css_rule
                })
            
            elif change_type == "js":
                if detect_dangerous_patterns(content):
                    sandbox_results.append({
                        "change_index": i,
                        "success": False,
                        "error": "JavaScript contains framework/build tool references"
                    })
                else:
                    await page.evaluate(content)
                    sandbox_results.append({
                        "change_index": i,
                        "success": True,
                        "type": "js_executed"
                    })
        
        except Exception as e:
            sandbox_results.append({
                "change_index": i,
                "success": False,
                "error": str(e)
            })
    
    result["sandbox_results"] = sandbox_results
    
    # Capture final state
    final_html = await page.content()
    result["final_snapshot"] = html_to_structured_data(final_html)
    
    # If preview mode, restore
    if preview:
        await page.set_content(original_html)
        result["restored"] = True
    else:
        result["applied"] = True
    
    # Summary
    successful = sum(1 for r in sandbox_results if r.get("success", False))
    result["summary"] = {
        "total_changes": len(changes),
        "successful": successful,
        "failed": len(changes) - successful
    }
    
    return result