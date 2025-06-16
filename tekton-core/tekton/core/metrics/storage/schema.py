"""
Database schema for metrics storage.
"""

# SQLite schema
SQLITE_SCHEMA = {
    "sessions": '''
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            prompt TEXT,
            config TEXT,
            start_time REAL,
            end_time REAL,
            response TEXT,
            performance TEXT,
            spectral_metrics TEXT,
            catastrophe_metrics TEXT,
            created_at REAL
        )
    ''',
    "component_activations": '''
        CREATE TABLE IF NOT EXISTS component_activations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            component_id TEXT,
            activation_data TEXT,
            timestamp REAL,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    ''',
    "propagation_steps": '''
        CREATE TABLE IF NOT EXISTS propagation_steps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            source TEXT,
            destination TEXT,
            info_content REAL,
            data TEXT,
            timestamp REAL,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    ''',
    "parameter_usage": '''
        CREATE TABLE IF NOT EXISTS parameter_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            component_id TEXT,
            total_params INTEGER,
            active_params INTEGER,
            utilization REAL,
            layer_data TEXT,
            timestamp REAL,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    ''',
    "latent_reasoning": '''
        CREATE TABLE IF NOT EXISTS latent_reasoning (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            component_id TEXT,
            iteration INTEGER,
            initial_confidence REAL,
            final_confidence REAL,
            iterations_required INTEGER,
            cognitive_convergence_rate REAL,
            reasoning_data TEXT,
            timestamp REAL,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    ''',
    "cross_modal_operations": '''
        CREATE TABLE IF NOT EXISTS cross_modal_operations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            source_modality TEXT,
            target_modality TEXT,
            operation_type TEXT,
            success INTEGER,
            operation_data TEXT,
            timestamp REAL,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    ''',
    "concept_stability": '''
        CREATE TABLE IF NOT EXISTS concept_stability (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            concept_id TEXT,
            context TEXT,
            vector_representation TEXT,
            stability_data TEXT,
            timestamp REAL,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        )
    '''
}

# SQLite indexes
SQLITE_INDEXES = [
    'CREATE INDEX IF NOT EXISTS idx_sessions_start_time ON sessions(start_time)',
    'CREATE INDEX IF NOT EXISTS idx_component_activations_session ON component_activations(session_id)',
    'CREATE INDEX IF NOT EXISTS idx_propagation_steps_session ON propagation_steps(session_id)',
    'CREATE INDEX IF NOT EXISTS idx_parameter_usage_session ON parameter_usage(session_id)',
    'CREATE INDEX IF NOT EXISTS idx_latent_reasoning_session ON latent_reasoning(session_id)',
    'CREATE INDEX IF NOT EXISTS idx_cross_modal_operations_session ON cross_modal_operations(session_id)',
    'CREATE INDEX IF NOT EXISTS idx_concept_stability_session ON concept_stability(session_id)',
    'CREATE INDEX IF NOT EXISTS idx_concept_stability_concept ON concept_stability(concept_id)'
]