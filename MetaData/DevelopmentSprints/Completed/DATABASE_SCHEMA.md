# Ergon v2 Database Schema

## Overview
PostgreSQL database with JSONB fields for flexible capability and configuration storage.

## Core Tables

### 1. solutions
Primary table for all reusable components (tools, agents, MCP servers, workflows).

```sql
CREATE TYPE solution_type AS ENUM ('tool', 'agent', 'mcp_server', 'workflow');
CREATE TYPE solution_status AS ENUM ('active', 'deprecated', 'experimental', 'archived');

CREATE TABLE solutions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255) NOT NULL,
    type solution_type NOT NULL,
    version VARCHAR(50) NOT NULL DEFAULT '1.0.0',
    source VARCHAR(500) NOT NULL, -- 'builtin', 'github:owner/repo', 'custom', 'pypi:package'
    description TEXT,
    long_description TEXT, -- Markdown supported
    
    -- Capabilities and metadata
    capabilities JSONB NOT NULL DEFAULT '[]', -- ["file.read", "data.csv.parse"]
    parameters JSONB DEFAULT '{}', -- Parameter definitions
    dependencies JSONB DEFAULT '{}', -- {"python": ["pandas>=1.0"], "system": ["ffmpeg"]}
    configuration_template JSONB DEFAULT '{}', -- Default config template
    
    -- Usage tracking
    usage_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMP,
    
    -- Metadata
    author VARCHAR(255),
    license VARCHAR(100),
    homepage_url VARCHAR(500),
    repository_url VARCHAR(500),
    documentation_url VARCHAR(500),
    
    -- Status and lifecycle
    status solution_status DEFAULT 'active',
    tags JSONB DEFAULT '[]', -- ["data-processing", "csv", "analytics"]
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_solutions_type (type),
    INDEX idx_solutions_status (status),
    INDEX idx_solutions_capabilities USING GIN (capabilities),
    INDEX idx_solutions_tags USING GIN (tags)
);
```

### 2. capabilities
Hierarchical taxonomy for categorizing solution capabilities.

```sql
CREATE TABLE capabilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE, -- "data.csv.parse"
    display_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL, -- "data"
    subcategory VARCHAR(100), -- "csv"
    action VARCHAR(100) NOT NULL, -- "parse"
    description TEXT,
    parent_id UUID REFERENCES capabilities(id),
    
    -- Metadata
    examples JSONB DEFAULT '[]', -- Usage examples
    related_capabilities JSONB DEFAULT '[]', -- Related capability names
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_capabilities_category (category),
    INDEX idx_capabilities_parent (parent_id)
);
```

### 3. integrations
Track how solutions are used and configured in different contexts.

```sql
CREATE TABLE integrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    solution_id UUID NOT NULL REFERENCES solutions(id) ON DELETE CASCADE,
    project_name VARCHAR(255) NOT NULL,
    project_type VARCHAR(100), -- 'tekton_component', 'external', 'test'
    
    -- Configuration used
    configuration JSONB NOT NULL,
    wrapper_type VARCHAR(100), -- 'fastapi', 'mcp', 'direct'
    
    -- Results
    success BOOLEAN NOT NULL,
    error_message TEXT,
    performance_metrics JSONB, -- {"startup_time": 1.2, "memory_usage": 150}
    
    -- Metadata
    notes TEXT,
    created_by VARCHAR(255),
    environment JSONB, -- {"os": "darwin", "python": "3.11"}
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_integrations_solution (solution_id),
    INDEX idx_integrations_project (project_name),
    INDEX idx_integrations_success (success)
);
```

### 4. analyses
Store results from GitHub repository analyses.

```sql
CREATE TYPE analysis_status AS ENUM ('pending', 'processing', 'completed', 'failed');

CREATE TABLE analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    repository_url VARCHAR(500) NOT NULL,
    branch VARCHAR(100) DEFAULT 'main',
    commit_sha VARCHAR(40),
    
    -- Analysis status
    status analysis_status NOT NULL DEFAULT 'pending',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Results
    found_components JSONB DEFAULT '[]', -- Array of discovered components
    dependencies_found JSONB DEFAULT '{}',
    capabilities_detected JSONB DEFAULT '[]',
    integration_complexity INTEGER, -- 1-10 scale
    
    -- Metadata
    file_count INTEGER,
    total_lines INTEGER,
    primary_language VARCHAR(50),
    license_detected VARCHAR(100),
    security_issues JSONB DEFAULT '[]',
    
    -- Errors
    error_message TEXT,
    warnings JSONB DEFAULT '[]',
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP + INTERVAL '30 days',
    
    -- Indexes
    INDEX idx_analyses_repository (repository_url),
    INDEX idx_analyses_status (status),
    INDEX idx_analyses_expires (expires_at)
);
```

### 5. configurations
Store generated configurations and wrappers.

```sql
CREATE TYPE config_status AS ENUM ('draft', 'validated', 'deployed', 'archived');

CREATE TABLE configurations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    solution_id UUID NOT NULL REFERENCES solutions(id),
    
    -- Configuration details
    template_used VARCHAR(100) NOT NULL, -- 'fastapi_wrapper', 'mcp_adapter'
    configuration JSONB NOT NULL,
    generated_code TEXT, -- Actual generated wrapper code
    
    -- Validation
    status config_status NOT NULL DEFAULT 'draft',
    validation_errors JSONB DEFAULT '[]',
    test_results JSONB,
    
    -- Deployment info
    deployment_id VARCHAR(255), -- Apollo deployment ID
    deployment_url VARCHAR(500),
    port INTEGER,
    
    -- Usage
    times_deployed INTEGER DEFAULT 0,
    last_deployed_at TIMESTAMP,
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    
    -- Indexes
    INDEX idx_configurations_solution (solution_id),
    INDEX idx_configurations_status (status)
);
```

### 6. templates
Configuration and wrapper templates.

```sql
CREATE TABLE templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255) NOT NULL,
    type VARCHAR(100) NOT NULL, -- 'wrapper', 'configuration', 'deployment'
    language VARCHAR(50), -- 'python', 'javascript', 'go'
    
    -- Template content
    template_content TEXT NOT NULL,
    example_config JSONB,
    required_fields JSONB DEFAULT '[]',
    optional_fields JSONB DEFAULT '[]',
    
    -- Metadata
    description TEXT,
    use_cases JSONB DEFAULT '[]',
    compatible_solution_types JSONB DEFAULT '[]', -- ['tool', 'agent']
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_templates_type (type)
);
```

### 7. chat_sessions
Store Tool Chat interactions for context and learning.

```sql
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_type VARCHAR(50) NOT NULL, -- 'tool_chat', 'team_chat'
    
    -- Conversation
    messages JSONB NOT NULL DEFAULT '[]', -- Array of {role, content, timestamp}
    context JSONB DEFAULT '{}', -- Current context/state
    
    -- Results
    solutions_recommended JSONB DEFAULT '[]',
    configurations_generated JSONB DEFAULT '[]',
    user_satisfaction INTEGER, -- 1-5 rating
    
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_chat_sessions_type (session_type),
    INDEX idx_chat_sessions_created (created_at)
);
```

## Database Functions

### 1. Update timestamp trigger
```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply to tables with updated_at
CREATE TRIGGER update_solutions_updated_at BEFORE UPDATE ON solutions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    
CREATE TRIGGER update_configurations_updated_at BEFORE UPDATE ON configurations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 2. Increment usage counter
```sql
CREATE OR REPLACE FUNCTION increment_solution_usage(solution_id UUID, success BOOLEAN)
RETURNS VOID AS $$
BEGIN
    UPDATE solutions
    SET usage_count = usage_count + 1,
        success_count = CASE WHEN success THEN success_count + 1 ELSE success_count END,
        failure_count = CASE WHEN NOT success THEN failure_count + 1 ELSE failure_count END,
        last_used_at = CURRENT_TIMESTAMP
    WHERE id = solution_id;
END;
$$ language 'plpgsql';
```

### 3. Search by capabilities
```sql
CREATE OR REPLACE FUNCTION search_solutions_by_capabilities(
    required_capabilities TEXT[]
)
RETURNS TABLE(
    id UUID,
    name VARCHAR,
    type solution_type,
    capabilities JSONB,
    match_count INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.id,
        s.name,
        s.type,
        s.capabilities,
        cardinality(
            ARRAY(
                SELECT unnest(required_capabilities)
                INTERSECT
                SELECT jsonb_array_elements_text(s.capabilities)
            )
        ) as match_count
    FROM solutions s
    WHERE s.status = 'active'
        AND s.capabilities ?| required_capabilities
    ORDER BY match_count DESC, s.usage_count DESC;
END;
$$ language 'plpgsql';
```

## Indexes for Performance

```sql
-- Full text search on descriptions
CREATE INDEX idx_solutions_description_fts ON solutions 
    USING GIN(to_tsvector('english', description || ' ' || COALESCE(long_description, '')));

-- Composite indexes for common queries
CREATE INDEX idx_solutions_type_status ON solutions(type, status);
CREATE INDEX idx_integrations_solution_success ON integrations(solution_id, success);
CREATE INDEX idx_analyses_status_created ON analyses(status, created_at);
```

## Initial Data

```sql
-- Capability taxonomy
INSERT INTO capabilities (name, display_name, category, subcategory, action) VALUES
('file.read', 'Read File', 'file', NULL, 'read'),
('file.write', 'Write File', 'file', NULL, 'write'),
('data.csv.parse', 'Parse CSV', 'data', 'csv', 'parse'),
('data.json.parse', 'Parse JSON', 'data', 'json', 'parse'),
('chart.generate', 'Generate Chart', 'visualization', 'chart', 'generate'),
('api.rest.create', 'Create REST API', 'api', 'rest', 'create');

-- Default templates
INSERT INTO templates (name, display_name, type, language, template_content) VALUES
('fastapi_wrapper', 'FastAPI Wrapper', 'wrapper', 'python', '...template content...'),
('mcp_adapter', 'MCP Server Adapter', 'wrapper', 'python', '...template content...');
```