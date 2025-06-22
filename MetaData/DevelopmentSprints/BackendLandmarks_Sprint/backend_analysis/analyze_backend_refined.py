#!/usr/bin/env python3
"""
Refined Tekton Backend AST Analyzer
Better filtering to focus on actual source code
"""

import ast
import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from analyze_backend import TektonAnalyzer


def should_skip_file(filepath: Path) -> bool:
    """Determine if a file should be skipped"""
    path_str = str(filepath).lower()
    
    # Skip patterns
    skip_patterns = [
        '__pycache__',
        '.pyc',
        'node_modules',
        'venv',
        '.egg-info',
        'build/',
        'dist/',
        '.git/',
        'test_',  # Test files
        '_test',
        'migrations/',
        'tests/',  # Test directories
        'examples/',  # Example files
        'scripts/',  # Utility scripts
        '.venv',
        'site-packages',
    ]
    
    # Check each pattern
    for pattern in skip_patterns:
        if pattern in path_str:
            return True
            
    # Skip if file is too large (likely generated)
    try:
        if filepath.stat().st_size > 100000:  # 100KB
            return True
    except:
        pass
        
    return False


def analyze_component_refined(component_path: Path) -> Dict[str, Any]:
    """Analyze component with better filtering"""
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
            'mcp_tools': 0,
            'websocket_handlers': 0,
            'skipped_files': 0
        }
    }
    
    # Find Python files with better filtering
    for py_file in component_path.rglob('*.py'):
        if should_skip_file(py_file):
            component_results['summary']['skipped_files'] += 1
            continue
            
        # Also skip __main__.py files for cleaner analysis
        if py_file.name == '__main__.py':
            continue
            
        result = analyzer.analyze_file(py_file)
        
        # Only include if it has meaningful content
        if 'error' not in result and result['analysis']['functions']:
            component_results['files'].append(result)
            
            # Update summary
            analysis = result['analysis']
            component_results['summary']['total_files'] += 1
            component_results['summary']['total_functions'] += len(analysis['functions'])
            component_results['summary']['total_classes'] += len(analysis['classes'])
            component_results['summary']['total_landmarks'] += len(analysis['landmarks'])
            component_results['summary']['api_endpoints'] += len(analysis['api_endpoints'])
            component_results['summary']['mcp_tools'] += len(analysis['mcp_tools'])
            component_results['summary']['websocket_handlers'] += len(analysis['websocket_handlers'])
            
            for pattern in analysis['patterns']:
                component_results['summary']['patterns'].add(pattern['type'])
    
    # Convert set to list
    component_results['summary']['patterns'] = list(component_results['summary']['patterns'])
    
    return component_results


def create_landmark_map(all_results: List[Dict]) -> Dict[str, Any]:
    """Create a focused landmark location map"""
    landmark_map = {
        'architectural_decisions': [],
        'performance_boundaries': [],
        'api_contracts': [],
        'danger_zones': [],
        'integration_points': [],
        'state_checkpoints': []
    }
    
    for component_result in all_results:
        for file_result in component_result.get('files', []):
            if 'error' in file_result:
                continue
                
            analysis = file_result['analysis']
            
            # API contracts
            for endpoint in analysis.get('api_endpoints', []):
                landmark_map['api_contracts'].append({
                    'component': component_result['component'],
                    'file': file_result['file'],
                    'line': endpoint['line'],
                    'name': endpoint['name'],
                    'method': endpoint['method']
                })
            
            # Integration points (MCP tools, WebSocket handlers)
            for tool in analysis.get('mcp_tools', []):
                landmark_map['integration_points'].append({
                    'component': component_result['component'],
                    'file': file_result['file'],
                    'line': tool['line'],
                    'name': tool['name'],
                    'type': 'mcp_tool'
                })
                
            for handler in analysis.get('websocket_handlers', []):
                landmark_map['integration_points'].append({
                    'component': component_result['component'],
                    'file': file_result['file'],
                    'line': handler['line'],
                    'name': handler['name'],
                    'type': 'websocket_handler'
                })
            
            # High complexity functions as danger zones
            for func in analysis.get('functions', []):
                if func['complexity'] == 'high':
                    landmark_map['danger_zones'].append({
                        'component': component_result['component'],
                        'file': file_result['file'],
                        'line': func['line'],
                        'name': func['name'],
                        'reason': 'high_complexity'
                    })
                    
            # Singleton classes as state checkpoints
            for cls in analysis.get('classes', []):
                if cls.get('is_singleton'):
                    landmark_map['state_checkpoints'].append({
                        'component': component_result['component'],
                        'file': file_result['file'],
                        'line': cls['line'],
                        'name': cls['name'],
                        'type': 'singleton'
                    })
    
    return landmark_map


def main():
    tekton_root = Path('/Users/cskoons/projects/github/Tekton')
    output_base = Path('/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/BackendLandmarks_Sprint/backend_analysis')
    
    # Core components only for refined analysis
    core_components = [
        'shared',
        'Hermes',
        'Apollo', 
        'Engram',
        'Athena',
        'Prometheus',
        'Budget',
        'Harmonia',
        'Rhetor',
        'Sophia',
        'Telos'
    ]
    
    all_results = []
    overall_summary = {
        'analysis_date': datetime.now().isoformat(),
        'components_analyzed': [],
        'total_files': 0,
        'total_functions': 0,
        'total_classes': 0,
        'total_landmarks': 0,
        'total_skipped': 0,
        'patterns_found': set()
    }
    
    print("=== Refined Backend Analysis ===\n")
    
    for component_name in core_components:
        component_path = tekton_root / component_name
        
        if not component_path.exists():
            continue
            
        print(f"📊 Analyzing {component_name}...")
        
        try:
            results = analyze_component_refined(component_path)
            all_results.append(results)
            
            # Save refined results
            output_dir = output_base / 'refined'
            output_dir.mkdir(exist_ok=True)
            
            json_path = output_dir / f"{component_name}_refined.json"
            with open(json_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            # Update summary
            summary = results['summary']
            overall_summary['components_analyzed'].append(component_name)
            overall_summary['total_files'] += summary['total_files']
            overall_summary['total_functions'] += summary['total_functions']
            overall_summary['total_classes'] += summary['total_classes']
            overall_summary['total_landmarks'] += summary['total_landmarks']
            overall_summary['total_skipped'] += summary['skipped_files']
            overall_summary['patterns_found'].update(summary['patterns'])
            
            print(f"   ✓ Source files: {summary['total_files']}")
            print(f"   ✓ Functions: {summary['total_functions']}")
            print(f"   ✓ Landmarks: {summary['total_landmarks']}")
            print(f"   ✓ Skipped: {summary['skipped_files']}\n")
            
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
    
    # Create landmark map
    print("=== Creating Landmark Map ===")
    landmark_map = create_landmark_map(all_results)
    
    landmark_path = output_base / 'landmark_locations.json'
    with open(landmark_path, 'w') as f:
        json.dump(landmark_map, f, indent=2)
    
    # Count landmarks by type
    print("\nLandmark Types:")
    for landmark_type, landmarks in landmark_map.items():
        print(f"  {landmark_type}: {len(landmarks)}")
    
    # Save refined summary
    overall_summary['patterns_found'] = list(overall_summary['patterns_found'])
    
    refined_summary_path = output_base / 'refined_summary.json'
    with open(refined_summary_path, 'w') as f:
        json.dump(overall_summary, f, indent=2)
    
    print(f"\n✅ Refined analysis complete!")
    print(f"   Source files analyzed: {overall_summary['total_files']}")
    print(f"   Total landmarks: {overall_summary['total_landmarks']}")
    print(f"   Files skipped: {overall_summary['total_skipped']}")


if __name__ == '__main__':
    main()