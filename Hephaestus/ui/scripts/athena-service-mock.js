/**
 * Athena Service Mock
 * Temporary mock service until backend routing is fixed
 */

(function() {
    'use strict';
    
    // Mock data
    const mockEntities = [
        {
            id: "entity-1",
            name: "Tekton Framework",
            type: "project",
            description: "CI orchestration and component management system",
            properties: {
                created: "2024-01-01",
                status: "active"
            }
        },
        {
            id: "entity-2", 
            name: "Casey Koons",
            type: "person",
            description: "Creator and architect of Tekton",
            properties: {
                role: "Principal Engineer",
                expertise: ["AI", "Systems Architecture", "UNIX"]
            }
        },
        {
            id: "entity-3",
            name: "Athena Component",
            type: "component",
            description: "Knowledge graph and entity management system",
            properties: {
                port: 8105,
                version: "0.1.0"
            }
        }
    ];
    
    const mockGraphData = {
        entities: [
            { id: "node-1", label: "Tekton", type: "project", x: 300, y: 200 },
            { id: "node-2", label: "Casey Koons", type: "person", x: 100, y: 100 },
            { id: "node-3", label: "Athena", type: "component", x: 500, y: 100 },
            { id: "node-4", label: "Apollo", type: "component", x: 500, y: 300 },
            { id: "node-5", label: "Hermes", type: "component", x: 300, y: 400 }
        ],
        relationships: [
            { source: "node-2", target: "node-1", type: "created" },
            { source: "node-3", target: "node-1", type: "part_of" },
            { source: "node-4", target: "node-1", type: "part_of" },
            { source: "node-5", target: "node-1", type: "part_of" }
        ]
    };
    
    // Mock service implementation
    window.AthenaServiceMock = {
        async getEntities() {
            console.log('[ATHENA MOCK] Returning mock entities');
            return [...mockEntities];
        },
        
        async createEntity(entityData) {
            console.log('[ATHENA MOCK] Creating entity:', entityData);
            const newEntity = {
                id: `entity-${Date.now()}`,
                ...entityData,
                properties: entityData.properties || {}
            };
            mockEntities.push(newEntity);
            return { status: 'success', data: newEntity };
        },
        
        async updateEntity(entityId, entityData) {
            console.log('[ATHENA MOCK] Updating entity:', entityId, entityData);
            const index = mockEntities.findIndex(e => e.id === entityId);
            if (index >= 0) {
                mockEntities[index] = { ...mockEntities[index], ...entityData };
                return { status: 'success', data: mockEntities[index] };
            }
            return { status: 'error', message: 'Entity not found' };
        },
        
        async deleteEntity(entityId) {
            console.log('[ATHENA MOCK] Deleting entity:', entityId);
            const index = mockEntities.findIndex(e => e.id === entityId);
            if (index >= 0) {
                mockEntities.splice(index, 1);
                return { status: 'success' };
            }
            return { status: 'error', message: 'Entity not found' };
        },
        
        async getGraphData(options = {}) {
            console.log('[ATHENA MOCK] Returning mock graph data');
            
            // Filter by type if requested
            if (options.type && options.type !== 'all') {
                const filteredEntities = mockGraphData.entities.filter(e => e.type === options.type);
                const entityIds = filteredEntities.map(e => e.id);
                const filteredRelationships = mockGraphData.relationships.filter(
                    r => entityIds.includes(r.source) || entityIds.includes(r.target)
                );
                return {
                    entities: filteredEntities,
                    relationships: filteredRelationships
                };
            }
            
            return mockGraphData;
        },
        
        async searchEntities(query) {
            console.log('[ATHENA MOCK] Searching for:', query);
            const results = mockEntities.filter(e => 
                e.name.toLowerCase().includes(query.toLowerCase()) ||
                e.description.toLowerCase().includes(query.toLowerCase())
            );
            return results;
        },
        
        async executeQuery(query) {
            console.log('[ATHENA MOCK] Executing query:', query);
            
            // Simple mock query execution
            let results = [...mockEntities];
            
            if (query.type && query.type !== 'any') {
                results = results.filter(e => e.type === query.type);
            }
            
            if (query.search) {
                results = results.filter(e => 
                    e.name.toLowerCase().includes(query.search.toLowerCase()) ||
                    e.description.toLowerCase().includes(query.search.toLowerCase())
                );
            }
            
            return { status: 'success', data: results };
        }
    };
    
    // Override real service with mock
    window.AthenaService = window.AthenaServiceMock;
    
    console.log('[ATHENA MOCK] Mock service activated - backend routing fix needed');
})();