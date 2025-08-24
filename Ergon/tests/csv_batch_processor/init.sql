-- PostgreSQL initialization for CSV Batch Processor
-- Optimized for high-volume data ingestion

-- Create schema if not exists
CREATE SCHEMA IF NOT EXISTS public;

-- Create optimized settings for bulk loading
ALTER SYSTEM SET shared_buffers = '2GB';
ALTER SYSTEM SET work_mem = '256MB';
ALTER SYSTEM SET maintenance_work_mem = '1GB';
ALTER SYSTEM SET effective_cache_size = '12GB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET max_wal_size = '4GB';

-- Create main import table (will be customized based on CSV structure)
CREATE TABLE IF NOT EXISTS public.csv_imports_template (
    id BIGSERIAL PRIMARY KEY,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    batch_id VARCHAR(50),
    source_file VARCHAR(255)
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_csv_imports_loaded_at ON public.csv_imports_template(loaded_at);
CREATE INDEX IF NOT EXISTS idx_csv_imports_batch_id ON public.csv_imports_template(batch_id);

-- Create monitoring table
CREATE TABLE IF NOT EXISTS public.processing_stats (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255),
    file_size_mb NUMERIC(10,2),
    rows_processed INTEGER,
    processing_time_seconds NUMERIC(10,2),
    throughput_mb_per_sec NUMERIC(10,2),
    errors INTEGER DEFAULT 0,
    started_at TIMESTAMP,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create error logging table
CREATE TABLE IF NOT EXISTS public.processing_errors (
    id SERIAL PRIMARY KEY,
    file_name VARCHAR(255),
    error_type VARCHAR(100),
    error_message TEXT,
    row_number INTEGER,
    occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO etl_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO etl_user;

-- Create function for table partitioning (for very large datasets)
CREATE OR REPLACE FUNCTION create_monthly_partition(table_name TEXT, partition_date DATE)
RETURNS void AS $$
DECLARE
    partition_name TEXT;
    start_date DATE;
    end_date DATE;
BEGIN
    partition_name := table_name || '_' || to_char(partition_date, 'YYYY_MM');
    start_date := date_trunc('month', partition_date);
    end_date := start_date + INTERVAL '1 month';
    
    EXECUTE format('CREATE TABLE IF NOT EXISTS %I PARTITION OF %I 
                    FOR VALUES FROM (%L) TO (%L)',
                    partition_name, table_name, start_date, end_date);
END;
$$ LANGUAGE plpgsql;

-- Optimize for bulk inserts
ALTER TABLE public.csv_imports_template SET (autovacuum_enabled = false);

-- Re-enable autovacuum after bulk load with a function
CREATE OR REPLACE FUNCTION enable_autovacuum_after_load(table_name TEXT)
RETURNS void AS $$
BEGIN
    EXECUTE format('ALTER TABLE %I SET (autovacuum_enabled = true)', table_name);
    EXECUTE format('ANALYZE %I', table_name);
END;
$$ LANGUAGE plpgsql;

-- Create materialized view for daily summaries (refresh after load)
CREATE MATERIALIZED VIEW IF NOT EXISTS public.daily_processing_summary AS
SELECT 
    DATE(completed_at) as processing_date,
    COUNT(*) as files_processed,
    SUM(file_size_mb) as total_mb_processed,
    SUM(rows_processed) as total_rows,
    AVG(throughput_mb_per_sec) as avg_throughput,
    SUM(errors) as total_errors
FROM public.processing_stats
GROUP BY DATE(completed_at);

CREATE UNIQUE INDEX ON public.daily_processing_summary(processing_date);

-- Refresh function for materialized view
CREATE OR REPLACE FUNCTION refresh_daily_summary()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY public.daily_processing_summary;
END;
$$ LANGUAGE plpgsql;

SELECT pg_reload_conf();