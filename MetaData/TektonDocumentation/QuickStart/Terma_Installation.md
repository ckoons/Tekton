# Terma Installation Guide

This guide provides instructions for installing, configuring, and running the Terma terminal system in various environments.

## System Requirements

Before installing Terma, ensure your system meets the following requirements:

- **Python**: 3.8 or higher
- **Operating System**: Linux, macOS, or Windows with WSL (Windows Subsystem for Linux)
- **Dependencies**: 
  - FastAPI and Uvicorn
  - Websockets
  - Ptyprocess (for terminal emulation)
  - Additional Python packages listed in requirements.txt

## Basic Installation

### Option 1: Standard Installation

```bash
# Clone the Tekton repository (if you haven't already)
git clone https://github.com/yourusername/Tekton.git
cd Tekton/Terma

# Run the setup script
./setup.sh
```

The setup script:
1. Creates a virtual environment
2. Installs required dependencies
3. Registers Terma with Hermes (optional)
4. Sets up configuration files

### Option 2: Manual Installation

If you prefer to install manually:

```bash
# Clone the Tekton repository (if you haven't already)
git clone https://github.com/yourusername/Tekton.git
cd Tekton/Terma

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
pip install -r requirements.txt
```

## Configuration

### Environment Variables

Terma can be configured using the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `TERMA_PORT` | HTTP API port | 8765 |
| `TERMA_WS_PORT` | WebSocket server port | 8767 |
| `TERMA_HOST` | Host interface to bind to | 0.0.0.0 |
| `REGISTER_WITH_HERMES` | Register with Hermes on startup | false |
| `HERMES_API_URL` | Hermes API URL | http://localhost:8000 |
| `TERMA_LOG_LEVEL` | Logging level | INFO |
| `TERMA_CONFIG_PATH` | Path to configuration file | None |

### Configuration File

For more advanced configuration, you can create a configuration file. By default, Terma looks for a configuration file in the following locations:

1. Path specified in `TERMA_CONFIG_PATH` environment variable
2. `~/.terma/config.json`
3. `/etc/terma/config.json`

Example configuration file (`config.json`):

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8765,
    "ws_port": 8767
  },
  "session": {
    "cleanup_interval": 3600,
    "idle_timeout": 86400,
    "default_shell": "/bin/bash"
  },
  "llm": {
    "adapter_url": "http://localhost:8300",
    "adapter_ws_url": "ws://localhost:8300/ws",
    "provider": "claude",
    "model": "claude-3-sonnet-20240229",
    "system_prompt": "You are a terminal assistant that helps users with command-line tasks."
  },
  "hermes": {
    "api_url": "http://localhost:8000",
    "register_on_startup": false
  },
  "logging": {
    "level": "INFO",
    "file": "/var/log/terma/terma_server.log"
  }
}
```

## Running Terma

### Starting the Terma Server

```bash
# Activate the virtual environment (if using one)
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Start the server
python -m terma.cli.main
```

To run with custom configuration:

```bash
# Using environment variables
TERMA_PORT=9000 TERMA_WS_PORT=9001 python -m terma.cli.main

# Or using a config file
TERMA_CONFIG_PATH=/path/to/config.json python -m terma.cli.main
```

### Verifying Installation

To verify that Terma is running correctly:

1. Check if the server is responding to HTTP requests:
   ```bash
   curl http://localhost:8765/health
   ```
   You should receive a JSON response with status "healthy".

2. Try creating a terminal session:
   ```bash
   curl -X POST http://localhost:8765/api/sessions \
     -H "Content-Type: application/json" \
     -d '{}'
   ```
   You should receive a JSON response with a session ID.

## Integration with Hephaestus UI

To integrate Terma with the Hephaestus UI:

```bash
# Run the integration script
./install_in_hephaestus.sh
```

This script:
1. Copies the Terma UI components to the Hephaestus UI directory
2. Configures the component to connect to the Terma server
3. Registers the component with Hephaestus

## Docker Installation

Terma can also be run in a Docker container:

```bash
# Build the Docker image
docker build -t terma .

# Run the container
docker run -p 8765:8765 -p 8767:8767 terma
```

Or using Docker Compose:

```yaml
# docker-compose.yml
version: '3'
services:
  terma:
    build: .
    ports:
      - "8765:8765"
      - "8767:8767"
    environment:
      - REGISTER_WITH_HERMES=true
      - HERMES_API_URL=http://hermes:8000
    volumes:
      - ./config.json:/app/config.json
```

```bash
docker-compose up -d
```

## Single Port Architecture Setup

Terma supports the Tekton Single Port Architecture pattern, allowing it to be accessed through a single port with path-based routing.

### With Nginx Reverse Proxy

Example Nginx configuration:

```nginx
server {
    listen 80;
    server_name terma.example.com;

    location /api/ {
        proxy_pass http://localhost:8765/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws/ {
        proxy_pass http://localhost:8767/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    location / {
        proxy_pass http://localhost:8765/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Troubleshooting

### Common Issues

1. **Port Conflicts**:
   If Terma fails to start due to port conflicts, try changing the port:
   ```bash
   TERMA_PORT=9000 TERMA_WS_PORT=9001 python -m terma.cli.main
   ```

2. **PTY Errors**:
   If you encounter PTY-related errors, ensure your system supports PTY:
   - On Linux/macOS: This should work by default
   - On Windows: Ensure WSL is installed and working properly

3. **WebSocket Connection Issues**:
   If WebSocket connections fail:
   - Check that the WebSocket port is accessible
   - Verify that no firewall is blocking WebSocket connections
   - Check that the WebSocket URL in the client matches the server configuration

4. **LLM Adapter Connectivity**:
   If LLM assistance features don't work:
   - Ensure the LLM adapter is running
   - Check the adapter URL in the configuration
   - Verify that the selected provider and model are available

### Logs

Check the logs for detailed error information:

- If running with default configuration, logs are printed to the console
- If configured with a log file, check the specified location
- Set `TERMA_LOG_LEVEL=DEBUG` for more detailed logging

## Upgrading

To upgrade to a newer version of Terma:

1. Pull the latest changes from the repository:
   ```bash
   git pull
   ```

2. Run the setup script again:
   ```bash
   ./setup.sh
   ```

3. Restart the Terma server.

## Uninstallation

To uninstall Terma:

1. If integrated with Hephaestus, remove the Terma component:
   ```bash
   # Navigate to Hephaestus UI directory
   cd ../Hephaestus/ui
   rm -rf components/terma-component.html
   ```

2. Remove the Terma directory:
   ```bash
   cd ..
   rm -rf Terma
   ```