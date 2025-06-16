FROM python:3.11-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PRELOAD_DOCS=false

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Install the package in development mode
RUN pip install -e .

# Create volume directories
RUN mkdir -p /data/database /data/vector_store

# Set environment variables for volumes
ENV DATABASE_URL=sqlite:////data/database/ergon.db \
    VECTOR_DB_PATH=/data/vector_store

# Create .env file from example if it doesn't exist
RUN if [ \! -f .env ]; then cp .env.example .env; fi

# Create .env.owner file as a template (will be overwritten by volume mount if provided)
RUN echo '# Owner configuration - this will be overwritten by volume mount if provided\n# See .env.example for available settings' > .env.owner

# Documentation preloading is handled by the UI when needed
# No automatic preloading during build to keep image lightweight

# Expose Streamlit port
EXPOSE 8501

# Copy entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command
CMD ["ui"]
