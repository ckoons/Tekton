#!/usr/bin/env python3
"""Test the match_purpose functionality"""

import sys
import os

# Add parent directory to path to import from src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.purpose_matcher import match_purpose, parse_purpose_list

def test_match_purpose():
    """Test the match_purpose function"""
    print("=== Testing match_purpose ===")
    
    # Test data
    terminals = [
        {"name": "Amy", "purpose": "Coding, Research"},
        {"name": "Bob", "purpose": "Testing"},
        {"name": "Carol", "purpose": "Planning, Research"},
        {"name": "Dave", "purpose": "coding"},  # lowercase
        {"name": "Eve", "purpose": ""},  # empty
        {"name": "Frank"}  # no purpose field
    ]
    
    # Test cases
    tests = [
        ("coding", ["Amy", "Dave"]),
        ("Coding", ["Amy", "Dave"]),  # case insensitive
        ("CODING", ["Amy", "Dave"]),  # case insensitive
        ("research", ["Amy", "Carol"]),
        ("Research", ["Amy", "Carol"]),
        ("testing", ["Bob"]),
        ("Testing", ["Bob"]),
        ("planning", ["Carol"]),
        ("Planning", ["Carol"]),
        ("cod", []),  # partial match should fail
        ("search", []),  # partial match should fail
        ("", []),  # empty should return nothing
        ("nonexistent", [])  # no matches
    ]
    
    passed = 0
    failed = 0
    
    for word, expected in tests:
        result = match_purpose(word, terminals)
        if sorted(result) == sorted(expected):
            print(f"✓ match_purpose('{word}') = {result}")
            passed += 1
        else:
            print(f"✗ match_purpose('{word}') = {result}, expected {expected}")
            failed += 1
    
    print(f"\nPassed: {passed}, Failed: {failed}")
    print()

def test_parse_purpose_list():
    """Test the parse_purpose_list function"""
    print("=== Testing parse_purpose_list ===")
    
    tests = [
        ("Coding, Research", ["Coding", "Research"]),
        ("Testing", ["Testing"]),
        ("Planning, Research, Testing", ["Planning", "Research", "Testing"]),
        ("  Coding  ,  Research  ", ["Coding", "Research"]),  # extra spaces
        ("", []),  # empty
        ("Coding,", ["Coding"]),  # trailing comma
        (",Research", ["Research"]),  # leading comma
        ("Coding,,Research", ["Coding", "Research"])  # double comma
    ]
    
    passed = 0
    failed = 0
    
    for input_str, expected in tests:
        result = parse_purpose_list(input_str)
        if result == expected:
            print(f"✓ parse_purpose_list('{input_str}') = {result}")
            passed += 1
        else:
            print(f"✗ parse_purpose_list('{input_str}') = {result}, expected {expected}")
            failed += 1
    
    print(f"\nPassed: {passed}, Failed: {failed}")

if __name__ == "__main__":
    test_match_purpose()
    test_parse_purpose_list()