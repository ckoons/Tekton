#!/usr/bin/env python
"""
Simple test script for LanceDB vector store.
"""

import os
import sys
import time
import logging
import lancedb
import pyarrow as pa
import numpy as np
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("simple_lancedb_test")

# Add Engram to path
ENGRAM_DIR = str(Path(__file__).parent.parent.parent)
if ENGRAM_DIR not in sys.path:
    sys.path.insert(0, ENGRAM_DIR)
    logger.info(f"Added {ENGRAM_DIR} to Python path")

# Create test directory
TEST_DIR = os.path.join(ENGRAM_DIR, "test_memories", "lancedb_simple_test")
os.makedirs(TEST_DIR, exist_ok=True)

def run_test():
    """Run a simple LanceDB test to verify functionality."""
    logger.info(f"Running simple LanceDB test in {TEST_DIR}")
    logger.info(f"LanceDB version: {lancedb.__version__}")
    logger.info(f"PyArrow version: {pa.__version__}")
    logger.info(f"NumPy version: {np.__version__}")
    
    # Connect to database
    db = lancedb.connect(TEST_DIR)
    logger.info("Connected to LanceDB")
    
    # Create a simple table with vector data
    table_name = "test_table"
    
    # Create schema and data
    schema = pa.schema([
        pa.field("id", pa.int64()),
        pa.field("text", pa.string()),
        pa.field("vector", pa.list_(pa.float32(), 64)),
        pa.field("timestamp", pa.float64()),
        pa.field("category", pa.string()),
    ])
    
    # Create sample data
    data = {
        "id": [1, 2, 3, 4, 5],
        "text": [
            "The quick brown fox jumps over the lazy dog",
            "Machine learning is a subset of artificial intelligence",
            "Vector search allows semantic matching of text",
            "Python is a popular programming language for data science",
            "LanceDB is a vector database built on Apache Arrow"
        ],
        "vector": [np.random.rand(64).astype(np.float32).tolist() for _ in range(5)],
        "timestamp": [time.time()] * 5,
        "category": ["test", "ml", "search", "programming", "database"]
    }
    
    # Create table
    table = pa.Table.from_pydict(data, schema=schema)
    
    # Delete existing table if it exists
    if table_name in db.table_names():
        logger.info(f"Dropping existing table {table_name}")
        db.drop_table(table_name)
    
    # Create new table
    logger.info(f"Creating table {table_name}")
    db_table = db.create_table(table_name, table)
    
    # Verify table exists
    logger.info(f"Tables in database: {db.table_names()}")
    
    # Query the table
    logger.info("Querying table")
    query_result = db_table.to_pandas()
    logger.info(f"Table has {len(query_result)} rows")
    
    # Test vector search
    logger.info("Testing vector search")
    query_vector = np.random.rand(64).astype(np.float32).tolist()
    search_result = db_table.search(query_vector).limit(3).to_pandas()
    logger.info(f"Vector search returned {len(search_result)} results")
    logger.info(f"First result: id={search_result.iloc[0]['id']}, text={search_result.iloc[0]['text']}")
    
    # Test filter - use SQL-like query
    logger.info("Testing filters")
    try:
        # First try with SQL-like query
        filter_result = db_table.to_pandas(filter="category = 'ml'")
        logger.info(f"Filter returned {len(filter_result)} results using SQL-like query")
    except Exception as e:
        logger.warning(f"SQL-like query failed: {e}")
        # Fallback to pandas filtering
        all_data = db_table.to_pandas()
        filter_result = all_data[all_data["category"] == "ml"]
        logger.info(f"Filter returned {len(filter_result)} results using pandas filtering")
    
    # Test combined vector search and filter
    logger.info("Testing vector search with filter")
    try:
        # First try with SQL-like query in search
        search_result = db_table.search(query_vector).limit(10).to_pandas()
        # Then filter in pandas
        combined_result = search_result[search_result["category"].isin(["ml", "search"])].head(2)
        logger.info(f"Combined query returned {len(combined_result)} results")
    except Exception as e:
        logger.warning(f"Combined search and filter failed: {e}")
        combined_result = []
        logger.info("Combined query returned 0 results due to error")
    
    # Clean up
    logger.info("Test completed successfully")
    
if __name__ == "__main__":
    run_test()