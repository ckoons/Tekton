/**
 * Athena Service
 * Handles all API interactions for the Athena component
 */

(function() {
    'use strict';
    
    // Athena service now uses tektonUrl for proper URL building
    
    // Athena API Service
    window.AthenaService = {
        // Entity Management
        async getEntities(limit = 1000) {
            try {
                const response = await fetch(window.athenaUrl(`/api/v1/entities/?limit=${limit}`));
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('[ATHENA] Error fetching entities:', error);
                return [];
            }
        },
        
        async createEntity(entityData) {
            try {
                const response = await fetch(window.athenaUrl('/api/v1/entities'), {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(entityData)
                });
                return await response.json();
            } catch (error) {
                console.error('[ATHENA] Error creating entity:', error);
                return { status: 'error', message: error.message };
            }
        },
        
        async updateEntity(entityId, entityData) {
            try {
                const response = await fetch(window.athenaUrl(`/api/v1/entities/${entityId}`), {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(entityData)
                });
                return await response.json();
            } catch (error) {
                console.error('[ATHENA] Error updating entity:', error);
                return { status: 'error', message: error.message };
            }
        },
        
        async deleteEntity(entityId) {
            try {
                const response = await fetch(window.athenaUrl(`/api/v1/entities/${entityId}`), {
                    method: 'DELETE'
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const result = await response.json();
                return { status: 'success', ...result };
            } catch (error) {
                console.error('[ATHENA] Error deleting entity:', error);
                return { status: 'error', message: error.message };
            }
        },
        
        // Knowledge Operations
        async getKnowledgeOverview() {
            try {
                const response = await fetch(window.athenaUrl('/api/v1/knowledge'));
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('[ATHENA] Error fetching knowledge overview:', error);
                return { status: 'error', data: {} };
            }
        },
        
        async searchEntities(query) {
            try {
                const response = await fetch(window.athenaUrl('/api/v1/query/search'), {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ query })
                });
                return await response.json();
            } catch (error) {
                console.error('[ATHENA] Error searching entities:', error);
                return { status: 'error', data: [] };
            }
        },
        
        // Graph Visualization
        async getGraphData(options = {}) {
            try {
                const params = new URLSearchParams(options);
                const response = await fetch(window.athenaUrl(`/api/v1/visualization/graph?${params}`));
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('[ATHENA] Error fetching graph data:', error);
                return { entities: [], relationships: [] };
            }
        },
        
        // Query Builder
        async executeQuery(query) {
            try {
                const response = await fetch(window.athenaUrl('/api/v1/query'), {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ 
                        question: query,
                        mode: 'hybrid',  // Use hybrid mode for best results
                        max_results: 10
                    })
                });
                const result = await response.json();
                if (response.ok) {
                    return { status: 'success', data: result };
                } else {
                    return { status: 'error', message: result.detail || 'Query failed' };
                }
            } catch (error) {
                console.error('[ATHENA] Error executing query:', error);
                return { status: 'error', data: [] };
            }
        },
        
        // LLM Integration
        async askQuestion(question) {
            try {
                const response = await fetch(window.athenaUrl('/api/v1/llm/ask'), {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ question })
                });
                return await response.json();
            } catch (error) {
                console.error('[ATHENA] Error asking question:', error);
                return { status: 'error', message: error.message };
            }
        },
        
        // Entity Types
        async getEntityTypes() {
            try {
                const response = await fetch(window.athenaUrl('/api/v1/entities/types'));
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('[ATHENA] Error fetching entity types:', error);
                return { status: 'error', data: [] };
            }
        },
        
        // Relationships
        async getRelationships(entityId) {
            try {
                const response = await fetch(window.athenaUrl(`/api/v1/entities/${entityId}/relationships`));
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('[ATHENA] Error fetching relationships:', error);
                return { status: 'error', data: [] };
            }
        },
        
        // Status check
        async checkStatus() {
            try {
                const response = await fetch(window.athenaUrl('/api/v1/status'));
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('[ATHENA] Error checking status:', error);
                return { status: 'error', healthy: false };
            }
        }
    };
    
    // Log service initialization
    console.log('[ATHENA] Service initialized using tektonUrl');
})();