#!/usr/bin/env python3
"""
CSV Batch Processor for PostgreSQL
High-performance batch processing engine for 100GB+ daily CSV files
"""

import os
import json
import csv
import psycopg2
from psycopg2.extras import execute_batch
from pathlib import Path
from datetime import datetime
import multiprocessing as mp
from typing import List, Dict, Any, Iterator
import logging
import tempfile
import hashlib
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CSVBatchProcessor:
    """Main processor for CSV to PostgreSQL batch operations."""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize processor with configuration."""
        with open(config_path) as f:
            self.config = json.load(f)
        
        self.chunk_size = self.config["components"]["chunker"]["chunk_size_mb"] * 1024 * 1024
        self.workers = self.config["components"]["processor"]["workers"]
        self.batch_size = self.config["components"]["processor"]["batch_size"]
        self.temp_dir = Path(self.config["components"]["chunker"]["temp_dir"])
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Performance tracking
        self.stats = {
            "start_time": None,
            "rows_processed": 0,
            "chunks_created": 0,
            "errors": 0,
            "bytes_processed": 0
        }
    
    @contextmanager
    def get_db_connection(self):
        """Get PostgreSQL connection with proper cleanup."""
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", self.config["components"]["postgres"]["host"]),
            port=self.config["components"]["postgres"]["port"],
            database=os.getenv("POSTGRES_DB", self.config["components"]["postgres"]["database"]),
            user=os.getenv("POSTGRES_USER", self.config["components"]["postgres"]["user"]),
            password=os.getenv("POSTGRES_PASSWORD", self.config["components"]["postgres"]["password"])
        )
        try:
            yield conn
        finally:
            conn.close()
    
    def split_csv_into_chunks(self, file_path: str) -> List[str]:
        """Split large CSV file into manageable chunks."""
        logger.info(f"Splitting {file_path} into chunks...")
        chunks = []
        file_size = os.path.getsize(file_path)
        
        with open(file_path, 'r', encoding='utf-8-sig') as infile:
            reader = csv.reader(infile)
            header = next(reader)
            
            chunk_num = 0
            current_size = 0
            chunk_file = None
            chunk_writer = None
            
            for row in reader:
                if current_size >= self.chunk_size or chunk_file is None:
                    if chunk_file:
                        chunk_file.close()
                    
                    chunk_num += 1
                    chunk_path = self.temp_dir / f"chunk_{chunk_num}_{hashlib.md5(file_path.encode()).hexdigest()[:8]}.csv"
                    chunks.append(str(chunk_path))
                    chunk_file = open(chunk_path, 'w', newline='', encoding='utf-8')
                    chunk_writer = csv.writer(chunk_file)
                    chunk_writer.writerow(header)
                    current_size = 0
                    logger.info(f"Created chunk {chunk_num}: {chunk_path.name}")
                
                chunk_writer.writerow(row)
                current_size += len(','.join(row).encode('utf-8'))
            
            if chunk_file:
                chunk_file.close()
        
        self.stats["chunks_created"] = len(chunks)
        logger.info(f"Created {len(chunks)} chunks from {file_size/1024/1024:.1f}MB file")
        return chunks
    
    def validate_row(self, row: Dict[str, Any], schema: Dict[str, type] = None) -> bool:
        """Validate a single row against schema."""
        if not self.config["components"]["processor"]["validation"]["enabled"]:
            return True
        
        if schema:
            for field, expected_type in schema.items():
                if field in row:
                    try:
                        expected_type(row[field])
                    except (ValueError, TypeError):
                        return False
        return True
    
    def process_chunk(self, chunk_path: str) -> int:
        """Process a single chunk and load to PostgreSQL."""
        logger.info(f"Processing chunk: {Path(chunk_path).name}")
        rows_processed = 0
        
        try:
            with self.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    with open(chunk_path, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        batch = []
                        
                        for row in reader:
                            if self.validate_row(row):
                                batch.append(tuple(row.values()))
                                
                                if len(batch) >= self.batch_size:
                                    self._insert_batch(cursor, batch, list(row.keys()))
                                    rows_processed += len(batch)
                                    batch = []
                        
                        if batch:
                            self._insert_batch(cursor, batch, list(row.keys()))
                            rows_processed += len(batch)
                    
                    conn.commit()
            
            logger.info(f"Completed chunk {Path(chunk_path).name}: {rows_processed} rows")
            
        except Exception as e:
            logger.error(f"Error processing chunk {chunk_path}: {e}")
            self.stats["errors"] += 1
            raise
        
        finally:
            # Clean up chunk file
            if os.path.exists(chunk_path):
                os.remove(chunk_path)
        
        return rows_processed
    
    def _insert_batch(self, cursor, batch: List[tuple], columns: List[str]):
        """Insert batch of rows using optimized COPY-like operation."""
        table = self.config["components"]["postgres"]["table"]
        schema = self.config["components"]["postgres"]["schema"]
        
        placeholders = ','.join(['%s'] * len(columns))
        columns_str = ','.join([f'"{col}"' for col in columns])
        
        query = f"""
            INSERT INTO {schema}.{table} ({columns_str})
            VALUES ({placeholders})
            ON CONFLICT DO NOTHING
        """
        
        execute_batch(cursor, query, batch, page_size=self.batch_size)
    
    def process_csv_file(self, file_path: str) -> Dict[str, Any]:
        """Main entry point for processing a CSV file."""
        self.stats["start_time"] = datetime.now()
        logger.info(f"Starting batch processing of {file_path}")
        
        # Split into chunks
        chunks = self.split_csv_into_chunks(file_path)
        
        # Process chunks in parallel
        with mp.Pool(processes=self.workers) as pool:
            results = pool.map(self.process_chunk, chunks)
        
        # Aggregate results
        self.stats["rows_processed"] = sum(results)
        self.stats["bytes_processed"] = os.path.getsize(file_path)
        
        elapsed = (datetime.now() - self.stats["start_time"]).total_seconds()
        throughput_mb = (self.stats["bytes_processed"] / 1024 / 1024) / elapsed
        
        logger.info(f"""
        Processing Complete:
        - File: {file_path}
        - Rows processed: {self.stats['rows_processed']:,}
        - Time: {elapsed:.1f}s
        - Throughput: {throughput_mb:.1f} MB/s
        - Errors: {self.stats['errors']}
        """)
        
        return self.stats
    
    def create_table_if_not_exists(self, sample_csv_path: str):
        """Create PostgreSQL table based on CSV structure."""
        with open(sample_csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            sample_row = next(reader)
        
        # Infer column types from sample
        columns = []
        for col, val in sample_row.items():
            if val.isdigit():
                col_type = "BIGINT"
            elif val.replace('.', '').isdigit():
                col_type = "NUMERIC"
            else:
                col_type = "TEXT"
            columns.append(f'"{col}" {col_type}')
        
        table = self.config["components"]["postgres"]["table"]
        schema = self.config["components"]["postgres"]["schema"]
        
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {schema}.{table} (
            id SERIAL PRIMARY KEY,
            {','.join(columns)},
            loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_{table}_loaded_at ON {schema}.{table}(loaded_at);
        """
        
        with self.get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(create_table_sql)
                conn.commit()
        
        logger.info(f"Table {schema}.{table} ready")


def main():
    """CLI entry point."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python processor.py <csv_file_path>")
        sys.exit(1)
    
    processor = CSVBatchProcessor()
    
    # Set up table if needed
    processor.create_table_if_not_exists(sys.argv[1])
    
    # Process the file
    stats = processor.process_csv_file(sys.argv[1])
    
    return 0 if stats["errors"] == 0 else 1


if __name__ == "__main__":
    exit(main())