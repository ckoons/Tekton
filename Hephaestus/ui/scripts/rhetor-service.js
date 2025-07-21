/**
 * Rhetor Service
 * Handles all API interactions for the Rhetor component
 */

(function() {
    'use strict';
    
    // Rhetor service uses tektonUrl for proper URL building
    
    // Rhetor API Service
    window.RhetorService = {
        // Model Management
        async getModels() {
            try {
                const response = await fetch(window.rhetorUrl('/api/v1/models'));
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('[RHETOR] Error fetching models:', error);
                return [];
            }
        },
        
        async getModelConfig() {
            try {
                const response = await fetch(window.rhetorUrl('/api/v1/models/config'));
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('[RHETOR] Error fetching model config:', error);
                return { orchestrator: 'claude-3-opus-20240229', memory: 'claude-3-haiku-20240307', coordinator: 'claude-3-sonnet-20240229' };
            }
        },
        
        async saveModelConfig(config) {
            try {
                const response = await fetch(window.rhetorUrl('/api/v1/models/config'), {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(config)
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return await response.json();
            } catch (error) {
                console.error('[RHETOR] Error saving model config:', error);
                return { status: 'error', message: error.message };
            }
        },
        
        async testModel(modelId) {
            try {
                const response = await fetch(window.rhetorUrl(`/api/v1/models/${modelId}/test`), {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: 'Hello, this is a test message.' })
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return await response.json();
            } catch (error) {
                console.error('[RHETOR] Error testing model:', error);
                return { status: 'error', message: error.message };
            }
        },
        
        // Prompt Management
        async getPrompts() {
            try {
                const response = await fetch(window.rhetorUrl('/api/v1/prompts'));
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('[RHETOR] Error fetching prompts:', error);
                return [];
            }
        },
        
        async getComponentPrompts(componentName) {
            try {
                const response = await fetch(window.rhetorUrl(`/api/v1/prompts/component/${componentName}`));
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('[RHETOR] Error fetching component prompts:', error);
                return { system_prompt: '', user_prompt: '', assistant_prompt: '' };
            }
        },
        
        async saveComponentPrompts(componentName, prompts) {
            try {
                const response = await fetch(window.rhetorUrl(`/api/v1/prompts/component/${componentName}`), {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(prompts)
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return await response.json();
            } catch (error) {
                console.error('[RHETOR] Error saving component prompts:', error);
                return { status: 'error', message: error.message };
            }
        },
        
        // Context Management
        async getContexts() {
            try {
                const response = await fetch(window.rhetorUrl('/api/v1/contexts'));
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('[RHETOR] Error fetching contexts:', error);
                return [];
            }
        },
        
        async getContext(componentName) {
            try {
                const response = await fetch(window.rhetorUrl(`/api/v1/contexts/${componentName}`));
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('[RHETOR] Error fetching context:', error);
                return { detailed_context: '', problem_context: '' };
            }
        },
        
        async saveContext(componentName, context) {
            try {
                const response = await fetch(window.rhetorUrl(`/api/v1/contexts/${componentName}`), {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(context)
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return await response.json();
            } catch (error) {
                console.error('[RHETOR] Error saving context:', error);
                return { status: 'error', message: error.message };
            }
        },
        
        // Specialist Management
        async getSpecialists() {
            try {
                const response = await fetch(window.rhetorUrl('/api/v1/specialists'));
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('[RHETOR] Error fetching specialists:', error);
                return [];
            }
        },
        
        async createSpecialist(specialistData) {
            try {
                const response = await fetch(window.rhetorUrl('/api/v1/specialists'), {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(specialistData)
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return await response.json();
            } catch (error) {
                console.error('[RHETOR] Error creating specialist:', error);
                return { status: 'error', message: error.message };
            }
        },
        
        async refreshSpecialists() {
            try {
                const response = await fetch(window.rhetorUrl('/api/v1/specialists/refresh'), {
                    method: 'POST'
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return await response.json();
            } catch (error) {
                console.error('[RHETOR] Error refreshing specialists:', error);
                return { status: 'error', message: error.message };
            }
        },
        
        // Orchestration Management
        async getOrchestration() {
            try {
                const response = await fetch(window.rhetorUrl('/api/v1/orchestration'));
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('[RHETOR] Error fetching orchestration:', error);
                return { settings: {} };
            }
        },
        
        async saveOrchestration(orchestrationData) {
            try {
                const response = await fetch(window.rhetorUrl('/api/v1/orchestration'), {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(orchestrationData)
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return await response.json();
            } catch (error) {
                console.error('[RHETOR] Error saving orchestration:', error);
                return { status: 'error', message: error.message };
            }
        },
        
        // Session Management
        async getSessions() {
            try {
                const response = await fetch(window.rhetorUrl('/api/v1/sessions'));
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('[RHETOR] Error fetching sessions:', error);
                return [];
            }
        },
        
        async createSession(sessionData) {
            try {
                const response = await fetch(window.rhetorUrl('/api/v1/sessions'), {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(sessionData)
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return await response.json();
            } catch (error) {
                console.error('[RHETOR] Error creating session:', error);
                return { status: 'error', message: error.message };
            }
        },
        
        async refreshSessions() {
            try {
                const response = await fetch(window.rhetorUrl('/api/v1/sessions/refresh'), {
                    method: 'POST'
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return await response.json();
            } catch (error) {
                console.error('[RHETOR] Error refreshing sessions:', error);
                return { status: 'error', message: error.message };
            }
        },
        
        // Component Status
        async getComponentStatus() {
            try {
                const response = await fetch(window.rhetorUrl('/api/v1/status/components'));
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('[RHETOR] Error fetching component status:', error);
                return [];
            }
        },
        
        // Configuration Management
        async getConfiguration() {
            try {
                const response = await fetch(window.rhetorUrl('/api/v1/config'));
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('[RHETOR] Error fetching configuration:', error);
                return { anthropic_max: false };
            }
        },
        
        async saveConfiguration(config) {
            try {
                const response = await fetch(window.rhetorUrl('/api/v1/config'), {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(config)
                });
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return await response.json();
            } catch (error) {
                console.error('[RHETOR] Error saving configuration:', error);
                return { status: 'error', message: error.message };
            }
        },
        
        // LLM Integration
        async askQuestion(question) {
            try {
                const response = await fetch(window.rhetorUrl('/api/v1/llm/ask'), {
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
                console.error('[RHETOR] Error asking question:', error);
                return { status: 'error', message: error.message };
            }
        },
        
        // Status check
        async checkStatus() {
            try {
                const response = await fetch(window.rhetorUrl('/api/v1/status'));
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                return data;
            } catch (error) {
                console.error('[RHETOR] Error checking status:', error);
                return { status: 'error', healthy: false };
            }
        }
    };
    
    // Log service initialization
    console.log('[RHETOR] Service initialized using tektonUrl');
})();