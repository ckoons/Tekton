#!/usr/bin/env bash
# shared-utils-demo.sh - Demo script for Tekton shared utilities
#
# This script demonstrates how to use the Tekton shared utilities
# to implement a component startup script.
#

# Find Tekton root directory and script directories
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TEKTON_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Load shared libraries
LIB_DIR="${TEKTON_ROOT}/scripts/lib"
source "${LIB_DIR}/tekton-utils.sh"
source "${LIB_DIR}/tekton-ports.sh"
source "${LIB_DIR}/tekton-process.sh"
source "${LIB_DIR}/tekton-config.sh"

# Enable debug mode
tekton_enable_debug

# Define component details
COMPONENT_ID="demo-component"
COMPONENT_NAME="Demo Component"
COMPONENT_PORT=8765

# Display banner
tekton_info "====== Tekton Shared Utilities Demo ======"
tekton_info "Demo component: ${COMPONENT_NAME}"
tekton_info "Using utilities from: ${LIB_DIR}"
echo ""

# Parse arguments
tekton_info "Parsing arguments..."
tekton_parse_args "$@"

# Check configuration
tekton_info "Checking configuration..."
PORT=$(tekton_get_config "port" "$COMPONENT_PORT")
tekton_success "Using port: $PORT"

# Check if port is available
tekton_info "Checking if port is available..."
if tekton_is_port_used "$PORT"; then
    tekton_warn "Port $PORT is in use"
    
    # Get the process using this port
    PROCESS_INFO=$(tekton_get_port_process "$PORT")
    if [ -n "$PROCESS_INFO" ]; then
        tekton_warn "Process using port $PORT: $PROCESS_INFO"
    fi
    
    # Ask if we should release the port
    if tekton_prompt_yes_no "Release port $PORT?" "y"; then
        tekton_release_port "$PORT" "$COMPONENT_NAME"
    else
        tekton_error_exit "Port $PORT is in use and cannot be released"
    fi
else
    tekton_success "Port $PORT is available"
fi

# Create a simple HTTP server to demonstrate process management
tekton_info "Creating a simple HTTP server..."
SERVER_SCRIPT="/tmp/tekton_demo_server.py"

# Create server script
cat > "$SERVER_SCRIPT" << 'PYTHON'
#!/usr/bin/env python3
import http.server
import socketserver
import sys
import os
import signal

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8765

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            # Health check endpoint
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "healthy"}')
        else:
            # Default response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<html><body><h1>Tekton Demo Server</h1><p>This is a demo server for the Tekton shared utilities.</p></body></html>')

    def log_message(self, format, *args):
        # Suppress logging
        pass

def signal_handler(sig, frame):
    print("Shutting down...")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Start the server
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at port {PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down...")
        httpd.server_close()
PYTHON

# Make script executable
chmod +x "$SERVER_SCRIPT"

# Start the server
tekton_info "Starting HTTP server on port $PORT..."
SERVER_PID=$(tekton_start_python_script "$SERVER_SCRIPT" "Demo HTTP Server" "$PORT")

if [ -n "$SERVER_PID" ]; then
    tekton_success "Server started with PID $SERVER_PID"
    
    # Wait for server to start responding
    tekton_info "Waiting for server to start responding..."
    if tekton_wait_for_port_responding "$PORT" 10 "Demo HTTP Server"; then
        tekton_success "Server is now responding"
        
        # Create a dummy YAML configuration for demonstration
        tekton_info "Creating component configuration..."
        CONFIG_DIR="/tmp/tekton_demo"
        mkdir -p "$CONFIG_DIR"
        CONFIG_FILE="$CONFIG_DIR/$COMPONENT_ID.yaml"
        
        cat > "$CONFIG_FILE" << YAML
component:
  id: $COMPONENT_ID
  name: $COMPONENT_NAME
  version: 0.1.0
  description: Demonstration of Tekton shared utilities
  port: $PORT

capabilities:
  - id: demo_capability
    name: Demo Capability
    description: A demonstration capability
    methods:
      - id: demo_method
        name: Demo Method
        description: A demonstration method
        parameters:
          - name: param_name
            type: string
            required: true
            description: A demonstration parameter
        returns:
          type: object
          description: A demonstration return value

config:
  demo_config_key: demo_value
YAML
        
        tekton_success "Component configuration created at $CONFIG_FILE"
        
        # Register with Hermes (if available)
        tekton_info "Checking if Hermes is available..."
        if tekton_is_port_responding "$HERMES_PORT" "localhost" "/api/health"; then
            tekton_success "Hermes is available, registering component..."
            "${TEKTON_ROOT}/scripts/tekton-register" status --component "$COMPONENT_ID"
            
            # Only continue registration if user confirms
            if tekton_prompt_yes_no "Register component with Hermes?" "y"; then
                tekton_info "Registering component with Hermes..."
                "${TEKTON_ROOT}/scripts/tekton-register" register --component "$COMPONENT_ID" --config "$CONFIG_FILE" &
                REGISTER_PID=$!
                
                # Give it a moment to register
                sleep 2
                
                # Check registration status
                tekton_info "Checking registration status..."
                "${TEKTON_ROOT}/scripts/tekton-register" status --component "$COMPONENT_ID"
            fi
        else
            tekton_warn "Hermes is not available, skipping registration"
        fi
        
        # Ask how long to run the server
        DURATION=$(tekton_prompt_with_default "How many seconds should the server run?" "30")
        
        # Run for the specified duration
        tekton_info "Server will run for $DURATION seconds"
        tekton_info "You can access it at: http://localhost:$PORT"
        tekton_info "Health check: http://localhost:$PORT/health"
        
        # Wait for the duration
        sleep "$DURATION"
        
        # Kill the server process
        tekton_info "Shutting down server..."
        tekton_kill_processes "$SERVER_SCRIPT" "Demo HTTP Server"
        
        # Unregister from Hermes (if registered)
        if [ -n "${REGISTER_PID:-}" ]; then
            tekton_info "Unregistering component from Hermes..."
            kill "$REGISTER_PID" 2>/dev/null || true
            "${TEKTON_ROOT}/scripts/tekton-register" unregister --component "$COMPONENT_ID"
        fi
        
        # Clean up temporary files
        tekton_info "Cleaning up temporary files..."
        rm -f "$SERVER_SCRIPT"
        rm -rf "$CONFIG_DIR"
        
        tekton_success "Demo completed successfully"
    else
        tekton_error_exit "Server failed to start responding"
    fi
else
    tekton_error_exit "Failed to start HTTP server"
fi

echo ""
tekton_info "====== Tekton Shared Utilities Demo Complete ======"