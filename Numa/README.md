# Numa - Platform CI Mentor

Numa is the platform-wide CI mentor for Tekton, providing guidance and oversight across all components.

## Overview

Numa serves as a collaborative mentor and facilitator for the Tekton ecosystem:
- Provides platform-wide perspective and guidance
- Mentors users through Companion Chat
- Coordinates with other CI specialists via Team Chat
- Monitors overall system health and patterns
- Offers coaching and suggestions (not commands)

## Port Assignment

Numa runs on port **8016** (configurable via `NUMA_PORT` environment variable).

## Features

- **Companion Chat**: Direct interaction with users for platform guidance
- **Team Chat**: Communication with other CI specialists
- **Platform Monitoring**: Observes patterns across all components
- **Component Mentoring**: Provides guidance to individual component CIs

## Running Numa

```bash
# Basic startup
./run_numa.sh
```

## API Endpoints

- `GET /` - Component information
- `GET /health` - Health check for Hermes registration
- `POST /api/companion-chat` - User interaction endpoint
- `POST /api/team-chat` - CI team communication
- `GET /api/status` - Detailed component status

## Environment Variables

- `NUMA_PORT` - Port to run on (default: 8016)
- `HERMES_URL` - Hermes service URL (default: http://localhost:8001)
- `RHETOR_URL` - Rhetor service URL (default: http://localhost:8003)

## Architecture

Numa operates as a peer CI with platform-wide visibility:
- Read access to all component sockets
- Can communicate with any component AI
- Provides guidance through knowledge, not authority
- Facilitates cross-component collaboration

## Development Status

This is a bare-bones implementation. Future enhancements will include:
- Full CI specialist integration with fixed port system
- Hermes registration for service discovery
- Socket-based communication with other CIs
- Platform pattern analysis and insights
- Advanced mentoring behaviors
