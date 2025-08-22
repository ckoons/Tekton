# Ergon Registry System Guide

## Overview

The Ergon Registry is a centralized storage system for all deployable units in the Tekton ecosystem. It provides JSON-based universal storage, automatic standards compliance checking, and solution lineage tracking. The Registry serves as the foundation for the Construct system and enables solution reuse across projects.

## Architecture

### Core Components

1. **Storage Layer (`ergon/registry/storage.py`)**
   - SQLite-based persistent storage
   - JSON schema validation
   - CRUD operations with safeguards
   - Lineage tracking

2. **Schema Definition (`ergon/registry/schema.py`)**
   - Pydantic models for type safety
   - Validation rules
   - Standard fields for all entries

3. **Standards Engine (`ergon/registry/standards.py`)**
   - Tekton standards compliance checking
   - Scoring algorithm
   - Automated recommendations

4. **API Layer (`ergon/api/registry.py`)**
   - RESTful endpoints
   - TektonCore integration
   - Search and filtering

## Registry Schema

### Base Structure
```json
{
    "id": "uuid",
    "type": "container|solution|tool|config",
    "version": "1.0.0",
    "name": "Human Readable Name",
    "created": "2025-01-20T10:00:00Z",
    "updated": "2025-01-20T12:00:00Z",
    "meets_standards": true,
    "lineage": ["parent_id", "grandparent_id"],
    "source": {
        "project_id": "tekton_core_project_id",
        "sprint_id": "development_sprint_id",
        "location": "local_path_or_github_url"
    },
    "content": {
        // Type-specific content
    }
}
```

### Content Types

#### Solution Type
```json
{
    "content": {
        "description": "AI-powered code analysis tool",
        "code": "def main():\n    pass",
        "main_file": "solution.py",
        "requirements": ["requests", "numpy"],
        "run_command": ["python", "solution.py"],
        "requires_network": true,
        "requires_gpu": false,
        "platform": "any",
        "memory_limit": "2g"
    }
}
```

#### Container Type
```json
{
    "content": {
        "dockerfile": "FROM python:3.11\n...",
        "base_image": "python:3.11-slim",
        "ports": [8080, 9090],
        "environment": {
            "API_KEY": "${ERGON_API_KEY}"
        },
        "volumes": ["/data", "/config"]
    }
}
```

#### Tool Type
```json
{
    "content": {
        "executable": "ergon-tool",
        "arguments": ["--help"],
        "installation": "pip install ergon-tool",
        "documentation": "https://docs.example.com"
    }
}
```

## API Endpoints

### Core Operations

```python
# Store a new entry
POST /api/ergon/registry/store
{
    "type": "solution",
    "name": "My Solution",
    "version": "1.0.0",
    "content": {...}
}

# Retrieve an entry
GET /api/ergon/registry/{entry_id}

# Search entries
GET /api/ergon/registry/search?type=solution&name=analyzer&meets_standards=true

# List all types
GET /api/ergon/registry/types

# Delete an entry (with dependency checking)
DELETE /api/ergon/registry/{entry_id}

# Get solution lineage
GET /api/ergon/registry/{entry_id}/lineage
```

### Standards Operations

```python
# Check standards compliance
POST /api/ergon/registry/{entry_id}/check-standards

# Get standards report
GET /api/ergon/registry/{entry_id}/standards-report
```

### TektonCore Integration

```python
# Import completed projects
POST /api/ergon/registry/import-completed

# Auto-import from specific project
POST /api/ergon/registry/import-project/{project_id}
```

## Workflow Integration

### Automatic Import Flow
```
TektonCore Project → Status: Complete → Registry Import → Standards Check → Available for Use
```

1. **Project Completion**: TektonCore marks project as complete
2. **Auto-Detection**: Registry monitors for completed projects
3. **Metadata Extraction**: Pull solution details from sprints
4. **Entry Creation**: Store in Registry with provenance
5. **Standards Check**: Automatic compliance validation
6. **Ready for Use**: Available in Registry UI and Construct

### Standards Compliance Flow
```
New Entry → Standards Check → Score < 100 → Create Refactor Sprint → Improved Version
```

1. **Initial Check**: Every new entry is checked
2. **Scoring**: 0-100 score based on standards
3. **Non-Compliant**: Score < 100 triggers action
4. **Refactor Sprint**: Automatic task creation
5. **New Version**: Improved version with lineage

## UI Integration

### Registry Tab Features
- **Browse by Type**: Filter solutions, containers, tools
- **Search**: Full-text search across names and descriptions
- **Standards Badges**: Visual compliance indicators
- **Test Buttons**: One-click sandbox testing
- **Import Status**: TektonCore sync status
- **Statistics**: Total solutions, compliance rates

### Solution Cards Display
```html
<div class="ergon__solution-card">
    <h4>Solution Name</h4>
    <span class="type">solution</span>
    <span class="version">v1.0.0</span>
    <span class="badge">✓ Standards</span>
    <p>Description of the solution...</p>
    <button>Test</button>
    <button>Details</button>
    <button>Check</button>
</div>
```

## Standards System

### Compliance Checks
1. **Code Quality**: Proper structure, documentation
2. **Security**: No hardcoded secrets, safe practices
3. **Performance**: Efficient algorithms, resource usage
4. **Maintainability**: Clear naming, modular design
5. **Testing**: Test coverage, examples provided

### Scoring Algorithm
```python
score = 0
score += 20 if has_documentation else 0
score += 20 if has_tests else 0
score += 20 if follows_naming_conventions else 0
score += 20 if no_security_issues else 0
score += 20 if efficient_code else 0
```

## Lineage Tracking

### Version Management
- **Never modify existing entries** - always create new versions
- **Parent references** maintained in lineage array
- **Complete history** from original to current

### Lineage Example
```
Original (v1.0.0) → Refactored (v1.1.0) → Optimized (v2.0.0)
         ↓                    ↓                    ↓
    [No parent]      [parent: v1.0.0]    [parent: v1.1.0]
```

## Best Practices

### Adding to Registry
1. **Complete metadata**: Fill all relevant fields
2. **Clear descriptions**: Explain what the solution does
3. **Specify requirements**: List all dependencies
4. **Include examples**: Provide usage examples
5. **Test first**: Verify in sandbox before storing

### Searching Registry
1. **Use filters**: Type, standards, date ranges
2. **Check lineage**: Find the latest version
3. **Review standards**: Prefer compliant solutions
4. **Test before use**: Verify in your environment

### Maintaining Quality
1. **Regular reviews**: Check for outdated solutions
2. **Update metadata**: Keep descriptions current
3. **Fix non-compliance**: Address standards issues
4. **Archive obsolete**: Mark deprecated solutions

## Database Schema

### Registry Table
```sql
CREATE TABLE registry (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    version TEXT,
    name TEXT,
    created TEXT,
    updated TEXT,
    meets_standards BOOLEAN DEFAULT 0,
    lineage TEXT,  -- JSON array
    source TEXT,    -- JSON object
    content TEXT    -- JSON object
);

CREATE INDEX idx_type ON registry(type);
CREATE INDEX idx_name ON registry(name);
CREATE INDEX idx_standards ON registry(meets_standards);
```

## Development

### Adding Custom Types
1. Define content schema in `schema.py`
2. Add validation rules
3. Update UI to handle new type
4. Document type-specific fields

### Extending Standards
1. Add check to `standards.py`
2. Update scoring algorithm
3. Provide fix recommendations
4. Test with existing entries

## Troubleshooting

### Common Issues

1. **"Entry not found"**
   - Check ID is correct
   - Verify entry wasn't deleted
   - Search by name if ID unknown

2. **"Validation error"**
   - Check required fields
   - Validate JSON structure
   - Review type-specific requirements

3. **"Import failed"**
   - Verify TektonCore connection
   - Check project is complete
   - Review project metadata

4. **"Standards check timeout"**
   - Large solution may take time
   - Check background process
   - Retry if needed

## Future Enhancements

- [ ] Version comparison and diff viewing
- [ ] Automated dependency resolution
- [ ] Solution templates and wizards
- [ ] Registry federation across Tekton instances
- [ ] Machine learning for standards improvement
- [ ] Solution marketplace with ratings
- [ ] Git-based version control integration
- [ ] Automated testing pipelines