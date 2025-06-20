#!/usr/bin/env python3
"""
Add zone tags to partially instrumented components

This tool helps complete components that have root tags but are missing zones.
It uses BEM naming conventions to identify zones.
"""
import os
import re
import sys
from typing import List, Tuple

def add_zone_tags(filepath: str, dry_run: bool = True) -> List[Tuple[str, str]]:
    """Add zone tags to a component file"""
    component_name = os.path.basename(filepath).replace('-component.html', '')
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Check if already has zones
    if 'data-tekton-zone=' in content:
        print(f"⚠️  {component_name} already has zone tags, skipping")
        return []
    
    changes = []
    modified_content = content
    
    # Pattern mappings from BEM classes to zones
    zone_patterns = [
        (f'{component_name}__header', 'header'),
        (f'{component_name}__menu-bar', 'menu'),
        (f'{component_name}__menu', 'menu'),
        (f'{component_name}__nav', 'menu'),
        (f'{component_name}__tabs', 'menu'),
        (f'{component_name}__content', 'content'),
        (f'{component_name}__main', 'content'),
        (f'{component_name}__body', 'content'),
        (f'{component_name}__footer', 'footer'),
    ]
    
    for class_pattern, zone in zone_patterns:
        # Find divs with these classes
        regex = f'(<div[^>]*class="[^"]*{class_pattern}[^"]*")'
        matches = re.finditer(regex, modified_content)
        
        for match in matches:
            old_tag = match.group(1)
            # Check if already has zone
            if 'data-tekton-zone=' not in old_tag:
                new_tag = old_tag + f' data-tekton-zone="{zone}"'
                modified_content = modified_content.replace(old_tag, new_tag, 1)
                changes.append((zone, class_pattern))
    
    # Special handling for sections
    if f'{component_name}__header' in content:
        # Also add section tag
        regex = f'(<div[^>]*class="[^"]*{component_name}__header[^"]*"[^>]*data-tekton-zone="header")'
        match = re.search(regex, modified_content)
        if match and 'data-tekton-section=' not in match.group(1):
            old_tag = match.group(1)
            new_tag = old_tag + ' data-tekton-section="header"'
            modified_content = modified_content.replace(old_tag, new_tag, 1)
            changes.append(('section', f'{component_name}__header'))
    
    # Add scrollable to content if needed
    content_regex = f'(<div[^>]*class="[^"]*{component_name}__content[^"]*"[^>]*data-tekton-zone="content")'
    match = re.search(content_regex, modified_content)
    if match and 'data-tekton-scrollable=' not in match.group(1):
        old_tag = match.group(1)
        new_tag = old_tag + ' data-tekton-scrollable="true"'
        modified_content = modified_content.replace(old_tag, new_tag, 1)
        changes.append(('scrollable', f'{component_name}__content'))
    
    # Add nav tag to menu if found
    menu_regex = f'(<div[^>]*class="[^"]*{component_name}__menu[^"]*"[^>]*data-tekton-zone="menu")'
    match = re.search(menu_regex, modified_content)
    if match and 'data-tekton-nav=' not in match.group(1):
        old_tag = match.group(1)
        new_tag = old_tag + ' data-tekton-nav="component-menu"'
        modified_content = modified_content.replace(old_tag, new_tag, 1)
        changes.append(('nav', f'{component_name}__menu'))
    
    if changes and not dry_run:
        with open(filepath, 'w') as f:
            f.write(modified_content)
    
    return changes

def main():
    """Process partially instrumented components"""
    import glob
    
    # Find components that need zones
    partial_components = [
        'apollo', 'athena', 'budget', 'engram', 'ergon', 
        'harmonia', 'metis', 'prometheus', 'sophia', 'synthesis', 'telos'
    ]
    
    dry_run = '--apply' not in sys.argv
    
    if dry_run:
        print("🔍 DRY RUN MODE - No files will be modified")
        print("   Use --apply flag to actually modify files\n")
    else:
        print("✏️  APPLYING CHANGES - Files will be modified\n")
    
    total_changes = 0
    
    for component in partial_components:
        filepath = f'ui/components/{component}/{component}-component.html'
        
        if not os.path.exists(filepath):
            print(f"❌ {component}: File not found")
            continue
        
        changes = add_zone_tags(filepath, dry_run)
        
        if changes:
            print(f"✅ {component}: Found {len(changes)} zones to tag")
            for zone_type, class_found in changes:
                print(f"   + {zone_type} (from {class_found})")
            total_changes += len(changes)
        else:
            print(f"⚠️  {component}: No changes needed or already has zones")
    
    print(f"\n{'Would add' if dry_run else 'Added'} {total_changes} zone tags total")
    
    if dry_run and total_changes > 0:
        print("\nRun with --apply flag to apply these changes:")
        print("  python3 tests/add_zone_tags.py --apply")

if __name__ == "__main__":
    main()