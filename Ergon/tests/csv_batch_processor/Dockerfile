FROM python:3.11-slim

WORKDIR /app

# Install PostgreSQL client libraries
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    psycopg2-binary \
    pandas \
    numpy \
    click \
    python-dotenv

# Copy application files
COPY processor.py .
COPY config.json .
COPY orchestrator.sh .

# Create directories
RUN mkdir -p /tmp/csv_chunks /data/input /data/processed

# Make orchestrator executable
RUN chmod +x orchestrator.sh

# Volume for input CSV files
VOLUME ["/data/input", "/data/processed"]

# Environment variables (override with -e flags)
ENV POSTGRES_HOST=localhost
ENV POSTGRES_DB=datawarehouse
ENV POSTGRES_USER=etl_user
ENV POSTGRES_PASSWORD=changeme
ENV TARGET_TABLE=csv_imports
ENV PYTHONUNBUFFERED=1

# Entry point for batch processing
ENTRYPOINT ["python", "processor.py"]