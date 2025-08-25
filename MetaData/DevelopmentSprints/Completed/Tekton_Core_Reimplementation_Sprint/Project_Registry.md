# Project Registry Specification

## Overview

The Project Registry is the central source of truth for all projects managed by tekton-core. It uses simple JSON storage initially, with a clear upgrade path when needed.

## Storage Location

```
~/.tekton/projects/
├── registry.json           # Main project registry
├── chats/                  # Chat histories
│   ├── tekton-main.json
│   ├── python-sdk.json
│   └── team-chat.json
└── backups/               # Automatic backups
    └── registry-20250105.json
```

## Registry Format

### Main Registry File
```json
{
  "version": "1.0",
  "last_updated": "2025-01-05T15:30:00Z",
  "projects": {
    "tekton-main": {
      "id": "tekton-main",
      "name": "Tekton",
      "repo": "https://github.com/casey/Tekton",
      "upstream": null,
      "working_dir": "/Users/casey/projects/github/Tekton",
      "companion_ai": "numa",
      "created_at": "2025-01-05T10:00:00Z",
      "last_activity": "2025-01-05T15:30:00Z",
      "metadata": {
        "description": "Multi-CI Engineering Platform",
        "language": "python",
        "type": "platform"
      },
      "status": {
        "branch": "main",
        "clean": true,
        "last_commit": "abc123",
        "uncommitted_changes": 0
      },
      "team": {
        "active_members": ["alice", "bob"],
        "companion_ai": "numa",
        "recent_contributors": ["apollo", "athena"]
      },
      "github": {
        "open_prs": [234, 235],
        "open_issues": [123, 124, 125],
        "stars": 42,
        "last_synced": "2025-01-05T15:00:00Z"
      }
    },
    "new-github-project": {
      "id": "new-github-project",
      "name": "New GitHub Project",
      "type": "template",
      "special": true,
      "metadata": {
        "description": "Click to add a new GitHub project",
        "icon": "plus"
      }
    }
  }
}
```

### Chat History Format
```json
{
  "project_id": "tekton-main",
  "type": "project",
  "participants": ["alice", "bob", "numa"],
  "message_count": 156,
  "messages": [
    {
      "id": "msg-2025-01-05-001",
      "timestamp": "2025-01-05T10:30:00Z",
      "sender": "alice",
      "sender_type": "ai",
      "content": "Starting work on authentication module",
      "metadata": {
        "terminal_id": "terma-001",
        "related_issue": 123
      }
    },
    {
      "id": "msg-2025-01-05-002",
      "timestamp": "2025-01-05T10:31:00Z",
      "sender": "numa",
      "sender_type": "ai",
      "content": "Good choice. Remember to follow our security patterns.",
      "metadata": {
        "in_reply_to": "msg-2025-01-05-001"
      }
    }
  ]
}
```

## Operations

### Creating a Project
```python
def create_project(self, config):
    """Create new project entry"""
    project_id = generate_id(config['name'])
    
    project = {
        'id': project_id,
        'name': config['name'],
        'repo': config['repo'],
        'upstream': config.get('upstream'),
        'working_dir': config['working_dir'],
        'companion_ai': config.get('companion_ai', 'numa'),
        'created_at': datetime.now().isoformat(),
        'last_activity': datetime.now().isoformat(),
        'metadata': {
            'description': config.get('description', ''),
            'language': detect_language(config['working_dir']),
            'type': config.get('type', 'project')
        },
        'status': {
            'branch': 'main',
            'clean': True
        },
        'team': {
            'active_members': [],
            'companion_ai': config.get('companion_ai', 'numa')
        },
        'github': {
            'open_prs': [],
            'open_issues': []
        }
    }
    
    # Add to registry
    self.registry['projects'][project_id] = project
    self.save()
    
    return project_id
```

### Cloning a Project
```python
def clone_project(self, source_id, new_config):
    """Clone existing project"""
    source = self.get_project(source_id)
    
    # Create new project based on source
    new_project = deep_copy(source)
    new_project.update({
        'id': generate_id(new_config['name']),
        'name': new_config['name'],
        'repo': new_config['repo'],
        'working_dir': new_config['working_dir'],
        'created_at': datetime.now().isoformat(),
        'upstream': source['repo']  # Original becomes upstream
    })
    
    # Reset statistics
    new_project['github'] = {
        'open_prs': [],
        'open_issues': []
    }
    new_project['team']['active_members'] = []
    
    self.registry['projects'][new_project['id']] = new_project
    self.save()
    
    return new_project['id']
```

### Updating Project Status
```python
def update_project_status(self, project_id):
    """Update project status from git"""
    project = self.get_project(project_id)
    working_dir = project['working_dir']
    
    # Get git status
    status = {
        'branch': get_current_branch(working_dir),
        'clean': is_working_tree_clean(working_dir),
        'last_commit': get_last_commit_hash(working_dir),
        'uncommitted_changes': count_uncommitted_changes(working_dir)
    }
    
    project['status'] = status
    project['last_activity'] = datetime.now().isoformat()
    
    self.save()
```

## Backup Strategy

### Automatic Backups
```python
def save(self):
    """Save registry with automatic backup"""
    # Create backup if significant time passed
    if self.should_backup():
        backup_path = self.backup_dir / f"registry-{date.today()}.json"
        shutil.copy(self.registry_path, backup_path)
    
    # Atomic write
    temp_path = self.registry_path.with_suffix('.tmp')
    with open(temp_path, 'w') as f:
        json.dump(self.registry, f, indent=2)
    
    # Replace original
    temp_path.replace(self.registry_path)
```

### Recovery
```python
def recover_from_backup(self, backup_date=None):
    """Restore from backup"""
    if backup_date:
        backup_file = self.backup_dir / f"registry-{backup_date}.json"
    else:
        # Get most recent backup
        backups = sorted(self.backup_dir.glob("registry-*.json"))
        backup_file = backups[-1] if backups else None
    
    if backup_file and backup_file.exists():
        shutil.copy(backup_file, self.registry_path)
        self.load()
        return True
    return False
```

## Migration Path

### To SQLite (When Needed)
```python
# When JSON becomes unwieldy (>100 projects or >10MB)
def migrate_to_sqlite(self):
    """Migrate JSON registry to SQLite"""
    import sqlite3
    
    conn = sqlite3.connect(self.data_dir / 'projects.db')
    
    # Create schema
    conn.execute('''
        CREATE TABLE projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            data JSON NOT NULL,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        )
    ''')
    
    # Migrate data
    for project_id, project in self.registry['projects'].items():
        conn.execute(
            'INSERT INTO projects VALUES (?, ?, ?, ?, ?)',
            (project_id, project['name'], json.dumps(project),
             project['created_at'], project['last_activity'])
        )
    
    conn.commit()
```

## Access Patterns

### Fast Lookups
```python
# In-memory index for quick access
class ProjectRegistry:
    def __init__(self):
        self.load()
        self._build_indices()
    
    def _build_indices(self):
        # Name -> ID mapping
        self.name_index = {
            p['name']: pid 
            for pid, p in self.registry['projects'].items()
        }
        
        # Repo -> ID mapping  
        self.repo_index = {
            p['repo']: pid
            for pid, p in self.registry['projects'].items()
        }
```

### Query Helpers
```python
def find_projects_by_ai(self, ai_name):
    """Find all projects with specific companion AI"""
    return [
        p for p in self.registry['projects'].values()
        if p.get('companion_ai') == ai_name
    ]

def get_active_projects(self):
    """Get projects with recent activity"""
    cutoff = datetime.now() - timedelta(days=7)
    return [
        p for p in self.registry['projects'].values()
        if datetime.fromisoformat(p['last_activity']) > cutoff
    ]
```

## Best Practices

1. **Atomic Writes**: Always write to temp file first
2. **Validation**: Validate data before saving
3. **Backups**: Daily automatic backups
4. **Indices**: Maintain in-memory indices for speed
5. **Versioning**: Include version field for migrations

---
*"Simple storage for a simple start"*