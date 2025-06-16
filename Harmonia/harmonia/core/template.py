"""
Template management for Harmonia.

This module provides functionality for managing workflow templates,
including template creation, versioning, and instantiation.
"""

import logging
import json
from typing import Dict, List, Optional, Union, Any
from uuid import UUID

from harmonia.models.template import (
    Template,
    TemplateVersion,
    TemplateCategory,
    TemplateInstantiation,
    ParameterDefinition
)
from harmonia.models.workflow import WorkflowDefinition
from harmonia.core.expressions import evaluate_expression, substitute_parameters

# Configure logger
logger = logging.getLogger(__name__)


class TemplateManager:
    """
    Manager for workflow templates.
    
    This class provides methods for creating, updating, versioning,
    and instantiating workflow templates.
    """
    
    def __init__(self, storage_manager=None):
        """
        Initialize the template manager.
        
        Args:
            storage_manager: Manager for storing templates
        """
        self.storage_manager = storage_manager
        self.templates: Dict[UUID, Template] = {}
        self.categories: Dict[UUID, TemplateCategory] = {}
        self.instantiations: Dict[UUID, TemplateInstantiation] = {}
        
        # Load templates if storage manager is provided
        if self.storage_manager:
            self._load_templates()
    
    def _load_templates(self) -> None:
        """Load templates from storage."""
        if not self.storage_manager:
            return
            
        try:
            # Load templates
            templates_data = self.storage_manager.load_templates()
            for template_data in templates_data:
                template = Template.parse_obj(template_data)
                self.templates[template.id] = template
                
            # Load categories
            categories_data = self.storage_manager.load_categories()
            for category_data in categories_data:
                category = TemplateCategory.parse_obj(category_data)
                self.categories[category.id] = category
                
            # Load instantiations
            instantiations_data = self.storage_manager.load_instantiations()
            for instantiation_data in instantiations_data:
                instantiation = TemplateInstantiation.parse_obj(instantiation_data)
                self.instantiations[instantiation.id] = instantiation
                
            logger.info(
                f"Loaded {len(self.templates)} templates, {len(self.categories)} categories, "
                f"and {len(self.instantiations)} instantiations"
            )
        except Exception as e:
            logger.error(f"Error loading templates: {e}")
    
    def save_template(self, template: Template) -> bool:
        """
        Save a template to storage.
        
        Args:
            template: Template to save
            
        Returns:
            True if saved successfully
        """
        self.templates[template.id] = template
        
        if self.storage_manager:
            try:
                self.storage_manager.save_template(template.dict())
                return True
            except Exception as e:
                logger.error(f"Error saving template: {e}")
                return False
        return True
    
    def get_template(self, template_id: UUID) -> Optional[Template]:
        """
        Get a template by ID.
        
        Args:
            template_id: ID of the template to get
            
        Returns:
            Template if found, None otherwise
        """
        return self.templates.get(template_id)
    
    def get_templates(self, category_id: Optional[UUID] = None, tags: Optional[List[str]] = None) -> List[Template]:
        """
        Get templates, optionally filtered by category or tags.
        
        Args:
            category_id: Category ID to filter by
            tags: Tags to filter by
            
        Returns:
            List of matching templates
        """
        templates = list(self.templates.values())
        
        # Filter by category
        if category_id:
            templates = [t for t in templates if category_id in t.category_ids]
        
        # Filter by tags
        if tags:
            templates = [t for t in templates if all(tag in t.tags for tag in tags)]
        
        return templates
    
    def create_template(
        self,
        name: str,
        workflow_definition: WorkflowDefinition,
        description: Optional[str] = None,
        parameters: Dict[str, ParameterDefinition] = None,
        category_ids: List[UUID] = None,
        tags: List[str] = None,
        is_public: bool = True,
        created_by: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ) -> Template:
        """
        Create a new template.
        
        Args:
            name: Name of the template
            workflow_definition: Base workflow definition
            description: Description of the template
            parameters: Parameters for the template
            category_ids: Categories for the template
            tags: Tags for the template
            is_public: Whether the template is public
            created_by: User who created the template
            metadata: Additional metadata
            
        Returns:
            Created template
        """
        # Create initial version
        version = TemplateVersion(
            version="1.0.0",
            workflow_definition=workflow_definition,
            is_latest=True
        )
        
        # Create template
        template = Template(
            name=name,
            description=description,
            parameters=parameters or {},
            current_version="1.0.0",
            versions={"1.0.0": version},
            category_ids=category_ids or [],
            tags=tags or [],
            is_public=is_public,
            created_by=created_by,
            metadata=metadata or {}
        )
        
        # Save template
        self.save_template(template)
        
        logger.info(f"Created template '{name}' with ID {template.id}")
        return template
    
    def create_template_version(
        self,
        template_id: UUID,
        workflow_definition: WorkflowDefinition,
        version: str,
        changes: Optional[str] = None
    ) -> Optional[Template]:
        """
        Create a new version of a template.
        
        Args:
            template_id: ID of the template
            workflow_definition: Updated workflow definition
            version: Version string (e.g., "1.1.0")
            changes: Description of changes
            
        Returns:
            Updated template if successful, None otherwise
        """
        template = self.get_template(template_id)
        if not template:
            logger.error(f"Template with ID {template_id} not found")
            return None
        
        # Check if version already exists
        if version in template.versions:
            logger.error(f"Version {version} already exists for template {template_id}")
            return None
        
        # Set all existing versions to not be latest
        for v in template.versions.values():
            v.is_latest = False
        
        # Create new version
        new_version = TemplateVersion(
            version=version,
            workflow_definition=workflow_definition,
            is_latest=True,
            changes=changes
        )
        
        # Update template
        template.versions[version] = new_version
        template.current_version = version
        template.updated_at = new_version.created_at
        
        # Save template
        self.save_template(template)
        
        logger.info(f"Created version {version} for template {template_id}")
        return template
    
    def instantiate_template(
        self,
        template_id: UUID,
        parameter_values: Dict[str, Any],
        created_by: Optional[str] = None
    ) -> Optional[TemplateInstantiation]:
        """
        Instantiate a template with parameter values.
        
        Args:
            template_id: ID of the template
            parameter_values: Values for template parameters
            created_by: User who created the instantiation
            
        Returns:
            Template instantiation if successful, None otherwise
        """
        template = self.get_template(template_id)
        if not template:
            logger.error(f"Template with ID {template_id} not found")
            return None
        
        # Get the current version
        version = template.get_current_version()
        if not version:
            logger.error(f"No current version found for template {template_id}")
            return None
        
        workflow_definition = version.workflow_definition
        
        # Validate parameter values
        for param_name, param in template.parameters.items():
            if param.required and param_name not in parameter_values:
                if param.default is not None:
                    parameter_values[param_name] = param.default
                else:
                    logger.error(f"Required parameter '{param_name}' not provided")
                    return None
        
        # Create a deep copy of the workflow definition
        workflow_dict = workflow_definition.dict()
        
        # Apply parameter substitution
        workflow_dict = substitute_parameters(workflow_dict, parameter_values)
        
        # Create new workflow definition
        new_workflow = WorkflowDefinition.parse_obj(workflow_dict)
        
        # Create instantiation record
        instantiation = TemplateInstantiation(
            template_id=template_id,
            template_version=template.current_version,
            workflow_id=new_workflow.id,
            parameter_values=parameter_values,
            created_by=created_by
        )
        
        # Save instantiation
        self.instantiations[instantiation.id] = instantiation
        if self.storage_manager:
            try:
                self.storage_manager.save_instantiation(instantiation.dict())
                self.storage_manager.save_workflow(new_workflow.dict())
            except Exception as e:
                logger.error(f"Error saving instantiation: {e}")
        
        logger.info(f"Instantiated template {template_id} with workflow ID {new_workflow.id}")
        return instantiation, new_workflow
    
    def delete_template(self, template_id: UUID) -> bool:
        """
        Delete a template.
        
        Args:
            template_id: ID of the template to delete
            
        Returns:
            True if deleted successfully
        """
        if template_id not in self.templates:
            logger.error(f"Template with ID {template_id} not found")
            return False
        
        # Remove from memory
        del self.templates[template_id]
        
        # Remove from storage
        if self.storage_manager:
            try:
                self.storage_manager.delete_template(template_id)
            except Exception as e:
                logger.error(f"Error deleting template from storage: {e}")
                return False
        
        logger.info(f"Deleted template with ID {template_id}")
        return True
    
    def create_category(
        self,
        name: str,
        description: Optional[str] = None,
        parent_id: Optional[UUID] = None
    ) -> TemplateCategory:
        """
        Create a new template category.
        
        Args:
            name: Name of the category
            description: Description of the category
            parent_id: ID of the parent category
            
        Returns:
            Created category
        """
        category = TemplateCategory(
            name=name,
            description=description,
            parent_id=parent_id
        )
        
        # Save category
        self.categories[category.id] = category
        if self.storage_manager:
            try:
                self.storage_manager.save_category(category.dict())
            except Exception as e:
                logger.error(f"Error saving category: {e}")
        
        logger.info(f"Created category '{name}' with ID {category.id}")
        return category
    
    def get_category(self, category_id: UUID) -> Optional[TemplateCategory]:
        """
        Get a category by ID.
        
        Args:
            category_id: ID of the category to get
            
        Returns:
            Category if found, None otherwise
        """
        return self.categories.get(category_id)
    
    def get_categories(self, parent_id: Optional[UUID] = None) -> List[TemplateCategory]:
        """
        Get categories, optionally filtered by parent.
        
        Args:
            parent_id: Parent ID to filter by
            
        Returns:
            List of matching categories
        """
        categories = list(self.categories.values())
        
        # Filter by parent
        if parent_id is not None:
            categories = [c for c in categories if c.parent_id == parent_id]
        
        return categories
    
    def delete_category(self, category_id: UUID) -> bool:
        """
        Delete a category.
        
        Args:
            category_id: ID of the category to delete
            
        Returns:
            True if deleted successfully
        """
        if category_id not in self.categories:
            logger.error(f"Category with ID {category_id} not found")
            return False
        
        # Check if category has templates
        for template in self.templates.values():
            if category_id in template.category_ids:
                logger.error(f"Cannot delete category {category_id} as it has templates")
                return False
        
        # Check if category has children
        for category in self.categories.values():
            if category.parent_id == category_id:
                logger.error(f"Cannot delete category {category_id} as it has child categories")
                return False
        
        # Remove from memory
        del self.categories[category_id]
        
        # Remove from storage
        if self.storage_manager:
            try:
                self.storage_manager.delete_category(category_id)
            except Exception as e:
                logger.error(f"Error deleting category from storage: {e}")
                return False
        
        logger.info(f"Deleted category with ID {category_id}")
        return True