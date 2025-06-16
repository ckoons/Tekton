# Apollo ~/.tekton Directory Usage Analysis

## Summary

Apollo uses the `~/.tekton/apollo` directory as its default data storage location. This can be overridden by setting the `APOLLO_DATA_DIR` environment variable.

## Directory Structure

```
~/.tekton/apollo/
├── context_data/      # Context monitoring data
├── prediction_data/   # Predictive engine data
├── action_data/       # Action planning data
├── message_data/      # Message handler data
├── protocol_data/     # Protocol enforcement data
└── budget_data/       # Token budget management data
```

## Usage by Component

### 1. ApolloManager (apollo_manager.py)
- **Line 97**: `self.data_dir = data_dir or os.path.expanduser("~/.tekton/apollo")`
- **Purpose**: Root data directory for all Apollo components
- **Creates**: Main directory and all subdirectories

### 2. ContextObserver (context_observer.py)
- **Line 60**: `self.data_dir = data_dir or os.path.expanduser("~/.tekton/apollo/context_data")`
- **Purpose**: Store context monitoring history
- **Files Created**: 
  - `{context_id}_{timestamp}.json` - Context history snapshots
  - Contains: Context state history, metrics, health status changes

### 3. PredictiveEngine (predictive_engine.py)
- **Line 645**: `self.data_dir = data_dir or os.path.expanduser("~/.tekton/apollo/prediction_data")`
- **Purpose**: Store prediction data and models
- **Files Created**: Prediction history and model state (implementation pending)

### 4. ActionPlanner (action_planner.py)
- **Line 512**: `self.data_dir = data_dir or os.path.expanduser("~/.tekton/apollo/action_data")`
- **Purpose**: Store action planning history
- **Files Created**:
  - `{context_id}_{timestamp}.json` - Action history for each context
  - Contains: Actions taken, priorities, timestamps, application status

### 5. MessageHandler (message_handler.py)
- **Line 378**: `self.data_dir = data_dir or os.path.expanduser("~/.tekton/apollo/message_data")`
- **Purpose**: Store message delivery records
- **Files Created**:
  - `delivery_records_{timestamp}.json` - Message delivery history
  - Contains: Message IDs, recipients, delivery status, timestamps

### 6. ProtocolEnforcer (protocol_enforcer.py)
- **Line 372**: `self.data_dir = data_dir or os.path.expanduser("~/.tekton/apollo/protocol_data")`
- **Purpose**: Store protocol definitions and violation logs
- **Files Created**:
  - `protocols/{protocol_id}.json` - Protocol definition files
  - `violations_{timestamp}.json` - Protocol violation logs
  - `protocol_stats.json` - Protocol usage statistics

### 7. TokenBudgetManager (token_budget.py)
- **Line 104**: `self.data_dir = data_dir or os.path.expanduser("~/.tekton/apollo/budget_data")`
- **Purpose**: Store token usage records
- **Files Created**:
  - `usage_records_{timestamp}.json` - Token usage history
  - Contains: Model usage, token counts, costs, timestamps

## API Server (app.py)
- **Line 136**: `data_dir = os.environ.get("APOLLO_DATA_DIR", os.path.expanduser("~/.tekton/apollo"))`
- **Purpose**: Initialize data directories on startup
- **Note**: Respects `APOLLO_DATA_DIR` environment variable

## Code Patterns Used

1. **Default with Override**:
   ```python
   self.data_dir = data_dir or os.path.expanduser("~/.tekton/apollo/component_data")
   ```

2. **Directory Creation**:
   ```python
   os.makedirs(self.data_dir, exist_ok=True)
   ```

3. **File Naming**:
   - Safe ID creation: `safe_id = context_id.replace("/", "_").replace(":", "_")`
   - Timestamped files: `f"{safe_id}_{int(time.time())}.json"`

4. **File Operations**:
   ```python
   with open(filename, "w") as f:
       json.dump(data, f, indent=2, default=str)
   ```

## Data Retention

Currently, Apollo creates timestamped files for historical data but does not implement automatic cleanup. This could lead to disk space issues over time.

## Environment Variable Override

The data directory can be overridden by setting:
```bash
export APOLLO_DATA_DIR=/custom/path/to/apollo/data
```

This is checked in the API server startup (app.py, line 136).