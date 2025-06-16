"""Document store for Ergon.

This module provides a vector-based document store for retrieving
content based on semantic similarity.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
from datetime import datetime

# Import shared Tekton vector store
from tekton.core.vector_store import get_vector_store

# Import Ergon models
from ergon.core.database.models import DocumentationPage, Agent as DatabaseAgent
from ergon.core.repository.models import Component, Tool, AgentComponent, Workflow
from ergon.utils.config.settings import settings

# Configure logger
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, settings.log_level.value))


class DocumentStore:
    """Vector-based document store for content retrieval.
    
    This class provides semantic search capabilities for documentation
    and component information using the Tekton vector store.
    """
    
    def __init__(self, vector_db_path: Optional[str] = None):
        """Initialize the document store.
        
        Args:
            vector_db_path: Path to store vector database files
        """
        self.vector_db_path = vector_db_path or settings.vector_db_path
        
        # Initialize shared vector store with hardware detection
        self.vector_store = get_vector_store(
            path=self.vector_db_path,
            dimension=384,
            distance_metric="cosine",
            embedding_model=settings.embedding_model
        )
        
        logger.info(f"Initialized document store with Tekton vector store at {self.vector_db_path}")
    
    def add_documentation(self, doc: DocumentationPage) -> str:
        """Add documentation to the vector store.
        
        Args:
            doc: Documentation page to add
            
        Returns:
            Document ID
        """
        try:
            doc_id = f"doc_{doc.id}"
            
            # Create document
            document = {
                "id": doc_id,
                "content": doc.content,
                "metadata": {
                    "title": doc.title,
                    "url": doc.url,
                    "source": doc.source,
                    "category": doc.category,
                    "tags": doc.tags,
                    "document_type": "documentation",
                    "last_updated": doc.last_updated.isoformat() if doc.last_updated else None
                }
            }
            
            # Add to vector store
            result = self.vector_store.add_documents([document])
            
            if result:
                logger.info(f"Added documentation to vector store: {doc.title}")
                return result[0]
            else:
                logger.error(f"Failed to add documentation to vector store: {doc.title}")
                return ""
                
        except Exception as e:
            logger.error(f"Error adding documentation to vector store: {e}")
            return ""
    
    def add_component(self, component: Component) -> str:
        """Add component to the vector store.
        
        Args:
            component: Component to add
            
        Returns:
            Document ID
        """
        try:
            doc_id = f"component_{component.id}"
            
            # Prepare component description
            if isinstance(component, Tool):
                component_type = "tool"
                content = f"Tool: {component.name}\n\nDescription: {component.description}\n\nCapabilities: {component.capabilities or ''}\n\nParameters: {component.parameters or '[]'}\n\nLanguage: {component.language or 'Not specified'}\n\nVersion: {component.version or 'Not specified'}"
            elif isinstance(component, AgentComponent):
                component_type = "agent"
                content = f"Agent: {component.name}\n\nDescription: {component.description}\n\nTools: {component.tools or '[]'}\n\nModel: {component.model or 'Not specified'}\n\nSystem Prompt: {component.system_prompt}\n\nVersion: {component.version or 'Not specified'}"
            elif isinstance(component, Workflow):
                component_type = "workflow"
                content = f"Workflow: {component.name}\n\nDescription: {component.description}\n\nSteps: {component.steps or '[]'}\n\nInputs: {component.inputs or '[]'}\n\nOutputs: {component.outputs or '[]'}\n\nVersion: {component.version or 'Not specified'}"
            else:
                component_type = "component"
                content = f"Component: {component.name}\n\nDescription: {component.description}\n\nVersion: {component.version or 'Not specified'}"
            
            # Create document
            document = {
                "id": doc_id,
                "content": content,
                "metadata": {
                    "name": component.name,
                    "component_type": component_type,
                    "document_type": "component",
                    "created_at": component.created_at.isoformat() if component.created_at else None,
                    "updated_at": component.updated_at.isoformat() if component.updated_at else None
                }
            }
            
            # Add to vector store
            result = self.vector_store.add_documents([document])
            
            if result:
                logger.info(f"Added component to vector store: {component.name}")
                return result[0]
            else:
                logger.error(f"Failed to add component to vector store: {component.name}")
                return ""
                
        except Exception as e:
            logger.error(f"Error adding component to vector store: {e}")
            return ""
    
    def update_documentation(self, doc: DocumentationPage) -> bool:
        """Update documentation in the vector store.
        
        Args:
            doc: Updated documentation page
            
        Returns:
            True if successful
        """
        try:
            doc_id = f"doc_{doc.id}"
            
            # Create document
            document = {
                "content": doc.content,
                "metadata": {
                    "title": doc.title,
                    "url": doc.url,
                    "source": doc.source,
                    "category": doc.category,
                    "tags": doc.tags,
                    "document_type": "documentation",
                    "last_updated": doc.last_updated.isoformat() if doc.last_updated else datetime.now().isoformat()
                }
            }
            
            # Update in vector store
            result = self.vector_store.update_document(doc_id, document)
            
            if result:
                logger.info(f"Updated documentation in vector store: {doc.title}")
            else:
                logger.error(f"Failed to update documentation in vector store: {doc.title}")
            
            return result
                
        except Exception as e:
            logger.error(f"Error updating documentation in vector store: {e}")
            return False
    
    def update_component(self, component: Component) -> bool:
        """Update component in the vector store.
        
        Args:
            component: Updated component
            
        Returns:
            True if successful
        """
        try:
            doc_id = f"component_{component.id}"
            
            # Prepare component description
            if isinstance(component, Tool):
                component_type = "tool"
                content = f"Tool: {component.name}\n\nDescription: {component.description}\n\nCapabilities: {component.capabilities or ''}\n\nParameters: {component.parameters or '[]'}\n\nLanguage: {component.language or 'Not specified'}\n\nVersion: {component.version or 'Not specified'}"
            elif isinstance(component, AgentComponent):
                component_type = "agent"
                content = f"Agent: {component.name}\n\nDescription: {component.description}\n\nTools: {component.tools or '[]'}\n\nModel: {component.model or 'Not specified'}\n\nSystem Prompt: {component.system_prompt}\n\nVersion: {component.version or 'Not specified'}"
            elif isinstance(component, Workflow):
                component_type = "workflow"
                content = f"Workflow: {component.name}\n\nDescription: {component.description}\n\nSteps: {component.steps or '[]'}\n\nInputs: {component.inputs or '[]'}\n\nOutputs: {component.outputs or '[]'}\n\nVersion: {component.version or 'Not specified'}"
            else:
                component_type = "component"
                content = f"Component: {component.name}\n\nDescription: {component.description}\n\nVersion: {component.version or 'Not specified'}"
            
            # Create document
            document = {
                "content": content,
                "metadata": {
                    "name": component.name,
                    "component_type": component_type,
                    "document_type": "component",
                    "created_at": component.created_at.isoformat() if component.created_at else None,
                    "updated_at": datetime.now().isoformat()
                }
            }
            
            # Update in vector store
            result = self.vector_store.update_document(doc_id, document)
            
            if result:
                logger.info(f"Updated component in vector store: {component.name}")
            else:
                # If update fails, try adding
                logger.info(f"Component not found in vector store, adding: {component.name}")
                add_result = self.add_component(component)
                return bool(add_result)
            
            return result
                
        except Exception as e:
            logger.error(f"Error updating component in vector store: {e}")
            return False
    
    def delete_documentation(self, doc_id: str) -> bool:
        """Delete documentation from the vector store.
        
        Args:
            doc_id: Documentation ID to delete
            
        Returns:
            True if successful
        """
        try:
            vector_doc_id = f"doc_{doc_id}"
            
            # Delete from vector store
            result = self.vector_store.delete_document(vector_doc_id)
            
            if result:
                logger.info(f"Deleted documentation from vector store: {doc_id}")
            else:
                logger.error(f"Failed to delete documentation from vector store: {doc_id}")
            
            return result
                
        except Exception as e:
            logger.error(f"Error deleting documentation from vector store: {e}")
            return False
    
    def delete_component(self, component_id: str) -> bool:
        """Delete component from the vector store.
        
        Args:
            component_id: Component ID to delete
            
        Returns:
            True if successful
        """
        try:
            vector_doc_id = f"component_{component_id}"
            
            # Delete from vector store
            result = self.vector_store.delete_document(vector_doc_id)
            
            if result:
                logger.info(f"Deleted component from vector store: {component_id}")
            else:
                logger.error(f"Failed to delete component from vector store: {component_id}")
            
            return result
                
        except Exception as e:
            logger.error(f"Error deleting component from vector store: {e}")
            return False
    
    def search(
        self, 
        query: str, 
        top_k: int = 5, 
        filter_type: Optional[str] = None,
        filter_category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search for documents and components by semantic similarity.
        
        Args:
            query: Query string
            top_k: Number of results to return
            filter_type: Optional filter by document type (documentation or component)
            filter_category: Optional filter by documentation category
            
        Returns:
            List of matching documents
        """
        try:
            filters = {}
            
            if filter_type:
                filters["document_type"] = filter_type
                
            if filter_category and filter_type == "documentation":
                filters["category"] = filter_category
            
            # Search vector store
            results = self.vector_store.search(query, top_k=top_k, filters=filters if filters else None)
            
            logger.info(f"Search for '{query}' returned {len(results)} results")
            return results
                
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            return []


# Create global instance
document_store = DocumentStore()
