#!/usr/bin/env python3
"""
Environment Usage Linter for Tekton

This script finds all direct os.environ usage in Tekton components.
It helps track progress during the refactoring to TektonEnviron.

Usage:
    python check_env_usage.py                    # Check all components
    python check_env_usage.py Hermes            # Check specific component
    python check_env_usage.py Hermes Rhetor     # Check multiple components
    python check_env_usage.py --summary         # Show summary only
"""

import os
import re
import sys
import ast
from pathlib import Path
from typing import List, Tuple, Dict
from collections import defaultdict

# Patterns to find (these should use TektonEnviron instead)
VIOLATION_PATTERNS = [
    (re.compile(r'\bos\.environ\b'), 'os.environ'),
    (re.compile(r'\bos\.getenv\b'), 'os.getenv'),
    (re.compile(r'\bos\.environ\.get\b'), 'TektonEnviron.get'),
    (re.compile(r'\bos\.environ\['), 'os.environ[]'),
    (re.compile(r'\bos\.environb\b'), 'os.environb'),
]

# Files to ignore
IGNORE_FILES = {
    'shared/env.py',  # This is where TektonEnviron lives
    'src/tekton-launcher/tekton-clean-launch.c',  # C file
    'scripts/check_env_usage.py',  # This file
}

# Directories to skip
SKIP_DIRS = {
    '__pycache__',
    '.git',
    'venv',
    '.venv',
    'node_modules',
    '.pytest_cache',
    '.mypy_cache',
}


class EnvUsageChecker:
    """Check for direct environment variable usage."""
    
    def __init__(self, tekton_root: Path):
        self.tekton_root = tekton_root
        self.violations: Dict[str, List[Tuple[int, str, str]]] = defaultdict(list)
        
    def check_file(self, filepath: Path) -> List[Tuple[int, str, str]]:
        """Check a single file for violations."""
        violations = []
        
        # Skip if in ignore list
        relative_path = filepath.relative_to(self.tekton_root)
        if str(relative_path) in IGNORE_FILES:
            return violations
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # First check if this file imports from shared.env
            uses_tekton_environ = 'from shared.env import' in content or 'import shared.env' in content
                
            # Check each line
            for line_num, line in enumerate(content.splitlines(), 1):
                # Skip comments and strings (basic check)
                stripped = line.strip()
                if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
                    continue
                    
                # Check patterns
                for pattern, name in VIOLATION_PATTERNS:
                    if pattern.search(line):
                        # Get context (the actual usage)
                        match = pattern.search(line)
                        start = max(0, match.start() - 20)
                        end = min(len(line), match.end() + 20)
                        context = line[start:end].strip()
                        
                        violations.append((line_num, name, context))
                        
        except Exception as e:
            print(f"Error reading {filepath}: {e}", file=sys.stderr)
            
        return violations
        
    def check_directory(self, dirpath: Path) -> None:
        """Recursively check all Python files in directory."""
        for item in dirpath.iterdir():
            if item.is_dir():
                if item.name not in SKIP_DIRS:
                    self.check_directory(item)
            elif item.suffix == '.py':
                violations = self.check_file(item)
                if violations:
                    relative_path = item.relative_to(self.tekton_root)
                    self.violations[str(relative_path)] = violations
                    
    def check_component(self, component_name: str) -> None:
        """Check a specific component."""
        component_path = self.tekton_root / component_name
        if not component_path.exists():
            print(f"Component not found: {component_name}", file=sys.stderr)
            return
            
        self.check_directory(component_path)
        
    def print_report(self, summary_only: bool = False) -> None:
        """Print violation report."""
        if not self.violations:
            print("✅ No environment violations found!")
            return
            
        total_violations = sum(len(v) for v in self.violations.values())
        print(f"\n🔍 Found {total_violations} environment violations in {len(self.violations)} files:\n")
        
        if not summary_only:
            # Group by component
            by_component = defaultdict(list)
            for filepath, violations in sorted(self.violations.items()):
                component = filepath.split('/')[0]
                by_component[component].append((filepath, violations))
                
            for component, files in sorted(by_component.items()):
                component_total = sum(len(v[1]) for v in files)
                print(f"\n📁 {component} ({component_total} violations):")
                
                for filepath, violations in files:
                    print(f"\n  {filepath}:")
                    for line_num, vtype, context in violations:
                        print(f"    Line {line_num}: {vtype}")
                        print(f"      {context}")
                        
        # Summary
        print("\n📊 Summary by component:")
        by_component_count = defaultdict(int)
        for filepath, violations in self.violations.items():
            component = filepath.split('/')[0]
            by_component_count[component] += len(violations)
            
        for component, count in sorted(by_component_count.items(), key=lambda x: -x[1]):
            print(f"  {component:20} {count:4d} violations")
            
        print(f"\nTotal: {total_violations} violations")
        
        # Suggest next steps
        print("\n💡 To fix violations:")
        print("  1. Add to imports: from shared.env import TektonEnviron")
        print("  2. Replace:")
        print("     TektonEnviron.get('KEY', 'default')  →  TektonEnviron.get('KEY', 'default')")
        print("     os.environ['KEY']                 →  TektonEnviron.get('KEY')")
        print("     os.getenv('KEY')                  →  TektonEnviron.get('KEY')")


def main():
    """Main entry point."""
    # Find Tekton root
    script_dir = Path(__file__).parent
    tekton_root = script_dir.parent
    
    if not (tekton_root / '.env.tekton').exists():
        print("Error: Not in a Tekton directory", file=sys.stderr)
        sys.exit(1)
        
    # Parse arguments
    components = []
    summary_only = False
    
    for arg in sys.argv[1:]:
        if arg == '--summary':
            summary_only = True
        elif not arg.startswith('-'):
            components.append(arg)
            
    # Create checker
    checker = EnvUsageChecker(tekton_root)
    
    # Check components
    if components:
        for component in components:
            checker.check_component(component)
    else:
        # Check all components
        for item in tekton_root.iterdir():
            if item.is_dir() and item.name[0].isupper() and item.name not in SKIP_DIRS:
                checker.check_component(item.name)
                
    # Print report
    checker.print_report(summary_only)
    
    # Exit with error if violations found
    sys.exit(1 if checker.violations else 0)


if __name__ == '__main__':
    main()