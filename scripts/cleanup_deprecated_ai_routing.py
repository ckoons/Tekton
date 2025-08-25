#!/usr/bin/env python3
"""
Cleanup script to remove deprecated CI routing code.

This script can be run to remove the overcomplicated CI routing
and personality mapping code that has been replaced by the simple
COMPONENT_EXPERTISE approach in generic_specialist.py.
"""

import os
import sys

def main():
    """Main cleanup function."""
    print("Deprecated CI Routing Code Cleanup")
    print("=" * 50)
    
    deprecated_items = [
        {
            "file": "shared/ai/registry_client.py",
            "description": "Remove _component_to_role mapping and _get_component_capabilities",
            "lines": "740-780"
        },
        {
            "file": "shared/ai/ai_discovery_service.py",
            "description": "Remove _get_ai_roles and _get_ai_capabilities methods",
            "lines": "388-410"
        },
        {
            "file": "Rhetor/rhetor/core/specialist_templates.py",
            "description": "Remove entire file - replaced by generic_specialist.py",
            "action": "delete_file"
        },
        {
            "file": "config/tekton_ai_config.json",
            "description": "Remove personality, description, expertise sections from each AI",
            "action": "manual_edit"
        }
    ]
    
    print("\nThe following deprecated code should be removed:\n")
    
    for item in deprecated_items:
        print(f"File: {item['file']}")
        print(f"  Action: {item['description']}")
        if 'lines' in item:
            print(f"  Lines: {item['lines']}")
        if 'action' in item:
            print(f"  Type: {item['action']}")
        print()
    
    print("\nRECOMMENDED APPROACH:")
    print("1. Review each file to ensure no active code depends on deprecated sections")
    print("2. Remove deprecated code sections")
    print("3. Run tests to ensure nothing breaks")
    print("4. Update any references to use COMPONENT_EXPERTISE in generic_specialist.py")
    
    print("\nNOTE: This is a guide - manual review is recommended before deletion")

if __name__ == "__main__":
    main()