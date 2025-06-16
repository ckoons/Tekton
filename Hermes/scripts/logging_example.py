#!/usr/bin/env python3
"""
Hermes Logging Example

This script demonstrates how to use the Hermes logging system with different
log levels, component-based logging, and structured logging features.
"""

import time
import random
import os
from pathlib import Path
import threading
from datetime import datetime

# Ensure Hermes is in Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from hermes.core.logging import get_logger, configure_logging

def basic_logging_example():
    """Demonstrate basic logging functionality."""
    print("\n=== Basic Logging Example ===")
    
    # Configure logging with default settings
    configure_logging(level="INFO")
    
    # Get loggers for different components
    main_logger = get_logger("hermes.examples.main")
    database_logger = get_logger("hermes.examples.database")
    api_logger = get_logger("hermes.examples.api")
    
    # Log messages at different levels
    main_logger.debug("This is a debug message (should not be visible at INFO level)")
    main_logger.info("This is an info message from the main component")
    main_logger.warning("This is a warning message from the main component")
    main_logger.error("This is an error message from the main component")
    
    database_logger.info("This is an info message from the database component")
    database_logger.warning("This is a warning message from the database component")
    
    api_logger.info("This is an info message from the API component")
    api_logger.error("This is an error message from the API component")
    
    # Try to log a critical message with exception
    try:
        result = 1 / 0
    except Exception as e:
        main_logger.critical(f"Critical error occurred: {e}", exc_info=True)

def component_based_logging_example():
    """Demonstrate component-based logging with different log levels."""
    print("\n=== Component-Based Logging Example ===")
    
    # Configure with component-specific levels
    configure_logging(
        level="INFO",  # Default level
        component_levels={
            "hermes.examples.database": "DEBUG",  # More verbose for database
            "hermes.examples.api": "WARNING"      # Less verbose for API
        }
    )
    
    # Get loggers for different components
    main_logger = get_logger("hermes.examples.main")
    database_logger = get_logger("hermes.examples.database")
    api_logger = get_logger("hermes.examples.api")
    
    # Log messages at different levels
    main_logger.debug("Main debug (should not be visible at INFO level)")
    main_logger.info("Main info (should be visible)")
    
    database_logger.debug("Database debug (should be visible due to DEBUG level)")
    database_logger.info("Database info (should be visible)")
    
    api_logger.debug("API debug (should not be visible)")
    api_logger.info("API info (should not be visible at WARNING level)")
    api_logger.warning("API warning (should be visible)")
    
    # Reset logging configuration to default
    configure_logging(level="INFO")

def structured_logging_example():
    """Demonstrate structured logging with additional context."""
    print("\n=== Structured Logging Example ===")
    
    # Configure logging
    configure_logging(level="INFO")
    
    # Get logger
    logger = get_logger("hermes.examples.structured")
    
    # Log with additional structured data
    logger.info("User logged in", 
                extra={
                    "user_id": "user123",
                    "ip_address": "192.168.1.1",
                    "login_time": datetime.now().isoformat()
                })
    
    logger.warning("High CPU usage detected",
                  extra={
                      "cpu_percent": 95.2,
                      "memory_percent": 87.3,
                      "process_count": 120
                  })
    
    logger.error("Database connection failed",
                extra={
                    "database": "postgres",
                    "host": "db.example.com",
                    "port": 5432,
                    "retry_count": 3,
                    "error_code": "ECONNREFUSED"
                })
    
    # Log with deeply nested data
    logger.info("Complex operation completed",
               extra={
                   "operation": "data_migration",
                   "stats": {
                       "records_processed": 1250,
                       "success_rate": 0.997,
                       "duration_ms": 3542,
                       "by_type": {
                           "users": 450,
                           "orders": 800
                       }
                   },
                   "context": {
                       "environment": "production",
                       "region": "us-west",
                       "initiated_by": "scheduled_job"
                   }
               })

def simulated_application_logging():
    """Simulate logging from a running application."""
    print("\n=== Simulated Application Logging ===")
    
    # Configure logging
    configure_logging(level="INFO")
    
    # Get loggers for different components
    api_logger = get_logger("app.api")
    db_logger = get_logger("app.database")
    auth_logger = get_logger("app.auth")
    
    # Simulate a series of operations with logging
    api_logger.info("Application started", 
                   extra={"version": "1.0.0", "environment": "development"})
    
    # Simulate user login
    user_id = f"user_{random.randint(1000, 9999)}"
    auth_logger.info(f"User login attempt", 
                    extra={"user_id": user_id, "ip": "192.168.1.1"})
    
    # Simulate successful login
    auth_logger.info(f"User login successful", 
                    extra={"user_id": user_id, "session_id": f"sess_{random.randint(1000, 9999)}"})
    
    # Simulate database queries
    db_logger.info("Executing database query", 
                  extra={"query_type": "SELECT", "table": "users"})
    
    # Simulate random errors (20% chance)
    if random.random() < 0.2:
        db_logger.error("Database query failed", 
                       extra={
                           "query_type": "SELECT", 
                           "table": "users",
                           "error_code": "DB-3542",
                           "retryable": True
                       })
        
        # Simulate retry
        db_logger.info("Retrying database query", 
                      extra={"query_type": "SELECT", "table": "users", "attempt": 2})
    
    # Simulate API response
    response_time = random.randint(50, 500)
    status_code = 200 if response_time < 300 else 500
    
    api_logger.info("API request completed", 
                   extra={
                       "path": "/api/users",
                       "method": "GET",
                       "status_code": status_code,
                       "response_time_ms": response_time,
                       "user_id": user_id
                   })
    
    # Log warning for slow responses
    if response_time > 200:
        api_logger.warning("Slow API response detected", 
                          extra={
                              "path": "/api/users",
                              "response_time_ms": response_time,
                              "threshold_ms": 200
                          })

def concurrent_logging_example():
    """Demonstrate logging from multiple threads concurrently."""
    print("\n=== Concurrent Logging Example ===")
    
    # Configure logging
    configure_logging(level="INFO")
    
    def worker_task(worker_id):
        """Simulated worker task that logs messages."""
        # Get a logger for this worker
        logger = get_logger(f"hermes.examples.worker.{worker_id}")
        
        # Log start
        logger.info(f"Worker {worker_id} started")
        
        # Simulate work with logging
        for i in range(3):
            # Simulate work
            work_time = random.uniform(0.1, 0.5)
            time.sleep(work_time)
            
            # Log progress
            logger.info(f"Worker {worker_id} completed step {i+1}",
                       extra={
                           "worker_id": worker_id,
                           "step": i+1,
                           "duration_ms": int(work_time * 1000)
                       })
            
            # Simulate occasional warnings
            if random.random() < 0.3:
                logger.warning(f"Worker {worker_id} encountered a non-critical issue",
                              extra={
                                  "worker_id": worker_id,
                                  "step": i+1,
                                  "issue_type": "performance_degradation"
                              })
        
        # Log completion
        logger.info(f"Worker {worker_id} completed all tasks")
    
    # Create and start worker threads
    threads = []
    for i in range(5):
        thread = threading.Thread(target=worker_task, args=(i+1,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Log overall completion
    main_logger = get_logger("hermes.examples.main")
    main_logger.info("All workers completed their tasks")

def log_level_demonstration():
    """Demonstrate different log levels and when to use them."""
    print("\n=== Log Level Demonstration ===")
    
    # Configure to show all logs
    configure_logging(level="DEBUG")
    
    # Get logger
    logger = get_logger("hermes.examples.levels")
    
    # DEBUG: Detailed information, typically of interest only when diagnosing problems
    logger.debug("Connecting to database with timeout=30s and max_connections=10")
    logger.debug("User preference loaded: display_mode=dark, notifications=enabled")
    
    # INFO: Confirmation that things are working as expected
    logger.info("Application started successfully")
    logger.info("User 'alice' logged in")
    logger.info("Database migration completed: 42 tables updated")
    
    # WARNING: An indication that something unexpected happened, or may happen in the near future
    logger.warning("API rate limit approaching: 980/1000 requests used")
    logger.warning("Disk usage above 85% threshold")
    logger.warning("Using deprecated function 'old_auth()' - will be removed in v2.0")
    
    # ERROR: Due to a more serious problem, the software has not been able to perform a function
    logger.error("Failed to connect to database after 3 retries")
    logger.error("User authentication failed: invalid credentials")
    logger.error("Unable to process payment: gateway timeout")
    
    # CRITICAL: A serious error indicating that the program itself may be unable to continue running
    logger.critical("Insufficient memory to continue operation")
    logger.critical("Database connection pool exhausted")
    logger.critical("Unhandled exception in main thread")
    
    # Reset to default
    configure_logging(level="INFO")

def main():
    """Run all logging examples."""
    print("Starting Hermes logging examples...")
    
    # Run examples
    basic_logging_example()
    component_based_logging_example()
    structured_logging_example()
    log_level_demonstration()
    simulated_application_logging()
    concurrent_logging_example()
    
    print("\nAll logging examples completed")

if __name__ == "__main__":
    main()