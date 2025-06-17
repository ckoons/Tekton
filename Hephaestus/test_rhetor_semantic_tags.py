#!/usr/bin/env python3
"""
Test that Rhetor's semantic tags are properly added
"""

import re

def test_rhetor_semantic_tags():
    """Check semantic tags in rhetor-component.html"""
    
    with open('ui/components/rhetor/rhetor-component.html', 'r') as f:
        html = f.read()
    
    # Find all data-tekton-* attributes
    semantic_tags = re.findall(r'data-tekton-[\w-]+="[^"]*"', html)
    
    print(f"📊 Found {len(semantic_tags)} semantic tag instances")
    
    # Count unique tag types
    tag_types = {}
    for tag in semantic_tags:
        tag_name = tag.split('=')[0]
        tag_types[tag_name] = tag_types.get(tag_name, 0) + 1
    
    print(f"\n🏷️  Unique semantic tag types ({len(tag_types)}):")
    for tag_name, count in sorted(tag_types.items()):
        print(f"   - {tag_name}: {count}")
    
    # Check for required patterns
    required_patterns = [
        ('data-tekton-area="rhetor"', "Component area tag"),
        ('data-tekton-component="rhetor"', "Component identifier"), 
        ('data-tekton-zone="header"', "Header zone"),
        ('data-tekton-zone="menu"', "Menu zone"),
        ('data-tekton-zone="content"', "Content zone"),
        ('data-tekton-zone="footer"', "Footer zone"),
        ('data-tekton-menu-item=', "Menu item tags"),
        ('data-tekton-panel=', "Panel tags"),
        ('data-tekton-chat=', "Chat interface tags")
    ]
    
    print(f"\n✅ Required patterns check:")
    all_good = True
    for pattern, description in required_patterns:
        if pattern in html:
            print(f"   ✓ {description}")
        else:
            print(f"   ✗ {description} - MISSING!")
            all_good = False
    
    # Show sample of actual tags
    print(f"\n📝 Sample tags found:")
    for tag in semantic_tags[:10]:
        print(f"   - {tag}")
    
    if all_good:
        print(f"\n✅ All required semantic patterns are present!")
    else:
        print(f"\n⚠️  Some required patterns are missing")

if __name__ == "__main__":
    test_rhetor_semantic_tags()