#!/usr/bin/env python3
"""
Dry-run dependency verification for Tekton components.
Checks all dependencies without installing anything.
"""

import subprocess
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional
from collections import defaultdict
import argparse


class DependencyVerifier:
    def __init__(self, tekton_root: Path):
        self.tekton_root = tekton_root
        self.shared_req_dir = tekton_root / "shared" / "requirements"
        self.components = self._find_components()
        self.all_requirements = defaultdict(set)  # package -> set of (component, version_spec)
        self.import_map = {
            'python-dotenv': 'dotenv',
            'pydantic-settings': 'pydantic_settings',
            'python-multipart': 'multipart',
            'beautifulsoup4': 'bs4',
            'faiss-cpu': 'faiss',
            'sentence-transformers': 'sentence_transformers',
            'qdrant-client': 'qdrant_client',
            'scikit-learn': 'sklearn',
            'huggingface-hub': 'huggingface_hub',
            'psycopg2-binary': 'psycopg2',
            'python-decouple': 'decouple',
            'asyncio-throttle': 'asyncio_throttle',
            'prometheus-client': 'prometheus_client',
            'PyYAML': 'yaml',
            'sse-starlette': 'sse_starlette',
            'pydantic-ai': 'pydantic_ai',
            'langchain-community': 'langchain_community',
        }
    
    def _find_components(self) -> List[Tuple[str, Path]]:
        """Find all Tekton components with requirements.txt."""
        components = []
        
        # Standard component directories
        for path in self.tekton_root.iterdir():
            if path.is_dir() and (path / "requirements.txt").exists():
                # Skip special cases
                if path.name in ["shared", "scripts", "data", "config", "MetaData", "images"]:
                    continue
                components.append((path.name, path))
        
        return sorted(components)
    
    def _parse_requirement_line(self, line: str) -> Optional[Tuple[str, str]]:
        """Parse a requirement line into (package, version_spec)."""
        line = line.strip()
        
        # Skip comments, empty lines
        if not line or line.startswith('#'):
            return None
            
        # Skip -r includes (we'll handle these separately)
        if line.startswith('-r '):
            return None
        
        # Parse package and version
        # Match: package==1.0.0, package>=1.0.0, package<2.0,>=1.0, etc.
        match = re.match(r'^([a-zA-Z0-9_.-]+)\s*([><=!~]+.*?)?\s*(?:#.*)?$', line)
        if match:
            package = match.group(1).lower()
            version_spec = match.group(2) or ""
            return package, version_spec
        
        return None
    
    def _resolve_includes(self, req_file: Path, base_path: Path) -> List[Path]:
        """Resolve -r includes in a requirements file."""
        includes = []
        
        with open(req_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('-r '):
                    include_path = line[3:].strip()
                    # Resolve relative to the requirements file location
                    resolved = (req_file.parent / include_path).resolve()
                    if resolved.exists():
                        includes.append(resolved)
                        # Recursively resolve includes
                        includes.extend(self._resolve_includes(resolved, base_path))
        
        return includes
    
    def _analyze_component(self, name: str, path: Path) -> Dict:
        """Analyze a component's requirements."""
        req_file = path / "requirements.txt"
        result = {
            'name': name,
            'path': path,
            'requirements': {},
            'includes': [],
            'errors': [],
            'warnings': []
        }
        
        if not req_file.exists():
            result['errors'].append("requirements.txt not found")
            return result
        
        # Get all files to parse (main + includes)
        files_to_parse = [req_file]
        includes = self._resolve_includes(req_file, path)
        files_to_parse.extend(includes)
        
        # Track which shared requirements are used
        for include in includes:
            if str(self.shared_req_dir) in str(include):
                result['includes'].append(include.name)
        
        # Parse all requirements
        for file_path in files_to_parse:
            with open(file_path, 'r') as f:
                for line in f:
                    parsed = self._parse_requirement_line(line)
                    if parsed:
                        package, version_spec = parsed
                        result['requirements'][package] = version_spec
                        self.all_requirements[package].add((name, version_spec))
        
        return result
    
    def _check_conflicts(self) -> List[Dict]:
        """Check for version conflicts between components."""
        conflicts = []
        
        for package, specs in self.all_requirements.items():
            if len(specs) > 1:
                # Group by version spec
                version_groups = defaultdict(list)
                for component, spec in specs:
                    version_groups[spec].append(component)
                
                # If multiple different specs, that's a potential conflict
                if len(version_groups) > 1:
                    conflicts.append({
                        'package': package,
                        'conflicts': [
                            {'spec': spec, 'components': components}
                            for spec, components in version_groups.items()
                        ]
                    })
        
        return conflicts
    
    def _check_installed(self, package: str) -> Tuple[bool, Optional[str]]:
        """Check if a package is installed and get its version."""
        success, output = self._run_command(["uv", "pip", "show", package])
        if success:
            # Parse version from output
            for line in output.split('\n'):
                if line.startswith('Version:'):
                    return True, line.split(':', 1)[1].strip()
        return False, None
    
    def _check_importable(self, package: str) -> bool:
        """Check if a package can be imported."""
        import_name = self.import_map.get(package, package)
        
        try:
            __import__(import_name)
            return True
        except ImportError:
            return False
    
    def _run_command(self, cmd: List[str]) -> Tuple[bool, str]:
        """Run a command and return success status and output."""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)
    
    def verify_all(self) -> Dict:
        """Run full verification and return results."""
        results = {
            'components': {},
            'conflicts': [],
            'summary': {
                'total_components': len(self.components),
                'healthy': 0,
                'warnings': 0,
                'errors': 0,
                'total_packages': 0,
                'installed': 0,
                'missing': 0,
                'importable': 0
            }
        }
        
        # Analyze each component
        print("Analyzing components...")
        for name, path in self.components:
            print(f"  - {name}")
            analysis = self._analyze_component(name, path)
            results['components'][name] = analysis
            
            if analysis['errors']:
                results['summary']['errors'] += 1
            elif analysis['warnings']:
                results['summary']['warnings'] += 1
            else:
                results['summary']['healthy'] += 1
        
        # Check for conflicts
        print("\nChecking for conflicts...")
        results['conflicts'] = self._check_conflicts()
        
        # Check package status
        print("\nChecking package status...")
        all_packages = set()
        for package in self.all_requirements.keys():
            all_packages.add(package)
        
        results['summary']['total_packages'] = len(all_packages)
        
        for package in all_packages:
            installed, version = self._check_installed(package)
            if installed:
                results['summary']['installed'] += 1
                if self._check_importable(package):
                    results['summary']['importable'] += 1
            else:
                results['summary']['missing'] += 1
        
        return results
    
    def generate_report(self, results: Dict, verbose: bool = False) -> str:
        """Generate a human-readable report."""
        lines = []
        lines.append("Tekton Dependency Verification Report")
        lines.append("=" * 50)
        lines.append("")
        
        # Summary
        s = results['summary']
        lines.append(f"Checked {s['total_components']} components")
        lines.append(f"Total unique packages: {s['total_packages']}")
        lines.append("")
        
        # Component health
        lines.append("Component Status:")
        lines.append(f"  ✅ Healthy: {s['healthy']}")
        lines.append(f"  ⚠️  Warnings: {s['warnings']}")
        lines.append(f"  ❌ Errors: {s['errors']}")
        lines.append("")
        
        # Package status
        lines.append("Package Status:")
        lines.append(f"  📦 Installed: {s['installed']}/{s['total_packages']}")
        lines.append(f"  ✓  Importable: {s['importable']}/{s['installed']}")
        lines.append(f"  ⬇️  Need install: {s['missing']}")
        lines.append("")
        
        # Conflicts
        if results['conflicts']:
            lines.append("Version Conflicts Found:")
            for conflict in results['conflicts']:
                lines.append(f"\n  {conflict['package']}:")
                for spec_info in conflict['conflicts']:
                    components = ", ".join(spec_info['components'])
                    lines.append(f"    - {spec_info['spec'] or 'no version'}: {components}")
        else:
            lines.append("✅ No version conflicts found")
        
        lines.append("")
        
        # Component details (if verbose)
        if verbose:
            lines.append("\nComponent Details:")
            lines.append("-" * 50)
            for name, info in results['components'].items():
                lines.append(f"\n{name}:")
                if info['includes']:
                    lines.append(f"  Uses shared: {', '.join(info['includes'])}")
                lines.append(f"  Packages: {len(info['requirements'])}")
                if info['errors']:
                    lines.append(f"  ❌ Errors: {', '.join(info['errors'])}")
                if info['warnings']:
                    lines.append(f"  ⚠️  Warnings: {', '.join(info['warnings'])}")
        
        # Recommendations
        lines.append("\nRecommendations:")
        if s['missing'] > 0:
            lines.append(f"  - Install {s['missing']} missing packages")
        if results['conflicts']:
            lines.append(f"  - Resolve {len(results['conflicts'])} version conflicts")
        if s['healthy'] < s['total_components']:
            lines.append(f"  - Fix {s['total_components'] - s['healthy']} components with issues")
        
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Verify Tekton dependencies without installing"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed component information"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    parser.add_argument(
        "--component",
        help="Check only a specific component"
    )
    
    args = parser.parse_args()
    
    # Find Tekton root
    tekton_root = Path(__file__).parent.parent.parent
    if not (tekton_root / "shared").exists():
        print("Error: Could not find Tekton root directory")
        return 1
    
    verifier = DependencyVerifier(tekton_root)
    
    # Run verification
    results = verifier.verify_all()
    
    # Output results
    if args.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        report = verifier.generate_report(results, verbose=args.verbose)
        print(report)
    
    # Return exit code based on health
    if results['summary']['errors'] > 0:
        return 1
    elif results['summary']['warnings'] > 0:
        return 2
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())