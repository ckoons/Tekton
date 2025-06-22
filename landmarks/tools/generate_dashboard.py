#!/usr/bin/env python3
"""
Generate an HTML dashboard visualizing landmarks across the Tekton system
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from landmarks import LandmarkRegistry


def generate_dashboard():
    """Generate HTML dashboard showing landmark visualization"""
    
    # Get all landmarks
    all_landmarks = LandmarkRegistry.list()
    stats = LandmarkRegistry.stats()
    
    # Group landmarks by component and type
    by_component = defaultdict(list)
    by_type = defaultdict(list)
    
    for lm in all_landmarks:
        by_component[lm.component].append(lm)
        by_type[lm.type].append(lm)
    
    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tekton Landmarks Dashboard</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .stat-card h3 {{
            margin: 0 0 10px 0;
            color: #7f8c8d;
            font-size: 14px;
            text-transform: uppercase;
        }}
        .stat-card .value {{
            font-size: 36px;
            font-weight: bold;
            color: #3498db;
        }}
        .component-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .component-card {{
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .component-header {{
            background: #34495e;
            color: white;
            padding: 15px;
            font-weight: bold;
        }}
        .landmark-list {{
            padding: 15px;
            max-height: 300px;
            overflow-y: auto;
        }}
        .landmark-item {{
            padding: 8px;
            margin: 5px 0;
            background: #ecf0f1;
            border-radius: 4px;
            font-size: 13px;
        }}
        .landmark-type {{
            display: inline-block;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 11px;
            font-weight: bold;
            margin-right: 5px;
        }}
        .architecture_decision {{ background: #e74c3c; color: white; }}
        .performance_boundary {{ background: #f39c12; color: white; }}
        .api_contract {{ background: #3498db; color: white; }}
        .danger_zone {{ background: #e67e22; color: white; }}
        .integration_point {{ background: #9b59b6; color: white; }}
        .state_checkpoint {{ background: #1abc9c; color: white; }}
        .chart {{
            margin: 30px 0;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .bar {{
            display: flex;
            align-items: center;
            margin: 10px 0;
        }}
        .bar-label {{
            width: 150px;
            font-size: 14px;
        }}
        .bar-value {{
            height: 25px;
            background: #3498db;
            color: white;
            padding: 0 10px;
            line-height: 25px;
            font-size: 12px;
            border-radius: 3px;
            margin-left: 10px;
        }}
        .timestamp {{
            text-align: center;
            color: #7f8c8d;
            margin: 20px 0;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 Tekton Landmarks Dashboard</h1>
        
        <div class="timestamp">
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>Total Landmarks</h3>
                <div class="value">{stats['total_landmarks']}</div>
            </div>
            <div class="stat-card">
                <h3>Components</h3>
                <div class="value">{len(stats['by_component'])}</div>
            </div>
            <div class="stat-card">
                <h3>Files</h3>
                <div class="value">{stats['total_files']}</div>
            </div>
            <div class="stat-card">
                <h3>Coverage</h3>
                <div class="value">{len(stats['by_component'])/15*100:.0f}%</div>
            </div>
        </div>
        
        <div class="chart">
            <h2>Landmarks by Type</h2>
            {"".join(f'''
            <div class="bar">
                <div class="bar-label">{lm_type.replace('_', ' ').title()}</div>
                <div class="bar-value" style="width: {count*50}px">{count}</div>
            </div>
            ''' for lm_type, count in sorted(stats['by_type'].items()))}
        </div>
        
        <h2>Components</h2>
        <div class="component-grid">
            {"".join(f'''
            <div class="component-card">
                <div class="component-header">{component} ({len(landmarks)} landmarks)</div>
                <div class="landmark-list">
                    {"".join(f'''
                    <div class="landmark-item">
                        <span class="landmark-type {lm.type}">{lm.type.replace('_', ' ')}</span>
                        <strong>{lm.title}</strong><br>
                        <small>{Path(lm.file_path).name}:{lm.line_number}</small>
                    </div>
                    ''' for lm in sorted(landmarks, key=lambda x: x.timestamp, reverse=True)[:10])}
                </div>
            </div>
            ''' for component, landmarks in sorted(by_component.items()))}
        </div>
        
        <div class="chart">
            <h2>Recent Landmarks</h2>
            <div style="background: #ecf0f1; padding: 15px; border-radius: 4px;">
                {"".join(f'''
                <div style="margin: 10px 0;">
                    <span class="landmark-type {lm.type}">{lm.type.replace('_', ' ')}</span>
                    <strong>{lm.title}</strong> - 
                    <span style="color: #7f8c8d">{lm.component}/{Path(lm.file_path).name}:{lm.line_number}</span>
                    <small style="float: right; color: #95a5a6">{lm.timestamp.strftime('%Y-%m-%d %H:%M')}</small>
                </div>
                ''' for lm in sorted(all_landmarks, key=lambda x: x.timestamp, reverse=True)[:20])}
            </div>
        </div>
    </div>
</body>
</html>"""
    
    # Save dashboard
    dashboard_path = Path(__file__).parent.parent / "dashboard.html"
    with open(dashboard_path, 'w') as f:
        f.write(html)
    
    print(f"✅ Dashboard generated: {dashboard_path}")
    print(f"   Total landmarks: {stats['total_landmarks']}")
    print(f"   Components covered: {len(stats['by_component'])}")
    
    return dashboard_path


if __name__ == "__main__":
    generate_dashboard()