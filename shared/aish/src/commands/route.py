"""
aish route command - Intelligent message pipelines with named routes and purposes
"""
import json
import sys
import shlex
from pathlib import Path
from typing import Dict, List, Optional, Union, Any

# Add parent to path for shared imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from shared.env import TektonEnviron

# Known AI names (should match main aish file)
KNOWN_AI_NAMES = [
    'numa', 'tekton', 'prometheus', 'telos', 'metis', 'harmonia',
    'synthesis', 'athena', 'sophia', 'noesis', 'engram', 'apollo',
    'rhetor', 'penia', 'hermes', 'ergon', 'terma', 'hephaestus',
    'team-chat', 'tekton-core', 'tekton_core'
]


class RouteRegistry:
    """Registry for named routes with purposes"""
    
    def __init__(self):
        # Load from persistent storage
        tekton_root = TektonEnviron.get('TEKTON_ROOT', str(Path.home()))
        self.registry_file = Path(tekton_root) / '.tekton' / 'aish' / 'routes.json'
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        self.routes = self._load_routes()
    
    def _load_routes(self) -> Dict[str, Any]:
        """Load routes from persistent storage"""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_routes(self):
        """Save routes to persistent storage"""
        with open(self.registry_file, 'w') as f:
            json.dump(self.routes, f, indent=2)
    
    def add_route(self, name: str, dest: str, hops: List[str], purposes: List[str]):
        """Add a named route with purposes"""
        # Build route key as dest:name
        route_key = f"{dest}:{name}"
        
        # Extract final purpose
        final_purpose = purposes[-1] if purposes else ""
        hop_purposes = purposes[:-1] if len(purposes) > 1 else []
        
        self.routes[route_key] = {
            "name": name,
            "dest": dest,
            "hops": hops,
            "purposes": hop_purposes,
            "final_purpose": final_purpose
        }
        self._save_routes()
    
    def get_route(self, dest: str, name: str = "default") -> Optional[Dict[str, Any]]:
        """Get a route by destination and name"""
        route_key = f"{dest}:{name}"
        return self.routes.get(route_key)
    
    def remove_route(self, name: str, dest: Optional[str] = None):
        """Remove a route by name (and optionally destination)"""
        if dest:
            # Remove specific route
            route_key = f"{dest}:{name}"
            if route_key in self.routes:
                del self.routes[route_key]
                self._save_routes()
                return True
        else:
            # Remove all routes with this name
            removed = False
            keys_to_remove = [k for k in self.routes.keys() if k.endswith(f":{name}")]
            for key in keys_to_remove:
                del self.routes[key]
                removed = True
            if removed:
                self._save_routes()
            return removed
        return False
    
    def list_routes(self, dest: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all routes or routes to specific destination"""
        if dest:
            # Routes to specific destination
            return [v for k, v in self.routes.items() if k.startswith(f"{dest}:")]
        else:
            # All routes
            return list(self.routes.values())


def parse_raw_route_command(raw_command: str):
    """Parse the raw route command preserving quotes
    
    Uses shlex to properly handle quoted strings
    """
    if not raw_command:
        return []
    
    try:
        # shlex preserves quoted strings as single tokens
        return shlex.split(raw_command)
    except ValueError as e:
        print(f"Error parsing command: {e}")
        return []


def parse_route_definition(tokens: List[str]) -> tuple:
    """Parse route definition tokens where quotes are preserved
    
    Format: <hop1> [purpose "text"] <hop2> [purpose "text"] ... <dest> [purpose "text"]
    """
    hops = []
    purposes = []
    
    i = 0
    while i < len(tokens):
        token = tokens[i]
        
        if token.lower() == 'purpose':
            # Next token is the purpose (already preserved with quotes)
            if i + 1 < len(tokens):
                purposes.append(tokens[i + 1])
                i += 2
            else:
                print("Warning: 'purpose' without value")
                i += 1
        elif token.lower() == 'project':
            # Next token is project name
            if i + 1 < len(tokens):
                hops.append(f"project:{tokens[i + 1]}")
                purposes.append("")  # No purpose yet
                i += 2
            else:
                print("Warning: 'project' without name")
                i += 1
        else:
            # Regular hop
            hops.append(token)
            # Check if next is purpose
            if i + 1 < len(tokens) and tokens[i + 1].lower() == 'purpose':
                # Purpose follows, will be handled next iteration
                pass
            else:
                purposes.append("")
            i += 1
    
    # Align purposes with hops
    while len(purposes) < len(hops):
        purposes.append("")
    purposes = purposes[:len(hops)]
    
    return hops, purposes


def format_route_display(route: Dict[str, Any]) -> str:
    """Format route for display"""
    hops_with_purpose = []
    
    # Format hops with their purposes
    for i, hop in enumerate(route['hops']):
        purpose = route['purposes'][i] if i < len(route['purposes']) else ""
        if purpose:
            hops_with_purpose.append(f'{hop} (purpose: "{purpose}")')
        else:
            hops_with_purpose.append(hop)
    
    # Add destination with final purpose
    if route['final_purpose']:
        hops_with_purpose.append(f"{route['dest']} (purpose: \"{route['final_purpose']}\")")
    else:
        hops_with_purpose.append(route['dest'])
    
    return f"{route['name']}: " + " → ".join(hops_with_purpose)


def handle_route_command(raw_args: str = None) -> bool:
    """Handle the aish route command - reads full command line itself"""
    
    # Get arguments directly from sys.argv (which preserves quoted strings)
    if raw_args is None:
        # sys.argv already has quotes parsed properly by the shell
        args = sys.argv[2:] if len(sys.argv) > 2 else []
    else:
        # Legacy path if called with raw_args
        args = parse_raw_route_command(raw_args)
    
    if not args:
        print("Usage: aish route <subcommand> [args...]")
        print("Subcommands:")
        print('  name <name> <hop1> [purpose "text"] ... <dest> [purpose "text"]')
        print("  list [dest]")
        print("  show <name>")
        print("  remove <name> [dest]")
        print("")
        print("Sending messages:")
        print('  aish route <dest> "message"     - Send through default route')
        print("  aish route <dest> '{json}'      - Send JSON through default route")
        print("")
        print("Examples:")
        print('  aish route name "review" numa purpose "prepare" apollo purpose "analyze" cari')
        print('  aish route cari "Should we implement this feature?"')
        return True
    
    registry = RouteRegistry()
    subcommand = args[0]
    
    if subcommand == "list":
        # List routes
        dest = args[1] if len(args) > 1 else None
        routes = registry.list_routes(dest)
        
        if not routes:
            if dest:
                print(f"No routes to {dest}")
            else:
                print("No routes defined")
            return True
        
        print("Active routes:")
        for route in routes:
            print(f"  {format_route_display(route)}")
        
        return True
    
    elif subcommand == "show":
        # Show specific route
        if len(args) < 2:
            print("Usage: aish route show <name>")
            return False
        
        route_name = args[1]
        matching_routes = [r for r in registry.list_routes() if r['name'] == route_name]
        
        if not matching_routes:
            print(f"No route named '{route_name}' found")
            return False
        
        for route in matching_routes:
            print(f"Route: {route['name']}")
            print(f"Destination: {route['dest']}")
            print("Path:")
            for i, hop in enumerate(route['hops']):
                purpose = route['purposes'][i] if i < len(route['purposes']) else ""
                if purpose:
                    print(f"  → {hop}")
                    print(f"    Purpose: \"{purpose}\"")
                else:
                    print(f"  → {hop}")
            final_purpose = route['final_purpose']
            print(f"  → {route['dest']} (final destination)")
            if final_purpose:
                print(f"    Purpose: \"{final_purpose}\"")
        
        return True
    
    elif subcommand == "remove":
        # Remove route
        if len(args) < 2:
            print("Usage: aish route remove <name> [dest]")
            return False
        
        route_name = args[1]
        dest = args[2] if len(args) > 2 else None
        
        if registry.remove_route(route_name, dest):
            print(f"Route '{route_name}' removed")
        else:
            print(f"No route '{route_name}' found")
        
        return True
    
    elif subcommand == "name":
        # Define a route OR send through named route
        if len(args) < 3:
            print('Usage: aish route name <name> <hop1> [purpose "text"] ... <dest>')
            return False
        
        route_name = args[1]
        
        # Check if this is a send operation
        # If we have exactly 4 args and the last looks like a message (not an AI name)
        if len(args) == 4 and not args[3] in KNOWN_AI_NAMES:
            # This is: route name <name> <dest> "message"
            dest = args[2]
            message = args[3]
            
            # Look up the named route
            route = registry.get_route(dest, route_name)
            if not route:
                print(f"No route named '{route_name}' to {dest}")
                return False
            
            # Send through the route
            return send_through_route(registry, route, route_name, dest, message)
        
        # Otherwise, this is route definition
        route_args = args[2:]
        hops, purposes = parse_route_definition(route_args)
        
        if len(hops) < 2:
            print("Error: Route must have at least one hop and a destination")
            return False
        
        # Last hop is destination
        dest = hops[-1]
        actual_hops = hops[:-1]
        
        registry.add_route(route_name, dest, actual_hops, purposes)
        print(f"Route '{route_name}' created: " + " → ".join(actual_hops + [dest]))
        return True
    
    else:
        # This is: route <dest> "message" or route <dest> {json}
        dest = subcommand
        if len(args) < 2:
            print(f'Usage: aish route {dest} "message" or aish route {dest} \'{{json}}\'')
            return False
        
        message = args[1]
        
        # Look up default route
        route = registry.get_route(dest, "default")
        
        # Send (through route if exists, direct if not)
        return send_through_route(registry, route, "default", dest, message)


def send_through_route(registry, route, route_name: str, dest: str, message: str) -> bool:
    """Send a message through a route (or direct if no route)"""
    
    # Check if message is JSON
    is_json = message.strip().startswith('{')
    
    if is_json:
        try:
            msg_data = json.loads(message)
        except json.JSONDecodeError:
            print("Error: Invalid JSON format")
            return False
    else:
        # Create initial JSON for text message
        msg_data = {
            "message": message,
            "annotations": []
        }
    
    if route:
        # We have a route - determine position and next hop
        next_hop = None
        next_purpose = ""
        
        # Check annotations to see where we are
        if 'annotations' in msg_data and msg_data['annotations']:
            last_author = msg_data['annotations'][-1].get('author')
            if last_author and last_author in route['hops']:
                try:
                    hop_index = route['hops'].index(last_author)
                    if hop_index + 1 < len(route['hops']):
                        next_hop = route['hops'][hop_index + 1]
                        next_purpose = route['purposes'][hop_index + 1] if hop_index + 1 < len(route['purposes']) else ""
                    else:
                        # Last hop complete, go to destination
                        next_hop = dest
                        next_purpose = route['final_purpose']
                except ValueError:
                    pass
        
        # If we couldn't determine position, start from beginning
        if next_hop is None:
            if route['hops']:
                next_hop = route['hops'][0]
                next_purpose = route['purposes'][0] if route['purposes'] else ""
            else:
                next_hop = dest
                next_purpose = route['final_purpose']
        
        # Update message with route metadata
        msg_data.update({
            "name": route_name,
            "dest": dest,
            "purpose": next_purpose
        })
        
        # Send to next hop
        from core.shell import AIShell
        shell = AIShell()
        shell.send_to_ai(next_hop, json.dumps(msg_data))
        
    else:
        # No route - direct send
        from core.shell import AIShell
        shell = AIShell()
        
        if is_json:
            shell.send_to_ai(dest, message)
        else:
            shell.send_to_ai(dest, message)
    
    return True