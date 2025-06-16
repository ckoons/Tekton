# Rhetor Process Group Implementation

## Overview

This implementation ensures that Rhetor and all its child AI processes can be cleanly terminated with a single command. When Rhetor spawns AI model processes, they all belong to the same process group, allowing `tekton-kill` to terminate them all at once.

## Components

### 1. Enhanced Launch Script (`run_rhetor_fixed.sh`)

Key features:
- Uses `setsid` to create Rhetor as a process group leader
- Stores the process group ID (PGID) in `~/.tekton/pids/rhetor.pgid`
- Implements proper signal handling to terminate the entire process group
- Two-stage shutdown: graceful (SIGTERM) then forced (SIGKILL) if needed

### 2. Process Manager (`rhetor/core/process_manager.py`)

Python-side process management:
- Tracks all spawned AI model processes
- Ensures children stay in the same process group
- Handles graceful shutdown when Rhetor receives signals
- Provides process statistics and monitoring

### 3. Model Spawner (`rhetor/core/model_spawner.py`)

Example implementation showing how to:
- Spawn individual AI models as child processes
- Create pools of models for load balancing
- Pass environment variables and configuration
- Monitor resource usage of child processes

## Usage

### Starting Rhetor with Process Group Support

```bash
# Use the new script
./run_rhetor_fixed.sh

# This creates a process group with Rhetor as the leader
# The PGID is stored in ~/.tekton/pids/rhetor.pgid
```

### Spawning AI Models from Rhetor

```python
from rhetor.core.model_spawner import AIModelSpawner

spawner = AIModelSpawner()

# Spawn a single model
llama = spawner.spawn_model("llama")

# Spawn a pool of models
codellama_pool = spawner.spawn_model_pool("codellama", count=3)

# All these processes are now part of Rhetor's process group
```

### Terminating Everything

When `tekton-kill` runs:
1. It reads the PGID from `~/.tekton/pids/rhetor.pgid`
2. Sends SIGTERM to the entire process group: `kill -TERM -$PGID`
3. All processes (Rhetor + all AI models) receive the signal
4. Rhetor's ProcessManager handles graceful shutdown of children
5. If any processes don't terminate gracefully, they're force killed

## Benefits

1. **Clean Termination**: One signal terminates everything
2. **No Orphans**: Child processes can't outlive Rhetor
3. **Graceful Shutdown**: AI models get a chance to clean up
4. **Resource Tracking**: Monitor all spawned processes
5. **Scalable**: Works whether Rhetor spawns 1 or 100 child processes

## Integration with tekton-kill

To update `tekton-kill` to use process groups:

```python
def kill_component(component_name):
    # Check for PGID file first
    pgid_file = f"{HOME}/.tekton/pids/{component_name}.pgid"
    if os.path.exists(pgid_file):
        with open(pgid_file) as f:
            pgid = int(f.read().strip())
        # Kill entire process group
        os.killpg(pgid, signal.SIGTERM)
    else:
        # Fall back to current PID-based approach
        kill_by_pid(component_name)
```

## Migration Path

1. Test with `run_rhetor_fixed.sh` first
2. Once verified, replace `run_rhetor.sh` with the fixed version
3. Update other components that may spawn children similarly
4. Update `tekton-kill` to prefer PGID files when available