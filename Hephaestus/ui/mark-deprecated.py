#!/usr/bin/env python3
"""Mark old JavaScript files as deprecated"""

import os
from pathlib import Path

# Files to mark as deprecated
DEPRECATED_FILES = [
    'scripts/terminal.js',
    'scripts/terminal-chat.js',
    'scripts/terminal-chat-enhanced.js',
    'scripts/websocket.js',
    'scripts/main.js',
    'scripts/component-utils.js',
    'scripts/storage.js',
    'scripts/ui-utils.js',
    'scripts/hermes-connector.js',
    'scripts/shared/component-loading-guard.js',
    'scripts/shared/tab-navigation.js',
    'scripts/settings/settings-manager.js',
    'scripts/settings/settings-env-bridge.js',
    'scripts/settings/settings-ui.js',
    'scripts/profile/profile-manager.js',
    'scripts/profile/profile-ui.js'
]

def mark_deprecated(filepath):
    """Add deprecation notice to a file"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Check if already marked
        if 'DEPRECATED: This file will be removed' in content:
            print(f"Already marked: {filepath}")
            return
        
        # Add deprecation notice at the beginning
        if content.startswith('/**'):
            # Insert after opening comment
            lines = content.split('\n')
            lines.insert(1, ' * DEPRECATED: This file will be removed after CSS-first migration is verified')
            content = '\n'.join(lines)
        elif content.startswith('/*'):
            # Insert after opening comment
            lines = content.split('\n')
            lines.insert(1, ' * DEPRECATED: This file will be removed after CSS-first migration is verified')
            content = '\n'.join(lines)
        else:
            # Add new comment block
            content = f"""// DEPRECATED: This file will be removed after CSS-first migration is verified
{content}"""
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        print(f"Marked deprecated: {filepath}")
        
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

if __name__ == '__main__':
    os.chdir(Path(__file__).parent)
    
    for filepath in DEPRECATED_FILES:
        if os.path.exists(filepath):
            mark_deprecated(filepath)
        else:
            print(f"File not found: {filepath}")