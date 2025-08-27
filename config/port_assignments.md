# Tekton Port Assignments

This document defines the standardized port assignments for all Tekton components following the Single Port Architecture pattern.

## Single Port Architecture

Tekton uses a Single Port Architecture where each component exposes its services through a single port number, using path-based routing to differentiate between HTTP, WebSocket, and Event endpoints.

## Port Assignments

| Component      | Port | Description                               | Environment Variable   |
|----------------|------|-------------------------------------------|------------------------|
| Hephaestus UI  | 8080 | UI system (using standard web port)       | `HEPHAESTUS_PORT`      |
| Engram         | 8000 | Memory system                             | `ENGRAM_PORT`          |
| Hermes         | 8001 | Service registry & messaging              | `HERMES_PORT`          |
| Ergon          | 8002 | Agent system                              | `ERGON_PORT`           |
| Rhetor         | 8003 | LLM management                            | `RHETOR_PORT`          |
| Terma          | 8004 | Terminal system                           | `TERMA_PORT`           |
| Athena         | 8005 | Knowledge graph                           | `ATHENA_PORT`          |
| Prometheus     | 8006 | Planning system                           | `PROMETHEUS_PORT`      |
| Harmonia       | 8007 | Workflow system                           | `HARMONIA_PORT`        |
| Telos          | 8008 | Requirements system                       | `TELOS_PORT`           |
| Synthesis      | 8009 | Execution engine                          | `SYNTHESIS_PORT`       |
| Tekton Core    | 8010 | Core orchestration                        | `TEKTON_CORE_PORT`     |
| Metis          | 8011 | Task management system                    | `METIS_PORT`           |
| Apollo         | 8012 | Local Insight system         | `APOLLO_PORT`          |
| Penia          | 8013 | Token/cost management system              | `PENIA_PORT`           |
| Sophia         | 8014 | Machine learning system                   | `SOPHIA_PORT`          |
| Noesis         | 8015 | Discovery CI system                       | `NOESIS_PORT`          |
| Numa           | 8016 | Platform CI mentor                        | `NUMA_PORT`            |

## Specialized Services

Some components may use additional ports for specialized services:

| Service        | Port | Description                               | Environment Variable   |
|----------------|------|-------------------------------------------|------------------------|

## Usage

Components should reference these environment variables rather than hardcoding port numbers. The environment variables are automatically set by the `tekton-launch` script and can be overridden as needed.

```bash
# Example: Starting a component with a standard port
uvicorn myapp:app --host 0.0.0.0 --port $COMPONENT_PORT
```

## URL Construction

Components should construct URLs using the following patterns:

- HTTP API: `http://hostname:port/api/...`
- WebSocket: `ws://hostname:port/ws/...`
- Events: `http://hostname:port/events/...`
- Health Check: `http://hostname:port/health`

## Port Configuration

The standard ports can be modified by:

1. Setting environment variables before launching components
2. Using the `--port` argument when launching components
3. Editing the Tekton configuration file
