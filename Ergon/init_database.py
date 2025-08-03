"""
Initialize Ergon database with tables
"""

import sqlite3
from datetime import datetime

# Create database
db_path = "ergon/ergon.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print(f"Creating database at: {db_path}")

# Create solutions table
cursor.execute("""
CREATE TABLE IF NOT EXISTS solutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    type TEXT NOT NULL,
    description TEXT,
    capabilities TEXT,  -- JSON array
    configuration TEXT,  -- JSON object
    implementation TEXT,  -- JSON object
    dependencies TEXT,  -- JSON array
    usage_count INTEGER DEFAULT 0,
    success_rate REAL DEFAULT 0.0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

# Create workflows table
cursor.execute("""
CREATE TABLE IF NOT EXISTS workflows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    steps TEXT,  -- JSON array
    success_rate REAL DEFAULT 0.0,
    last_used_at TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

# Create tools table
cursor.execute("""
CREATE TABLE IF NOT EXISTS tools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    component TEXT,
    description TEXT,
    parameters TEXT,  -- JSON object
    capabilities TEXT,  -- JSON array
    discovered_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

# Create configurations table
cursor.execute("""
CREATE TABLE IF NOT EXISTS configurations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    solution_id INTEGER,
    name TEXT NOT NULL,
    type TEXT,
    content TEXT,
    metadata TEXT,  -- JSON object
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (solution_id) REFERENCES solutions(id)
)
""")

conn.commit()
print("Database tables created successfully!")

# Show tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("\nCreated tables:")
for table in tables:
    print(f"  - {table[0]}")

conn.close()