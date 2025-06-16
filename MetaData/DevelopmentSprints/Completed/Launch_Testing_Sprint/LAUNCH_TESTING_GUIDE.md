# Tekton Launch Testing Guide

This guide provides instructions for testing Tekton component launches and troubleshooting common issues. It's intended to help developers verify that their components work correctly within the Tekton ecosystem.

## Prerequisites

- All components should be properly installed
- The Tekton scripts directory should be in your PATH
- Python 3.9+ should be installed

## Testing Component Launches

### 1. Individual Component Launch Testing

To test launching an individual component:

```bash
# Change to the component directory
cd /path/to/component

# Run the component's launch script
./run_component.sh
```

For components that don't have a dedicated launch script, use the `tekton-launch` script:

```bash
tekton-launch --components component_name
```

### 2. Component Port Verification

Verify that each component uses the correct port according to the Single Port Architecture:

| Component | Expected Port | Environment Variable |
|-----------|---------------|----------------------|
| Hephaestus UI | 8080 | `HEPHAESTUS_PORT` |
| Engram | 8000 | `ENGRAM_PORT` |
| Hermes | 8001 | `HERMES_PORT` |
| Ergon | 8002 | `ERGON_PORT` |
| Rhetor | 8003 | `RHETOR_PORT` |
| Terma | 8004 | `TERMA_PORT` |
| Athena | 8005 | `ATHENA_PORT` |
| Prometheus | 8006 | `PROMETHEUS_PORT` |
| Harmonia | 8007 | `HARMONIA_PORT` |
| Telos | 8008 | `TELOS_PORT` |
| Synthesis | 8009 | `SYNTHESIS_PORT` |
| Tekton Core | 8010 | `TEKTON_CORE_PORT` |

Check that the port is active and the service is responding:

```bash
# Check if port is in use
lsof -i :PORT_NUMBER

# Test health endpoint
curl http://localhost:PORT_NUMBER/health
```

### 3. Hermes Registration Testing

Verify that components can register with Hermes:

```bash
# Start Hermes first
tekton-launch --components hermes

# Check Hermes is running
curl http://localhost:8001/api/health

# Start the component to test
tekton-launch --components component_name

# Verify component registration
curl http://localhost:8001/api/registry/services
```

### 4. Multi-Component Launch Testing

Test launching multiple components together:

```bash
# Launch core components
tekton-launch --components hermes,engram,rhetor

# Check status
tekton-status

# Launch additional components
tekton-launch --components component_name
```

### 5. Component Shutdown Testing

Test that components can be shut down cleanly:

```bash
# Shut down specific components
./tekton-kill component_name

# Shut down all components
./tekton-kill
```

## Common Issues and Solutions

### Port Already in Use

**Issue**: Component fails to start because the port is already in use.

**Solution**:
1. Check what process is using the port:
   ```bash
   lsof -i :PORT_NUMBER
   ```
2. Terminate the process:
   ```bash
   kill -9 PID
   ```
3. Or use the port release utility:
   ```bash
   tekton-kill clean_ports
   ```

### Component Directory Issues

**Issue**: Component fails to start because it can't find its own files.

**Solution**:
1. Ensure you're running the script from the component's directory
2. Check if the component has relative path references:
   ```bash
   grep -r "os.path.join" --include="*.py" .
   ```
3. Update paths to use absolute paths with the component's directory

### Hermes Connection Failures

**Issue**: Component fails to register with Hermes.

**Solution**:
1. Ensure Hermes is running and its port is accessible:
   ```bash
   curl http://localhost:8001/api/health
   ```
2. Check for Hermes URL configuration issues in the component
3. Verify that the component's registration parameters are correct

### Import Errors

**Issue**: Component fails to start due to import errors.

**Solution**:
1. Check Python path issues:
   ```bash
   echo $PYTHONPATH
   ```
2. Install missing dependencies:
   ```bash
   pip install -e .
   ```
3. Check for version conflicts between dependencies

### Process Termination Problems

**Issue**: `tekton-kill` terminates unintended processes.

**Solution**:
1. Use more specific patterns in `tekton_kill_processes_safe`
2. Add exclusion patterns for protected processes
3. Check for orphaned processes that might match kill patterns

## Implementing Launch Testing for a New Component

When implementing a new component, follow these steps for launch testing:

1. **Port Configuration**:
   - Assign the appropriate port based on the Single Port Architecture
   - Implement the standardized `port_config.py` utility
   - Use environment variables for all port references

2. **Health Endpoint**:
   - Implement a `/health` endpoint that returns component status
   - Include version, uptime, and dependency information

3. **Hermes Registration**:
   - Register with Hermes during startup
   - Include component capabilities in the registration
   - Handle registration failures gracefully

4. **Launch Script**:
   - Create a standardized launch script (`run_component.sh`)
   - Include port configuration and Python path setup
   - Add proper error handling and logging

5. **Graceful Shutdown**:
   - Handle SIGTERM and SIGINT signals properly
   - Close resources and connections cleanly
   - Unregister from Hermes during shutdown

## Testing Script

Here's a simple script to test launching and stopping a component:

```bash
#!/bin/bash
# test_component_launch.sh

COMPONENT=$1
echo "Testing launch for component: $COMPONENT"

# Start component
echo "Starting $COMPONENT..."
tekton-launch --components $COMPONENT

# Wait for component to initialize
sleep 5

# Check if component is running
tekton-status | grep $COMPONENT

# Test health endpoint
COMPONENT_PORT=$(tekton-status | grep $COMPONENT | grep -o "Port [0-9]* " | awk '{print $2}')
echo "Testing health endpoint on port $COMPONENT_PORT..."
curl -s http://localhost:$COMPONENT_PORT/health

# Stop component
echo "Stopping $COMPONENT..."
tekton-kill $COMPONENT

# Verify component has stopped
tekton-status | grep $COMPONENT

echo "Test complete for $COMPONENT"
```

Usage:
```bash
./test_component_launch.sh component_name
```

## Conclusion

Proper launch testing is essential for ensuring that Tekton components work correctly together. By following this guide, you can verify that your components are correctly integrated into the Tekton ecosystem and can be launched, stopped, and managed reliably.

Remember to run these tests regularly, especially after making significant changes to a component's structure or dependencies.