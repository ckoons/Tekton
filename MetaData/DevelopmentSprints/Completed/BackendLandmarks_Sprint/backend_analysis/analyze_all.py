#!/usr/bin/env python3
"""
Analyze all Tekton components for landmark placement
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from analyze_backend import analyze_component, save_results


def main():
    tekton_root = Path('/Users/cskoons/projects/github/Tekton')
    output_base = Path('/Users/cskoons/projects/github/Tekton/MetaData/DevelopmentSprints/BackendLandmarks_Sprint/backend_analysis')
    
    # Priority components to analyze
    priority_components = [
        'shared',      # Common patterns and utilities
        'Hermes',      # Central nervous system
        'Apollo',      # Orchestration
        'Engram',      # Memory/state
        'Athena',      # Knowledge graph
        'Prometheus',  # LLM integration
    ]
    
    # Additional components
    other_components = [
        'Budget',
        'Ergon', 
        'Harmonia',
        'Metis',
        'Rhetor',
        'Sophia',
        'Synthesis',
        'Telos',
        'Terma',  # Light instrumentation only
    ]
    
    # Track overall progress
    overall_summary = {
        'analysis_date': datetime.now().isoformat(),
        'components_analyzed': [],
        'total_files': 0,
        'total_functions': 0,
        'total_classes': 0,
        'total_landmarks': 0,
        'patterns_found': set()
    }
    
    # Analyze priority components first
    print("=== Analyzing Priority Components ===\n")
    for component_name in priority_components:
        component_path = tekton_root / component_name
        
        if not component_path.exists():
            print(f"⚠️  {component_name} not found, skipping...")
            continue
            
        print(f"📊 Analyzing {component_name}...")
        
        try:
            results = analyze_component(component_path)
            
            # Save component results
            output_dir = output_base / 'components'
            save_results(results, output_dir)
            
            # Update overall summary
            summary = results['summary']
            overall_summary['components_analyzed'].append(component_name)
            overall_summary['total_files'] += summary['total_files']
            overall_summary['total_functions'] += summary['total_functions']
            overall_summary['total_classes'] += summary['total_classes']
            overall_summary['total_landmarks'] += summary['total_landmarks']
            overall_summary['patterns_found'].update(summary['patterns'])
            
            print(f"   ✓ Files: {summary['total_files']}")
            print(f"   ✓ Functions: {summary['total_functions']}")
            print(f"   ✓ Classes: {summary['total_classes']}")
            print(f"   ✓ Landmarks: {summary['total_landmarks']}")
            print(f"   ✓ Patterns: {', '.join(summary['patterns'])}\n")
            
        except Exception as e:
            print(f"   ❌ Error analyzing {component_name}: {e}\n")
    
    # Quick pass on other components
    print("\n=== Analyzing Other Components ===\n")
    for component_name in other_components:
        component_path = tekton_root / component_name
        
        if not component_path.exists():
            continue
            
        print(f"📊 Analyzing {component_name}...")
        
        try:
            results = analyze_component(component_path)
            output_dir = output_base / 'components'
            save_results(results, output_dir)
            
            summary = results['summary']
            overall_summary['components_analyzed'].append(component_name)
            overall_summary['total_files'] += summary['total_files']
            overall_summary['total_functions'] += summary['total_functions']
            overall_summary['total_classes'] += summary['total_classes']
            overall_summary['total_landmarks'] += summary['total_landmarks']
            overall_summary['patterns_found'].update(summary['patterns'])
            
            print(f"   ✓ Landmarks: {summary['total_landmarks']}\n")
            
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
    
    # Convert patterns set to list
    overall_summary['patterns_found'] = list(overall_summary['patterns_found'])
    
    # Save overall summary
    print("\n=== Saving Overall Summary ===")
    summary_path = output_base / 'overall_summary.json'
    with open(summary_path, 'w') as f:
        json.dump(overall_summary, f, indent=2)
    
    # Create executive summary
    exec_summary_path = output_base / 'executive_summary.md'
    with open(exec_summary_path, 'w') as f:
        f.write("# Tekton Backend Analysis - Executive Summary\n\n")
        f.write(f"**Analysis Date**: {overall_summary['analysis_date']}\n\n")
        f.write("## Overall Statistics\n")
        f.write(f"- Components analyzed: {len(overall_summary['components_analyzed'])}\n")
        f.write(f"- Total files: {overall_summary['total_files']}\n")
        f.write(f"- Total functions: {overall_summary['total_functions']}\n")
        f.write(f"- Total classes: {overall_summary['total_classes']}\n")
        f.write(f"- Total landmarks identified: {overall_summary['total_landmarks']}\n\n")
        
        f.write("## Components Analyzed\n")
        for comp in overall_summary['components_analyzed']:
            f.write(f"- {comp}\n")
            
        f.write("\n## Patterns Found Across Codebase\n")
        for pattern in overall_summary['patterns_found']:
            f.write(f"- {pattern}\n")
    
    print(f"\n✅ Analysis complete!")
    print(f"   Total landmarks identified: {overall_summary['total_landmarks']}")
    print(f"   Results saved to: {output_base}")
    
    # Create progress dashboard
    create_progress_dashboard(overall_summary, output_base)


def create_progress_dashboard(summary, output_base):
    """Create a simple HTML progress dashboard"""
    dashboard_path = output_base / 'progress_dashboard.html'
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Tekton Backend Analysis Progress</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .metric {{ display: inline-block; margin: 20px; padding: 20px; background: #f0f0f0; border-radius: 8px; }}
        .metric h3 {{ margin: 0 0 10px 0; color: #333; }}
        .metric .value {{ font-size: 2em; font-weight: bold; color: #0066cc; }}
        .component {{ margin: 10px 0; padding: 10px; background: #fff; border: 1px solid #ddd; }}
        .pattern {{ display: inline-block; margin: 5px; padding: 5px 10px; background: #e0e0e0; border-radius: 4px; }}
    </style>
</head>
<body>
    <h1>Tekton Backend Analysis Progress</h1>
    <p>Generated: {summary['analysis_date']}</p>
    
    <div class="metrics">
        <div class="metric">
            <h3>Components</h3>
            <div class="value">{len(summary['components_analyzed'])}</div>
        </div>
        <div class="metric">
            <h3>Files</h3>
            <div class="value">{summary['total_files']}</div>
        </div>
        <div class="metric">
            <h3>Functions</h3>
            <div class="value">{summary['total_functions']}</div>
        </div>
        <div class="metric">
            <h3>Landmarks</h3>
            <div class="value">{summary['total_landmarks']}</div>
        </div>
    </div>
    
    <h2>Components Analyzed</h2>
    {''.join(f'<div class="component">✓ {comp}</div>' for comp in summary['components_analyzed'])}
    
    <h2>Patterns Found</h2>
    {''.join(f'<span class="pattern">{pattern}</span>' for pattern in summary['patterns_found'])}
</body>
</html>"""
    
    with open(dashboard_path, 'w') as f:
        f.write(html)
    
    print(f"\n📊 Progress dashboard created: {dashboard_path}")


if __name__ == '__main__':
    main()