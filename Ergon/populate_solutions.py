"""
Populate Ergon's solution registry database
"""

import sqlite3
import json
from datetime import datetime

# Solution definitions
solutions = [
    {
        "name": "Codebase Indexer",
        "type": "analysis",
        "description": "Comprehensive codebase analysis that indexes all methods, calls, data structures, and semantic tags",
        "capabilities": [
            "method_extraction",
            "call_graph_analysis",
            "data_structure_mapping",
            "semantic_tag_detection",
            "cross_reference_building"
        ],
        "configuration": {
            "include_patterns": ["*.py", "*.js", "*.ts", "*.java"],
            "exclude_patterns": ["*_test.*", "*/tests/*", "*/node_modules/*"],
            "index_on_change": True,
            "cache_results": True
        },
        "implementation": {
            "class": "CodebaseIndexer",
            "module": "ergon.solutions.codebase_indexer",
            "version": "1.0.0"
        }
    },
    {
        "name": "RAG Engine",
        "type": "intelligence",
        "description": "Retrieval-Augmented Generation for intelligent code understanding and generation",
        "capabilities": [
            "code_explanation",
            "contextual_search",
            "improvement_suggestions",
            "call_graph_analysis",
            "semantic_understanding"
        ],
        "configuration": {
            "max_contexts": 5,
            "include_call_graph": True,
            "confidence_threshold": 0.7,
            "use_cache": True
        },
        "dependencies": ["Codebase Indexer"],
        "implementation": {
            "class": "RAGEngine",
            "module": "ergon.solutions.rag_solution",
            "version": "1.0.0"
        }
    },
    {
        "name": "Cache RAG",
        "type": "intelligence",
        "description": "Intelligent caching layer for RAG with pattern learning and precomputation",
        "capabilities": [
            "smart_caching",
            "pattern_learning",
            "query_precomputation",
            "cache_warming",
            "performance_optimization"
        ],
        "configuration": {
            "cache_dir": ".ergon_cache",
            "max_memory_entries": 1000,
            "default_ttl": 3600,
            "precompute_threshold": 3,
            "warm_on_startup": True
        },
        "dependencies": ["RAG Engine", "Codebase Indexer"],
        "implementation": {
            "class": "CacheRAGEngine",
            "module": "ergon.solutions.cache_rag",
            "version": "1.0.0"
        }
    },
    {
        "name": "Companion Intelligence",
        "type": "intelligence",
        "description": "Binds a CI with a codebase for deep understanding and intelligent development assistance",
        "capabilities": [
            "codebase_understanding",
            "task_assistance",
            "adaptation_planning",
            "pattern_learning",
            "autonomy_recommendation"
        ],
        "configuration": {
            "ci_name": "Ergon",
            "learning_enabled": True,
            "autonomy_assessment": True,
            "pattern_recognition": True
        },
        "dependencies": ["Cache RAG", "Codebase Indexer"],
        "implementation": {
            "class": "CompanionIntelligence",
            "module": "ergon.solutions.companion_intelligence",
            "version": "1.0.0"
        }
    }
]

# Connect to database
db_path = "ergon/ergon.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print(f"Connected to database: {db_path}")

# Add solutions to database
for solution in solutions:
    try:
        # Check if solution already exists
        cursor.execute("SELECT id FROM solutions WHERE name = ?", (solution['name'],))
        if cursor.fetchone():
            print(f"Solution '{solution['name']}' already exists, updating...")
            cursor.execute("""
                UPDATE solutions 
                SET type = ?, description = ?, capabilities = ?, 
                    configuration = ?, implementation = ?, dependencies = ?,
                    updated_at = ?
                WHERE name = ?
            """, (
                solution['type'],
                solution['description'],
                json.dumps(solution['capabilities']),
                json.dumps(solution['configuration']),
                json.dumps(solution['implementation']),
                json.dumps(solution.get('dependencies', [])),
                datetime.now().isoformat(),
                solution['name']
            ))
        else:
            # Insert new solution
            cursor.execute("""
                INSERT INTO solutions 
                (name, type, description, capabilities, configuration, 
                 implementation, dependencies, usage_count, success_rate, 
                 created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                solution['name'],
                solution['type'],
                solution['description'],
                json.dumps(solution['capabilities']),
                json.dumps(solution['configuration']),
                json.dumps(solution['implementation']),
                json.dumps(solution.get('dependencies', [])),
                0,  # usage_count
                0.95,  # success_rate
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            print(f"Added solution: {solution['name']}")
            
    except Exception as e:
        print(f"Error adding solution '{solution['name']}': {e}")

# Commit changes
conn.commit()

# Display all solutions
cursor.execute("SELECT name, type, description FROM solutions")
solutions = cursor.fetchall()

print("\n" + "="*60)
print("Current solutions in database:")
print("="*60)
for i, (name, type_, desc) in enumerate(solutions, 1):
    print(f"\n{i}. {name} ({type_})")
    print(f"   {desc}")

# Show count
cursor.execute("SELECT COUNT(*) FROM solutions")
count = cursor.fetchone()[0]
print(f"\nTotal solutions in registry: {count}")

conn.close()