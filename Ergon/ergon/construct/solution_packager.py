"""
Solution Packager for Ergon Construct

Takes GitHub projects and packages them as deployable solutions with:
- Programming standards applied
- CI Guide included
- Deployment configuration
"""

import os
import json
import asyncio
import logging
import subprocess
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

logger = logging.getLogger(__name__)


class RepositoryAnalyzer:
    """Analyzes GitHub repositories to understand structure and needs."""

    def __init__(self):
        self.supported_languages = {
            'python': ['.py', 'requirements.txt', 'setup.py', 'pyproject.toml'],
            'javascript': ['.js', '.jsx', 'package.json', 'node_modules'],
            'typescript': ['.ts', '.tsx', 'tsconfig.json'],
            'go': ['.go', 'go.mod', 'go.sum'],
            'rust': ['.rs', 'Cargo.toml', 'Cargo.lock'],
        }

    async def analyze(self, repo_path: Path) -> Dict[str, Any]:
        """Analyze repository structure and content."""
        analysis = {
            'project_type': 'unknown',
            'structure': {},
            'files': [],
            'config_files': [],
            'dependencies': {},
            'hardcoded_values': [],
            'large_files': [],
            'missing_docs': []
        }

        # Detect project type
        analysis['project_type'] = self._detect_project_type(repo_path)

        # Scan files
        for root, dirs, files in os.walk(repo_path):
            # Skip hidden and vendor directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'vendor', '__pycache__']]

            for file in files:
                if file.startswith('.'):
                    continue

                file_path = Path(root) / file
                rel_path = file_path.relative_to(repo_path)

                # Track all files
                analysis['files'].append(str(rel_path))

                # Check for config files
                if file.endswith(('.json', '.yaml', '.yml', '.toml', '.ini', '.env.example')):
                    analysis['config_files'].append(str(rel_path))

                # Check for large files
                try:
                    line_count = sum(1 for _ in open(file_path, 'r', errors='ignore'))
                    if line_count > 500:
                        analysis['large_files'].append({
                            'path': str(rel_path),
                            'lines': line_count
                        })
                except:
                    pass

                # Scan for hardcoded values
                hardcoded = await self._scan_hardcoded_values(file_path)
                if hardcoded:
                    analysis['hardcoded_values'].extend(hardcoded)

        # Check for missing documentation
        doc_files = ['README.md', 'README.rst', 'README.txt', 'INSTALL.md', 'CONFIG.md']
        for doc in doc_files:
            if not (repo_path / doc).exists():
                analysis['missing_docs'].append(doc)

        # Extract dependencies
        analysis['dependencies'] = await self._extract_dependencies(repo_path, analysis['project_type'])

        return analysis

    def _detect_project_type(self, repo_path: Path) -> str:
        """Detect the primary language/framework of the project."""
        scores = {}

        for lang, indicators in self.supported_languages.items():
            score = 0
            for indicator in indicators:
                if indicator.startswith('.'):
                    # File extension - count files
                    count = len(list(repo_path.rglob(f'*{indicator}')))
                    score += count
                else:
                    # Specific file - check existence
                    if (repo_path / indicator).exists():
                        score += 10

            if score > 0:
                scores[lang] = score

        if scores:
            return max(scores, key=scores.get)
        return 'unknown'

    async def _scan_hardcoded_values(self, file_path: Path) -> List[Dict[str, Any]]:
        """Scan file for hardcoded values."""
        hardcoded = []

        try:
            with open(file_path, 'r', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    # Check for URLs
                    if 'http://' in line or 'https://' in line:
                        if not line.strip().startswith('#') and not line.strip().startswith('//'):
                            hardcoded.append({
                                'type': 'url',
                                'file': str(file_path.name),
                                'line': line_num,
                                'value': line.strip()[:100]
                            })

                    # Check for ports
                    if ':' in line and any(str(port) in line for port in [3000, 8000, 8080, 5000, 3306, 5432, 6379]):
                        hardcoded.append({
                            'type': 'port',
                            'file': str(file_path.name),
                            'line': line_num,
                            'value': line.strip()[:100]
                        })

                    # Check for API keys patterns
                    if 'api_key' in line.lower() or 'apikey' in line.lower() or 'secret' in line.lower():
                        if '=' in line and not line.strip().startswith('#'):
                            hardcoded.append({
                                'type': 'potential_secret',
                                'file': str(file_path.name),
                                'line': line_num,
                                'value': 'REDACTED'
                            })
        except:
            pass

        return hardcoded

    async def _extract_dependencies(self, repo_path: Path, project_type: str) -> Dict[str, Any]:
        """Extract project dependencies."""
        deps = {}

        if project_type == 'python':
            req_file = repo_path / 'requirements.txt'
            if req_file.exists():
                deps['python'] = req_file.read_text().splitlines()

        elif project_type == 'javascript' or project_type == 'typescript':
            pkg_file = repo_path / 'package.json'
            if pkg_file.exists():
                try:
                    pkg = json.loads(pkg_file.read_text())
                    deps['npm'] = {
                        'dependencies': pkg.get('dependencies', {}),
                        'devDependencies': pkg.get('devDependencies', {})
                    }
                except:
                    pass

        elif project_type == 'go':
            mod_file = repo_path / 'go.mod'
            if mod_file.exists():
                deps['go'] = mod_file.read_text()

        return deps


class StandardsEngine:
    """Applies programming standards to projects."""

    STANDARDS = {
        'extract_hardcoded': {
            'name': 'Extract Hardcoded Values',
            'description': 'Move hardcoded URLs, ports, and paths to configuration'
        },
        'split_large_files': {
            'name': 'Split Large Files',
            'description': 'Break files over 500 lines into smaller modules'
        },
        'add_documentation': {
            'name': 'Add Missing Documentation',
            'description': 'Generate README, INSTALL, and CONFIG documentation'
        },
        'add_error_handling': {
            'name': 'Add Error Handling',
            'description': 'Add try/catch blocks to unprotected code'
        },
        'enforce_naming': {
            'name': 'Enforce Naming Conventions',
            'description': 'Apply consistent naming to files and functions'
        },
        'add_config_example': {
            'name': 'Add Configuration Examples',
            'description': 'Create .env.example and config templates'
        }
    }

    async def recommend_standards(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Recommend standards based on analysis."""
        recommendations = []

        # Check for hardcoded values
        if analysis['hardcoded_values']:
            recommendations.append({
                'standard_id': 'extract_hardcoded',
                'reason': f"Found {len(analysis['hardcoded_values'])} hardcoded values",
                'auto_apply': True,
                'items': analysis['hardcoded_values'][:5]  # Show first 5
            })

        # Check for large files
        if analysis['large_files']:
            for file_info in analysis['large_files']:
                if file_info['lines'] > 500:
                    recommendations.append({
                        'standard_id': 'split_large_files',
                        'reason': f"{file_info['path']} has {file_info['lines']} lines",
                        'auto_apply': False,
                        'items': [file_info['path']]
                    })

        # Check for missing docs
        if analysis['missing_docs']:
            recommendations.append({
                'standard_id': 'add_documentation',
                'reason': f"Missing {', '.join(analysis['missing_docs'])}",
                'auto_apply': True,
                'items': analysis['missing_docs']
            })

        # Check for config examples
        if not any('.example' in f for f in analysis['config_files']):
            recommendations.append({
                'standard_id': 'add_config_example',
                'reason': 'No configuration examples found',
                'auto_apply': True,
                'items': []
            })

        return recommendations

    async def apply_standards(self, repo_path: Path, standards: List[str]) -> Dict[str, Any]:
        """Apply selected standards to repository."""
        results = {'applied': [], 'errors': []}

        for standard_id in standards:
            try:
                if standard_id == 'extract_hardcoded':
                    await self._extract_hardcoded_values(repo_path)
                    results['applied'].append(standard_id)

                elif standard_id == 'add_documentation':
                    await self._add_documentation(repo_path)
                    results['applied'].append(standard_id)

                elif standard_id == 'add_config_example':
                    await self._add_config_examples(repo_path)
                    results['applied'].append(standard_id)

                # Other standards would be implemented here

            except Exception as e:
                results['errors'].append({
                    'standard': standard_id,
                    'error': str(e)
                })

        return results

    async def _extract_hardcoded_values(self, repo_path: Path):
        """Extract hardcoded values to config file."""
        config = {}
        config_file = repo_path / 'config.yaml'

        # Would scan files and extract values
        # For now, create a template
        config = {
            'server': {
                'host': '0.0.0.0',
                'port': 8000
            },
            'database': {
                'url': 'postgresql://localhost/db'
            },
            'api': {
                'base_url': 'https://api.example.com'
            }
        }

        import yaml
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)

    async def _add_documentation(self, repo_path: Path):
        """Add missing documentation files."""
        # Add README if missing
        readme = repo_path / 'README.md'
        if not readme.exists():
            readme.write_text("""# Project Name

## Description
This project has been packaged by Tekton Ergon.

## Installation
See INSTALL.md for installation instructions.

## Configuration
See CONFIG.md for configuration options.

## Usage
[Add usage instructions here]

## License
[Specify license]
""")

        # Add INSTALL.md
        install = repo_path / 'INSTALL.md'
        if not install.exists():
            install.write_text("""# Installation Guide

## Prerequisites
- List prerequisites here

## Installation Steps
1. Clone the repository
2. Install dependencies
3. Configure the application
4. Run the application

## Troubleshooting
[Add common issues and solutions]
""")

    async def _add_config_examples(self, repo_path: Path):
        """Add configuration example files."""
        env_example = repo_path / '.env.example'
        if not env_example.exists():
            env_example.write_text("""# Environment Configuration Example
# Copy this file to .env and update values

# Server Configuration
PORT=8000
HOST=0.0.0.0

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/dbname

# API Keys (obtain from providers)
API_KEY=your_api_key_here
SECRET_KEY=your_secret_key_here
""")


class PlanCreator:
    """Creates and manages execution plans."""

    def __init__(self):
        self.plan_version = 0

    async def create_plan(self, config: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create execution plan based on config and analysis."""
        self.plan_version += 1

        steps = []

        # Step 1: Clone/Pull repository
        steps.append({
            'id': 'clone',
            'type': 'git',
            'description': f"Clone repository from {config['github_url']}",
            'command': f"git clone {config['github_url']}",
            'estimated_time': 10
        })

        # Step 2: Apply standards
        if config.get('apply_standards'):
            for standard in config['standards']:
                steps.append({
                    'id': f'standard_{standard}',
                    'type': 'standard',
                    'description': f"Apply standard: {StandardsEngine.STANDARDS[standard]['name']}",
                    'standard': standard,
                    'estimated_time': 5
                })

        # Step 3: Generate CI Guide
        if config.get('include_ci'):
            steps.append({
                'id': 'ci_guide',
                'type': 'ci_guide',
                'description': 'Generate CI Guide for solution',
                'provider': config.get('ci_provider', 'anthropic'),
                'model': config.get('ci_model', 'claude-3-5-sonnet'),
                'estimated_time': 15
            })

        # Step 4: Create new repository
        steps.append({
            'id': 'create_repo',
            'type': 'github',
            'description': 'Create solution repository',
            'repo_name': self._generate_repo_name(config['github_url']),
            'estimated_time': 5
        })

        # Step 5: Add to menu (if requested)
        if config.get('add_to_menu'):
            steps.append({
                'id': 'add_menu',
                'type': 'menu',
                'description': 'Add to deployment menu',
                'category': config.get('menu_category', 'solutions'),
                'estimated_time': 2
            })

        plan = {
            'version': self.plan_version,
            'created_at': datetime.now().isoformat(),
            'summary': self._generate_summary(config, analysis),
            'steps': steps,
            'total_time': sum(s['estimated_time'] for s in steps),
            'output_repo': self._generate_repo_name(config['github_url']) + '-solution',
            'warnings': self._check_warnings(analysis)
        }

        return plan

    def _generate_repo_name(self, github_url: str) -> str:
        """Generate repository name from GitHub URL."""
        # Extract repo name from URL
        parts = github_url.rstrip('/').split('/')
        if len(parts) >= 2:
            return parts[-1]
        return 'unnamed-project'

    def _generate_summary(self, config: Dict, analysis: Dict) -> str:
        """Generate plan summary."""
        actions = []

        if config.get('apply_standards'):
            actions.append(f"Apply {len(config['standards'])} standards")

        if config.get('include_ci'):
            actions.append('Add CI Guide')

        if config.get('add_to_menu'):
            actions.append('Add to deployment menu')

        return f"Package {analysis['project_type']} project: " + ', '.join(actions)

    def _check_warnings(self, analysis: Dict) -> List[str]:
        """Check for potential issues."""
        warnings = []

        if analysis['project_type'] == 'unknown':
            warnings.append('Could not detect project type')

        if len(analysis['large_files']) > 10:
            warnings.append(f"Found {len(analysis['large_files'])} large files")

        if analysis.get('potential_secrets'):
            warnings.append('Potential secrets detected - review before publishing')

        return warnings


class SolutionPackager:
    """Main packager that orchestrates the solution packaging process."""

    def __init__(self):
        self.analyzer = RepositoryAnalyzer()
        self.standards = StandardsEngine()
        self.planner = PlanCreator()
        self.work_dir = Path('/tmp/ergon-packager')
        self.work_dir.mkdir(exist_ok=True)

    async def analyze_repository(self, github_url: str, session_id: str) -> Dict[str, Any]:
        """Analyze repository and return analysis."""
        # Clone to temp directory
        repo_name = github_url.rstrip('/').split('/')[-1]
        repo_path = self.work_dir / session_id / repo_name
        repo_path.parent.mkdir(exist_ok=True)

        # Clone repository
        if not repo_path.exists():
            logger.info(f"Cloning {github_url}")
            subprocess.run(['git', 'clone', github_url, str(repo_path)], check=True)
        else:
            logger.info(f"Repository already exists, pulling latest")
            subprocess.run(['git', 'pull'], cwd=repo_path, check=True)

        # Analyze
        analysis = await self.analyzer.analyze(repo_path)

        # Get recommendations
        recommendations = await self.standards.recommend_standards(analysis)

        return {
            'analysis': analysis,
            'recommendations': recommendations,
            'repo_path': str(repo_path)
        }

    async def create_plan(self, config: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Create execution plan."""
        # Get stored analysis
        repo_name = config['github_url'].rstrip('/').split('/')[-1]
        repo_path = self.work_dir / session_id / repo_name

        # Re-analyze for latest state
        analysis = await self.analyzer.analyze(repo_path)

        # Create plan
        plan = await self.planner.create_plan(config, analysis)

        return plan

    async def execute_plan(self, plan: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """Execute the plan deterministically."""
        results = {'steps': [], 'success': True}

        for step in plan['steps']:
            try:
                logger.info(f"Executing: {step['description']}")

                if step['type'] == 'git':
                    # Already cloned during analysis
                    result = {'status': 'complete', 'message': 'Repository ready'}

                elif step['type'] == 'standard':
                    repo_path = self._get_repo_path(plan, session_id)
                    result = await self.standards.apply_standards(
                        repo_path,
                        [step['standard']]
                    )

                elif step['type'] == 'ci_guide':
                    result = await self._generate_ci_guide(
                        self._get_repo_path(plan, session_id),
                        step['provider'],
                        step['model']
                    )

                elif step['type'] == 'github':
                    result = await self._create_github_repo(plan['output_repo'])

                elif step['type'] == 'menu':
                    result = await self._add_to_menu(plan)

                else:
                    result = {'status': 'skipped', 'message': f"Unknown step type: {step['type']}"}

                results['steps'].append({
                    'step': step['id'],
                    'result': result
                })

            except Exception as e:
                logger.error(f"Error in step {step['id']}: {e}")
                results['steps'].append({
                    'step': step['id'],
                    'error': str(e)
                })
                results['success'] = False
                break

        return results

    def _get_repo_path(self, plan: Dict, session_id: str) -> Path:
        """Get repository path from plan."""
        repo_name = plan['output_repo'].replace('-solution', '')
        return self.work_dir / session_id / repo_name

    async def _generate_ci_guide(self, repo_path: Path, provider: str, model: str) -> Dict:
        """Generate CI guide for the solution."""
        guide_dir = repo_path / '.ci_guide'
        guide_dir.mkdir(exist_ok=True)

        # Generate guide metadata
        metadata = {
            'solution_id': repo_path.name,
            'analyzed_at': datetime.now().isoformat(),
            'provider': provider,
            'model': model,
            'codebase_summary': {
                'files': len(list(repo_path.rglob('*'))),
                'language': 'python',  # Would be detected
                'entry_points': ['main.py', 'app.py']  # Would be detected
            }
        }

        with open(guide_dir / 'metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)

        return {'status': 'complete', 'guide_path': str(guide_dir)}

    async def _create_github_repo(self, repo_name: str) -> Dict:
        """Create new GitHub repository."""
        # In production, would use GitHub API
        return {'status': 'complete', 'repo_url': f'github.com/user/{repo_name}'}

    async def _add_to_menu(self, plan: Dict) -> Dict:
        """Add solution to deployment menu."""
        # In production, would update Till's menu
        return {'status': 'complete', 'menu_entry': plan['output_repo']}


# Singleton instance
_packager = None

def get_packager() -> SolutionPackager:
    """Get or create packager instance."""
    global _packager
    if _packager is None:
        _packager = SolutionPackager()
    return _packager