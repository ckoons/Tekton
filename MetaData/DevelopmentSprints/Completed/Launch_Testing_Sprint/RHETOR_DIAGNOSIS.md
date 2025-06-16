# Rhetor Launch Issue Diagnosis

## Issue Overview

When launching Rhetor using the `tekton-launch` script, the following error occurs:
```
Error starting rhetor server: name 'component_dir' is not defined
```

## Investigation Findings

1. **Debug Script Results**
   - Rhetor app can be imported successfully
   - The app.py module contains a `start_server` function
   - The FastAPI app object is accessible
   - There are no predefined HOST or PORT configurations in the app module

2. **Launch Mechanism**
   - Rhetor is launched via `launch_component "rhetor" "Rhetor LLM Management System" "$RHETOR_DIR" "rhetor.api.app" "$RHETOR_PORT"`
   - This calls `tekton_start_component_server` which then constructs a Python script to start the server

3. **Error Cause**
   - The error occurs when executing the dynamically generated Python code in `tekton_start_component_server`
   - The issue is in the `from {module} import start_server` line where `{component_dir}` is not properly passed to the f-string
   - The component directory is properly defined in `tekton_start_component_server` but not correctly passed to the inner subprocess

4. **Port Mismatch**
   - The scripts attempt to run Rhetor on port 8003 (`$RHETOR_PORT`)
   - Previous successful runs show Rhetor running on port 8300
   - This inconsistency should be addressed in configurations

## Recommended Fixes

1. **Fix the Component Directory Variable**
   - The issue is in `tekton-process.sh` line 227-230:
   ```python
   server_process = subprocess.Popen(
       [sys.executable, '-c', f'''
   import sys, asyncio
   sys.path.insert(0, '{component_dir}')
   ```
   - The Python code uses an f-string, but the outer Python context doesn't properly escape the inner f-string, causing the variable to be undefined

   **Proposed fix:**
   ```python
   server_process = subprocess.Popen(
       [sys.executable, '-c', '''
   import sys, asyncio
   sys.path.insert(0, '{}'')'''.format(component_dir)
   ```

2. **Port Standardization**
   - Update Rhetor's configuration to consistently use port 8003
   - Modify the `start_server` function to accept port as an argument
   - Ensure all components use the standard ports defined in `tekton-ports.sh`

## Rhetor Launch Analysis

The debug script confirmed that Rhetor itself is functioning correctly, with both the module and the start_server function being accessible. The issue is in the launch script's handling of the component directory variable in the nested Python code.

A common pattern when working with nested code generation is to ensure all variables are properly passed and escaped. The issue here is a classic problem with nested string interpolation where variables from an outer scope aren't properly passed to an inner scope.

Once this issue is fixed, Rhetor should launch successfully using the standard port configuration.