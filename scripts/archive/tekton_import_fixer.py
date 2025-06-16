#!/usr/bin/env python3
"""
Interactive Import Fixer for Tekton

This script reads the analysis results and interactively asks if you want to fix specific issues.

Usage:
    python tekton_import_fixer.py [--auto-backup]
"""

import ast
import json
import os
import sys
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class Colors:
    """Terminal colors for better readability."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class TektonImportFixer:
    def __init__(self, tekton_root: str, auto_backup: bool = True):
        self.tekton_root = Path(tekton_root)
        self.auto_backup = auto_backup
        self.changes_made = []
        self.backups = []
        
    def load_results(self, results_file: str = "import_analysis_results.json") -> Dict:
        """Load analysis results from JSON file."""
        results_path = self.tekton_root / results_file
        if not results_path.exists():
            print(f"{Colors.FAIL}Error: No analysis results found.{Colors.ENDC}")
            print("Please run 'python tekton_import_analyzer.py' first.")
            sys.exit(1)
            
        with open(results_path, 'r') as f:
            return json.load(f)
    
    def prompt_user(self, question: str, options: List[str] = ["y", "n", "s"]) -> str:
        """Prompt user for input with options."""
        options_str = "/".join(options)
        while True:
            response = input(f"{question} ({options_str}): ").lower().strip()
            if response in options:
                return response
            print(f"Please enter one of: {options_str}")
    
    def backup_file(self, filepath: Path) -> Optional[Path]:
        """Create a backup of a file before modifying it."""
        if not self.auto_backup:
            return None
            
        backup_dir = self.tekton_root / ".import_fixes_backup" / datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        relative_path = filepath.relative_to(self.tekton_root)
        backup_path = backup_dir / relative_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(filepath, backup_path)
        self.backups.append((filepath, backup_path))
        return backup_path
    
    def fix_star_imports(self, component_data: Dict):
        """Interactively fix star imports."""
        star_imports = component_data.get("star_imports", [])
        if not star_imports:
            return
            
        print(f"\n{Colors.HEADER}=== Star Imports in {component_data['name']} ==={Colors.ENDC}")
        print(f"Found {len(star_imports)} star imports\n")
        
        for i, star in enumerate(star_imports, 1):
            print(f"{Colors.CYAN}[{i}/{len(star_imports)}] {star['file']}:{star['line']}{Colors.ENDC}")
            print(f"  {Colors.WARNING}{star['full_import']}{Colors.ENDC}")
            
            response = self.prompt_user(
                "Fix this star import?",
                ["y", "n", "s", "a"]  # yes, no, skip all, auto-fix all
            )
            
            if response == "s":
                break
            elif response == "n":
                continue
            elif response == "y" or response == "a":
                self._fix_single_star_import(star, auto=response == "a")
                
                if response == "a":
                    # Auto-fix remaining star imports
                    for remaining in star_imports[i:]:
                        self._fix_single_star_import(remaining, auto=True)
                    break
    
    def _fix_single_star_import(self, star_info: Dict, auto: bool = False):
        """Fix a single star import."""
        filepath = self.tekton_root / star_info['file']
        
        try:
            # Parse the file to find what's actually used
            with open(filepath, 'r') as f:
                content = f.read()
                
            tree = ast.parse(content)
            
            # Find all names used from this module
            # This is simplified - a real implementation would need more sophisticated analysis
            used_names = self._find_used_names_from_module(tree, star_info['module'])
            
            if not used_names and not auto:
                print(f"  {Colors.WARNING}Warning: Could not determine which names are used.{Colors.ENDC}")
                manual_names = input("  Enter comma-separated names to import (or press Enter to skip): ")
                if manual_names:
                    used_names = [n.strip() for n in manual_names.split(',')]
                else:
                    return
            
            if used_names:
                # Create the new import statement
                new_import = f"from {star_info['module']} import {', '.join(sorted(used_names))}"
                
                # Backup and modify the file
                self.backup_file(filepath)
                
                # Replace the star import
                lines = content.split('\n')
                if star_info['line'] <= len(lines):
                    lines[star_info['line'] - 1] = new_import
                    
                    with open(filepath, 'w') as f:
                        f.write('\n'.join(lines))
                    
                    self.changes_made.append({
                        'type': 'star_import_fix',
                        'file': str(filepath),
                        'old': star_info['full_import'],
                        'new': new_import
                    })
                    
                    print(f"  {Colors.GREEN}✓ Fixed: {new_import}{Colors.ENDC}")
                    
        except Exception as e:
            print(f"  {Colors.FAIL}Error fixing import: {e}{Colors.ENDC}")
    
    def _find_used_names_from_module(self, tree: ast.AST, module: str) -> List[str]:
        """Find names that might be imported from a module."""
        # This is a simplified implementation
        # A real implementation would need to track scope and actual usage
        potential_names = set()
        
        class NameCollector(ast.NodeVisitor):
            def visit_Name(self, node):
                potential_names.add(node.id)
                self.generic_visit(node)
                
            def visit_Attribute(self, node):
                if isinstance(node.value, ast.Name):
                    potential_names.add(node.value.id)
                self.generic_visit(node)
        
        NameCollector().visit(tree)
        
        # Filter to likely imported names (capitalized or common patterns)
        # This is very simplified - real implementation would be more sophisticated
        likely_names = [
            name for name in potential_names
            if name[0].isupper() or name.startswith('_') or name in ['app', 'router', 'logger']
        ]
        
        return likely_names[:10]  # Limit to prevent huge imports
    
    def fix_circular_dependencies(self, component_data: Dict):
        """Show circular dependencies and suggest fixes."""
        circular_deps = component_data.get("circular_dependencies", [])
        if not circular_deps:
            return
            
        print(f"\n{Colors.HEADER}=== Circular Dependencies in {component_data['name']} ==={Colors.ENDC}")
        print(f"Found {len(circular_deps)} circular dependencies\n")
        
        # Group by cycle
        cycles = {}
        for dep in circular_deps:
            cycle_key = " → ".join(dep.get("cycle", []))
            if cycle_key not in cycles:
                cycles[cycle_key] = []
            cycles[cycle_key].append(dep)
        
        for i, (cycle, deps) in enumerate(cycles.items(), 1):
            print(f"{Colors.CYAN}[{i}/{len(cycles)}] Cycle: {cycle}{Colors.ENDC}")
            print(f"  Affected files: {len(deps)}")
            
            response = self.prompt_user(
                "Show detailed suggestions for breaking this cycle?",
                ["y", "n", "s"]
            )
            
            if response == "s":
                break
            elif response == "y":
                self._suggest_circular_fix(cycle, deps)
    
    def _suggest_circular_fix(self, cycle: str, deps: List[Dict]):
        """Suggest fixes for circular dependencies."""
        print(f"\n{Colors.WARNING}Suggestions for breaking cycle: {cycle}{Colors.ENDC}")
        print("\n1. Use lazy imports (import inside functions):")
        print("   def get_module():")
        print("       from other_module import SomeClass")
        print("       return SomeClass")
        
        print("\n2. Create an interface/protocol module:")
        print("   # interfaces.py")
        print("   class ComponentInterface(Protocol): ...")
        
        print("\n3. Move shared code to a common module:")
        print("   # common.py or base.py")
        print("   # Move shared classes/functions here")
        
        print("\n4. Use dependency injection:")
        print("   def __init__(self, dependency=None):")
        print("       self.dependency = dependency or DefaultImplementation()")
        
        print(f"\n{Colors.CYAN}Manual fix required - these patterns need careful consideration{Colors.ENDC}")
    
    def suggest_flattening(self, component_data: Dict):
        """Suggest and implement flattening improvements."""
        candidates = component_data.get("flattening_candidates", [])
        if not candidates:
            return
            
        print(f"\n{Colors.HEADER}=== Flattening Opportunities in {component_data['name']} ==={Colors.ENDC}")
        print(f"Found {len(candidates)} items imported frequently from deep paths\n")
        
        component_name = component_data['name'].lower()
        
        for i, cand in enumerate(candidates[:10], 1):  # Show top 10
            print(f"{Colors.CYAN}[{i}] {cand['item']} from {cand['module']}{Colors.ENDC}")
            print(f"  Imported {cand['count']} times (depth: {cand['depth']})")
            
            if cand['conflicts']:
                print(f"  {Colors.WARNING}⚠️  Conflicts with: {', '.join(cand['conflicts'])}{Colors.ENDC}")
                continue
            
            response = self.prompt_user(
                "Add to component's __init__.py for easier imports?",
                ["y", "n", "s"]
            )
            
            if response == "s":
                break
            elif response == "y":
                self._add_to_init(component_data['name'], cand)
    
    def _add_to_init(self, component: str, candidate: Dict):
        """Add an import to the component's __init__.py file."""
        init_path = self.tekton_root / component / component.lower() / "__init__.py"
        
        if not init_path.exists():
            print(f"  {Colors.FAIL}Error: {init_path} not found{Colors.ENDC}")
            return
            
        try:
            # Backup the file
            self.backup_file(init_path)
            
            with open(init_path, 'r') as f:
                content = f.read()
            
            # Parse to find where to add import
            tree = ast.parse(content)
            
            # Prepare the new import
            module_path = candidate['module']
            if module_path.startswith(f"{component.lower()}."):
                # Convert to relative import
                relative_path = module_path[len(f"{component.lower()}."):]
                new_import = f"from .{relative_path} import {candidate['item']}"
            else:
                new_import = f"from {module_path} import {candidate['item']}"
            
            # Find where to insert (after other imports)
            insert_line = self._find_import_insert_position(tree)
            
            # Add to __all__ if it exists
            all_export = self._update_all_export(content, candidate['item'])
            
            # Insert the import
            lines = content.split('\n')
            lines.insert(insert_line, new_import)
            
            # Write back
            with open(init_path, 'w') as f:
                f.write('\n'.join(lines))
            
            self.changes_made.append({
                'type': 'flattening',
                'file': str(init_path),
                'added': new_import,
                'item': candidate['item']
            })
            
            print(f"  {Colors.GREEN}✓ Added to {init_path}{Colors.ENDC}")
            print(f"  {Colors.GREEN}  Users can now use: from {component.lower()} import {candidate['item']}{Colors.ENDC}")
            
        except Exception as e:
            print(f"  {Colors.FAIL}Error adding to __init__.py: {e}{Colors.ENDC}")
    
    def _find_import_insert_position(self, tree: ast.AST) -> int:
        """Find the best position to insert a new import."""
        last_import_line = 0
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if hasattr(node, 'lineno'):
                    last_import_line = max(last_import_line, node.lineno)
        
        return last_import_line + 1 if last_import_line > 0 else 1
    
    def _update_all_export(self, content: str, item: str) -> str:
        """Update __all__ if it exists."""
        # This is simplified - real implementation would use AST
        if "__all__" in content:
            # Find and update __all__
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.strip().startswith("__all__"):
                    # Simple append to the list
                    if "]" in line:
                        lines[i] = line.replace("]", f", '{item}']")
                    break
            return '\n'.join(lines)
        return content
    
    def show_summary(self):
        """Show summary of changes made."""
        if not self.changes_made:
            print(f"\n{Colors.WARNING}No changes were made.{Colors.ENDC}")
            return
            
        print(f"\n{Colors.HEADER}=== Summary of Changes ==={Colors.ENDC}")
        print(f"Total changes: {len(self.changes_made)}")
        
        # Group by type
        by_type = {}
        for change in self.changes_made:
            change_type = change['type']
            if change_type not in by_type:
                by_type[change_type] = []
            by_type[change_type].append(change)
        
        for change_type, changes in by_type.items():
            print(f"\n{change_type.replace('_', ' ').title()}: {len(changes)}")
            for change in changes[:3]:  # Show first 3
                if change_type == 'star_import_fix':
                    print(f"  - {Path(change['file']).relative_to(self.tekton_root)}")
                    print(f"    {change['old']} → {change['new']}")
                elif change_type == 'flattening':
                    print(f"  - Added {change['item']} to {Path(change['file']).name}")
        
        if self.backups:
            print(f"\n{Colors.CYAN}Backups created in: .import_fixes_backup/{Colors.ENDC}")
            print(f"Total files backed up: {len(self.backups)}")
    
    def run(self):
        """Main interactive loop."""
        print(f"{Colors.HEADER}Tekton Import Fixer{Colors.ENDC}")
        print("This tool will help you fix import issues interactively.\n")
        
        # Load results
        results = self.load_results()
        components = results.get("components", [])
        
        if not components:
            print(f"{Colors.FAIL}No components found in analysis results.{Colors.ENDC}")
            return
        
        # Show overview
        total_issues = sum(
            len(c.get("circular_dependencies", [])) +
            len(c.get("star_imports", [])) +
            len(c.get("flattening_candidates", []))
            for c in components
        )
        
        print(f"Found {total_issues} total issues across {len(components)} components")
        print("\nOptions for each fix:")
        print("  y = yes, fix this")
        print("  n = no, skip this")  
        print("  s = skip all remaining in this category")
        print("  a = auto-fix all (where available)\n")
        
        # Process each component
        for component in components:
            if "error" in component:
                continue
                
            issues = (
                len(component.get("circular_dependencies", [])) +
                len(component.get("star_imports", [])) +
                len(component.get("flattening_candidates", []))
            )
            
            if issues == 0:
                continue
                
            print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
            print(f"{Colors.BOLD}Component: {component['name']} ({issues} issues){Colors.ENDC}")
            print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
            
            response = self.prompt_user(
                f"Process {component['name']}?",
                ["y", "n", "q"]  # yes, no, quit
            )
            
            if response == "q":
                break
            elif response == "n":
                continue
            
            # Fix different types of issues
            self.fix_star_imports(component)
            self.fix_circular_dependencies(component)
            self.suggest_flattening(component)
        
        # Show summary
        self.show_summary()


def show_help():
    """Show help message."""
    help_text = f"""
{Colors.HEADER}Tekton Import Fixer - Step 2 of 2{Colors.ENDC}
{Colors.HEADER}=================================={Colors.ENDC}

This tool interactively fixes import issues found by the analyzer.

{Colors.CYAN}USAGE:{Colors.ENDC}
    python tekton_import_fixer.py --help         Show this help
    python tekton_import_fixer.py                Run interactive fixer
    python tekton_import_fixer.py --auto-backup  Run with automatic backups (default)

{Colors.CYAN}PREREQUISITES:{Colors.ENDC}
    You must run the analyzer first:
    python tekton_import_analyzer.py --all

{Colors.CYAN}WHAT IT FIXES:{Colors.ENDC}
    {Colors.GREEN}✓{Colors.ENDC} Star imports → Converts to explicit imports
    {Colors.GREEN}✓{Colors.ENDC} Flattening → Adds frequently imported items to __init__.py
    {Colors.WARNING}!{Colors.ENDC} Circular deps → Shows suggestions (manual fix required)

{Colors.CYAN}INTERACTIVE OPTIONS:{Colors.ENDC}
    y = yes, fix this issue
    n = no, skip this issue
    s = skip all remaining in this category
    a = auto-fix all similar issues (where available)
    q = quit

{Colors.CYAN}SAFETY FEATURES:{Colors.ENDC}
    - Creates backups before modifying files
    - Shows what will be changed before applying
    - Provides summary of all changes made

{Colors.CYAN}WORKFLOW:{Colors.ENDC}
    1. Run analyzer: python tekton_import_analyzer.py --all
    2. Review report: cat import_analysis_report.md  
    3. {Colors.BOLD}Run this fixer: python tekton_import_fixer.py{Colors.ENDC}
    4. Review changes and test your code

{Colors.WARNING}Note: Always test your code after making import changes!{Colors.ENDC}
"""
    print(help_text)
    sys.exit(0)


def main():
    # Check for help
    if "--help" in sys.argv or "-h" in sys.argv or "help" in sys.argv:
        show_help()
    
    tekton_root = os.getenv('TEKTON_ROOT', '/Users/cskoons/projects/github/Tekton')
    
    # Parse arguments
    auto_backup = "--auto-backup" in sys.argv or not "--no-backup" in sys.argv  # Default to True
    
    fixer = TektonImportFixer(tekton_root, auto_backup=auto_backup)
    
    try:
        fixer.run()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Interrupted by user{Colors.ENDC}")
        fixer.show_summary()
    except Exception as e:
        print(f"\n{Colors.FAIL}Error: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()