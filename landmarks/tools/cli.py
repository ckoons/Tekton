#!/usr/bin/env python3
"""
Tekton Landmark CLI - Manage landmarks from the command line
"""

import click
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from landmarks import LandmarkRegistry, Landmark
from landmarks.memory.ci_memory import NumaMemory


@click.group()
def landmark():
    """Tekton landmark management CLI"""
    pass


@landmark.command()
@click.option('--type', '-t', required=True, 
              type=click.Choice(['architecture_decision', 'performance_boundary', 
                                'api_contract', 'danger_zone', 'integration_point', 
                                'state_checkpoint']),
              help='Type of landmark')
@click.option('--title', required=True, help='Landmark title')
@click.option('--description', '-d', help='Detailed description')
@click.option('--file', '-f', required=True, help='File path')
@click.option('--line', '-l', required=True, type=int, help='Line number')
@click.option('--author', default='cli', help='Author name')
@click.option('--metadata', '-m', multiple=True, help='Key=value metadata pairs')
def add(type, title, description, file, line, author, metadata):
    """Add a new landmark"""
    # Parse metadata
    meta_dict = {}
    for item in metadata:
        if '=' in item:
            key, value = item.split('=', 1)
            meta_dict[key] = value
    
    # Create landmark
    landmark = Landmark.create(
        type=type,
        title=title,
        description=description or "",
        file_path=file,
        line_number=line,
        author=author,
        metadata=meta_dict
    )
    
    # Register it
    LandmarkRegistry.register(landmark)
    
    click.echo(f"✅ Landmark created: {landmark.id}")
    click.echo(f"   Type: {type}")
    click.echo(f"   Title: {title}")
    click.echo(f"   Location: {file}:{line}")


@landmark.command()
@click.option('--type', '-t', help='Filter by type')
@click.option('--component', '-c', help='Filter by component')
@click.option('--limit', '-n', default=20, help='Maximum results to show')
@click.option('--format', '-f', type=click.Choice(['simple', 'detailed', 'json']), 
              default='simple', help='Output format')
def list(type, component, limit, format):
    """List landmarks with optional filters"""
    landmarks = LandmarkRegistry.list(type=type, component=component)
    
    if not landmarks:
        click.echo("No landmarks found matching criteria")
        return
    
    # Limit results
    landmarks = landmarks[:limit]
    
    if format == 'json':
        data = [lm.to_dict() for lm in landmarks]
        click.echo(json.dumps(data, indent=2))
    elif format == 'detailed':
        for lm in landmarks:
            click.echo(f"\n{'='*60}")
            click.echo(f"ID: {lm.id}")
            click.echo(f"Type: {lm.type}")
            click.echo(f"Title: {lm.title}")
            click.echo(f"Description: {lm.description}")
            click.echo(f"Location: {lm.file_path}:{lm.line_number}")
            click.echo(f"Component: {lm.component}")
            click.echo(f"Author: {lm.author}")
            click.echo(f"Created: {lm.timestamp.strftime('%Y-%m-%d %H:%M')}")
            if lm.metadata:
                click.echo("Metadata:")
                for k, v in lm.metadata.items():
                    click.echo(f"  {k}: {v}")
    else:  # simple
        click.echo(f"Found {len(landmarks)} landmarks:")
        click.echo("-" * 80)
        for lm in landmarks:
            click.echo(f"[{lm.type}] {lm.title}")
            click.echo(f"  📍 {Path(lm.file_path).name}:{lm.line_number}")
            click.echo(f"  🕐 {lm.timestamp.strftime('%Y-%m-%d %H:%M')}")
            click.echo()


@landmark.command()
@click.argument('query')
@click.option('--limit', '-n', default=10, help='Maximum results')
@click.option('--component', '-c', help='Search within component')
def search(query, limit, component):
    """Search landmarks by text"""
    results = LandmarkRegistry.search(query)
    
    # Filter by component if specified
    if component:
        results = [lm for lm in results if lm.component == component]
    
    # Limit results
    results = results[:limit]
    
    if not results:
        click.echo(f"No landmarks found matching '{query}'")
        return
    
    click.echo(f"Found {len(results)} landmarks matching '{query}':")
    click.echo("-" * 80)
    
    for lm in results:
        # Highlight matching text
        title_highlighted = lm.title
        if query.lower() in lm.title.lower():
            title_highlighted = lm.title.replace(
                query, click.style(query, fg='yellow', bold=True)
            )
        
        click.echo(f"[{lm.type}] {title_highlighted}")
        click.echo(f"  📍 {lm.component}/{Path(lm.file_path).name}:{lm.line_number}")
        
        # Show matching context
        if query.lower() in lm.description.lower():
            # Find the matching part
            desc_lower = lm.description.lower()
            idx = desc_lower.find(query.lower())
            start = max(0, idx - 40)
            end = min(len(lm.description), idx + len(query) + 40)
            context = lm.description[start:end]
            if start > 0:
                context = "..." + context
            if end < len(lm.description):
                context = context + "..."
            click.echo(f"  📝 {context}")
        
        click.echo()


@landmark.command()
def stats():
    """Show landmark statistics"""
    stats = LandmarkRegistry.stats()
    
    click.echo("🎯 Tekton Landmark Statistics")
    click.echo("=" * 50)
    
    click.echo(f"\n📊 Overview:")
    click.echo(f"  Total landmarks: {stats['total_landmarks']}")
    click.echo(f"  Files with landmarks: {stats['total_files']}")
    click.echo(f"  Components covered: {len(stats['by_component'])}")
    
    click.echo(f"\n📋 By Type:")
    for lm_type, count in sorted(stats['by_type'].items()):
        bar = "█" * (count // 2) if count > 0 else ""
        click.echo(f"  {lm_type:25} {count:4} {bar}")
    
    click.echo(f"\n🧩 By Component:")
    for comp, count in sorted(stats['by_component'].items(), 
                              key=lambda x: x[1], reverse=True)[:10]:
        bar = "█" * (count // 2) if count > 0 else ""
        click.echo(f"  {comp:25} {count:4} {bar}")
    
    # Show coverage
    all_components = ['shared', 'Hermes', 'Apollo', 'Engram', 'Athena', 
                     'Prometheus', 'Budget', 'Harmonia', 'Rhetor', 'Sophia', 
                     'Telos', 'Ergon', 'Synthesis', 'Metis', 'Terma']
    covered = len([c for c in all_components if c in stats['by_component']])
    coverage = (covered / len(all_components)) * 100
    
    click.echo(f"\n📈 Coverage: {coverage:.1f}% ({covered}/{len(all_components)} components)")


@landmark.command()
@click.argument('landmark_id')
def show(landmark_id):
    """Show detailed information about a specific landmark"""
    lm = LandmarkRegistry.get(landmark_id)
    
    if not lm:
        click.echo(f"Landmark {landmark_id} not found")
        return
    
    click.echo(f"\n🎯 Landmark Details")
    click.echo("=" * 60)
    click.echo(f"ID: {lm.id}")
    click.echo(f"Type: {lm.type}")
    click.echo(f"Title: {lm.title}")
    click.echo(f"\nDescription:")
    click.echo(f"  {lm.description}")
    click.echo(f"\nLocation:")
    click.echo(f"  File: {lm.file_path}")
    click.echo(f"  Line: {lm.line_number}")
    click.echo(f"  Component: {lm.component}")
    click.echo(f"\nMetadata:")
    click.echo(f"  Author: {lm.author}")
    click.echo(f"  Created: {lm.timestamp}")
    
    if lm.metadata:
        click.echo(f"\nAdditional Metadata:")
        for key, value in lm.metadata.items():
            if isinstance(value, list):
                click.echo(f"  {key}:")
                for item in value:
                    click.echo(f"    - {item}")
            elif isinstance(value, dict):
                click.echo(f"  {key}:")
                for k, v in value.items():
                    click.echo(f"    {k}: {v}")
            else:
                click.echo(f"  {key}: {value}")
    
    if lm.related_landmarks:
        click.echo(f"\nRelated Landmarks:")
        for related_id in lm.related_landmarks:
            related = LandmarkRegistry.get(related_id)
            if related:
                click.echo(f"  - {related.title} ({related.type})")


@landmark.group()
def ci():
    """CI memory operations"""
    pass


@ci.command()
@click.argument('key')
@click.argument('value')
@click.option('--category', '-c', default='general', help='Memory category')
def remember(key, value, category):
    """Store something in Numa's memory"""
    numa = NumaMemory()
    numa.remember(key, value, category)
    click.echo(f"✅ Stored '{key}' in Numa's {category} memory")


@ci.command()
@click.argument('key')
@click.option('--category', '-c', default='general', help='Memory category')
def recall(key, category):
    """Recall something from Numa's memory"""
    numa = NumaMemory()
    value = numa.recall(key, category)
    
    if value is None:
        click.echo(f"❌ '{key}' not found in {category} memory")
    else:
        click.echo(f"📝 {key}: {value}")


@ci.command()
@click.argument('query')
def ask(query):
    """Ask Numa about landmarks"""
    numa = NumaMemory()
    
    # Determine which CI should handle this
    target_ci = numa.route_to_ci(query)
    click.echo(f"🤖 Routing to: {target_ci}")
    
    # Search for relevant landmarks
    landmarks = numa.search_landmarks(query)
    
    if not landmarks:
        click.echo(f"\nNo landmarks found related to '{query}'")
        return
    
    click.echo(f"\nFound {len(landmarks)} relevant landmarks:")
    click.echo("-" * 60)
    
    for lm in landmarks[:5]:  # Show top 5
        click.echo(f"\n[{lm.type}] {lm.title}")
        click.echo(f"📍 {lm.component}/{Path(lm.file_path).name}:{lm.line_number}")
        
        # Show relevant metadata
        if lm.type == 'architecture_decision' and 'rationale' in lm.metadata:
            click.echo(f"💡 Rationale: {lm.metadata['rationale']}")
        elif lm.type == 'performance_boundary' and 'sla' in lm.metadata:
            click.echo(f"⚡ SLA: {lm.metadata['sla']}")
        elif lm.type == 'integration_point' and 'protocol' in lm.metadata:
            click.echo(f"🔗 Protocol: {lm.metadata['protocol']}")


def main():
    """Main entry point"""
    landmark()


if __name__ == '__main__':
    main()