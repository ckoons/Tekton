# Athena User Guide

This guide provides practical instructions for users of the Athena knowledge graph component, focusing on day-to-day usage rather than technical implementation details.

## Table of Contents

- [Introduction](#introduction)
- [Getting Started](#getting-started)
- [Knowledge Graph Basics](#knowledge-graph-basics)
- [Entity Management](#entity-management)
- [Relationship Management](#relationship-management)
- [Querying the Knowledge Graph](#querying-the-knowledge-graph)
- [Visualization](#visualization)
- [Integration with Tekton Components](#integration-with-tekton-components)
- [Advanced Usage](#advanced-usage)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Introduction

Athena is the knowledge graph component of the Tekton ecosystem, designed to store, manage, and visualize structured knowledge. It allows you to create a rich semantic network of entities and their relationships, making it easy to discover connections, analyze patterns, and extract insights from your data.

## Getting Started

### Installation and Setup

Athena is typically installed as part of the Tekton ecosystem:

```bash
# Launch Athena using the Tekton launcher
./scripts/tekton-launch --components athena

# Verify Athena is running
./scripts/tekton-status | grep athena
```

### Accessing Athena

Athena provides multiple interfaces:

1. **REST API**: For programmatic access
   ```
   http://localhost:8002/api/
   ```

2. **Web UI**: Through the Hephaestus component
   ```
   http://localhost:8080/
   ```
   Then navigate to the Athena component in the sidebar.

3. **CLI**: For command-line operations
   ```bash
   python -m athena.cli
   ```

## Knowledge Graph Basics

### Understanding Knowledge Graphs

A knowledge graph consists of:

- **Entities**: Objects, concepts, or things (e.g., people, organizations, projects)
- **Relationships**: Connections between entities (e.g., "works for", "depends on")
- **Properties**: Attributes that describe entities (e.g., name, description, creation date)

### Core Concepts

In Athena, the knowledge graph is structured with:

1. **Entity Types**: Categories of entities (e.g., Person, Organization, Project)
2. **Relationship Types**: Categories of relationships (e.g., WORKS_FOR, DEPENDS_ON)
3. **Properties**: Entity attributes stored as key-value pairs
4. **Schemas**: Define the structure for entity types and property validation

## Entity Management

### Creating Entities

You can create entities through the UI or API:

#### Using the UI:
1. Navigate to the Athena component in Hephaestus
2. Click "Create Entity"
3. Select an entity type
4. Fill in the required properties
5. Click "Save"

#### Using the API:
```bash
curl -X POST http://localhost:8002/api/entities \
  -H "Content-Type: application/json" \
  -d '{
    "type": "Project",
    "properties": {
      "name": "Tekton Knowledge Graph",
      "description": "A project to build a knowledge graph for Tekton",
      "status": "active",
      "start_date": "2024-01-01"
    }
  }'
```

### Viewing Entities

#### Using the UI:
1. Navigate to the Athena component
2. Use the search bar to find entities
3. Click on an entity to view its details

#### Using the API:
```bash
# Get entity by ID
curl http://localhost:8002/api/entities/entity_id_here

# Search entities
curl "http://localhost:8002/api/entities?type=Project&q=knowledge"
```

### Updating Entities

#### Using the UI:
1. Navigate to the entity detail view
2. Click "Edit"
3. Modify the properties
4. Click "Save"

#### Using the API:
```bash
curl -X PUT http://localhost:8002/api/entities/entity_id_here \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "name": "Tekton Knowledge Graph System",
      "status": "completed"
    }
  }'
```

### Deleting Entities

#### Using the UI:
1. Navigate to the entity detail view
2. Click "Delete"
3. Confirm deletion

#### Using the API:
```bash
curl -X DELETE http://localhost:8002/api/entities/entity_id_here
```

## Relationship Management

### Creating Relationships

#### Using the UI:
1. Navigate to the entity detail view
2. Scroll to the "Relationships" section
3. Click "Add Relationship"
4. Select the relationship type
5. Search for and select the target entity
6. Add any properties to the relationship
7. Click "Save"

#### Using the API:
```bash
curl -X POST http://localhost:8002/api/relationships \
  -H "Content-Type: application/json" \
  -d '{
    "source_id": "source_entity_id",
    "target_id": "target_entity_id",
    "type": "DEPENDS_ON",
    "properties": {
      "strength": "high",
      "notes": "Critical dependency"
    }
  }'
```

### Viewing Relationships

#### Using the UI:
1. Navigate to the entity detail view
2. The "Relationships" section shows all relationships
3. Toggle between incoming and outgoing relationships

#### Using the API:
```bash
# Get relationships for an entity
curl http://localhost:8002/api/entities/entity_id_here/relationships

# Filter by relationship type
curl "http://localhost:8002/api/entities/entity_id_here/relationships?type=DEPENDS_ON"

# Get specific relationship
curl http://localhost:8002/api/relationships/relationship_id_here
```

### Updating Relationships

#### Using the UI:
1. Navigate to the entity detail view
2. Find the relationship in the "Relationships" section
3. Click "Edit"
4. Modify the properties
5. Click "Save"

#### Using the API:
```bash
curl -X PUT http://localhost:8002/api/relationships/relationship_id_here \
  -H "Content-Type: application/json" \
  -d '{
    "properties": {
      "strength": "medium",
      "notes": "Updated dependency"
    }
  }'
```

### Deleting Relationships

#### Using the UI:
1. Navigate to the entity detail view
2. Find the relationship in the "Relationships" section
3. Click "Delete"
4. Confirm deletion

#### Using the API:
```bash
curl -X DELETE http://localhost:8002/api/relationships/relationship_id_here
```

## Querying the Knowledge Graph

### Simple Queries

#### Using the UI:
1. Use the search bar in the Athena component
2. Enter keywords or entity properties
3. Filter by entity type using the dropdown

#### Using the API:
```bash
# Basic search
curl "http://localhost:8002/api/search?q=knowledge"

# Filter by entity type
curl "http://localhost:8002/api/search?q=knowledge&type=Project"

# Filter by property
curl "http://localhost:8002/api/search?property.status=active"
```

### Advanced Queries

Athena supports advanced query capabilities:

#### Using the UI:
1. Click "Advanced Search" in the Athena component
2. Build a query using the query builder
3. Add conditions for entity types, properties, and relationships
4. Execute the query

#### Using the API:
```bash
# Complex query with relationship filters
curl -X POST http://localhost:8002/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "entities": [
      {
        "variable": "p",
        "type": "Project",
        "properties": {
          "status": "active"
        }
      },
      {
        "variable": "t",
        "type": "Task"
      }
    ],
    "relationships": [
      {
        "source": "p",
        "target": "t",
        "type": "HAS_TASK"
      }
    ],
    "return": ["p", "t"]
  }'
```

### Path Queries

Find paths between entities:

#### Using the UI:
1. Navigate to the "Path Analysis" tab
2. Select a start entity and end entity
3. Set the maximum path length
4. Click "Find Paths"

#### Using the API:
```bash
curl -X POST http://localhost:8002/api/paths \
  -H "Content-Type: application/json" \
  -d '{
    "start_id": "start_entity_id",
    "end_id": "end_entity_id",
    "max_depth": 3,
    "relationship_types": ["DEPENDS_ON", "PART_OF"]
  }'
```

## Visualization

### Graph Visualization

Athena provides interactive graph visualization:

#### Using the UI:
1. Navigate to the "Visualization" tab
2. Start with a search or select entities
3. Click "Visualize"
4. Interact with the graph:
   - Zoom in/out with the scroll wheel
   - Pan by clicking and dragging
   - Click on nodes to see details
   - Double-click to expand a node's relationships
   - Use the controls to adjust the visualization:
     - Filter by relationship type
     - Adjust node size and color
     - Change the layout algorithm

### Exporting Visualizations

#### Using the UI:
1. Create your visualization
2. Click "Export"
3. Choose the format (PNG, SVG, or JSON)
4. Save the file

#### Using the API:
```bash
curl -X POST http://localhost:8002/api/visualize/export \
  -H "Content-Type: application/json" \
  -d '{
    "entity_ids": ["entity_id_1", "entity_id_2"],
    "depth": 2,
    "format": "svg"
  }' \
  -o graph.svg
```

## Integration with Tekton Components

### Integration with Engram

Athena integrates with Engram for memory persistence:

1. Knowledge entities can be stored in Engram's memory system
2. Query results can be saved as memories
3. Memories can be converted into knowledge graph entities

#### Using the UI:
1. Navigate to an entity detail view
2. Click "Store in Memory"
3. Set memory parameters
4. Click "Save"

#### Using the API:
```bash
curl -X POST http://localhost:8002/api/entities/entity_id_here/store_memory \
  -H "Content-Type: application/json" \
  -d '{
    "memory_type": "knowledge_entity",
    "collection": "important_entities"
  }'
```

### Integration with Ergon

Athena integrates with Ergon for task management:

1. Create knowledge entities from tasks
2. Link tasks to relevant knowledge entities
3. Visualize task dependencies through the knowledge graph

#### Using the UI:
1. Navigate to the "Integrations" tab
2. Select "Ergon Integration"
3. Choose tasks to import as entities
4. Configure the import settings
5. Click "Import"

#### Using the API:
```bash
curl -X POST http://localhost:8002/api/integrations/ergon/import \
  -H "Content-Type: application/json" \
  -d '{
    "task_ids": ["task_id_1", "task_id_2"],
    "create_relationships": true
  }'
```

## Advanced Usage

### Knowledge Graph Schemas

Define schemas for entity types:

#### Using the UI:
1. Navigate to the "Administration" tab
2. Select "Schemas"
3. Click "Create Schema"
4. Define the entity type and properties
5. Set validation rules for properties
6. Click "Save"

#### Using the API:
```bash
curl -X POST http://localhost:8002/api/schemas \
  -H "Content-Type: application/json" \
  -d '{
    "entity_type": "Document",
    "properties": [
      {
        "name": "title",
        "type": "string",
        "required": true
      },
      {
        "name": "author",
        "type": "string",
        "required": false
      },
      {
        "name": "publication_date",
        "type": "date",
        "required": true
      },
      {
        "name": "tags",
        "type": "array",
        "items": {
          "type": "string"
        }
      }
    ]
  }'
```

### Batch Operations

Perform operations on multiple entities:

#### Using the API:
```bash
# Batch create entities
curl -X POST http://localhost:8002/api/batch/entities \
  -H "Content-Type: application/json" \
  -d '{
    "entities": [
      {
        "type": "Person",
        "properties": {
          "name": "John Doe",
          "role": "Developer"
        }
      },
      {
        "type": "Person",
        "properties": {
          "name": "Jane Smith",
          "role": "Manager"
        }
      }
    ]
  }'

# Batch create relationships
curl -X POST http://localhost:8002/api/batch/relationships \
  -H "Content-Type: application/json" \
  -d '{
    "relationships": [
      {
        "source_id": "source_id_1",
        "target_id": "target_id_1",
        "type": "WORKS_WITH"
      },
      {
        "source_id": "source_id_2",
        "target_id": "target_id_2",
        "type": "REPORTS_TO"
      }
    ]
  }'
```

### Knowledge Graph Analytics

Analyze your knowledge graph:

#### Using the UI:
1. Navigate to the "Analytics" tab
2. Select an analysis type:
   - Centrality Analysis: Find key entities in the graph
   - Community Detection: Identify clusters of related entities
   - Similarity Analysis: Find similar entities
3. Configure analysis parameters
4. Run the analysis

#### Using the API:
```bash
# Centrality analysis
curl -X POST http://localhost:8002/api/analytics/centrality \
  -H "Content-Type: application/json" \
  -d '{
    "algorithm": "pagerank",
    "entity_types": ["Person", "Organization"],
    "relationship_types": ["WORKS_FOR", "COLLABORATES_WITH"]
  }'

# Community detection
curl -X POST http://localhost:8002/api/analytics/communities \
  -H "Content-Type: application/json" \
  -d '{
    "algorithm": "louvain",
    "entity_types": ["Project", "Task"],
    "relationship_types": ["DEPENDS_ON", "PART_OF"]
  }'
```

## Troubleshooting

### Common Issues

**Issue**: Entities not appearing in search results
**Solution**:
1. Check if the entity was created correctly
2. Verify the search terms match entity properties
3. Ensure you have the correct entity type filter
4. Check if there are permission issues

**Issue**: Visualization not loading or is too complex
**Solution**:
1. Reduce the number of entities in the visualization
2. Filter by specific relationship types
3. Decrease the depth of relationship expansion
4. Try a different browser or clear cache

**Issue**: API requests returning errors
**Solution**:
1. Check the error message for specific issues
2. Verify your request format and parameters
3. Ensure Athena is running (`./scripts/tekton-status`)
4. Check the logs for more detailed error information

### Checking Logs

```bash
# View Athena logs
tail -f /path/to/tekton/logs/athena.log

# Check for specific error patterns
grep "ERROR" /path/to/tekton/logs/athena.log
```

### Resetting the Knowledge Graph

In some cases, you may need to reset the knowledge graph:

#### Using the CLI:
```bash
# Reset the entire knowledge graph (USE WITH CAUTION)
python -m athena.cli reset --confirm

# Reset specific entity types
python -m athena.cli reset --entity-types Project,Task --confirm
```

## Best Practices

### Knowledge Graph Design

1. **Plan your entity types**: Define clear entity types that align with your domain
2. **Create meaningful relationships**: Use relationship types that accurately describe connections
3. **Use descriptive properties**: Include relevant properties that help identify and search entities
4. **Define schemas**: Create schemas to ensure data consistency and quality
5. **Keep entities focused**: Each entity should represent a single concept

### Querying Effectively

1. **Start specific**: Begin with specific queries and broaden as needed
2. **Use property filters**: Filter by properties to narrow results
3. **Combine entity types**: Query across multiple entity types to uncover connections
4. **Limit query depth**: Keep path queries to a reasonable depth (3-4 levels)
5. **Save common queries**: Save frequently used queries for easy access

### Visualization Tips

1. **Focus on a subset**: Visualize a manageable subset of the knowledge graph
2. **Use filters**: Filter relationships to highlight specific connections
3. **Adjust layouts**: Try different layout algorithms for different views
4. **Color-code entities**: Use colors to distinguish entity types
5. **Save and share**: Export visualizations for documentation and sharing

### Performance Optimization

1. **Batch operations**: Use batch operations for creating multiple entities
2. **Index key properties**: Ensure important properties are indexed
3. **Limit relationship depth**: Avoid querying very deep relationship paths
4. **Cache results**: Save query results for frequently accessed data
5. **Archive old data**: Move infrequently accessed entities to an archive

### Integration Workflow

1. **Automate entity creation**: Use integrations to automatically create entities
2. **Maintain consistency**: Ensure consistent naming across integrated systems
3. **Establish clear relationships**: Define relationships between entities from different sources
4. **Review imported data**: Periodically review and clean up imported entities
5. **Document integration points**: Maintain documentation of integration configurations