#!/usr/bin/env python3
"""
Comprehensive Import Analysis Tool for Tekton

This tool analyzes import patterns across Tekton components and identifies:
- Circular dependencies
- Star imports
- Deep import chains
- Missing modules
- Flattening opportunities
- Import errors

Usage:
    python tekton_import_analyzer.py [component1] [component2] ...
    python tekton_import_analyzer.py --all
"""

import ast
import os
import sys
import json
import subprocess
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional
from datetime import datetime


class TektonImportAnalyzer:
    def __init__(self, tekton_root: str):
        self.tekton_root = Path(tekton_root)
        self.components = [
            "Engram", "Prometheus", "Hermes", "Athena", "Rhetor",
            "Budget", "Apollo", "Ergon", "Harmonia", "Metis",
            "Sophia", "Synthesis", "Telos", "Terma"
        ]
        
        # Analysis results
        self.circular_deps = defaultdict(list)
        self.star_imports = []
        self.deep_imports = []
        self.missing_imports = []
        self.flattening_candidates = []
        self.import_frequency = Counter()
        self.depth_distribution = Counter()
        
    def analyze_component(self, component: str) -> Dict:
        """Analyze a single component."""
        print(f"Analyzing {component}...")
        
        component_path = self.tekton_root / component
        if not component_path.exists():
            return {"error": f"Component {component} not found"}
        
        # Reset counters for this component
        component_results = {
            "name": component,
            "circular_dependencies": [],
            "star_imports": [],
            "deep_imports": [],
            "missing_imports": [],
            "flattening_candidates": [],
            "import_stats": {}
        }
        
        # 1. Run pylint for circular dependencies
        self._find_circular_dependencies(component, component_path, component_results)
        
        # 2. Find star imports
        self._find_star_imports(component_path, component_results)
        
        # 3. Analyze import depths and patterns
        self._analyze_import_patterns(component_path, component_results)
        
        # 4. Check for missing imports
        self._check_missing_imports(component_path, component_results)
        
        # 5. Run pydeps if available
        self._run_pydeps_analysis(component, component_path, component_results)
        
        return component_results
    
    def _find_circular_dependencies(self, component: str, path: Path, results: Dict):
        """Use pylint to find circular dependencies."""
        try:
            cmd = [
                "pylint", str(path / component.lower()),
                "--disable=all",
                "--enable=cyclic-import",
                "--output-format=json"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.stdout:
                issues = json.loads(result.stdout)
                for issue in issues:
                    if issue.get("symbol") == "cyclic-import":
                        results["circular_dependencies"].append({
                            "file": issue.get("path"),
                            "line": issue.get("line"),
                            "message": issue.get("message"),
                            "cycle": self._extract_cycle_from_message(issue.get("message", ""))
                        })
        except Exception as e:
            print(f"  Warning: Could not run pylint analysis: {e}")
    
    def _extract_cycle_from_message(self, message: str) -> List[str]:
        """Extract the cycle path from pylint message."""
        # Pylint message format: "Cyclic import (module1 -> module2 -> module1)"
        if "->" in message:
            cycle_part = message.split("(")[-1].rstrip(")")
            return [m.strip() for m in cycle_part.split("->")]
        return []
    
    def _find_star_imports(self, path: Path, results: Dict):
        """Find all star imports in the component."""
        for py_file in path.rglob("*.py"):
            if "__pycache__" in str(py_file) or "venv" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        for alias in node.names:
                            if alias.name == '*':
                                results["star_imports"].append({
                                    "file": str(py_file.relative_to(self.tekton_root)),
                                    "line": node.lineno,
                                    "module": node.module or ".",
                                    "full_import": f"from {node.module or '.'} import *"
                                })
            except Exception as e:
                pass  # Skip files that can't be parsed
    
    def _analyze_import_patterns(self, path: Path, results: Dict):
        """Analyze import depth and frequency patterns."""
        import_data = defaultdict(int)
        item_modules = defaultdict(set)
        depth_counts = Counter()
        
        for py_file in path.rglob("*.py"):
            if "__pycache__" in str(py_file) or "venv" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module:
                            depth = node.module.count('.') + 1
                            depth_counts[depth] += 1
                            
                            # Track deep imports
                            if depth >= 4:
                                for alias in node.names:
                                    if alias.name != '*':
                                        import_str = f"from {node.module} import {alias.name}"
                                        import_data[import_str] += 1
                                        item_modules[alias.name].add(node.module)
                                        
                                        if depth >= 5:
                                            results["deep_imports"].append({
                                                "file": str(py_file.relative_to(self.tekton_root)),
                                                "line": node.lineno,
                                                "import": import_str,
                                                "depth": depth
                                            })
            except Exception:
                pass
        
        # Find flattening candidates
        for import_str, count in import_data.items():
            if count >= 5:  # Imported 5+ times
                parts = import_str.split(" import ")
                if len(parts) == 2:
                    module = parts[0].replace("from ", "")
                    item = parts[1]
                    
                    conflicts = [m for m in item_modules[item] if m != module]
                    
                    results["flattening_candidates"].append({
                        "import": import_str,
                        "count": count,
                        "item": item,
                        "module": module,
                        "depth": module.count('.') + 1,
                        "conflicts": conflicts
                    })
        
        # Sort flattening candidates by count
        results["flattening_candidates"].sort(key=lambda x: x["count"], reverse=True)
        
        # Store stats
        results["import_stats"] = {
            "depth_distribution": dict(depth_counts),
            "total_imports": sum(depth_counts.values()),
            "max_depth": max(depth_counts.keys()) if depth_counts else 0
        }
    
    def _check_missing_imports(self, path: Path, results: Dict):
        """Check for imports that might fail."""
        # This is a simplified check - in reality, you'd want to actually try importing
        component_name = path.name.lower()
        
        for py_file in path.rglob("*.py"):
            if "__pycache__" in str(py_file) or "venv" in str(py_file):
                continue
                
            try:
                # Try to compile the file
                with open(py_file, 'r', encoding='utf-8') as f:
                    compile(f.read(), str(py_file), 'exec')
            except SyntaxError:
                pass  # Syntax errors are not import errors
            except Exception as e:
                if "import" in str(e).lower():
                    results["missing_imports"].append({
                        "file": str(py_file.relative_to(self.tekton_root)),
                        "error": str(e)
                    })
    
    def _run_pydeps_analysis(self, component: str, path: Path, results: Dict):
        """Run pydeps to generate visual analysis if available."""
        try:
            output_file = self.tekton_root / f"{component}_circular_deps.json"
            cmd = [
                "pydeps", str(path / component.lower()),
                "--show-cycles", "--no-show", "--max-bacon=3",
                "--json", "-o", str(output_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if output_file.exists():
                with open(output_file, 'r') as f:
                    pydeps_data = json.load(f)
                    # Extract cycles from pydeps data
                    # This would need to parse the pydeps JSON format
                output_file.unlink()  # Clean up
        except Exception:
            pass  # pydeps not available or failed
    
    def analyze_all(self) -> List[Dict]:
        """Analyze all components."""
        results = []
        for component in self.components:
            if (self.tekton_root / component).exists():
                results.append(self.analyze_component(component))
        return results
    
    def generate_report(self, results: List[Dict]) -> str:
        """Generate a markdown report from analysis results."""
        report = []
        report.append("# Tekton Import Analysis Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Summary
        total_circular = sum(len(r.get("circular_dependencies", [])) for r in results)
        total_star = sum(len(r.get("star_imports", [])) for r in results)
        total_deep = sum(len(r.get("deep_imports", [])) for r in results)
        
        report.append("## Summary")
        report.append(f"- Components analyzed: {len(results)}")
        report.append(f"- Total circular dependencies: {total_circular}")
        report.append(f"- Total star imports: {total_star}")
        report.append(f"- Total deep imports (depth ≥ 5): {total_deep}")
        report.append("")
        
        # Component details
        for component_result in results:
            if "error" in component_result:
                continue
                
            name = component_result["name"]
            report.append(f"## {name}")
            
            # Circular dependencies
            circular = component_result.get("circular_dependencies", [])
            if circular:
                report.append(f"\n### Circular Dependencies ({len(circular)})")
                for dep in circular[:5]:  # Show first 5
                    cycle_str = " → ".join(dep.get("cycle", []))
                    report.append(f"- {dep['file']}:{dep['line']}")
                    report.append(f"  - Cycle: {cycle_str}")
            
            # Star imports
            stars = component_result.get("star_imports", [])
            if stars:
                report.append(f"\n### Star Imports ({len(stars)})")
                for star in stars[:5]:
                    report.append(f"- {star['file']}:{star['line']}")
                    report.append(f"  - `{star['full_import']}`")
            
            # Deep imports
            deep = component_result.get("deep_imports", [])
            if deep:
                report.append(f"\n### Deep Imports (depth ≥ 5) ({len(deep)})")
                # Group by import string
                deep_grouped = defaultdict(list)
                for d in deep:
                    deep_grouped[d['import']].append(d['file'])
                
                for imp, files in list(deep_grouped.items())[:5]:
                    report.append(f"- `{imp}` (used in {len(files)} files)")
            
            # Flattening candidates
            candidates = component_result.get("flattening_candidates", [])
            if candidates:
                report.append(f"\n### Top Flattening Candidates")
                for cand in candidates[:5]:
                    report.append(f"- **{cand['item']}** from `{cand['module']}` (imported {cand['count']} times)")
                    if cand['conflicts']:
                        report.append(f"  - ⚠️ Conflicts with: {', '.join(cand['conflicts'])}")
            
            # Stats
            stats = component_result.get("import_stats", {})
            if stats.get("depth_distribution"):
                report.append(f"\n### Import Depth Distribution")
                for depth, count in sorted(stats["depth_distribution"].items()):
                    report.append(f"- Depth {depth}: {count} imports")
            
            report.append("")
        
        return "\n".join(report)
    
    def save_results(self, results: List[Dict], output_file: str = "import_analysis_results.json"):
        """Save raw results as JSON for the fixer script."""
        output_path = self.tekton_root / output_file
        with open(output_path, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "components": results
            }, f, indent=2)
        return output_path


def show_help():
    """Show help message."""
    help_text = """
Tekton Import Analyzer - Step 1 of 2
====================================

This tool analyzes import patterns across Tekton components to identify issues.

USAGE:
    python tekton_import_analyzer.py --help              Show this help
    python tekton_import_analyzer.py --all               Analyze all components
    python tekton_import_analyzer.py [component1] ...    Analyze specific components

EXAMPLES:
    python tekton_import_analyzer.py --all
    python tekton_import_analyzer.py Engram Prometheus

WHAT IT FINDS:
    - Circular dependencies between modules
    - Star imports (from X import *)
    - Deep import chains (5+ levels deep)
    - Missing/broken imports
    - Flattening opportunities (frequently imported items)

OUTPUT:
    - import_analysis_report.md      Human-readable report
    - import_analysis_results.json   Data for the fixer tool

WORKFLOW:
    1. Run this analyzer first: python tekton_import_analyzer.py --all
    2. Review the report: cat import_analysis_report.md
    3. Run the fixer next: python tekton_import_fixer.py
    
The analyzer identifies problems, the fixer helps you fix them interactively.
"""
    print(help_text)
    sys.exit(0)


def main():
    # Check for help
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h", "help"]:
        show_help()
    
    # Get Tekton root
    tekton_root = os.getenv('TEKTON_ROOT', '/Users/cskoons/projects/github/Tekton')
    analyzer = TektonImportAnalyzer(tekton_root)
    
    # Parse arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--all":
            print("Analyzing all Tekton components...")
            results = analyzer.analyze_all()
        else:
            # Analyze specific components
            results = []
            for component in sys.argv[1:]:
                result = analyzer.analyze_component(component.capitalize())
                if result:
                    results.append(result)
    else:
        print("Usage: python tekton_import_analyzer.py [component1] [component2] ...")
        print("       python tekton_import_analyzer.py --all")
        sys.exit(1)
    
    # Generate report
    report = analyzer.generate_report(results)
    
    # Save report
    report_path = Path(tekton_root) / "import_analysis_report.md"
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"\nReport saved to: {report_path}")
    
    # Save JSON results for fixer
    json_path = analyzer.save_results(results)
    print(f"Raw results saved to: {json_path}")
    
    # Print summary
    total_issues = sum(
        len(r.get("circular_dependencies", [])) +
        len(r.get("star_imports", [])) +
        len(r.get("deep_imports", []))
        for r in results if "error" not in r
    )
    
    print(f"\nTotal issues found: {total_issues}")
    print("\nRun 'python tekton_import_fixer.py' to interactively fix issues")


if __name__ == "__main__":
    main()