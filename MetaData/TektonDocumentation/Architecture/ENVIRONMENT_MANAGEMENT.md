# Tekton Environment Management System

## Overview

Tekton now implements a comprehensive three-tier environment variable management system that provides clean separation between user settings, project configuration, and secrets.

## Three-Tier Architecture

### 1. `~/.env` - User-Wide Settings
- **Location**: User's home directory
- **Purpose**: Settings shared across all applications on the user's system
- **Examples**: User preferences, global tool configurations
- **Tracked**: No (personal user file)

### 2. `Tekton/.env.tekton` - Project Settings
- **Location**: Tekton project root directory
- **Purpose**: Project-specific configuration that can be shared with the team
- **Examples**: Component ports, theme settings, feature flags, debug settings
- **Tracked**: Yes (committed to git)
- **Contains**: All non-secret Tekton configuration

### 3. `Tekton/.env.local` - Local Secrets
- **Location**: Tekton project root directory  
- **Purpose**: Local secrets and API keys that should never be shared
- **Examples**: API keys, database URLs, personal overrides
- **Tracked**: No (gitignored)
- **Template**: `.env.local.template` provides structure

## Reading Priority

Environment variables are loaded in this order (later files override earlier ones):
1. System environment variables
2. `~/.env` (user-wide settings)
3. `Tekton/.env.tekton` (project settings)
4. `Tekton/.env.local` (local secrets)

## Implementation Components

### Core Components

#### `shared/utils/env_manager.py`
- **TektonEnvManager Class**: Handles three-tier environment loading and saving
- **Key Methods**:
  - `load_environment()`: Load all environment files in priority order
  - `save_tekton_settings()`: Save settings to .env.tekton
  - `get_tekton_variables()`: Get Tekton-specific environment variables
  - `get_component_port()`: Get component port from environment

#### `shared/utils/tekton_startup.py`
- **Component Startup Utilities**: Common startup functionality for components
- **Key Functions**:
  - `tekton_component_startup()`: Main startup function for components
  - `initialize_tekton_environment()`: Load environment with proper logging
  - `setup_component_logging()`: Configure logging based on environment
  - `get_component_port()`: Helper for component port discovery

### UI Integration

#### `Hephaestus/ui/scripts/settings/settings-env-bridge.js`
- **Settings Environment Bridge**: JavaScript interface to TektonEnvManager
- **Features**:
  - Syncs SettingsManager with environment variables
  - Provides Save/Load functionality for Settings UI
  - Automatic synchronization between UI and .env.tekton

#### Hephaestus Server API Endpoints
- **GET `/api/environment`**: Return all environment variables
- **GET `/api/environment/tekton`**: Return Tekton-specific variables
- **POST `/api/settings`**: Save settings to .env.tekton

### Component Integration

Components can integrate environment management by adding this to their main module:

```python
# At the beginning of component startup
try:
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "shared", "utils"))
    from tekton_startup import tekton_component_startup
    tekton_component_startup("component_name")
except ImportError:
    print("Could not load Tekton environment manager, using system environment")
```

## Environment Variables Reference

### UI Display Settings
- `SHOW_GREEK_NAMES`: Whether to show Greek names for components (true/false)

### Theme Settings  
- `TEKTON_THEME_MODE`: Theme mode ('dark' or 'light')
- `TEKTON_THEME_COLOR`: Theme color ('blue', 'green', or 'purple')

### Debug Settings
- `TEKTON_DEBUG`: Master debug switch (true/false)
- `TEKTON_LOG_LEVEL`: Logging level (TRACE, DEBUG, INFO, WARN, ERROR, FATAL, OFF)

### Component Ports (Single Port Architecture)
- `HEPHAESTUS_PORT`: 8080 (UI system)
- `ENGRAM_PORT`: 8000 (Memory system)
- `HERMES_PORT`: 8001 (Service registry & messaging)
- `ERGON_PORT`: 8002 (Agent system)
- `RHETOR_PORT`: 8003 (LLM management)
- `TERMA_PORT`: 8004 (Terminal system)
- `ATHENA_PORT`: 8005 (Knowledge graph)
- `PROMETHEUS_PORT`: 8006 (Planning system)
- `HARMONIA_PORT`: 8007 (Workflow system)
- `TELOS_PORT`: 8008 (Requirements system)
- `SYNTHESIS_PORT`: 8009 (Execution engine)
- `TEKTON_CORE_PORT`: 8010 (Core orchestration)
- `METIS_PORT`: 8011 (Task management)
- `APOLLO_PORT`: 8012 (Attention/Prediction)
- `BUDGET_PORT`: 8013 (Cost management)
- `SOPHIA_PORT`: 8014 (Machine learning)

### Specialized Ports
- `TERMA_WS_PORT`: 8767 (Terma WebSocket legacy)

### Terminal Settings
- `TEKTON_TERMINAL_MODE`: Terminal mode ('advanced' or 'simple')
- `TEKTON_TERMINAL_FONT_SIZE`: Font size in pixels (8-24)
- `TEKTON_TERMINAL_FONT_FAMILY`: Font family
- `TEKTON_TERMINAL_THEME`: Terminal theme
- `TEKTON_TERMINAL_CURSOR_STYLE`: Cursor style ('block', 'bar', 'underline')
- `TEKTON_TERMINAL_CURSOR_BLINK`: Cursor blink (true/false)
- `TEKTON_TERMINAL_SCROLLBACK`: Scrollback enabled (true/false)
- `TEKTON_TERMINAL_SCROLLBACK_LINES`: Scrollback lines

### Chat Settings
- `TEKTON_CHAT_HISTORY_ENABLED`: Chat history enabled (true/false)
- `TEKTON_CHAT_HISTORY_MAX_ENTRIES`: Maximum chat history entries

### Performance Settings
- `TEKTON_AUTO_LAUNCH`: Auto-launch components (true/false)
- `TEKTON_COMPONENT_TIMEOUT`: Component startup timeout (seconds)

### Integration Settings
- `TEKTON_MCP_ENABLED`: MCP integration enabled (true/false)
- `TEKTON_HERMES_DISCOVERY`: Hermes service discovery enabled (true/false)

### User Preferences
- `TEKTON_DEFAULT_MODEL`: Default LLM model
- `TEKTON_DEFAULT_PROVIDER`: Default LLM provider
- `TEKTON_NOTIFICATIONS_ENABLED`: Notifications enabled (true/false)

### Component Feature Flags
- `TEKTON_APOLLO_PREDICTIONS`: Apollo predictions enabled (true/false)
- `TEKTON_SOPHIA_ML`: Sophia ML features enabled (true/false)
- `TEKTON_BUDGET_TRACKING`: Budget tracking enabled (true/false)
- `TEKTON_ERGON_AUTOMATION`: Ergon automation enabled (true/false)

## Usage Examples

### For Component Developers

1. **Component Startup**:
```python
from shared.utils.tekton_startup import tekton_component_startup

# Load environment and configure logging
env_data = tekton_component_startup("mycomponent")
```

2. **Get Component Port**:
```python
from shared.utils.tekton_startup import get_component_port

port = get_component_port("mycomponent", default=8000)
```

3. **Check Settings**:
```python
from shared.utils.tekton_startup import get_tekton_bool_setting

debug_enabled = get_tekton_bool_setting("DEBUG")
```

### For Settings UI

1. **Load Settings from Environment**:
```javascript
await window.settingsEnvBridge.syncFromEnvironment();
```

2. **Save Settings to Environment**:
```javascript
await window.settingsEnvBridge.saveSettings();
```

### For Profile Management

The system is designed to be extended for Profile management with similar patterns for user-specific data that should be saved to .env.tekton.

## Security Considerations

- **Never commit .env.local**: Contains secrets and is gitignored
- **Review .env.tekton carefully**: Publicly visible, only non-secret configuration
- **Use proper variable naming**: TEKTON_ prefix for project settings
- **Template for secrets**: .env.local.template shows structure without exposing values

## Dependencies

- **Python**: `python-dotenv>=1.0.0` (already included in component requirements)
- **JavaScript**: No additional dependencies (uses fetch API)

## Migration Guide

For existing components:

1. Add environment loading to component startup (see Apollo example)
2. Replace hardcoded ports with environment variable lookups
3. Test component with new environment loading
4. Add component-specific environment variables to .env.tekton

The environment management system is backwards compatible - components will continue to work with existing environment variables while gaining the benefits of the three-tier system.
