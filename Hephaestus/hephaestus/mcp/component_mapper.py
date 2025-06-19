"""
Component Architecture Mapper for Hephaestus UI DevTools - Phase 3

This module analyzes component relationships by examining:
1. Event flow (addEventListener, dispatchEvent, WebSocket messages)
2. Component dependencies (imports/exports, script tags)
3. Data flow (shared state, WebSocket channels)

NO BROWSER REQUIRED - Pure file-based analysis!
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from bs4 import BeautifulSoup
from collections import defaultdict

# Component relationship types
RELATIONSHIP_TYPES = {
    "event_listener": "→",      # Component listens for events
    "event_emitter": "←",       # Component emits events
    "websocket": "⟷",          # WebSocket communication
    "import": "⇒",             # ES6 imports
    "script_tag": "⇨",         # Script tag dependencies
    "shared_state": "⟺",       # Shared state/storage
}

# Event patterns to detect
EVENT_PATTERNS = {
    "addEventListener": re.compile(r'addEventListener\s*\(\s*[\'"]([^\'"\)]+)[\'"]', re.MULTILINE),
    "dispatchEvent": re.compile(r'dispatchEvent\s*\(\s*new\s+(?:Custom)?Event\s*\(\s*[\'"]([^\'"\)]+)[\'"]', re.MULTILINE),
    "dispatch_custom": re.compile(r'\.dispatch\s*\(\s*[\'"]([^\'"\)]+)[\'"]', re.MULTILINE),
    "emit_event": re.compile(r'\.emit\s*\(\s*[\'"]([^\'"\)]+)[\'"]', re.MULTILINE),
    "on_event": re.compile(r'\.on\s*\(\s*[\'"]([^\'"\)]+)[\'"]', re.MULTILINE),
    "onclick": re.compile(r'onclick\s*=\s*[\'"]([^\'"\(]+)\(', re.MULTILINE),
}

# WebSocket patterns
WEBSOCKET_PATTERNS = {
    "send_message": re.compile(r'sendMessage\s*\(\s*\{[^}]*type\s*:\s*[\'"]([^\'"\)]+)[\'"]', re.MULTILINE),
    "message_type": re.compile(r'message\.type\s*===?\s*[\'"]([^\'"\)]+)[\'"]', re.MULTILINE),
    "websocket_send": re.compile(r'socket\.send\s*\([^)]*[\'"]([^\'"\)]+)[\'"]', re.MULTILINE),
}

# Import/export patterns
IMPORT_PATTERNS = {
    "es6_import": re.compile(r'import\s+.*?\s+from\s+[\'"]([^\'"\)]+)[\'"]', re.MULTILINE),
    "require": re.compile(r'require\s*\(\s*[\'"]([^\'"\)]+)[\'"]', re.MULTILINE),
    "dynamic_import": re.compile(r'import\s*\(\s*[\'"]([^\'"\)]+)[\'"]', re.MULTILINE),
}

# State management patterns
STATE_PATTERNS = {
    "localStorage": re.compile(r'localStorage\.[gs]etItem\s*\(\s*[\'"]([^\'"\)]+)[\'"]', re.MULTILINE),
    "sessionStorage": re.compile(r'sessionStorage\.[gs]etItem\s*\(\s*[\'"]([^\'"\)]+)[\'"]', re.MULTILINE),
    "shared_state": re.compile(r'window\.([a-zA-Z_]\w*(?:State|Store|Manager))', re.MULTILINE),
}


class ComponentMapper:
    """Maps relationships between Hephaestus UI components"""
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize the component mapper
        
        Args:
            base_path: Base path for components (defaults to Hephaestus UI path)
        """
        self.base_path = Path(base_path or "/Users/cskoons/projects/github/Tekton/Hephaestus/ui")
        self.components_path = self.base_path / "components"
        self.scripts_path = self.base_path / "scripts"
        self.relationships = defaultdict(lambda: defaultdict(set))
        self.component_info = {}
        
    def find_component_files(self, component_name: str) -> Dict[str, Path]:
        """
        Find all files related to a component
        
        Args:
            component_name: Name of the component
            
        Returns:
            Dictionary of file types to paths
        """
        files = {}
        
        # Check component directory
        comp_dir = self.components_path / component_name
        if comp_dir.exists():
            # Look for HTML file
            for pattern in [f"{component_name}-component.html", "index.html", f"{component_name}.html"]:
                html_path = comp_dir / pattern
                if html_path.exists():
                    files["html"] = html_path
                    break
            
            # Look for JS files
            scripts_dir = comp_dir / "scripts"
            if scripts_dir.exists():
                files["scripts"] = list(scripts_dir.glob("*.js"))
            
        # Check scripts directory
        script_dir = self.scripts_path / component_name
        if script_dir.exists():
            js_files = list(script_dir.glob("*.js"))
            if "scripts" in files:
                files["scripts"].extend(js_files)
            else:
                files["scripts"] = js_files
                
        # Check for direct script files
        for pattern in [f"{component_name}-component.js", f"{component_name}-service.js", f"{component_name}.js"]:
            script_path = self.scripts_path / component_name / pattern
            if script_path.exists():
                if "scripts" not in files:
                    files["scripts"] = []
                if script_path not in files["scripts"]:
                    files["scripts"].append(script_path)
        
        return files
    
    def analyze_event_flow(self, content: str, component_name: str) -> Dict[str, Set[str]]:
        """
        Analyze event listeners and emitters in content
        
        Args:
            content: File content to analyze
            component_name: Name of the component being analyzed
            
        Returns:
            Dictionary of event types to event names
        """
        events = {
            "listeners": set(),
            "emitters": set(),
            "handlers": set(),
        }
        
        # Find event listeners
        for pattern_name, pattern in EVENT_PATTERNS.items():
            matches = pattern.findall(content)
            if "listen" in pattern_name or pattern_name == "on_event":
                events["listeners"].update(matches)
            elif "dispatch" in pattern_name or "emit" in pattern_name:
                events["emitters"].update(matches)
            elif pattern_name == "onclick":
                # Extract function names from onclick handlers
                events["handlers"].update(matches)
                
        return events
    
    def analyze_websocket_flow(self, content: str) -> Set[str]:
        """
        Analyze WebSocket message types in content
        
        Args:
            content: File content to analyze
            
        Returns:
            Set of WebSocket message types
        """
        message_types = set()
        
        for pattern_name, pattern in WEBSOCKET_PATTERNS.items():
            matches = pattern.findall(content)
            message_types.update(matches)
            
        return message_types
    
    def analyze_imports(self, content: str, file_path: Path) -> Set[str]:
        """
        Analyze import statements to find dependencies
        
        Args:
            content: File content to analyze
            file_path: Path of the file being analyzed
            
        Returns:
            Set of imported component names
        """
        imports = set()
        
        for pattern_name, pattern in IMPORT_PATTERNS.items():
            matches = pattern.findall(content)
            for match in matches:
                # Extract component name from import path
                if "/" in match:
                    parts = match.split("/")
                    # Look for component names in the path
                    for part in parts:
                        if part in ["athena", "hermes", "rhetor", "prometheus", "engram", 
                                   "terma", "apollo", "metis", "sophia", "harmonia", 
                                   "synthesis", "telos", "ergon", "settings", "profile", 
                                   "budget", "tekton", "tekton-dashboard"]:
                            imports.add(part)
                            
        return imports
    
    def analyze_state_management(self, content: str) -> Dict[str, Set[str]]:
        """
        Analyze state management patterns
        
        Args:
            content: File content to analyze
            
        Returns:
            Dictionary of state types to keys/names
        """
        state = {
            "localStorage": set(),
            "sessionStorage": set(),
            "shared_objects": set(),
        }
        
        # Find storage keys
        for storage_type in ["localStorage", "sessionStorage"]:
            pattern = STATE_PATTERNS[storage_type]
            matches = pattern.findall(content)
            state[storage_type].update(matches)
            
        # Find shared state objects
        shared_pattern = STATE_PATTERNS["shared_state"]
        matches = shared_pattern.findall(content)
        state["shared_objects"].update(matches)
        
        return state
    
    def analyze_html_relationships(self, html_path: Path, component_name: str) -> None:
        """
        Analyze HTML file for component relationships
        
        Args:
            html_path: Path to HTML file
            component_name: Name of the component
        """
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        soup = BeautifulSoup(content, 'html.parser')
        
        # Analyze script tags for dependencies
        script_deps = set()
        for script in soup.find_all('script', src=True):
            src = script['src']
            for comp in ["athena", "hermes", "rhetor", "prometheus", "engram", 
                        "terma", "apollo", "metis", "sophia", "harmonia", 
                        "synthesis", "telos", "ergon", "settings", "profile", 
                        "budget", "tekton", "tekton-dashboard"]:
                if comp in src and comp != component_name:
                    script_deps.add(comp)
                    
        # Analyze inline scripts
        for script in soup.find_all('script', src=False):
            if script.string:
                events = self.analyze_event_flow(script.string, component_name)
                ws_messages = self.analyze_websocket_flow(script.string)
                state = self.analyze_state_management(script.string)
                
                # Store findings
                self.component_info[component_name] = self.component_info.get(component_name, {})
                self.component_info[component_name]["events"] = events
                self.component_info[component_name]["websocket"] = ws_messages
                self.component_info[component_name]["state"] = state
                
        # Store script dependencies
        for dep in script_deps:
            self.relationships[component_name]["script_tag"].add(dep)
    
    def analyze_javascript_relationships(self, js_paths: List[Path], component_name: str) -> None:
        """
        Analyze JavaScript files for component relationships
        
        Args:
            js_paths: List of JavaScript file paths
            component_name: Name of the component
        """
        all_events = {"listeners": set(), "emitters": set(), "handlers": set()}
        all_ws_messages = set()
        all_imports = set()
        all_state = {"localStorage": set(), "sessionStorage": set(), "shared_objects": set()}
        
        for js_path in js_paths:
            with open(js_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Analyze different aspects
            events = self.analyze_event_flow(content, component_name)
            ws_messages = self.analyze_websocket_flow(content)
            imports = self.analyze_imports(content, js_path)
            state = self.analyze_state_management(content)
            
            # Merge results
            for key in all_events:
                all_events[key].update(events.get(key, set()))
            all_ws_messages.update(ws_messages)
            all_imports.update(imports)
            for key in all_state:
                all_state[key].update(state.get(key, set()))
                
        # Store findings
        if component_name not in self.component_info:
            self.component_info[component_name] = {}
            
        self.component_info[component_name]["events"] = all_events
        self.component_info[component_name]["websocket"] = all_ws_messages
        self.component_info[component_name]["imports"] = all_imports
        self.component_info[component_name]["state"] = all_state
        
        # Build import relationships
        for imported in all_imports:
            if imported != component_name:
                self.relationships[component_name]["import"].add(imported)
    
    def analyze_component(self, component_name: str) -> Dict[str, Any]:
        """
        Analyze a single component's relationships
        
        Args:
            component_name: Name of the component
            
        Returns:
            Analysis results
        """
        files = self.find_component_files(component_name)
        
        if not files:
            return {
                "error": f"No files found for component: {component_name}",
                "component": component_name
            }
            
        # Analyze HTML if present
        if "html" in files:
            self.analyze_html_relationships(files["html"], component_name)
            
        # Analyze JavaScript if present
        if "scripts" in files and files["scripts"]:
            self.analyze_javascript_relationships(files["scripts"], component_name)
            
        return {
            "component": component_name,
            "files": {
                "html": str(files.get("html", "")),
                "scripts": [str(p) for p in files.get("scripts", [])]
            },
            "info": self.component_info.get(component_name, {}),
            "relationships": dict(self.relationships.get(component_name, {}))
        }
    
    def build_relationship_graph(self) -> Dict[str, Any]:
        """
        Build a complete relationship graph from analyzed components
        
        Returns:
            Graph structure with nodes and edges
        """
        nodes = []
        edges = []
        
        # Create nodes for each component
        for component in self.component_info:
            node = {
                "id": component,
                "label": component.title(),
                "events": len(self.component_info[component].get("events", {}).get("listeners", [])) +
                         len(self.component_info[component].get("events", {}).get("emitters", [])),
                "websocket": len(self.component_info[component].get("websocket", [])),
                "imports": len(self.component_info[component].get("imports", [])),
            }
            nodes.append(node)
            
        # Create edges for relationships
        edge_id = 0
        for source, rel_types in self.relationships.items():
            for rel_type, targets in rel_types.items():
                for target in targets:
                    edge = {
                        "id": edge_id,
                        "source": source,
                        "target": target,
                        "type": rel_type,
                        "symbol": RELATIONSHIP_TYPES.get(rel_type, "→")
                    }
                    edges.append(edge)
                    edge_id += 1
                    
        return {
            "nodes": nodes,
            "edges": edges,
            "stats": {
                "total_components": len(nodes),
                "total_relationships": len(edges),
                "relationship_types": dict(self.count_relationship_types())
            }
        }
    
    def count_relationship_types(self) -> Dict[str, int]:
        """Count relationships by type"""
        counts = defaultdict(int)
        for component, rel_types in self.relationships.items():
            for rel_type, targets in rel_types.items():
                counts[rel_type] += len(targets)
        return counts
    
    def generate_ascii_visualization(self, max_width: int = 80) -> str:
        """
        Generate ASCII art visualization of component relationships
        
        Args:
            max_width: Maximum width for the visualization
            
        Returns:
            ASCII art string
        """
        lines = []
        lines.append("=" * max_width)
        lines.append("COMPONENT ARCHITECTURE MAP".center(max_width))
        lines.append("=" * max_width)
        lines.append("")
        
        # Show each component and its relationships
        for component, rel_types in sorted(self.relationships.items()):
            if not any(rel_types.values()):
                continue
                
            lines.append(f"┌─ {component.upper()} ─┐")
            
            for rel_type, targets in sorted(rel_types.items()):
                if targets:
                    symbol = RELATIONSHIP_TYPES.get(rel_type, "→")
                    for target in sorted(targets):
                        lines.append(f"│  {symbol} {target:<20} ({rel_type})")
                        
            lines.append("└" + "─" * (len(component) + 6) + "┘")
            lines.append("")
            
        # Show summary statistics
        lines.append("-" * max_width)
        lines.append("SUMMARY".center(max_width))
        lines.append("-" * max_width)
        
        stats = self.count_relationship_types()
        total_components = len(self.component_info)
        total_relationships = sum(stats.values())
        
        lines.append(f"Total Components: {total_components}")
        lines.append(f"Total Relationships: {total_relationships}")
        lines.append("")
        lines.append("Relationship Types:")
        for rel_type, count in sorted(stats.items()):
            symbol = RELATIONSHIP_TYPES.get(rel_type, "?")
            lines.append(f"  {symbol} {rel_type:<20}: {count}")
            
        lines.append("=" * max_width)
        
        return "\n".join(lines)
    
    def find_circular_dependencies(self) -> List[List[str]]:
        """
        Find circular dependencies in the component graph
        
        Returns:
            List of circular dependency chains
        """
        cycles = []
        
        def dfs(node: str, path: List[str], visited: Set[str]) -> None:
            if node in path:
                # Found a cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                if cycle not in cycles:
                    cycles.append(cycle)
                return
                
            if node in visited:
                return
                
            visited.add(node)
            path.append(node)
            
            # Check all relationship types
            for rel_type, targets in self.relationships.get(node, {}).items():
                for target in targets:
                    dfs(target, path.copy(), visited.copy())
                    
        # Run DFS from each component
        for component in self.component_info:
            dfs(component, [], set())
            
        return cycles
    
    def analyze_system(self, components: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze the entire system or specific components
        
        Args:
            components: List of component names to analyze (None for all)
            
        Returns:
            Complete analysis results
        """
        # Get list of components to analyze
        if components is None:
            # Find all components
            components = []
            if self.components_path.exists():
                for item in self.components_path.iterdir():
                    if item.is_dir() and not item.name.startswith('.'):
                        components.append(item.name)
                        
        # Analyze each component
        results = []
        for component in components:
            result = self.analyze_component(component)
            results.append(result)
            
        # Build relationship graph
        graph = self.build_relationship_graph()
        
        # Find circular dependencies
        cycles = self.find_circular_dependencies()
        
        # Generate visualization
        visualization = self.generate_ascii_visualization()
        
        return {
            "components": results,
            "graph": graph,
            "circular_dependencies": cycles,
            "visualization": visualization
        }


# Convenience functions for testing
def analyze_component(component_name: str) -> Dict[str, Any]:
    """Analyze a single component"""
    mapper = ComponentMapper()
    return mapper.analyze_component(component_name)


def analyze_system(components: Optional[List[str]] = None) -> Dict[str, Any]:
    """Analyze the entire system"""
    mapper = ComponentMapper()
    return mapper.analyze_system(components)


def print_visualization(components: Optional[List[str]] = None) -> None:
    """Print ASCII visualization of the system"""
    mapper = ComponentMapper()
    results = mapper.analyze_system(components)
    print(results["visualization"])


if __name__ == "__main__":
    # Test with a few components
    print("Testing Component Architecture Mapper...")
    print("\nAnalyzing rhetor component:")
    rhetor_analysis = analyze_component("rhetor")
    print(json.dumps(rhetor_analysis, indent=2))
    
    print("\n\nAnalyzing system relationships:")
    system_analysis = analyze_system(["rhetor", "hermes", "prometheus"])
    print(system_analysis["visualization"])