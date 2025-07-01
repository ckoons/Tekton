#!/usr/bin/env python3
"""
Build simplified index.html by inlining all components
"""

import os
import re
from pathlib import Path

# Component list in order they appear in navigation
COMPONENTS = [
    'numa', 'tekton', 'prometheus', 'telos', 'metis', 'harmonia', 
    'synthesis', 'athena', 'sophia', 'noesis', 'engram', 'apollo', 
    'rhetor', 'budget', 'hermes', 'ergon', 'terma', 'profile', 'settings'
]

# Component metadata
COMPONENT_INFO = {
    'numa': {'title': 'Numa', 'subtitle': 'Companion', 'color': '#9C27B0'},
    'tekton': {'title': 'Tekton', 'subtitle': 'Projects', 'color': '#FBBC05'},
    'prometheus': {'title': 'Prometheus', 'subtitle': 'Planning', 'color': '#C2185B'},
    'telos': {'title': 'Telos', 'subtitle': 'Requirements', 'color': '#00796B'},
    'metis': {'title': 'Metis', 'subtitle': 'Workflows', 'color': '#00BFA5'},
    'harmonia': {'title': 'Harmonia', 'subtitle': 'Orchestration', 'color': '#F57C00'},
    'synthesis': {'title': 'Synthesis', 'subtitle': 'Integration', 'color': '#3949AB'},
    'athena': {'title': 'Athena', 'subtitle': 'Knowledge', 'color': '#7B1FA2'},
    'sophia': {'title': 'Sophia', 'subtitle': 'Learning', 'color': '#7CB342'},
    'noesis': {'title': 'Noesis', 'subtitle': 'Discovery', 'color': '#FF6F00'},
    'engram': {'title': 'Engram', 'subtitle': 'Memory', 'color': '#34A853'},
    'apollo': {'title': 'Apollo', 'subtitle': 'Attention/Prediction', 'color': '#FFD600'},
    'rhetor': {'title': 'Rhetor', 'subtitle': 'LLM/Prompt/Context', 'color': '#D32F2F'},
    'budget': {'title': 'Penia', 'subtitle': 'LLM Cost', 'color': '#34A853'},
    'hermes': {'title': 'Hermes', 'subtitle': 'Messages/Data', 'color': '#4285F4'},
    'ergon': {'title': 'Ergon', 'subtitle': 'Agents/Tools/MCP', 'color': '#0097A7'},
    'terma': {'title': 'Terma', 'subtitle': 'Terminal', 'color': '#5D4037'},
    'profile': {'title': 'Profile', 'subtitle': 'Profile', 'color': '#757575', 'icon': '👤'},
    'settings': {'title': 'Settings', 'subtitle': 'Settings', 'color': '#757575', 'icon': '⚙️'}
}

def read_component(component_name):
    """Read component HTML and extract parts"""
    component_path = Path(f"components/{component_name}/{component_name}-component.html")
    if not component_path.exists():
        print(f"Warning: {component_path} not found")
        return None
    
    content = component_path.read_text()
    
    # Extract styles
    style_match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
    styles = style_match.group(1) if style_match else ''
    
    # Extract script
    script_match = re.search(r'<script>(.*?)</script>', content, re.DOTALL)
    script = script_match.group(1) if script_match else ''
    
    # Remove style and script tags from HTML
    html = re.sub(r'<style>.*?</style>', '', content, flags=re.DOTALL)
    html = re.sub(r'<script>.*?</script>', '', html, flags=re.DOTALL)
    
    return {
        'html': html.strip(),
        'styles': styles.strip(),
        'script': script.strip()
    }

def build_simplified_index():
    """Build the simplified index.html"""
    
    # Read all components
    components_data = {}
    all_styles = []
    
    for component in COMPONENTS:
        data = read_component(component)
        if data:
            components_data[component] = data
            if data['styles']:
                all_styles.append(f"/* {component.upper()} COMPONENT STYLES */\n{data['styles']}")
    
    # Build navigation items
    nav_items = []
    footer_nav_items = []
    
    # Collect component scripts
    component_scripts = []
    for component in COMPONENTS:
        if component in components_data and components_data[component]['script']:
            component_scripts.append(f"// {component.upper()} COMPONENT SCRIPT")
            component_scripts.append(components_data[component]['script'])
    
    for component in COMPONENTS:
        info = COMPONENT_INFO.get(component, {})
        icon = info.get('icon', '')
        
        nav_item = f'''
                    <li class="nav-item" 
                        data-component="{component}"
                        data-tekton-nav-item="{component}"
                        data-tekton-nav-target="{component}"
                        data-tekton-state="inactive">
                        <a href="#{component}" class="nav-link">
                            {f'<span class="button-icon">{icon}</span>' if icon else ''}
                            <span class="nav-label">{info.get('title', component)} - {info.get('subtitle', '')}</span>
                            <span class="status-indicator" 
                                 data-tekton-status="{component}-health"
                                 data-status="inactive"></span>
                        </a>
                    </li>'''
        
        if component in ['profile', 'settings']:
            footer_nav_items.append(nav_item)
        else:
            nav_items.append(nav_item)
    
    # Build component divs
    component_divs = []
    
    for component in COMPONENTS:
        if component in components_data:
            # Wrap component HTML in a div with proper ID
            component_html = components_data[component]['html']
            component_div = f'''
            <!-- {component.upper()} COMPONENT -->
            <div id="{component}" class="component" 
                 data-tekton-area="{component}"
                 data-tekton-type="component-container"
                 data-tekton-visibility="hidden">
{component_html}
            </div>'''
            component_divs.append(component_div)
    
    # Build the final HTML (use double braces for CSS to escape format strings)
    html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tekton - AI Orchestration System</title>
    <link rel="stylesheet" href="styles/main.css">
    <link rel="stylesheet" href="styles/themes/theme-base.css">
    <link rel="stylesheet" href="styles/themes/theme-pure-black.css">
    
    <!-- Apply theme immediately -->
    <script>
        document.documentElement.setAttribute('data-theme-base', 'pure-black');
    </script>
    
    <!-- CSS-based navigation and component visibility -->
    <style>
        /* Hide all components by default */
        .component {{
            display: none;
            height: 100%;
            width: 100%;
            overflow: auto;
        }}
        
        /* Show targeted component */
        .component:target {{
            display: block;
        }}
        
        /* Show numa by default when no hash */
        #numa {{ display: block; }}
        :target ~ #numa {{ display: none; }}
        
        /* Navigation link styling */
        .nav-link {{
            display: flex;
            align-items: center;
            width: 100%;
            text-decoration: none;
            color: inherit;
            padding: 11px 16px;
            margin: -11px -16px;
        }}
        
        .nav-link .nav-label {{
            flex: 1;
        }}
        
        .nav-item:hover {{
            background-color: var(--bg-hover, #3a3a4a);
        }}
        
        /* Active state based on URL hash */
        .nav-item:has(a[href="#numa"]) {{ background-color: var(--bg-hover, #3a3a4a); }}
        :target ~ * .nav-item:has(a[href="#numa"]) {{ background-color: transparent; }}
        
        /* Highlight matching hash */
{active_states}
        
        /* Status indicators */
        .status-indicator {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
            opacity: 0.5;
            transition: all 0.3s ease;
        }}
        
        .status-indicator.connected {{
            opacity: 1;
            box-shadow: 0 0 8px currentColor, 0 0 12px currentColor;
            animation: pulse-subtle 2s infinite;
        }}
        
        @keyframes pulse-subtle {{
            0% {{ box-shadow: 0 0 5px 2px rgba(255, 255, 255, 0.3); }}
            50% {{ box-shadow: 0 0 7px 3px rgba(255, 255, 255, 0.4); }}
            100% {{ box-shadow: 0 0 5px 2px rgba(255, 255, 255, 0.3); }}
        }}
        
        /* Component color indicators */
{color_styles}
        
        /* Main content area */
        .main-content {{
            position: relative;
            flex: 1;
            height: 100%;
            overflow: hidden;
        }}
        
        /* Left panel adjustments */
        .left-panel-header {{
            padding: 12px 16px;
            height: 85px;
        }}
        
        .nav-item {{
            padding: 0;
            height: auto;
        }}
        
        .pillar-icon {{
            height: 85px;
            margin-left: 10px;
            position: absolute;
            right: 0;
            top: 0;
            display: block;
            z-index: 5;
        }}
    </style>
    
    <!-- Component styles -->
    <style>
{all_styles}
    </style>
</head>
<body data-theme-base="pure-black">
    <div class="app-container" data-tekton-root="true">
        <!-- Main Content Area FIRST (for CSS sibling selectors) -->
        <div class="main-content" 
             data-tekton-area="content"
             data-tekton-type="workspace">
{component_divs}
        </div>
        
        <!-- Left Panel Navigation -->
        <div class="left-panel" 
             data-tekton-nav="main"
             data-tekton-area="navigation">
            <div class="left-panel-header" 
                 data-tekton-zone="header"
                 data-tekton-section="nav-header">
                <div class="tekton-logo">
                    <div class="logo-text">
                        <h1 style="color: #007bff; font-size: 2.5rem;">Tekton</h1>
                        <div class="subtitle" style="font-size: 0.9rem; color: #aaa;">Multi-AI Engineering</div>
                    </div>
                    <img src="images/Tekton.png" alt="Tekton Pillar" class="pillar-icon">
                </div>
            </div>
            
            <div class="left-panel-nav" 
                 data-tekton-zone="main"
                 data-tekton-section="nav-main">
                <ul class="component-nav" 
                    data-tekton-list="components"
                    data-tekton-nav-type="primary">
{nav_items}
                </ul>
            </div>
            
            <div class="left-panel-footer" 
                 data-tekton-zone="footer"
                 data-tekton-section="nav-footer">
                <div class="footer-separator"></div>
                <ul class="component-nav" 
                    data-tekton-list="utilities"
                    data-tekton-nav-type="secondary">
{footer_nav_items}
                </ul>
            </div>
        </div>
    </div>
    
    <!-- Component Scripts -->
    <script>
{component_scripts}
    </script>
</body>
</html>'''

    # Generate active states CSS
    active_states = []
    for component in COMPONENTS:
        active_states.append(f'        #{component}:target ~ * .nav-item:has(a[href="#{component}"]) {{ background-color: var(--bg-hover, #3a3a4a); }}')
    
    # Generate color styles
    color_styles = []
    for component, info in COMPONENT_INFO.items():
        color = info.get('color', '#757575')
        color_styles.append(f'        .nav-item[data-component="{component}"] .status-indicator {{ background-color: {color}; }}')
    
    # Format the template
    final_html = html_template.format(
        active_states='\n'.join(active_states),
        color_styles='\n'.join(color_styles),
        all_styles='\n\n'.join(all_styles),
        component_divs='\n'.join(component_divs),
        nav_items=''.join(nav_items),
        footer_nav_items=''.join(footer_nav_items),
        component_scripts='\n\n'.join(component_scripts)
    )
    
    # Write the file
    with open('index-simplified.html', 'w') as f:
        f.write(final_html)
    
    print(f"Built index-simplified.html with {len(components_data)} components")
    print(f"Total size: {len(final_html):,} bytes")

if __name__ == '__main__':
    os.chdir(Path(__file__).parent)
    build_simplified_index()