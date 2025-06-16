"""Entry point for python -m engram"""
import os
import sys
import argparse

# Add Tekton root to path if not already present
tekton_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if tekton_root not in sys.path:
    sys.path.insert(0, tekton_root)

from shared.utils.socket_server import run_component_server
from shared.utils.global_config import GlobalConfig

if __name__ == "__main__":
    # Parse arguments to check for standalone mode
    parser = argparse.ArgumentParser(description="Engram Memory Service")
    parser.add_argument("--standalone", action="store_true", 
                        help="Run in standalone MCP mode without Hermes integration")
    parser.add_argument("--client-id", default="default",
                        help="Client ID for standalone mode")
    parser.add_argument("--data-dir", default=None,
                        help="Data directory for standalone mode")
    args, remaining_args = parser.parse_known_args()
    
    if args.standalone or os.environ.get("ENGRAM_STANDALONE_MODE", "").lower() == "true":
        # Run in standalone FastMCP mode
        from engram.api.fastmcp_server import main as fastmcp_main
        # Restore sys.argv for fastmcp_server to parse
        sys.argv = [sys.argv[0]] + remaining_args
        if args.client_id:
            sys.argv.extend(["--client-id", args.client_id])
        if args.data_dir:
            sys.argv.extend(["--data-dir", args.data_dir])
        fastmcp_main()
    else:
        # Run in Tekton integrated mode
        global_config = GlobalConfig.get_instance()
        default_port = global_config.config.engram.port
        
        run_component_server(
            component_name="engram",
            app_module="engram.api.server",
            default_port=default_port,
            reload=False
        )