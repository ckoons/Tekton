"""
Athena API Endpoints for LLM Integration

Provides REST API endpoints for LLM-powered knowledge graph operations.
"""

import logging
import json
import os
from typing import Dict, List, Any, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, Query, Body, BackgroundTasks
from fastapi.responses import StreamingResponse

# Use Rhetor client instead of tekton-llm-client
from shared.rhetor_client import RhetorClient
from shared.env import TektonEnviron

# Create compatibility classes
class PromptTemplateRegistry:
    def __init__(self):
        self.templates = {}
        
    def load_from_directory(self, path):
        pass
        
    def register_template(self, name, template):
        self.templates[name] = template
        
    def get_template(self, name):
        return self.templates.get(name)
        
class PromptTemplate:
    def __init__(self, template, variables=None, output_format=None):
        self.template = template
        self.variables = variables or []
        self.output_format = output_format
        
    def format(self, **kwargs):
        return self.template.format(**kwargs)
        
class OutputFormat:
    JSON = "json"
    TEXT = "text"
    LIST = "list"
    
class JSONParser:
    def parse(self, text):
        try:
            return json.loads(text)
        except:
            return {"raw": text}
            
def parse_json(text):
    try:
        return json.loads(text)
    except:
        return None
        
def extract_json(text):
    if "```json" in text:
        json_str = text.split("```json", 1)[1]
        json_str = json_str.split("```", 1)[0]
        try:
            return json.loads(json_str.strip())
        except:
            pass
    return None
    
def get_env(key, default=None):
    return TektonEnviron.get(key, default)

from athena.api.models.llm import (
    KnowledgeContextRequest,
    KnowledgeContextResponse,
    KnowledgeChatRequest,
    KnowledgeChatResponse,
    EntityExtractionRequest,
    EntityExtractionResponse,
    RelationshipInferenceRequest,
    RelationshipInferenceResponse
)
from athena.core.engine import get_knowledge_engine
from athena.core.entity import Entity
from athena.core.relationship import Relationship

# Set up logging
logger = logging.getLogger("athena.api.llm_integration")

# Set up router
router = APIRouter(tags=["llm"])

# Initialize prompt registry
template_registry = PromptTemplateRegistry()

# Create Rhetor client
try:
    from shared.urls import rhetor_url
    default_rhetor_url = rhetor_url("")
except ImportError:
    default_rhetor_url = None
    
llm_client = None

def get_llm_client() -> RhetorClient:
    """Get or create the LLM client."""
    global llm_client
    if llm_client is None:
        llm_client = RhetorClient(component="athena")
    return llm_client

# Load prompt templates
def load_templates():
    """Load default prompt templates for knowledge operations."""
    
    # Knowledge context template
    template_registry.register_template(
        "knowledge_context",
        PromptTemplate(
            template="""Given the following query: {query}

And the following knowledge graph context:
{context}

Provide a comprehensive answer that integrates all relevant information from the knowledge graph.
Format your response as JSON with 'answer', 'entities', 'relationships', and 'confidence' fields.""",
            variables=["query", "context"],
            output_format=OutputFormat.JSON
        )
    )
    
    # Entity extraction template
    template_registry.register_template(
        "entity_extraction",
        PromptTemplate(
            template="""Extract all entities from the following text:
{text}

Context: {context}

Return a JSON array of entity objects with the following structure:
[{{"name": "...", "type": "...", "attributes": {{}}, "confidence": 0.0-1.0}}]""",
            variables=["text", "context"],
            output_format=OutputFormat.JSON
        )
    )
    
    # Relationship inference template
    template_registry.register_template(
        "relationship_inference",
        PromptTemplate(
            template="""Given the following entities:
{entities}

And the following context:
{context}

Infer relationships between these entities.
Return a JSON array of relationship objects with the following structure:
[{{"source": "entity_name", "target": "entity_name", "type": "relationship_type", "attributes": {{}}, "confidence": 0.0-1.0}}]""",
            variables=["entities", "context"],
            output_format=OutputFormat.JSON
        )
    )
    
    # Knowledge chat template
    template_registry.register_template(
        "knowledge_chat",
        PromptTemplate(
            template="""You are Athena's Knowledge Assistant. You have access to a knowledge graph with the following context:
{context}

Conversation history:
{history}

User: {message}

Provide a helpful response based on the knowledge graph. Be specific and cite entities and relationships when relevant.""",
            variables=["context", "history", "message"],
            output_format=OutputFormat.TEXT
        )
    )

# Load templates on import
load_templates()

@router.post("/knowledge/context", response_model=KnowledgeContextResponse)
async def get_knowledge_context(
    request: KnowledgeContextRequest,
    engine=Depends(get_knowledge_engine)
) -> KnowledgeContextResponse:
    """
    Get LLM-enhanced knowledge context for a query.
    
    This endpoint retrieves relevant knowledge from the graph and uses
    an LLM to synthesize a comprehensive answer.
    """
    try:
        # Get relevant entities and relationships from the graph
        context_entities = []
        context_relationships = []
        
        # Search for relevant entities
        if request.entity_types:
            for entity_type in request.entity_types:
                entities = await engine.search_entities(
                    query=request.query,
                    entity_type=entity_type,
                    limit=request.max_entities or 10
                )
                context_entities.extend(entities)
        else:
            # Search all entities
            entities = await engine.search_entities(
                query=request.query,
                limit=request.max_entities or 10
            )
            context_entities.extend(entities)
        
        # Get relationships for found entities
        for entity in context_entities:
            relationships = await engine.get_entity_relationships(
                entity.id,
                limit=request.max_relationships or 5
            )
            context_relationships.extend(relationships)
        
        # Build context for LLM
        context = {
            "entities": [
                {
                    "id": e.id,
                    "type": e.type,
                    "attributes": e.attributes
                }
                for e in context_entities
            ],
            "relationships": [
                {
                    "source": r.source.id,
                    "target": r.target.id,
                    "type": r.type,
                    "attributes": r.attributes
                }
                for r in context_relationships
            ]
        }
        
        # Get the knowledge context template
        template = template_registry.get_template("knowledge_context")
        prompt = template.format(
            query=request.query,
            context=json.dumps(context, indent=2)
        )
        
        # Generate response using LLM
        client = get_llm_client()
        response = await client.generate(
            prompt=prompt,
            capability="reasoning",
            temperature=request.temperature or 0.7,
            max_tokens=request.max_tokens or 1500
        )
        
        # Parse response
        parsed = parse_json(response)
        if not parsed:
            parsed = {
                "answer": response,
                "entities": [],
                "relationships": [],
                "confidence": 0.7
            }
        
        return KnowledgeContextResponse(
            query=request.query,
            answer=parsed.get("answer", response),
            entities=[e.id for e in context_entities],
            relationships=[r.id for r in context_relationships],
            confidence=parsed.get("confidence", 0.7),
            metadata={
                "total_entities": len(context_entities),
                "total_relationships": len(context_relationships),
                "llm_model": "rhetor-managed"
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting knowledge context: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/knowledge/extract_entities", response_model=EntityExtractionResponse)
async def extract_entities(
    request: EntityExtractionRequest,
    engine=Depends(get_knowledge_engine)
) -> EntityExtractionResponse:
    """
    Extract entities from text using LLM.
    
    This endpoint uses an LLM to identify and extract entities from
    unstructured text, optionally adding them to the knowledge graph.
    """
    try:
        # Build context
        context = request.context or {}
        
        # Get the entity extraction template
        template = template_registry.get_template("entity_extraction")
        prompt = template.format(
            text=request.text,
            context=json.dumps(context, indent=2)
        )
        
        # Generate response using LLM
        client = get_llm_client()
        response = await client.generate(
            prompt=prompt,
            capability="reasoning",
            temperature=0.3,
            max_tokens=2000
        )
        
        # Parse extracted entities
        entities_data = parse_json(response)
        if not entities_data:
            entities_data = []
        
        extracted_entities = []
        created_entities = []
        
        for entity_data in entities_data:
            entity = Entity(
                id=entity_data.get("name", "").lower().replace(" ", "_"),
                type=entity_data.get("type", "unknown"),
                attributes=entity_data.get("attributes", {})
            )
            entity.attributes["confidence"] = entity_data.get("confidence", 0.7)
            entity.attributes["extracted_from"] = request.text[:100] + "..."
            
            extracted_entities.append(entity)
            
            # Add to knowledge graph if requested
            if request.add_to_graph:
                try:
                    await engine.add_entity(entity)
                    created_entities.append(entity.id)
                except:
                    # Entity might already exist
                    pass
        
        return EntityExtractionResponse(
            text=request.text,
            entities=extracted_entities,
            created_entities=created_entities,
            metadata={
                "extraction_model": "rhetor-managed",
                "entities_found": len(extracted_entities),
                "entities_created": len(created_entities)
            }
        )
        
    except Exception as e:
        logger.error(f"Error extracting entities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/knowledge/infer_relationships", response_model=RelationshipInferenceResponse)
async def infer_relationships(
    request: RelationshipInferenceRequest,
    engine=Depends(get_knowledge_engine)
) -> RelationshipInferenceResponse:
    """
    Infer relationships between entities using LLM.
    
    This endpoint uses an LLM to identify potential relationships between
    entities, optionally adding them to the knowledge graph.
    """
    try:
        # Get entities from the graph
        entities = []
        for entity_id in request.entity_ids:
            entity = await engine.get_entity(entity_id)
            if entity:
                entities.append(entity)
        
        if len(entities) < 2:
            raise HTTPException(
                status_code=400,
                detail="At least 2 entities are required to infer relationships"
            )
        
        # Build entities context
        entities_context = [
            {
                "id": e.id,
                "type": e.type,
                "attributes": e.attributes
            }
            for e in entities
        ]
        
        # Get the relationship inference template
        template = template_registry.get_template("relationship_inference")
        prompt = template.format(
            entities=json.dumps(entities_context, indent=2),
            context=json.dumps(request.context or {}, indent=2)
        )
        
        # Generate response using LLM
        client = get_llm_client()
        response = await client.generate(
            prompt=prompt,
            capability="reasoning",
            temperature=0.3,
            max_tokens=2000
        )
        
        # Parse inferred relationships
        relationships_data = parse_json(response)
        if not relationships_data:
            relationships_data = []
        
        inferred_relationships = []
        created_relationships = []
        
        # Create entity map
        entity_map = {e.id: e for e in entities}
        
        for rel_data in relationships_data:
            source_id = rel_data.get("source")
            target_id = rel_data.get("target")
            
            if source_id in entity_map and target_id in entity_map:
                relationship = Relationship(
                    id=f"{source_id}_{rel_data.get('type', 'related')}_{target_id}",
                    source=entity_map[source_id],
                    target=entity_map[target_id],
                    type=rel_data.get("type", "related"),
                    attributes=rel_data.get("attributes", {})
                )
                relationship.attributes["confidence"] = rel_data.get("confidence", 0.7)
                relationship.attributes["inferred"] = True
                
                inferred_relationships.append(relationship)
                
                # Add to knowledge graph if requested
                if request.add_to_graph:
                    try:
                        await engine.add_relationship(relationship)
                        created_relationships.append(relationship.id)
                    except:
                        # Relationship might already exist
                        pass
        
        return RelationshipInferenceResponse(
            entity_ids=request.entity_ids,
            relationships=inferred_relationships,
            created_relationships=created_relationships,
            metadata={
                "inference_model": "rhetor-managed",
                "relationships_found": len(inferred_relationships),
                "relationships_created": len(created_relationships)
            }
        )
        
    except Exception as e:
        logger.error(f"Error inferring relationships: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/knowledge/chat", response_model=KnowledgeChatResponse)
async def knowledge_chat(
    request: KnowledgeChatRequest,
    engine=Depends(get_knowledge_engine)
) -> KnowledgeChatResponse:
    """
    Chat with the knowledge graph using LLM.
    
    This endpoint provides a conversational interface to the knowledge graph,
    allowing users to ask questions and get answers based on the stored knowledge.
    """
    try:
        # Build conversation history
        history = ""
        if request.conversation_history:
            for msg in request.conversation_history[-5:]:  # Last 5 messages
                history += f"{msg['role']}: {msg['content']}\n"
        
        # Get relevant context from the knowledge graph
        context_entities = await engine.search_entities(
            query=request.message,
            limit=10
        )
        
        context = {
            "entities": [
                {
                    "id": e.id,
                    "type": e.type,
                    "attributes": e.attributes
                }
                for e in context_entities
            ],
            "total_entities": await engine.get_entity_count(),
            "total_relationships": await engine.get_relationship_count()
        }
        
        # Get the knowledge chat template
        template = template_registry.get_template("knowledge_chat")
        prompt = template.format(
            context=json.dumps(context, indent=2),
            history=history,
            message=request.message
        )
        
        # Generate response using LLM
        client = get_llm_client()
        
        if request.stream:
            # Streaming response
            async def generate_stream():
                # For now, get full response and simulate streaming
                response = await client.generate(
                    prompt=prompt,
                    capability="chat",
                    temperature=request.temperature or 0.7,
                    max_tokens=request.max_tokens or 1500
                )
                
                # Simulate streaming by yielding chunks
                chunk_size = 50
                for i in range(0, len(response), chunk_size):
                    chunk = response[i:i+chunk_size]
                    yield json.dumps({"content": chunk}) + "\n"
            
            return StreamingResponse(generate_stream(), media_type="application/x-ndjson")
        
        else:
            # Regular response
            response = await client.generate(
                prompt=prompt,
                capability="chat",
                temperature=request.temperature or 0.7,
                max_tokens=request.max_tokens or 1500
            )
            
            return KnowledgeChatResponse(
                message=request.message,
                response=response,
                entities=[e.id for e in context_entities],
                metadata={
                    "context_entities": len(context_entities),
                    "model": "rhetor-managed"
                }
            )
        
    except Exception as e:
        logger.error(f"Error in knowledge chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@router.get("/llm/health")
async def llm_health():
    """Check the health of the LLM integration."""
    try:
        client = get_llm_client()
        
        # Try a simple generation
        response = await client.generate(
            prompt="Respond with 'OK' if you are working.",
            capability="chat",
            max_tokens=10
        )
        
        return {
            "status": "healthy",
            "llm_available": True,
            "test_response": response[:20],
            "templates_loaded": len(template_registry.templates)
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "llm_available": False,
            "error": str(e),
            "templates_loaded": len(template_registry.templates)
        }