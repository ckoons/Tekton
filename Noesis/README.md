# Noesis - Discovery System

Noesis is the discovery and insight generation system for Tekton, finding patterns and connections across the ecosystem.

## Overview

Noesis serves as the pattern recognition and discovery engine:
- Discovers hidden patterns across components
- Generates insights from system behavior
- Provides discovery chat for exploration
- Coordinates discoveries via Team Chat
- Identifies optimization opportunities

## Port Assignment

Noesis runs on port **8015** (configurable via `NOESIS_PORT` environment variable).

## Features

- **Discovery Chat**: Interactive pattern and insight discovery
- **Team Chat**: Share discoveries with other CI specialists
- **Pattern Recognition**: Identify recurring patterns (future)
- **Insight Generation**: Generate actionable insights (future)

## Running Noesis

```bash
# Basic startup
./run_noesis.sh
```

## API Endpoints

- `GET /` - Component information
- `GET /health` - Health check for Hermes registration
- `POST /api/discovery-chat` - Pattern discovery endpoint
- `POST /api/team-chat` - CI team communication
- `GET /api/status` - Detailed component status

## Environment Variables

- `NOESIS_PORT` - Port to run on (default: 8015)
- `HERMES_URL` - Hermes service URL (default: http://localhost:8001)
- `RHETOR_URL` - Rhetor service URL (default: http://localhost:8003)

## Architecture

Noesis operates as a specialized discovery system:
- Analyzes patterns across all components
- Identifies optimization opportunities
- Generates insights from system behavior
- Shares discoveries with other CIs

## Development Status

This is a bare-bones implementation serving as a placeholder for future discovery capabilities:
- Full pattern recognition engine to be implemented
- Machine learning integration planned
- Advanced insight generation algorithms
- Cross-component correlation analysis