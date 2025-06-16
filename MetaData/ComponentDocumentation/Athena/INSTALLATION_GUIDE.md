# Athena Installation Guide

## Prerequisites

- Python 3.10 or higher
- Neo4j (optional, for production deployments)
- Hermes (for integration with other Tekton components)
- Docker and Docker Compose (optional, for containerized deployment)

## Local Development Installation

### 1. Clone the Repository

If you haven't already cloned the Tekton repository:

```bash
git clone https://github.com/yourusername/Tekton.git
cd Tekton
```

### 2. Set Up Python Environment

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate

# Install dependencies
cd Athena
pip install -r requirements.txt
```

### 3. Install Athena Package

```bash
pip install -e .
```

### 4. Configure Environment

Create a `.env` file in the Athena directory with the following environment variables:

```
# Core Configuration
ATHENA_HOST=0.0.0.0
ATHENA_PORT=8001
ATHENA_DEBUG=true
ATHENA_LOG_LEVEL=info

# Neo4j Configuration (if using Neo4j)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Hermes Configuration
HERMES_HOST=localhost
HERMES_PORT=8000
HERMES_API_KEY=your_api_key

# LLM Configuration
LLM_ADAPTER_URL=http://localhost:8003
LLM_PROVIDER=openai
LLM_MODEL=gpt-3.5-turbo
```

### 5. Initialize Database

If using Neo4j, ensure it's running and then run the initialization script:

```bash
python -m athena.scripts.init_database
```

### 6. Start Athena

```bash
# Run directly
python -m athena.api.app

# Or use the provided script
./run_athena.sh
```

Athena will be available at `http://localhost:8001`.

## Docker Installation

### 1. Build the Docker Image

```bash
cd Tekton/Athena
docker build -t athena:latest .
```

### 2. Run with Docker Compose

Create a `docker-compose.yml` file in the Athena directory:

```yaml
version: '3'

services:
  athena:
    image: athena:latest
    ports:
      - "8001:8001"
    environment:
      - ATHENA_HOST=0.0.0.0
      - ATHENA_PORT=8001
      - ATHENA_DEBUG=true
      - ATHENA_LOG_LEVEL=info
      - HERMES_HOST=hermes
      - HERMES_PORT=8000
      - HERMES_API_KEY=your_api_key
      - NEO4J_URI=bolt://neo4j:7687
      - NEO4J_USER=neo4j
      - NEO4J_PASSWORD=password
      - LLM_ADAPTER_URL=http://llm-adapter:8003
      - LLM_PROVIDER=openai
      - LLM_MODEL=gpt-3.5-turbo
    depends_on:
      - neo4j
      - hermes
    volumes:
      - ./data:/app/data

  neo4j:
    image: neo4j:4.4
    ports:
      - "7474:7474"  # HTTP
      - "7687:7687"  # Bolt
    environment:
      - NEO4J_AUTH=neo4j/password
    volumes:
      - neo4j_data:/data

volumes:
  neo4j_data:
```

Start the services:

```bash
docker-compose up -d
```

## Production Deployment

### System Requirements

For production deployments, consider the following resource guidelines:

- **CPU**: 4+ cores recommended
- **Memory**: 8GB+ RAM recommended
- **Storage**: Depends on graph size, start with 20GB
- **Neo4j**: Dedicated instance with appropriate sizing

### Configuration Recommendations

For production deployments, adjust the following settings:

```
ATHENA_DEBUG=false
ATHENA_LOG_LEVEL=warning
```

Ensure that secure passwords are used for all services and that API keys are properly managed.

### Monitoring and Logging

Consider integrating with monitoring tools:

- Prometheus for metrics
- ELK stack for log aggregation
- Grafana for visualization

## Hermes Integration

Register Athena with Hermes to enable component discovery and communication:

```bash
python register_with_hermes.py
```

This will register Athena's endpoints and capabilities with the Hermes service registry.

## Troubleshooting

### Common Issues

1. **Neo4j Connection Errors**
   - Ensure Neo4j is running and accessible
   - Verify credentials in the .env file
   - Check network connectivity between Athena and Neo4j

2. **API Endpoint Not Responding**
   - Check the Athena logs for errors
   - Verify the port is not being used by another service
   - Ensure Athena is properly configured

3. **Hermes Communication Failures**
   - Verify Hermes is running
   - Check the API key configuration
   - Review network connectivity

### Logging

Increase log verbosity for debugging:

```
ATHENA_LOG_LEVEL=debug
```

Logs are available at:
- Standard output/console
- `/app/logs/athena.log` (when running in Docker)

## Updating Athena

To update Athena:

1. Pull the latest code:
   ```bash
   git pull origin main
   ```

2. Update dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run any database migrations:
   ```bash
   python -m athena.scripts.migrate_database
   ```

4. Restart the service

## Next Steps

After installation, see the [Integration Guide](./INTEGRATION_GUIDE.md) for connecting Athena with other Tekton components.