#!/usr/bin/env python3
"""
Test how delimiter is parsed and passed through the system
"""

import sys
import argparse

# Test what argparse does with the delimiter argument
parser = argparse.ArgumentParser()
parser.add_argument('ai', help='AI name')
parser.add_argument('message', help='Message')
parser.add_argument('-x', '--execute', nargs='?', const='\n', default=None)

# Simulate your command: aish tina-ci "print('hello')" -x "\r\n"
test_cases = [
    ['tina-ci', "print('hello')", '-x', '\\r\\n'],  # What shell passes
    ['tina-ci', "print('hello')", '-x', '\r\n'],    # If shell interpreted it
    ['tina-ci', "print('hello')", '-x'],             # Default case
]

for i, test_args in enumerate(test_cases, 1):
    print(f"\nTest {i}: {test_args}")
    args = parser.parse_args(test_args)
    
    print(f"  ai: {args.ai}")
    print(f"  message: {args.message}")
    print(f"  execute raw: {repr(args.execute)}")
    print(f"  execute bytes: {args.execute.encode('utf-8') if args.execute else None}")
    
    # Show what happens when we try to interpret escape sequences
    if args.execute:
        # This is what the code currently does - takes it literally
        literal = args.execute
        print(f"  Literal interpretation: {repr(literal)} -> bytes: {literal.encode('utf-8')}")
        
        # This is what we might want - interpret escape sequences
        try:
            # Decode escape sequences
            interpreted = args.execute.encode('utf-8').decode('unicode_escape')
            print(f"  Escape interpretation: {repr(interpreted)} -> bytes: {interpreted.encode('utf-8')}")
        except:
            print(f"  Could not interpret escapes")