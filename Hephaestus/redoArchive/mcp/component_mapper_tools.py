"""
Component Mapper Tools for UI DevTools - Phase 3
Provides MCP tool endpoints for component architecture analysis
"""

from typing import Dict, Any, List, Optional
try:
    from .component_mapper import ComponentMapper
except ImportError:
    # For direct execution and testing
    from component_mapper import ComponentMapper
import json


async def ui_component_map(component: str) -> Dict[str, Any]:
    """
    Analyze relationships for a single component
    
    Args:
        component: Name of the component to analyze (e.g., 'rhetor', 'hermes')
        
    Returns:
        Component relationship analysis including:
        - Event flow (listeners, emitters)
        - WebSocket messages
        - Import dependencies
        - State management
        - ASCII visualization
    """
    try:
        mapper = ComponentMapper()
        
        # Analyze the component
        analysis = mapper.analyze_component(component)
        
        if "error" in analysis:
            return {
                "error": analysis["error"],
                "component": component
            }
        
        # Build relationships for this component
        mapper.analyze_system([component])
        
        # Generate a focused visualization
        visualization = _generate_component_visualization(mapper, component)
        
        return {
            "component": component,
            "files": analysis.get("files", {}),
            "relationships": {
                "events": analysis.get("info", {}).get("events", {}),
                "websocket": list(analysis.get("info", {}).get("websocket", [])),
                "imports": list(analysis.get("info", {}).get("imports", [])),
                "state": analysis.get("info", {}).get("state", {}),
                "outgoing": dict(mapper.relationships.get(component, {}))
            },
            "visualization": visualization,
            "summary": _generate_component_summary(analysis, mapper)
        }
        
    except Exception as e:
        return {
            "error": f"Failed to analyze component: {str(e)}",
            "component": component
        }


async def ui_architecture_scan(components: Optional[List[str]] = None, 
                              max_components: int = 20) -> Dict[str, Any]:
    """
    Perform system-wide architecture scan
    
    Args:
        components: List of components to analyze (None for all)
        max_components: Maximum number of components to analyze
        
    Returns:
        System-wide analysis including:
        - Component graph
        - Circular dependencies
        - Relationship statistics
        - ASCII visualization
    """
    try:
        mapper = ComponentMapper()
        
        # If no components specified, discover them
        if components is None:
            components = _discover_components(mapper.components_path)
            # Limit to max_components
            if len(components) > max_components:
                components = components[:max_components]
        
        # Analyze the system
        results = mapper.analyze_system(components)
        
        return {
            "analyzed_components": len(components),
            "components": components,
            "graph": results["graph"],
            "circular_dependencies": results["circular_dependencies"],
            "visualization": results["visualization"],
            "statistics": _generate_system_statistics(results),
            "recommendations": _generate_recommendations(results)
        }
        
    except Exception as e:
        return {
            "error": f"Failed to perform architecture scan: {str(e)}"
        }


async def ui_dependency_graph(format: str = "ascii", 
                             focus: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate dependency graph visualization
    
    Args:
        format: Output format ('ascii', 'json', 'mermaid')
        focus: Optional component to focus on
        
    Returns:
        Dependency graph in requested format
    """
    try:
        mapper = ComponentMapper()
        
        # Analyze system
        components = _discover_components(mapper.components_path)
        if focus and focus in components:
            # Focus on specific component and its connections
            related = _find_related_components(mapper, focus)
            components = [focus] + list(related)
            
        results = mapper.analyze_system(components)
        
        if format == "ascii":
            return {
                "format": "ascii",
                "visualization": results["visualization"],
                "focus": focus
            }
        elif format == "json":
            return {
                "format": "json",
                "graph": results["graph"],
                "focus": focus
            }
        elif format == "mermaid":
            return {
                "format": "mermaid",
                "visualization": _generate_mermaid_diagram(results["graph"], focus),
                "focus": focus
            }
        else:
            return {
                "error": f"Unsupported format: {format}",
                "supported_formats": ["ascii", "json", "mermaid"]
            }
            
    except Exception as e:
        return {
            "error": f"Failed to generate dependency graph: {str(e)}"
        }


# Helper functions

def _discover_components(components_path) -> List[str]:
    """Discover all available components"""
    components = []
    if components_path.exists():
        for item in components_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                # Skip non-component directories
                if item.name not in ["shared", "test"]:
                    components.append(item.name)
    return sorted(components)


def _generate_component_visualization(mapper: ComponentMapper, component: str) -> str:
    """Generate focused visualization for a single component"""
    lines = []
    lines.append(f"{'='*60}")
    lines.append(f"{component.upper()} - COMPONENT RELATIONSHIPS".center(60))
    lines.append(f"{'='*60}")
    lines.append("")
    
    # Outgoing relationships
    if component in mapper.relationships:
        lines.append("OUTGOING CONNECTIONS:")
        for rel_type, targets in mapper.relationships[component].items():
            if targets:
                symbol = mapper.RELATIONSHIP_TYPES.get(rel_type, "→")
                lines.append(f"  {rel_type}:")
                for target in sorted(targets):
                    lines.append(f"    {symbol} {target}")
        lines.append("")
    
    # Incoming relationships (reverse lookup)
    incoming = []
    for source, rel_types in mapper.relationships.items():
        if source == component:
            continue
        for rel_type, targets in rel_types.items():
            if component in targets:
                incoming.append((source, rel_type))
                
    if incoming:
        lines.append("INCOMING CONNECTIONS:")
        for source, rel_type in sorted(incoming):
            symbol = mapper.RELATIONSHIP_TYPES.get(rel_type, "→")
            lines.append(f"  {source} {symbol} {component} ({rel_type})")
        lines.append("")
    
    # Component info
    info = mapper.component_info.get(component, {})
    if info:
        lines.append("COMPONENT DETAILS:")
        
        # Events
        events = info.get("events", {})
        if any(events.values()):
            lines.append("  Events:")
            if events.get("listeners"):
                lines.append(f"    Listens to: {', '.join(sorted(events['listeners']))}")
            if events.get("emitters"):
                lines.append(f"    Emits: {', '.join(sorted(events['emitters']))}")
            if events.get("handlers"):
                lines.append(f"    Handlers: {', '.join(sorted(events['handlers']))}")
                
        # WebSocket
        ws = info.get("websocket", [])
        if ws:
            lines.append(f"  WebSocket messages: {', '.join(sorted(ws))}")
            
        # State
        state = info.get("state", {})
        if any(state.values()):
            lines.append("  State management:")
            for storage_type, keys in state.items():
                if keys:
                    lines.append(f"    {storage_type}: {', '.join(sorted(keys))}")
    
    lines.append(f"{'='*60}")
    return "\n".join(lines)


def _generate_component_summary(analysis: Dict[str, Any], mapper: ComponentMapper) -> str:
    """Generate a summary of component relationships"""
    info = analysis.get("info", {})
    relationships = mapper.relationships.get(analysis["component"], {})
    
    summary_parts = []
    
    # Count relationships
    total_outgoing = sum(len(targets) for targets in relationships.values())
    if total_outgoing > 0:
        summary_parts.append(f"{total_outgoing} outgoing connections")
    
    # Count events
    events = info.get("events", {})
    event_count = len(events.get("listeners", [])) + len(events.get("emitters", []))
    if event_count > 0:
        summary_parts.append(f"{event_count} event interactions")
    
    # WebSocket
    ws_count = len(info.get("websocket", []))
    if ws_count > 0:
        summary_parts.append(f"{ws_count} WebSocket message types")
    
    # State
    state = info.get("state", {})
    state_count = sum(len(keys) for keys in state.values())
    if state_count > 0:
        summary_parts.append(f"{state_count} state keys")
    
    return "; ".join(summary_parts) if summary_parts else "No relationships detected"


def _generate_system_statistics(results: Dict[str, Any]) -> Dict[str, Any]:
    """Generate system-wide statistics"""
    graph = results.get("graph", {})
    stats = graph.get("stats", {})
    
    # Calculate additional statistics
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    
    # Find most connected components
    connection_counts = {}
    for edge in edges:
        source = edge["source"]
        target = edge["target"]
        connection_counts[source] = connection_counts.get(source, 0) + 1
        connection_counts[target] = connection_counts.get(target, 0) + 1
    
    most_connected = sorted(connection_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return {
        "total_components": stats.get("total_components", 0),
        "total_relationships": stats.get("total_relationships", 0),
        "relationship_breakdown": stats.get("relationship_types", {}),
        "circular_dependencies": len(results.get("circular_dependencies", [])),
        "most_connected": [{"component": c, "connections": n} for c, n in most_connected],
        "isolated_components": [n["id"] for n in nodes if n["id"] not in connection_counts]
    }


def _generate_recommendations(results: Dict[str, Any]) -> List[str]:
    """Generate architectural recommendations based on analysis"""
    recommendations = []
    
    # Check for circular dependencies
    cycles = results.get("circular_dependencies", [])
    if cycles:
        recommendations.append(f"⚠️  Found {len(cycles)} circular dependencies that should be resolved")
        for cycle in cycles[:3]:  # Show first 3
            recommendations.append(f"   • {' → '.join(cycle)}")
    
    # Check for isolated components
    stats = _generate_system_statistics(results)
    isolated = stats.get("isolated_components", [])
    if isolated:
        recommendations.append(f"ℹ️  Found {len(isolated)} isolated components with no connections")
        recommendations.append(f"   Consider integrating: {', '.join(isolated[:5])}")
    
    # Check for highly coupled components
    most_connected = stats.get("most_connected", [])
    if most_connected and most_connected[0]["connections"] > 10:
        recommendations.append(f"⚠️  Component '{most_connected[0]['component']}' has {most_connected[0]['connections']} connections")
        recommendations.append("   Consider refactoring to reduce coupling")
    
    # Check relationship balance
    rel_types = stats.get("relationship_breakdown", {})
    if rel_types.get("websocket", 0) > rel_types.get("event_listener", 0) * 2:
        recommendations.append("ℹ️  Heavy WebSocket usage detected")
        recommendations.append("   Consider using more event-based communication for loose coupling")
    
    if not recommendations:
        recommendations.append("✅ Architecture looks healthy - no major issues detected")
    
    return recommendations


def _find_related_components(mapper: ComponentMapper, focus: str) -> set:
    """Find all components related to the focus component"""
    related = set()
    
    # Outgoing relationships
    for rel_type, targets in mapper.relationships.get(focus, {}).items():
        related.update(targets)
    
    # Incoming relationships
    for source, rel_types in mapper.relationships.items():
        for rel_type, targets in rel_types.items():
            if focus in targets:
                related.add(source)
                
    return related


def _generate_mermaid_diagram(graph: Dict[str, Any], focus: Optional[str] = None) -> str:
    """Generate Mermaid diagram syntax"""
    lines = ["graph LR"]
    
    # Add nodes
    for node in graph.get("nodes", []):
        node_id = node["id"]
        label = node["label"]
        if focus and node_id == focus:
            lines.append(f"    {node_id}[<b>{label}</b>]")
        else:
            lines.append(f"    {node_id}[{label}]")
    
    # Add edges
    for edge in graph.get("edges", []):
        source = edge["source"]
        target = edge["target"]
        rel_type = edge["type"]
        symbol = edge["symbol"]
        
        lines.append(f"    {source} -->|{rel_type}| {target}")
    
    # Add styling
    if focus:
        lines.append(f"    style {focus} fill:#f9f,stroke:#333,stroke-width:4px")
    
    return "\n".join(lines)