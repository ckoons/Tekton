# Athena Auto-Population Guide

This guide describes how Athena automatically populates itself with Tekton component relationships during startup.

## Overview

Athena can automatically populate its knowledge graph with Tekton component relationships and dependencies when the system starts up. This ensures that Athena always has up-to-date information about the system architecture.

## Auto-Population Methods

### 1. Enhanced Launcher Integration (Default)

When using the enhanced Tekton launcher, Athena is automatically populated after all components are successfully started:

```bash
# Launch all components with auto-population (default)
python scripts/enhanced_tekton_launcher.py --launch-all

# Launch without auto-population
python scripts/enhanced_tekton_launcher.py --launch-all --no-populate-athena
```

The launcher will:
1. Start all components in dependency order
2. Wait for successful startup
3. Automatically run the `populate_athena_relationships.py` script
4. Log the results

### 2. Athena Self-Population

Athena can also populate itself during its own startup process. This is controlled by an environment variable:

```bash
# Enable auto-population (default)
export ATHENA_AUTO_POPULATE=true

# Disable auto-population
export ATHENA_AUTO_POPULATE=false
```

When enabled, Athena will:
1. Initialize itself normally
2. Wait 10 seconds for other components to start
3. Run the population script automatically
4. Log the results

### 3. Manual Population

You can manually populate Athena at any time using:

```bash
# Using the convenience script
./scripts/populate_athena.sh

# Or directly
python populate_athena_relationships.py
```

## What Gets Populated

The auto-population process creates:

1. **Component Entities**: Each Tekton component (Hermes, Apollo, Rhetor, etc.)
2. **Relationships**: Dependencies and integrations between components
3. **Metadata**: Ports, capabilities, categories, and descriptions
4. **Integration Points**: How components interact with each other

## Configuration

### Environment Variables

- `ATHENA_AUTO_POPULATE`: Enable/disable Athena self-population (default: true)
- `ATHENA_API`: API endpoint for Athena (default: http://localhost:8005/api/v1)

### Launcher Options

- `--no-populate-athena`: Skip automatic population when using the launcher

## Troubleshooting

### Population Fails

If auto-population fails:

1. Check that Athena is running and healthy:
   ```bash
   curl http://localhost:8005/health
   ```

2. Check the logs:
   ```bash
   tail -f .tekton/logs/athena.log
   ```

3. Run manual population with verbose output:
   ```bash
   python populate_athena_relationships.py
   ```

### Missing Components

The population script is resilient and will:
- Skip components that fail to create
- Continue with other components
- Log any errors encountered

### Duplicate Entities

The population script checks for existing entities and:
- Updates existing component entities
- Preserves manual modifications
- Only creates new relationships if they don't exist

## Best Practices

1. **Use Auto-Population**: Let the system handle population automatically
2. **Manual Updates**: Use Athena's API for custom entities and relationships
3. **Verify Population**: Check Athena's UI or API to confirm successful population
4. **Monitor Logs**: Watch for population errors in component logs

## API Verification

After population, verify the data:

```bash
# List all components
curl http://localhost:8005/api/v1/entities?type=component

# Get component relationships
curl http://localhost:8005/api/v1/entities/{component_id}/relationships

# Query the knowledge graph
curl -X POST http://localhost:8005/api/v1/query/search \
  -H "Content-Type: application/json" \
  -d '{"query": "component", "limit": 20}'
```