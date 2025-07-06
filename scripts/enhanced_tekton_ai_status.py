#!/usr/bin/env python3
"""
Enhanced Tekton AI Status

Shows status of AI specialists for Tekton components.
"""
import os
import sys
import argparse
import asyncio
import json
import psutil
from typing import Dict, List, Optional
from datetime import datetime
from tabulate import tabulate

# Add Tekton root to path
script_path = os.path.realpath(__file__)
tekton_root = os.path.dirname(os.path.dirname(script_path))
sys.path.insert(0, tekton_root)

# Registry client removed - using fixed port discovery
from shared.utils.env_config import get_component_config
from shared.utils.logging_setup import setup_component_logging
import socket


class AIStatus:
    """Manages AI specialist status reporting."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.config = get_component_config()
        
        # Setup logging
        log_level = 'DEBUG' if verbose else 'WARNING'  # Only show warnings unless verbose
        self.logger = setup_component_logging('ai_status', log_level)
        
        # Load model display names
        self.model_display_names = self._load_model_display_names()
        
        # Known AI components
        self.ai_components = ['engram', 'hermes', 'ergon', 'rhetor', 'terma', 'athena',
                            'prometheus', 'harmonia', 'telos', 'synthesis', 'tekton_core',
                            'metis', 'apollo', 'penia', 'sophia', 'noesis', 'numa', 'hephaestus']
    
    def _load_model_display_names(self) -> Dict[str, str]:
        """Load model display names from config."""
        config_path = os.path.join(tekton_root, 'config', 'ai_model_display_names.json')
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
                return data.get('model_display_names', {})
        except Exception as e:
            self.logger.warning(f"Could not load model display names: {e}")
            return {}
    
    def _get_display_model_name(self, model: str) -> str:
        """Get display name for a model."""
        if not model:
            return "Unknown"
        # Check mapping first
        if model in self.model_display_names:
            return self.model_display_names[model]
        # Clean up raw model name
        if ':' in model:
            # Ollama format: llama3:70b -> Llama3 70B
            base, variant = model.split(':', 1)
            return f"{base.title()} {variant.upper()}"
        return model
        
    async def check_ai_health(self, ai_id: str, socket_info: tuple) -> str:
        """
        Check if an AI is responding.
        
        Args:
            ai_id: AI identifier
            socket_info: (host, port) tuple
            
        Returns:
            Health status string
        """
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(socket_info[0], socket_info[1]),
                timeout=2.0
            )
            
            # Send ping
            writer.write(b'{"type": "ping"}\n')
            await writer.drain()
            
            # Wait for response
            response = await asyncio.wait_for(reader.readline(), timeout=2.0)
            
            writer.close()
            await writer.wait_closed()
            
            if response:
                return "✓ Healthy"
            else:
                return "⚠ No Response"
                
        except asyncio.TimeoutError:
            return "⚠ Timeout"
        except ConnectionRefusedError:
            return "✗ Connection Refused"
        except Exception as e:
            return f"✗ Error: {str(e)[:20]}"
    
    def get_process_info(self, pid: Optional[int]) -> Dict[str, any]:
        """Get process information if PID is available."""
        if not pid:
            return {'cpu': 'N/A', 'memory': 'N/A', 'uptime': 'N/A'}
        
        try:
            process = psutil.Process(pid)
            create_time = datetime.fromtimestamp(process.create_time())
            uptime = datetime.now() - create_time
            
            return {
                'cpu': f"{process.cpu_percent(interval=0.1):.1f}%",
                'memory': f"{process.memory_info().rss / 1024 / 1024:.1f}MB",
                'uptime': str(uptime).split('.')[0]  # Remove microseconds
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return {'cpu': 'N/A', 'memory': 'N/A', 'uptime': 'N/A'}
    
    async def get_ai_info(self, ai_id: str, socket_info: tuple) -> Dict[str, str]:
        """Get AI info including model."""
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(socket_info[0], socket_info[1]),
                timeout=2.0
            )
            
            # Send info request
            writer.write(b'{"type": "info"}\n')
            await writer.drain()
            
            # Get response
            response = await asyncio.wait_for(reader.readline(), timeout=2.0)
            
            writer.close()
            await writer.wait_closed()
            
            if response:
                data = json.loads(response.decode())
                return {
                    'model_provider': data.get('model_provider', 'unknown'),
                    'model_name': data.get('model_name', 'unknown'),
                    'description': data.get('description', ''),
                    'system_prompt': data.get('system_prompt', '')
                }
                
        except Exception:
            pass
            
        return {'model_provider': 'unknown', 'model_name': 'unknown'}
    
    async def get_ai_status(self) -> List[Dict]:
        """Get status for all AI specialists."""
        status_data = []
        
        for component in self.ai_components:
            ai_id = f"{component}-ai"
            component_port = self.config.get_port(component)
            if not component_port:
                continue
                
            ai_port = (component_port - self.config.tekton_port_base) + self.config.tekton_ai_port_base
            socket_info = {'host': 'localhost', 'port': ai_port}
            
            # Check health and get info
            health = await self.check_ai_health(ai_id, socket_info)
            if health.startswith("✓"):
                ai_details = await self.get_ai_info(ai_id, socket_info)
                model = ai_details.get('model_name', 'unknown')
            else:
                model = 'unknown'
            
            # Get process info by searching for the AI process
            pid = None
            for proc in psutil.process_iter(['pid', 'cmdline']):
                try:
                    cmdline = proc.info['cmdline']
                    if cmdline and 'generic_specialist' in ' '.join(cmdline) and f'--ai-id {ai_id}' in ' '.join(cmdline):
                        pid = proc.info['pid']
                        break
                except:
                    continue
                    
            proc_info = self.get_process_info(pid)
            
            # Format model name
            display_model = self._get_display_model_name(model)
            
            # Only add if AI is running
            if health.startswith("✓") or self.verbose:
                status_data.append({
                    'AI Specialist': ai_id,
                    'Component': component.title(),
                    'Model': display_model,
                    'Status': health,
                    'CPU': proc_info['cpu'],
                    'Memory': proc_info['memory'],
                    'Uptime': proc_info['uptime']
                })
        
        return status_data
    
    def get_component_ai_status(self) -> List[Dict]:
        """Get AI enablement status for all components."""
        from scripts.enhanced_tekton_ai_launcher import AI_COMPONENTS
        
        status_data = []
        
        for component, ai_config in AI_COMPONENTS.items():
            # Check if AI is enabled for component
            enabled = ai_config['config_check'](self.config)
            
            # Check if AI is running by trying to connect
            ai_id = ai_config['ai_id']
            component_port = self.config.get_port(component)
            running = False
            if component_port:
                ai_port = (component_port - self.config.tekton_port_base) + self.config.tekton_ai_port_base
                try:
                    # Quick connection test
                    s = socket.socket()
                    s.settimeout(0.5)
                    s.connect(('localhost', ai_port))
                    s.close()
                    running = True
                except:
                    pass
            
            status_data.append({
                'Component': component.title(),
                'AI ID': ai_id,
                'Enabled': '✓' if enabled else '✗',
                'Running': '✓' if running else '✗',
                'Description': ai_config['description']
            })
        
        return status_data
    
    async def display_status(self, show_full: bool = False, components: Optional[List[str]] = None):
        """Display AI status information."""
        # Get AI status
        ai_status = await self.get_ai_status()
        
        # Filter by components if specified
        if components:
            component_set = {c.lower() for c in components}
            ai_status = [s for s in ai_status 
                        if s['Component'].lower() in component_set or 
                           s['AI Specialist'].lower() in component_set]
        
        if ai_status:
            # Use fancy_grid for box formatting like enhanced_tekton_status
            print(tabulate(ai_status, headers='keys', tablefmt='fancy_grid'))
        else:
            # Show empty table with headers
            empty_data = []
            headers = ['AI Specialist', 'Component', 'Model', 'Status', 'CPU', 'Memory', 'Uptime']
            print(tabulate(empty_data, headers=headers, tablefmt='fancy_grid'))
            
            # Check global AI status
            # Check Tekton config for AI status
            config = get_component_config()
            ai_enabled = config.tekton.register_ai
            if not ai_enabled:
                print("\nNo AI specialists running (AI support disabled)")
                print("Set TEKTON_REGISTER_AI=true in .env.tekton to enable AI support")
            else:
                print("\nNo AI specialists are currently running.")
        
        # Show full details if requested
        if show_full and ai_status:
            print("\n" + "═" * 60)
            for ai in ai_status:
                await self._display_ai_details(ai['AI Specialist'])
    
    async def _display_ai_details(self, ai_id: str):
        """Display detailed information for a specific AI."""
        # Extract component from ai_id
        component = ai_id.replace('-ai', '')
        component_port = self.config.get_port(component)
        if not component_port:
            print(f"\nComponent {component} not found")
            return
            
        ai_port = (component_port - self.config.tekton_port_base) + self.config.tekton_ai_port_base
        socket_info = {'host': 'localhost', 'port': ai_port}
        
        # Check if AI is running
        health = await self.check_ai_health(ai_id, socket_info)
        if not health.startswith("✓"):
            print(f"\n{ai_id} is not running")
            return
            
        print(f"\n═══ {ai_id} ═══")
        print(f"Component: {component.title()}")
        
        # Get component expertise from generic_specialist
        from shared.ai.generic_specialist import COMPONENT_EXPERTISE
        expertise = COMPONENT_EXPERTISE.get(component, {})  
        print(f"Description: {expertise.get('title', 'AI Specialist')}")
        
        # Get AI details
        details = await self.get_ai_info(ai_id, socket_info)
        model_name = self._get_display_model_name(details.get('model_name', 'unknown'))
        print(f"Model: {model_name} (via {details.get('model_provider', 'unknown').title()})")
        
        if details.get('system_prompt'):
            print(f"\nSystem Prompt:")
            prompt = details['system_prompt']
            # Show first 300 chars of prompt
            if len(prompt) > 300:
                prompt = prompt[:297] + "..."
            print(f"  {prompt}")
        
        print("═" * (len(ai_id) + 8))


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Show status of AI specialists for Tekton components',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    Show all AI specialists
  %(prog)s -c rhetor          Show AI for Rhetor component  
  %(prog)s -a rhetor-ai       Show specific AI by ID
  %(prog)s -f                 Show full details for all AIs
  %(prog)s -c apollo -f       Show full details for Apollo AI
        """
    )
    
    # Component/AI selection (interchangeable)
    parser.add_argument(
        '-c', '--component', '-a', '--ai',
        nargs='+',
        dest='components',
        help='Show specific components or AI IDs'
    )
    
    parser.add_argument(
        '-f', '--full',
        action='store_true',
        help='Show full details including system prompts'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '-j', '--json',
        action='store_true',
        help='Output in JSON format'
    )
    
    args = parser.parse_args()
    
    status = AIStatus(verbose=args.verbose)
    
    if args.json:
        data = {
            'ais': await status.get_ai_status(),
            'global_enabled': config.tekton.register_ai
        }
        print(json.dumps(data, indent=2))
    else:
        await status.display_status(show_full=args.full, components=args.components)


if __name__ == '__main__':
    asyncio.run(main())