# Tekton Shared Utilities Examples

This directory contains examples of using the Tekton shared utilities.

## Demo Script

The `shared-utils-demo.sh` script demonstrates how to use the Tekton shared utilities to implement a component startup script. It shows:

- Loading shared utilities
- Detecting the Tekton root directory
- Parsing command-line arguments
- Working with configuration
- Managing ports
- Starting and stopping processes
- Registering with Hermes

To run the demo:

```bash
./shared-utils-demo.sh
```

## Example Component Script

The following is an example of a simple component startup script using shared utilities:

```bash
#!/usr/bin/env bash
# example-component.sh - Example component startup script

# Find Tekton root directory and script directories
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TEKTON_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Load shared libraries
LIB_DIR="${TEKTON_ROOT}/scripts/lib"
source "${LIB_DIR}/tekton-utils.sh"
source "${LIB_DIR}/tekton-ports.sh"
source "${LIB_DIR}/tekton-process.sh"
source "${LIB_DIR}/tekton-config.sh"

# Define component details
COMPONENT_ID="example-component"
COMPONENT_PORT=8123

# Parse arguments
tekton_parse_args "$@"

# Check configuration
PORT=$(tekton_get_config "port" "$COMPONENT_PORT")

# Check if port is available
if tekton_is_port_used "$PORT"; then
    tekton_release_port "$PORT" "$COMPONENT_ID"
fi

# Register with Hermes
tekton-register register --component "$COMPONENT_ID" &
REGISTER_PID=$!

# Start the component
tekton_start_component_server "$COMPONENT_ID" "example.api.app" "$TEKTON_ROOT/Example" "$PORT"

# Set up signal handlers
trap cleanup SIGTERM SIGINT

cleanup() {
    # Kill processes
    tekton_kill_processes "example.api.app" "$COMPONENT_ID"
    
    # Unregister from Hermes
    kill $REGISTER_PID 2>/dev/null || true
    tekton-register unregister --component "$COMPONENT_ID"
    
    exit 0
}

# Wait forever
while true; do
    sleep 1
done
```

## Component Registration Example

This example shows how to use the component registration utilities:

```bash
#!/usr/bin/env bash
# register-component.sh - Example component registration script

# Register component with Hermes
tekton-register register --component my-component
```

You can also use the Python API directly:

```python
#!/usr/bin/env python3
# register_component.py - Example component registration script

import asyncio
from tekton.utils.registration import (
    load_component_config,
    register_component,
    unregister_component,
    get_registration_status
)

async def main():
    # Load component configuration
    config = load_component_config("my-component")
    
    # Register component
    success, client = await register_component("my-component", config)
    
    if success:
        print("Component registered successfully")
        
        # Wait for signals
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            pass
        
        # Unregister when done
        await client.unregister()
        await client.close()
    else:
        print("Failed to register component")

if __name__ == "__main__":
    asyncio.run(main())
```

## Additional Examples

For more examples, see:

- `scripts/tekton-launch-new`: Example of using shared utilities in a complex script
- `scripts/tekton-status-new`: Example of checking component status
- `scripts/tekton-kill-new`: Example of process management
- `scripts/lib/test-utils.sh`: Test script for shared utilities