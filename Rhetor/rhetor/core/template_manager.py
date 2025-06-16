"""Template Manager for Rhetor.

This module provides a robust template management system with versioning,
categorization, and flexible variable interpolation.
"""

import os
import json
import yaml
import logging
import shutil
import jinja2
from typing import Dict, List, Optional, Union, Any, Tuple
from pathlib import Path
from datetime import datetime
import uuid
import re

logger = logging.getLogger(__name__)

class TemplateVersion:
    """Represents a specific version of a template with metadata."""

    def __init__(
        self,
        content: str,
        version_id: Optional[str] = None,
        created_at: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize a template version.
        
        Args:
            content: The template content
            version_id: Unique identifier for this version
            created_at: Timestamp when this version was created
            metadata: Additional metadata for this version
        """
        self.content = content
        self.version_id = version_id or str(uuid.uuid4())
        self.created_at = created_at or datetime.now().isoformat()
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the version to a dictionary for serialization."""
        return {
            "content": self.content,
            "version_id": self.version_id,
            "created_at": self.created_at,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TemplateVersion':
        """Create a version from a dictionary."""
        return cls(
            content=data["content"],
            version_id=data.get("version_id"),
            created_at=data.get("created_at"),
            metadata=data.get("metadata", {})
        )


class Template:
    """A template with versioning support."""

    def __init__(
        self,
        template_id: str,
        name: str,
        description: Optional[str] = None,
        category: Optional[str] = None,
        variables: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        current_version: Optional[TemplateVersion] = None,
        versions: Optional[List[TemplateVersion]] = None
    ):
        """Initialize a template.
        
        Args:
            template_id: Unique identifier for the template
            name: Human-readable name
            description: Optional description
            category: Optional category (system, task, component)
            variables: Optional list of variables used in the template
            tags: Optional tags for categorization
            current_version: The current version of the template
            versions: List of historical versions
        """
        self.template_id = template_id
        self.name = name
        self.description = description or ""
        self.category = category or "general"
        self.variables = variables or []
        self.tags = tags or []
        self.versions = versions or []
        
        # Create initial version if needed
        if current_version:
            self.versions.append(current_version)
        elif not self.versions:
            self.versions.append(TemplateVersion(
                content="",
                metadata={"created_by": "system", "note": "Initial empty version"}
            ))
    
    @property
    def current_version(self) -> TemplateVersion:
        """Get the current (latest) version of the template."""
        if not self.versions:
            raise ValueError(f"Template '{self.template_id}' has no versions")
        return self.versions[-1]
    
    @property
    def content(self) -> str:
        """Get the content of the current version."""
        return self.current_version.content
    
    def add_version(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> TemplateVersion:
        """Add a new version of the template.
        
        Args:
            content: The template content
            metadata: Additional metadata for this version
            
        Returns:
            The new version
        """
        # Extract variables from content
        self._update_variables(content)
        
        # Create the new version
        version = TemplateVersion(
            content=content,
            metadata=metadata or {}
        )
        
        # Add to versions list
        self.versions.append(version)
        
        return version
    
    def _update_variables(self, content: str) -> None:
        """Update the variables list based on template content."""
        # Find Jinja2 variables
        pattern = r'{{\s*(\w+)\s*}}'
        found_vars = set(re.findall(pattern, content))
        
        # Add any new variables
        for var in found_vars:
            if var not in self.variables:
                self.variables.append(var)
    
    def get_version(self, version_id: str) -> Optional[TemplateVersion]:
        """Get a specific version by ID."""
        for version in self.versions:
            if version.version_id == version_id:
                return version
        return None
    
    def revert_to_version(self, version_id: str, metadata: Optional[Dict[str, Any]] = None) -> Optional[TemplateVersion]:
        """Revert to a previous version, creating a new version with the same content.
        
        Args:
            version_id: ID of the version to revert to
            metadata: Additional metadata for the new version
            
        Returns:
            The new version or None if target version not found
        """
        target_version = self.get_version(version_id)
        if not target_version:
            return None
        
        # Create metadata if not provided
        if not metadata:
            metadata = {
                "reverted_from": version_id,
                "revert_date": datetime.now().isoformat(),
                "note": f"Reverted to version {version_id}"
            }
        
        # Create new version with content from target
        return self.add_version(target_version.content, metadata)
    
    def render(
        self,
        variables: Dict[str, Any],
        version_id: Optional[str] = None,
        strict: bool = False
    ) -> str:
        """Render the template with provided variables.
        
        Args:
            variables: Dictionary of variables to use for rendering
            version_id: Optional specific version to render
            strict: If True, raise error for missing variables
            
        Returns:
            Rendered template string
            
        Raises:
            ValueError: If strict and missing variables
        """
        # Get the content to render
        if version_id:
            version = self.get_version(version_id)
            if not version:
                raise ValueError(f"Version '{version_id}' not found")
            content = version.content
        else:
            content = self.current_version.content
        
        # Create Jinja2 environment
        env = jinja2.Environment(
            undefined=jinja2.StrictUndefined if strict else jinja2.Undefined
        )
        
        try:
            # Render template
            template = env.from_string(content)
            return template.render(**variables)
        except jinja2.exceptions.UndefinedError as e:
            if strict:
                raise ValueError(f"Missing required variables: {str(e)}")
            # Replace undefined variables with empty string
            env = jinja2.Environment(undefined=jinja2.ChainableUndefined)
            template = env.from_string(content)
            return template.render(**variables)
    
    def to_dict(self, include_versions: bool = True) -> Dict[str, Any]:
        """Convert the template to a dictionary for serialization.
        
        Args:
            include_versions: Whether to include all versions
        
        Returns:
            Dictionary representation
        """
        result = {
            "template_id": self.template_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "variables": self.variables,
            "tags": self.tags,
            "current_version": self.current_version.to_dict()
        }
        
        if include_versions:
            result["versions"] = [v.to_dict() for v in self.versions]
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Template':
        """Create a template from a dictionary."""
        # Process versions if present
        versions = None
        if "versions" in data:
            versions = [TemplateVersion.from_dict(v) for v in data["versions"]]
        
        # Create the template
        return cls(
            template_id=data["template_id"],
            name=data["name"],
            description=data.get("description", ""),
            category=data.get("category", "general"),
            variables=data.get("variables", []),
            tags=data.get("tags", []),
            versions=versions,
            # Add current_version only if versions not provided
            current_version=None if versions else TemplateVersion.from_dict(data["current_version"])
        )


class TemplateManager:
    """Manager for template storage, retrieval, and versioning."""

    def __init__(self, base_dir: Optional[str] = None):
        """Initialize the template manager.
        
        Args:
            base_dir: Base directory for template storage
        """
        # Set default base directory if not provided
        if not base_dir:
            base_dir = os.path.join(
                os.environ.get('TEKTON_DATA_DIR', 
                              os.path.join(os.environ.get('TEKTON_ROOT', os.path.expanduser('~')), '.tekton', 'data')),
                'rhetor', 'templates'
            )
        
        self.base_dir = Path(base_dir)
        self.templates: Dict[str, Template] = {}
        
        # Create template directories if they don't exist
        self._ensure_directories()
        
        # Load existing templates
        self.load_all_templates()
    
    def _ensure_directories(self) -> None:
        """Ensure all necessary directories exist."""
        categories = ["system", "task", "component", "user", "general"]
        
        # Create base directory
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Create category subdirectories
        for category in categories:
            category_dir = self.base_dir / category
            category_dir.mkdir(exist_ok=True)
    
    def get_template_path(self, template: Template) -> Path:
        """Get the file path for a template.
        
        Args:
            template: The template
            
        Returns:
            Path object for the template file
        """
        return self.base_dir / template.category / f"{template.template_id}.yaml"
    
    def load_all_templates(self) -> int:
        """Load all templates from disk.
        
        Returns:
            Number of templates loaded
        """
        count = 0
        
        # Iterate through all category directories
        for category_dir in self.base_dir.iterdir():
            if category_dir.is_dir():
                # Load templates from this category
                for file_path in category_dir.glob("*.yaml"):
                    try:
                        template = self.load_template_from_file(file_path)
                        if template:
                            self.templates[template.template_id] = template
                            count += 1
                    except Exception as e:
                        logger.warning(f"Error loading template from {file_path}: {e}")
        
        logger.info(f"Loaded {count} templates from {self.base_dir}")
        return count
    
    def load_template_from_file(self, file_path: Union[str, Path]) -> Optional[Template]:
        """Load a template from a file.
        
        Args:
            file_path: Path to the template file
            
        Returns:
            Loaded template or None if error
        """
        path = Path(file_path)
        if not path.exists():
            return None
        
        try:
            with open(path, 'r') as f:
                if path.suffix.lower() == '.yaml':
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
            
            template = Template.from_dict(data)
            return template
        
        except Exception as e:
            logger.error(f"Error loading template from {path}: {e}")
            return None
    
    def save_template(self, template: Template) -> bool:
        """Save a template to disk.
        
        Args:
            template: The template to save
            
        Returns:
            Success status
        """
        file_path = self.get_template_path(template)
        
        try:
            # Create temporary dict to save
            data = template.to_dict()
            
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create backup of existing file
            if file_path.exists():
                backup_path = file_path.with_suffix(f".backup.{int(datetime.now().timestamp())}")
                shutil.copy2(file_path, backup_path)
            
            # Write to file
            with open(file_path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(f"Saved template '{template.name}' to {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error saving template to {file_path}: {e}")
            return False
    
    def create_template(
        self,
        name: str,
        content: str,
        category: str = "general",
        description: str = "",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Template:
        """Create a new template.
        
        Args:
            name: Template name
            content: Initial template content
            category: Template category
            description: Template description
            tags: Optional tags
            metadata: Optional metadata for initial version
            
        Returns:
            Newly created template
        """
        # Generate a safe template ID from name
        template_id = self._safe_template_id(name)
        
        # Check if template already exists
        if template_id in self.templates:
            # Add a unique suffix
            base_id = template_id
            suffix = 1
            while template_id in self.templates:
                template_id = f"{base_id}_{suffix}"
                suffix += 1
        
        # Create initial version
        initial_version = TemplateVersion(
            content=content,
            metadata=metadata or {"created_by": "user"}
        )
        
        # Create the template
        template = Template(
            template_id=template_id,
            name=name,
            description=description,
            category=category,
            tags=tags or [],
            current_version=initial_version
        )
        
        # Extract variables from content
        template._update_variables(content)
        
        # Store in memory
        self.templates[template_id] = template
        
        # Save to disk
        self.save_template(template)
        
        return template
    
    def update_template(
        self,
        template_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Template]:
        """Update an existing template with a new version.
        
        Args:
            template_id: Template identifier
            content: New content
            metadata: Optional metadata for the new version
            
        Returns:
            Updated template or None if not found
        """
        if template_id not in self.templates:
            return None
        
        template = self.templates[template_id]
        
        # Add a new version
        template.add_version(content, metadata)
        
        # Save to disk
        self.save_template(template)
        
        return template
    
    def get_template(self, template_id: str) -> Optional[Template]:
        """Get a template by ID.
        
        Args:
            template_id: Template identifier
            
        Returns:
            Template or None if not found
        """
        return self.templates.get(template_id)
    
    def delete_template(self, template_id: str) -> bool:
        """Delete a template.
        
        Args:
            template_id: Template identifier
            
        Returns:
            Success status
        """
        if template_id not in self.templates:
            return False
        
        template = self.templates[template_id]
        file_path = self.get_template_path(template)
        
        try:
            # Remove from memory
            del self.templates[template_id]
            
            # Remove from disk
            if file_path.exists():
                file_path.unlink()
            
            logger.info(f"Deleted template '{template_id}'")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting template '{template_id}': {e}")
            return False
    
    def list_templates(
        self,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """List templates with optional filtering.
        
        Args:
            category: Optional category filter
            tags: Optional tags filter
            
        Returns:
            List of template summary dictionaries
        """
        results = []
        
        for template_id, template in self.templates.items():
            # Apply category filter
            if category and template.category != category:
                continue
            
            # Apply tags filter
            if tags and not all(tag in template.tags for tag in tags):
                continue
            
            # Add to results
            results.append({
                "template_id": template_id,
                "name": template.name,
                "category": template.category,
                "description": template.description,
                "variables": template.variables,
                "tags": template.tags,
                "version_count": len(template.versions),
                "last_updated": template.current_version.created_at
            })
        
        # Sort by name
        results.sort(key=lambda x: x["name"])
        
        return results
    
    def render_template(
        self,
        template_id: str,
        variables: Dict[str, Any],
        version_id: Optional[str] = None,
        strict: bool = False
    ) -> Optional[str]:
        """Render a template with provided variables.
        
        Args:
            template_id: Template identifier
            variables: Variables for rendering
            version_id: Optional specific version to render
            strict: If True, raise error for missing variables
            
        Returns:
            Rendered template or None if error
        """
        template = self.get_template(template_id)
        if not template:
            return None
        
        try:
            return template.render(variables, version_id, strict)
        
        except Exception as e:
            logger.error(f"Error rendering template '{template_id}': {e}")
            return None
    
    def _safe_template_id(self, name: str) -> str:
        """Generate a safe template ID from a name.
        
        Args:
            name: Template name
            
        Returns:
            Safe template ID
        """
        # Convert to lowercase, replace spaces and non-alphanumeric chars
        safe_id = re.sub(r'[^a-z0-9_]', '_', name.lower())
        # Remove repeated underscores
        safe_id = re.sub(r'_+', '_', safe_id)
        # Remove leading/trailing underscores
        safe_id = safe_id.strip('_')
        # Ensure not empty
        if not safe_id:
            safe_id = "template"
        return safe_id
    
    def get_category_templates(self, category: str) -> List[Template]:
        """Get all templates in a category.
        
        Args:
            category: Category name
            
        Returns:
            List of templates in the category
        """
        return [t for t in self.templates.values() if t.category == category]
    
    def search_templates(self, query: str) -> List[Dict[str, Any]]:
        """Search templates by name, description, or tags.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching template summaries
        """
        query = query.lower()
        results = []
        
        for template in self.templates.values():
            # Check for match in name, description, or tags
            if (query in template.name.lower() or
                query in template.description.lower() or
                any(query in tag.lower() for tag in template.tags)):
                
                results.append({
                    "template_id": template.template_id,
                    "name": template.name,
                    "category": template.category,
                    "description": template.description,
                    "version_count": len(template.versions),
                    "last_updated": template.current_version.created_at
                })
        
        return results
    
    def import_template(self, source_path: Union[str, Path]) -> Optional[Template]:
        """Import a template from a file.
        
        Args:
            source_path: Path to the template file
            
        Returns:
            Imported template or None if error
        """
        source = Path(source_path)
        if not source.exists():
            logger.error(f"Source file not found: {source}")
            return None
        
        try:
            # Load the template
            template = self.load_template_from_file(source)
            if not template:
                return None
            
            # Add to managed templates
            self.templates[template.template_id] = template
            
            # Save to appropriate location
            self.save_template(template)
            
            return template
        
        except Exception as e:
            logger.error(f"Error importing template from {source}: {e}")
            return None
    
    def export_template(
        self,
        template_id: str,
        destination: Union[str, Path],
        format: str = "yaml"
    ) -> bool:
        """Export a template to a file.
        
        Args:
            template_id: Template identifier
            destination: Destination file path
            format: Output format (yaml or json)
            
        Returns:
            Success status
        """
        template = self.get_template(template_id)
        if not template:
            return False
        
        dest_path = Path(destination)
        
        try:
            # Create parent directory if needed
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Get template data
            data = template.to_dict()
            
            # Write to file in specified format
            with open(dest_path, 'w') as f:
                if format.lower() == 'json':
                    json.dump(data, f, indent=2)
                else:
                    yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(f"Exported template '{template_id}' to {dest_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error exporting template '{template_id}': {e}")
            return False