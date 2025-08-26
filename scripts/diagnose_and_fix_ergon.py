#!/usr/bin/env python3
"""
Complete diagnosis and fix for Ergon's prompt size issue
"""

import sys
import subprocess
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment
from shared.env import TektonEnvironLock
TektonEnvironLock.load()

from shared.aish.src.registry.ci_registry import get_registry
from shared.aish.src.core.unified_sender import get_buffered_messages

def diagnose_and_fix():
    """Complete diagnosis and fix for Ergon."""
    registry = get_registry()
    
    print("\n" + "=" * 70)
    print("ERGON COMPLETE DIAGNOSIS AND FIX")
    print("=" * 70)
    
    # Check all possible CI names
    ci_names = ['ergon', 'ergon-ci', 'ergon-api']
    
    print("\n1. CHECKING ALL ERGON VARIANTS")
    print("-" * 50)
    
    for ci_name in ci_names:
        print(f"\n{ci_name}:")
        
        # Forward state
        forward = registry.get_forward_state(ci_name)
        if forward:
            print(f"  Forward: {forward.get('model', 'unknown')}")
        else:
            print(f"  Forward: None")
        
        # Fresh start flag
        needs_fresh = registry.get_needs_fresh_start(ci_name)
        print(f"  Needs fresh: {needs_fresh}")
        
        # Buffered messages
        msgs = get_buffered_messages(ci_name, clear=False)
        if msgs:
            print(f"  Buffered: {len(msgs)} chars")
        else:
            print(f"  Buffered: None")
        
        # Next prompt
        next_prompt = registry.get_next_prompt(ci_name)
        if next_prompt:
            print(f"  Next prompt: {next_prompt[:50]}...")
        else:
            print(f"  Next prompt: None")
    
    print("\n2. APPLYING FIXES")
    print("-" * 50)
    
    for ci_name in ci_names:
        print(f"\nFixing {ci_name}:")
        
        # Set fresh start
        registry.set_needs_fresh_start(ci_name, True)
        print(f"  ✓ Set needs_fresh_start = True")
        
        # Clear buffered messages
        get_buffered_messages(ci_name, clear=True)
        print(f"  ✓ Cleared buffered messages")
        
        # Clear next prompt
        registry.clear_next_prompt(ci_name)
        print(f"  ✓ Cleared next_prompt")
        
        # Clear sunrise context
        registry.clear_sunrise_context(ci_name)
        print(f"  ✓ Cleared sunrise_context")
    
    print("\n3. TESTING CLAUDE DIRECTLY")
    print("-" * 50)
    
    # Test with a simple prompt
    test_cmd = [
        'claude',
        '--model', 'claude-opus-4-1-20250805',
        '--print'
    ]
    
    test_prompt = "Say 'OK' if you can hear me"
    
    print(f"Testing: {' '.join(test_cmd)}")
    print(f"Prompt: '{test_prompt}'")
    
    try:
        result = subprocess.run(
            test_cmd,
            input=test_prompt.encode(),
            capture_output=True,
            timeout=10
        )
        
        if result.returncode == 0:
            response = result.stdout.decode().strip()
            print(f"✓ Claude responded: {response[:100]}")
        else:
            error = result.stderr.decode().strip()
            print(f"✗ Claude error: {error}")
            
            if "Prompt is too long" in error:
                print("\n⚠️  CLAUDE HAS ACCUMULATED CONTEXT")
                print("This means Claude CLI itself has saved context")
                print("Solution: Clear Claude's context file")
                
    except subprocess.TimeoutExpired:
        print("✗ Claude timed out")
    except Exception as e:
        print(f"✗ Error testing Claude: {e}")
    
    print("\n4. CHECKING CLAUDE CONTEXT FILES")
    print("-" * 50)
    
    # Check for Claude snapshot files
    claude_dir = Path.home() / '.claude'
    snapshot_dir = claude_dir / 'shell-snapshots'
    
    if snapshot_dir.exists():
        snapshots = list(snapshot_dir.glob('*'))
        print(f"Found {len(snapshots)} snapshot files")
        
        # Look for recent large files
        large_files = []
        for f in snapshots:
            size = f.stat().st_size
            if size > 100000:  # >100KB
                large_files.append((f, size))
        
        if large_files:
            print(f"\n⚠️  Found {len(large_files)} large context files:")
            for f, size in sorted(large_files, key=lambda x: x[1], reverse=True)[:5]:
                print(f"  {f.name}: {size/1024:.1f}KB")
            
            # Find the current shell snapshot
            latest = max(snapshots, key=lambda f: f.stat().st_mtime)
            print(f"\nLatest snapshot: {latest.name}")
            print(f"Size: {latest.stat().st_size/1024:.1f}KB")
            
            if latest.stat().st_size > 500000:  # >500KB
                print("\n⚠️  CURRENT CONTEXT TOO LARGE")
                print("This is likely causing the 'Prompt too long' error")
    
    print("\n5. FINAL RECOMMENDATIONS")
    print("-" * 50)
    
    print("\nTo fix Ergon completely:")
    print("1. ✓ Fresh start flags set for all variants")
    print("2. ✓ Buffered messages cleared")
    print("3. ✓ Next prompts cleared")
    
    print("\nIf still getting 'Prompt too long':")
    print("• The issue is in Claude CLI's saved context")
    print("• Try: rm ~/.claude/shell-snapshots/[current-snapshot]")
    print("• Or: claude --new (if supported)")
    print("• Or: Use a different terminal/session")
    
    print("\n" + "=" * 70)
    print("DIAGNOSIS COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    diagnose_and_fix()