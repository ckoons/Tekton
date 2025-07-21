/**
 * Ergon Service
 * Handles all API interactions for the Ergon component
 */

(function() {
    'use strict';
    
    // Ergon service uses tektonUrl for proper URL building
    
    // Ergon API Service
    window.ErgonService = {
        // Agent Management
        async getAgents() {
            try {
                const response = await fetch(window.ergonUrl('/api/v1/agents'));
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('[ERGON] Error fetching agents:', error);
                return [];
            }
        },
        
        async createAgent(agentData) {
            try {
                const response = await fetch(window.ergonUrl('/api/v1/agents'), {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(agentData)
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return await response.json();
            } catch (error) {
                console.error('[ERGON] Error creating agent:', error);
                return { status: 'error', message: error.message };
            }
        },
        
        async updateAgent(agentId, agentData) {
            try {
                const response = await fetch(window.ergonUrl(`/api/v1/agents/${agentId}`), {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(agentData)
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return await response.json();
            } catch (error) {
                console.error('[ERGON] Error updating agent:', error);
                return { status: 'error', message: error.message };
            }
        },
        
        async deleteAgent(agentId) {
            try {
                const response = await fetch(window.ergonUrl(`/api/v1/agents/${agentId}`), {
                    method: 'DELETE'
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const result = await response.json();
                return { status: 'success', ...result };
            } catch (error) {
                console.error('[ERGON] Error deleting agent:', error);
                return { status: 'error', message: error.message };
            }
        },
        
        // Tool Management
        async getTools() {
            try {
                const response = await fetch(window.ergonUrl('/api/v1/tools'));
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('[ERGON] Error fetching tools:', error);
                return [];
            }
        },
        
        async installTool(toolData) {
            try {
                const response = await fetch(window.ergonUrl('/api/v1/tools'), {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(toolData)
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return await response.json();
            } catch (error) {
                console.error('[ERGON] Error installing tool:', error);
                return { status: 'error', message: error.message };
            }
        },
        
        async uninstallTool(toolId) {
            try {
                const response = await fetch(window.ergonUrl(`/api/v1/tools/${toolId}`), {
                    method: 'DELETE'
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const result = await response.json();
                return { status: 'success', ...result };
            } catch (error) {
                console.error('[ERGON] Error uninstalling tool:', error);
                return { status: 'error', message: error.message };
            }
        },
        
        // MCP (Model Context Protocol) Management
        async getMcpConnections() {
            try {
                const response = await fetch(window.ergonUrl('/api/v1/mcp/connections'));
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('[ERGON] Error fetching MCP connections:', error);
                return [];
            }
        },
        
        async createMcpConnection(connectionData) {
            try {
                const response = await fetch(window.ergonUrl('/api/v1/mcp/connections'), {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(connectionData)
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return await response.json();
            } catch (error) {
                console.error('[ERGON] Error creating MCP connection:', error);
                return { status: 'error', message: error.message };
            }
        },
        
        async deleteMcpConnection(connectionId) {
            try {
                const response = await fetch(window.ergonUrl(`/api/v1/mcp/connections/${connectionId}`), {
                    method: 'DELETE'
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const result = await response.json();
                return { status: 'success', ...result };
            } catch (error) {
                console.error('[ERGON] Error deleting MCP connection:', error);
                return { status: 'error', message: error.message };
            }
        },
        
        async getMcpStats() {
            try {
                const response = await fetch(window.ergonUrl('/api/v1/mcp/stats'));
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('[ERGON] Error fetching MCP stats:', error);
                return { active_connections: 0, available_models: 0, token_usage: 0 };
            }
        },
        
        // Memory Management
        async getMemoryStats() {
            try {
                const response = await fetch(window.ergonUrl('/api/v1/memory/stats'));
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('[ERGON] Error fetching memory stats:', error);
                return { active_memories: 0, total_storage: '0 MB', retention_period: '30 days' };
            }
        },
        
        async getMemories() {
            try {
                const response = await fetch(window.ergonUrl('/api/v1/memory'));
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('[ERGON] Error fetching memories:', error);
                return [];
            }
        },
        
        async clearMemories() {
            try {
                const response = await fetch(window.ergonUrl('/api/v1/memory'), {
                    method: 'DELETE'
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const result = await response.json();
                return { status: 'success', ...result };
            } catch (error) {
                console.error('[ERGON] Error clearing memories:', error);
                return { status: 'error', message: error.message };
            }
        },
        
        // LLM Integration
        async askQuestion(question) {
            try {
                const response = await fetch(window.ergonUrl('/api/v1/llm/ask'), {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ question })
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return await response.json();
            } catch (error) {
                console.error('[ERGON] Error asking question:', error);
                return { status: 'error', message: error.message };
            }
        },
        
        // Status check
        async checkStatus() {
            try {
                const response = await fetch(window.ergonUrl('/api/v1/status'));
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('[ERGON] Error checking status:', error);
                return { status: 'error', healthy: false };
            }
        }
    };
    
    // Log service initialization
    console.log('[ERGON] Service initialized using tektonUrl');
})();