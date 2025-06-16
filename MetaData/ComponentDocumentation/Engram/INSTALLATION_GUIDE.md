# Engram Installation Guide

## Prerequisites

- Python 3.10 or higher
- Vector database (FAISS, LanceDB, or other supported backend)
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
cd Engram
pip install -r requirements.txt
```

### 3. Install Engram Package

```bash
pip install -e .
```

### 4. Choose and Set Up a Vector Database

Engram supports multiple vector database backends. Choose one based on your needs:

#### Option A: FAISS (In-memory, Fast)

FAISS is included in the requirements and requires no additional setup.

#### Option B: LanceDB (Persistent, Easy setup)

LanceDB provides a persistent vector store with good performance:

```bash
# Run the LanceDB setup script
python -m engram.utils.vector_db_setup --db lancedb
```

#### Option C: Other Vector Databases

For other supported databases, refer to their specific installation instructions and then run:

```bash
python -m engram.utils.vector_db_setup --db [database_name]
```

The setup script will detect the best available vector database if none is specified:

```bash
python -m engram.utils.detect_best_vector_db
```

### 5. Configure Environment

Create a `.env` file in the Engram directory with the following environment variables:

```
# Core Configuration
ENGRAM_HOST=0.0.0.0
ENGRAM_PORT=8002
ENGRAM_DEBUG=true
ENGRAM_LOG_LEVEL=info

# Vector Database Configuration
VECTOR_DB_TYPE=faiss  # or lancedb, etc.
VECTOR_DB_PATH=./vector_store

# Embedding Model Configuration
EMBEDDING_MODEL=default  # or openai, sentence-transformers, etc.
EMBEDDING_DIMENSIONS=1536

# Hermes Configuration
HERMES_HOST=localhost
HERMES_PORT=8000
HERMES_API_KEY=your_api_key

# LLM Configuration (for enhanced features)
LLM_ADAPTER_URL=http://localhost:8003
LLM_PROVIDER=openai
LLM_MODEL=gpt-3.5-turbo
```

### 6. Initialize Engram

Run the initialization script to set up the database and default compartments:

```bash
python -m engram.core.memory_manager --init
```

### 7. Start Engram

```bash
# Run directly
python -m engram.api.server

# Or use the provided script
./run_engram.sh
```

Engram will be available at `http://localhost:8002`.

## Docker Installation

### 1. Build the Docker Image

```bash
cd Tekton/Engram
docker build -t engram:latest .
```

### 2. Run with Docker Compose

Create a `docker-compose.yml` file in the Engram directory:

```yaml
version: '3'

services:
  engram:
    image: engram:latest
    ports:
      - "8002:8002"
    environment:
      - ENGRAM_HOST=0.0.0.0
      - ENGRAM_PORT=8002
      - ENGRAM_DEBUG=true
      - ENGRAM_LOG_LEVEL=info
      - VECTOR_DB_TYPE=lancedb
      - VECTOR_DB_PATH=/app/data/vector_store
      - EMBEDDING_MODEL=default
      - EMBEDDING_DIMENSIONS=1536
      - HERMES_HOST=hermes
      - HERMES_PORT=8000
      - HERMES_API_KEY=your_api_key
      - LLM_ADAPTER_URL=http://llm-adapter:8003
      - LLM_PROVIDER=openai
      - LLM_MODEL=gpt-3.5-turbo
    depends_on:
      - hermes
    volumes:
      - ./data:/app/data

volumes:
  engram_data:
```

Start the services:

```bash
docker-compose up -d
```

## Production Deployment

### System Requirements

For production deployments, consider the following resource guidelines:

- **CPU**: 4+ cores recommended
- **Memory**: 8GB+ RAM recommended (more for larger vector stores)
- **Storage**: 20GB+ for vector database (scales with memory size)
- **Network**: Low-latency connections to other Tekton components

### Configuration Recommendations

For production deployments, adjust the following settings:

```
ENGRAM_DEBUG=false
ENGRAM_LOG_LEVEL=warning
```

Consider using a persistent vector database like LanceDB for production:

```
VECTOR_DB_TYPE=lancedb
VECTOR_DB_PATH=/path/to/persistent/storage
```

Ensure that secure passwords and API keys are used for all services.

### Scaling Considerations

- For heavy workloads, consider using a specialized vector database like Pinecone or Weaviate
- Implement a load balancer for multiple Engram instances if needed
- Use separate instances for read-heavy and write-heavy workloads

### Monitoring and Logging

Consider integrating with monitoring tools:

- Prometheus for metrics
- ELK stack for log aggregation
- Grafana for visualization

## Hermes Integration

Register Engram with Hermes to enable component discovery and communication:

```bash
python -m engram.cli.register_with_hermes
```

This will register Engram's endpoints and capabilities with the Hermes service registry.

## Troubleshooting

### Common Issues

1. **Vector Database Errors**
   - Ensure the selected vector database is properly installed
   - Check that the database path is writable
   - Verify environment variables are correctly set

2. **API Endpoint Not Responding**
   - Check the Engram logs for errors
   - Verify the port is not being used by another service
   - Ensure Engram is properly configured

3. **Embedding Generation Failures**
   - Verify the embedding model is available
   - Check network connectivity to API services (if using remote embeddings)
   - Ensure API keys are valid for external embedding services

4. **Memory Storage Issues**
   - Check disk space for persistent storage
   - Verify file permissions on storage directories
   - Check for database corruption and run repair utilities if needed

### Logging

Increase log verbosity for debugging:

```
ENGRAM_LOG_LEVEL=debug
```

Logs are available at:
- Standard output/console
- `/app/logs/engram.log` (when running in Docker)

### Diagnostic Tools

Engram includes several diagnostic tools:

```bash
# Test vector database connection
python -m engram.utils.test_vector_db

# Benchmark embedding performance
python -m engram.utils.benchmark_embeddings

# Verify memory storage and retrieval
python -m engram.utils.memory_integrity_check
```

## Updating Engram

To update Engram:

1. Pull the latest code:
   ```bash
   git pull origin main
   ```

2. Update dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run database migrations if needed:
   ```bash
   python -m engram.utils.migrate_vector_store
   ```

4. Restart the service

## Next Steps

After installation, see the [Integration Guide](./INTEGRATION_GUIDE.md) for connecting Engram with other Tekton components and learning how to use its API effectively.