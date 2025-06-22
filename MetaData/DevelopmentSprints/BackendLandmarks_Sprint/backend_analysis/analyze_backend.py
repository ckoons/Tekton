#!/usr/bin/env python3
"""
Tekton Backend AST Analyzer
Pragmatic approach to index codebase and identify landmark locations
"""

import ast
import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class TektonAnalyzer(ast.NodeVisitor):
    """AST analyzer focused on landmark identification"""
    
    def __init__(self):
        self.current_file = None
        self.current_class = None
        self.results = {
            'functions': [],
            'classes': [],
            'api_endpoints': [],
            'mcp_tools': [],
            'websocket_handlers': [],
            'decorators': [],
            'imports': [],
            'patterns': [],
            'side_effects': [],
            'landmarks': []  # Primary landmark candidates
        }
        
    def analyze_file(self, filepath: Path) -> Dict[str, Any]:
        """Analyze a single Python file"""
        self.current_file = str(filepath)
        self.results = {
            'functions': [],
            'classes': [],
            'api_endpoints': [],
            'mcp_tools': [],
            'websocket_handlers': [],
            'decorators': [],
            'imports': [],
            'patterns': [],
            'side_effects': [],
            'landmarks': []
        }
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse AST
            tree = ast.parse(content, filename=str(filepath))
            self.visit(tree)
            
            # Quick pattern detection
            self._detect_patterns(content)
            
            return {
                'file': self.current_file,
                'analysis': self.results,
                'line_count': len(content.splitlines()),
                'has_tests': 'test' in str(filepath).lower()
            }
            
        except Exception as e:
            return {
                'file': self.current_file,
                'error': str(e),
                'analysis': self.results
            }
    
    def visit_ClassDef(self, node: ast.ClassDef):
        """Analyze class definitions"""
        self.current_class = node.name
        
        class_info = {
            'name': node.name,
            'line': node.lineno,
            'methods': [],
            'decorators': [self._get_decorator_name(d) for d in node.decorator_list],
            'docstring': ast.get_docstring(node),
            'is_singleton': False,  # Will detect pattern
            'landmark_priority': 'high'  # All classes get landmarks
        }
        
        # Check for singleton pattern
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                if item.name in ['get_instance', '__new__', '_instance']:
                    class_info['is_singleton'] = True
                    self.results['patterns'].append({
                        'type': 'singleton',
                        'location': f"{node.name}.{item.name}",
                        'line': item.lineno
                    })
                    
                class_info['methods'].append(item.name)
        
        self.results['classes'].append(class_info)
        
        # Add landmark
        self.results['landmarks'].append({
            'type': 'class_definition',
            'name': node.name,
            'file': self.current_file,
            'line': node.lineno,
            'priority': 'high',
            'reason': 'Class definition'
        })
        
        self.generic_visit(node)
        self.current_class = None
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Analyze function definitions"""
        self._visit_function(node, is_async=False)
        
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Analyze async function definitions"""
        self._visit_function(node, is_async=True)
        
    def _visit_function(self, node, is_async: bool):
        """Common function analysis"""
        decorators = [self._get_decorator_name(d) for d in node.decorator_list]
        
        func_info = {
            'name': node.name,
            'line': node.lineno,
            'async': is_async,
            'decorators': decorators,
            'docstring': ast.get_docstring(node),
            'args': [arg.arg for arg in node.args.args],
            'class': self.current_class,
            'complexity': self._estimate_complexity(node),
            'has_side_effects': self._check_side_effects(node)
        }
        
        self.results['functions'].append(func_info)
        
        # Check for specific patterns
        self._check_api_endpoint(node, decorators)
        self._check_mcp_tool(node, decorators)
        self._check_websocket_handler(node, decorators)
        
        # Determine landmark priority
        priority = self._determine_landmark_priority(func_info)
        if priority:
            self.results['landmarks'].append({
                'type': 'function',
                'name': f"{self.current_class}.{node.name}" if self.current_class else node.name,
                'file': self.current_file,
                'line': node.lineno,
                'priority': priority,
                'reason': self._get_landmark_reason(func_info)
            })
        
        self.generic_visit(node)
    
    def _estimate_complexity(self, node) -> str:
        """Quick complexity estimate"""
        # Count branches, loops, exception handlers
        complexity = 0
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.Try)):
                complexity += 1
                
        if complexity <= 2:
            return 'low'
        elif complexity <= 5:
            return 'medium'
        else:
            return 'high'
    
    def _check_side_effects(self, node) -> bool:
        """Check if function has obvious side effects"""
        for child in ast.walk(node):
            # File I/O
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    if child.func.id in ['open', 'write', 'save']:
                        return True
                elif isinstance(child.func, ast.Attribute):
                    if child.func.attr in ['write', 'save', 'commit', 'execute', 'send']:
                        return True
            # Database operations
            if isinstance(child, ast.Attribute):
                if child.attr in ['commit', 'rollback', 'execute', 'insert', 'update', 'delete']:
                    return True
                    
        return False
    
    def _check_api_endpoint(self, node, decorators):
        """Check if function is an API endpoint"""
        api_decorators = ['@app.', '@router.', 'get', 'post', 'put', 'delete', 'patch']
        for dec in decorators:
            if any(api_dec in dec.lower() for api_dec in api_decorators):
                self.results['api_endpoints'].append({
                    'name': node.name,
                    'line': node.lineno,
                    'method': dec,
                    'async': isinstance(node, ast.AsyncFunctionDef)
                })
                
    def _check_mcp_tool(self, node, decorators):
        """Check if function is an MCP tool"""
        mcp_indicators = ['@mcp', 'mcp_tool', '@tool', 'fastmcp']
        for dec in decorators:
            if any(mcp in dec.lower() for mcp in mcp_indicators):
                self.results['mcp_tools'].append({
                    'name': node.name,
                    'line': node.lineno,
                    'decorator': dec
                })
                
    def _check_websocket_handler(self, node, decorators):
        """Check if function handles WebSocket connections"""
        # Check decorators and function name
        ws_indicators = ['websocket', 'ws', 'on_message', 'on_connect']
        func_name_lower = node.name.lower()
        
        if any(ws in func_name_lower for ws in ws_indicators):
            self.results['websocket_handlers'].append({
                'name': node.name,
                'line': node.lineno,
                'async': isinstance(node, ast.AsyncFunctionDef)
            })
    
    def _determine_landmark_priority(self, func_info: dict) -> Optional[str]:
        """Determine if function needs a landmark and its priority"""
        # All public functions get landmarks
        if not func_info['name'].startswith('_'):
            return 'high'
            
        # Private functions with complexity or side effects
        if func_info['complexity'] == 'high' or func_info['has_side_effects']:
            return 'medium'
            
        # Large private functions (would need line count)
        # Skip for now in pragmatic approach
        
        return None
    
    def _get_landmark_reason(self, func_info: dict) -> str:
        """Get reason for landmark placement"""
        reasons = []
        
        if func_info['async']:
            reasons.append('Async function')
        if func_info['has_side_effects']:
            reasons.append('Has side effects')
        if func_info['complexity'] == 'high':
            reasons.append('High complexity')
        if 'route' in str(func_info['decorators']):
            reasons.append('API endpoint')
        if 'mcp' in str(func_info['decorators']):
            reasons.append('MCP tool')
            
        return ', '.join(reasons) if reasons else 'Public function'
    
    def visit_Import(self, node: ast.Import):
        """Track imports"""
        for alias in node.names:
            self.results['imports'].append({
                'module': alias.name,
                'alias': alias.asname,
                'line': node.lineno
            })
            
    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Track from imports"""
        if node.module:
            for alias in node.names:
                self.results['imports'].append({
                    'module': f"{node.module}.{alias.name}",
                    'from': node.module,
                    'name': alias.name,
                    'alias': alias.asname,
                    'line': node.lineno
                })
    
    def _get_decorator_name(self, decorator) -> str:
        """Extract decorator name"""
        if isinstance(decorator, ast.Name):
            return f"@{decorator.id}"
        elif isinstance(decorator, ast.Attribute):
            return f"@{decorator.attr}"
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return f"@{decorator.func.id}"
            elif isinstance(decorator.func, ast.Attribute):
                return f"@{decorator.func.attr}"
        return "@unknown"
    
    def _detect_patterns(self, content: str):
        """Quick pattern detection in source"""
        patterns = []
        
        # Singleton pattern
        if 'get_instance' in content or '_instance' in content:
            patterns.append('singleton')
            
        # FastAPI/REST
        if 'FastAPI' in content or '@app.' in content or '@router.' in content:
            patterns.append('fastapi')
            
        # WebSocket
        if 'websocket' in content.lower() or 'WebSocket' in content:
            patterns.append('websocket')
            
        # MCP
        if 'mcp' in content.lower() or 'fastmcp' in content:
            patterns.append('mcp')
            
        # Async patterns
        if 'async def' in content or 'await' in content:
            patterns.append('async')
            
        # Error handling
        if 'try:' in content and 'except' in content:
            patterns.append('error_handling')
            
        for pattern in patterns:
            if pattern not in [p['type'] for p in self.results['patterns']]:
                self.results['patterns'].append({
                    'type': pattern,
                    'location': 'file',
                    'line': 0
                })


def analyze_component(component_path: Path) -> Dict[str, Any]:
    """Analyze all Python files in a component"""
    analyzer = TektonAnalyzer()
    component_results = {
        'component': component_path.name,
        'files': [],
        'summary': {
            'total_files': 0,
            'total_functions': 0,
            'total_classes': 0,
            'total_landmarks': 0,
            'patterns': set(),
            'api_endpoints': 0,
            'mcp_tools': 0
        }
    }
    
    # Find all Python files
    for py_file in component_path.rglob('*.py'):
        # Skip test files for now
        if 'test' in str(py_file).lower() or '__pycache__' in str(py_file):
            continue
            
        result = analyzer.analyze_file(py_file)
        component_results['files'].append(result)
        
        # Update summary
        if 'error' not in result:
            analysis = result['analysis']
            component_results['summary']['total_files'] += 1
            component_results['summary']['total_functions'] += len(analysis['functions'])
            component_results['summary']['total_classes'] += len(analysis['classes'])
            component_results['summary']['total_landmarks'] += len(analysis['landmarks'])
            component_results['summary']['api_endpoints'] += len(analysis['api_endpoints'])
            component_results['summary']['mcp_tools'] += len(analysis['mcp_tools'])
            
            for pattern in analysis['patterns']:
                component_results['summary']['patterns'].add(pattern['type'])
    
    # Convert set to list for JSON serialization
    component_results['summary']['patterns'] = list(component_results['summary']['patterns'])
    
    return component_results


def save_results(results: Dict[str, Any], output_dir: Path):
    """Save analysis results"""
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save JSON
    json_path = output_dir / f"{results['component']}_analysis.json"
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    # Generate summary markdown
    md_path = output_dir / f"{results['component']}_summary.md"
    with open(md_path, 'w') as f:
        f.write(f"# {results['component']} Analysis Summary\n\n")
        f.write(f"**Generated**: {datetime.now().isoformat()}\n\n")
        
        summary = results['summary']
        f.write("## Statistics\n")
        f.write(f"- Files analyzed: {summary['total_files']}\n")
        f.write(f"- Functions: {summary['total_functions']}\n")
        f.write(f"- Classes: {summary['total_classes']}\n")
        f.write(f"- Landmarks identified: {summary['total_landmarks']}\n")
        f.write(f"- API endpoints: {summary['api_endpoints']}\n")
        f.write(f"- MCP tools: {summary['mcp_tools']}\n\n")
        
        f.write("## Patterns Found\n")
        for pattern in summary['patterns']:
            f.write(f"- {pattern}\n")
        
        f.write("\n## High Priority Landmarks\n")
        for file_result in results['files']:
            if 'error' not in file_result:
                high_priority = [l for l in file_result['analysis']['landmarks'] 
                               if l['priority'] == 'high']
                if high_priority:
                    f.write(f"\n### {file_result['file']}\n")
                    for landmark in high_priority[:5]:  # Top 5 per file
                        f.write(f"- {landmark['name']} (line {landmark['line']}): {landmark['reason']}\n")


if __name__ == '__main__':
    # Test on a small component first
    print("Tekton Backend Analyzer - Starting analysis...")
    
    # Define Tekton root
    tekton_root = Path('/Users/cskoons/projects/github/Tekton')
    
    # Start with shared/utils as a test
    test_component = tekton_root / 'shared' / 'utils'
    
    if test_component.exists():
        print(f"\nAnalyzing {test_component}...")
        results = analyze_component(test_component)
        
        # Save results
        output_dir = Path('/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/BackendLandmarks_Sprint/backend_analysis/components')
        save_results(results, output_dir)
        
        print(f"\nAnalysis complete!")
        print(f"Results saved to {output_dir}")
        print(f"\nSummary:")
        print(f"  Files: {results['summary']['total_files']}")
        print(f"  Functions: {results['summary']['total_functions']}")
        print(f"  Classes: {results['summary']['total_classes']}")
        print(f"  Landmarks: {results['summary']['total_landmarks']}")