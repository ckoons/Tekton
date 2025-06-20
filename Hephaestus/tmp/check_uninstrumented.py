#!/usr/bin/env python3
"""
Find components without semantic instrumentation
"""
import os
import glob

# Get all component HTML files
component_files = glob.glob('ui/components/**/*.html', recursive=True)

# Check each for data-tekton attributes
uninstrumented = []
partially_instrumented = []
fully_instrumented = []

for file in component_files:
    with open(file, 'r') as f:
        content = f.read()
        
    # Count different types of semantic tags
    tag_counts = {
        'area': content.count('data-tekton-area='),
        'zone': content.count('data-tekton-zone='),
        'component': content.count('data-tekton-component='),
        'action': content.count('data-tekton-action='),
        'panel': content.count('data-tekton-panel='),
        'menu': content.count('data-tekton-menu-'),
    }
    
    total_tags = sum(tag_counts.values())
    component_name = os.path.basename(file)
    
    if total_tags == 0:
        uninstrumented.append(component_name)
    elif tag_counts['area'] > 0 and tag_counts['zone'] >= 2:
        fully_instrumented.append((component_name, total_tags))
    else:
        partially_instrumented.append((component_name, total_tags, tag_counts))

# Report findings
print("=== Tekton Component Instrumentation Status ===\n")

print(f"✅ Fully Instrumented ({len(fully_instrumented)} components):")
for name, count in sorted(fully_instrumented, key=lambda x: x[1], reverse=True):
    print(f"   {name}: {count} tags")

print(f"\n⚠️  Partially Instrumented ({len(partially_instrumented)} components):")
for name, count, details in partially_instrumented:
    print(f"   {name}: {count} tags")
    missing = []
    if details['area'] == 0:
        missing.append('area')
    if details['zone'] == 0:
        missing.append('zones')
    if missing:
        print(f"      Missing: {', '.join(missing)}")

print(f"\n❌ Not Instrumented ({len(uninstrumented)} components):")
for name in uninstrumented:
    print(f"   {name}")

print(f"\nTotal: {len(component_files)} components")