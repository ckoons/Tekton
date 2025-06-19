"""
Enhanced help content for UI DevTools based on real pain points
"""

COMMON_PATTERNS_HELP = {
    "title": "Common Patterns That Actually Work",
    "explanation": "Based on real experience, here are the patterns that work reliably",
    
    "the_golden_workflow": {
        "title": "🏆 The Golden Workflow (Use This!)",
        "steps": [
            "1. Navigate to component: await ui_navigate(component='hermes')",
            "2. Wait for load: await asyncio.sleep(1)",
            "3. Capture CONTENT area: await ui_capture(area='content')",
            "4. Modify CONTENT area: await ui_sandbox(area='content', changes=[...])",
            "5. Screenshot to verify: await ui_screenshot(component='hermes')"
        ],
        "example": """# Complete working example
await ui_navigate(component="hermes")
await asyncio.sleep(1)  # Yes, it's ugly but necessary
capture = await ui_capture(area="content")  # NOT area="hermes"!
await ui_sandbox(
    area="content",  # Always content for component mods!
    changes=[{
        "selector": ".hermes__header",
        "content": '<div class="status">🟢 Connected</div>',
        "action": "append"
    }],
    preview=False
)
screenshot = await ui_screenshot(component="hermes", save_to_file=True)""",
        "why_this_works": "Navigate loads the component INTO the content area. Always modify content, not the component name!"
    },
    
    "component_vs_area_confusion": {
        "title": "❗ Component vs Area - The #1 Source of Pain",
        "the_problem": "Component names (hermes, rhetor) are BOTH navigation targets AND area names!",
        "the_solution": {
            "navigate_to": "component (hermes, rhetor, etc.)",
            "capture_from": "area='content' after navigation",
            "never_do": "ui_capture(area='hermes') - this gets the nav button!"
        },
        "visual_explanation": """
Navigation Panel          Content Area
┌─────────────┐          ┌────────────────┐
│ [Rhetor]    │          │                │
│ [Hermes] ←──┼─click───>│ Hermes Content │ ← Capture THIS
│ [Apollo]    │          │                │
└─────────────┘          └────────────────┘
   area="hermes"            area="content"
   (nav button)             (actual component)
""",
        "remember": "After navigation, ALWAYS use area='content' for the actual component!"
    },
    
    "response_structure": {
        "title": "📦 Finding Data in Responses",
        "the_maze": "Response data is nested deeper than you think!",
        "structure_map": {
            "capture_elements": 'result["result"]["structure"]["elements"]',
            "screenshot_path": 'result["result"]["file_path"]',
            "loaded_component": 'result["result"]["loaded_component"]',
            "html_content": 'result["result"]["html"]'
        },
        "example": """# Getting elements from capture
capture = await ui_capture(area="content")
# WRONG: elements = capture["elements"]
# WRONG: elements = capture["result"]["elements"]
# RIGHT:
elements = capture["result"]["structure"]["elements"]""",
        "pro_tip": "Always check result['status'] == 'success' first!"
    },
    
    "debugging_workflow": {
        "title": "🔍 When Things Don't Work",
        "steps": [
            "1. Check what's loaded: capture = await ui_capture(area='content')",
            "2. Look at loaded_component: capture['result']['loaded_component']",
            "3. Search HTML for your component: 'hermes' in capture['result']['html']",
            "4. Try ui_workflow for debugging: await ui_workflow(workflow='debug_component', component='hermes')"
        ],
        "common_issues": {
            "Component not loading": "Navigation succeeded but content didn't change - wait longer",
            "Selector not found": "Component might not be loaded, or selector is wrong",
            "Changes not visible": "Make sure preview=False and you're modifying the right area"
        }
    },
    
    "new_workflow_tool": {
        "title": "✨ NEW: ui_workflow - The Easy Way!",
        "explanation": "Tired of the confusion? Use ui_workflow to do it all automatically!",
        "example": """# Old way: 7+ steps with confusion
# New way: One command that just works!

result = await ui_workflow(
    workflow="modify_component",
    component="hermes",
    changes=[{
        "selector": ".hermes__header",
        "content": '<div class="status">🟢 Connected</div>',
        "action": "append"
    }]
)

# It automatically:
# - Navigates to the component
# - Waits for it to load
# - Uses the RIGHT area (content)
# - Takes before/after screenshots
# - Provides clear feedback""",
        "available_workflows": [
            "modify_component - Make changes to a component",
            "add_to_component - Add new elements",
            "verify_component - Quick verification",
            "debug_component - Smart debugging"
        ]
    }
}

def get_enhanced_help(topic: str = None):
    """Get enhanced help content based on topic"""
    if topic == "patterns" or topic == "common":
        return COMMON_PATTERNS_HELP
    
    # Quick reference card
    if topic == "quick":
        return {
            "title": "🎯 Quick Reference - Copy & Paste These!",
            "navigate": "await ui_navigate(component='hermes')",
            "wait": "await asyncio.sleep(1)",
            "capture": "await ui_capture(area='content')",
            "modify": "await ui_sandbox(area='content', changes=[...])",
            "screenshot": "await ui_screenshot(component='hermes', save_to_file=True)",
            "elements": "capture['result']['structure']['elements']",
            "new_way": "await ui_workflow(workflow='modify_component', component='hermes', changes=[...])"
        }
    
    return None