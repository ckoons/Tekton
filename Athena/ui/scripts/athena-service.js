/**
 * Athena API Client
 * 
 * Provides a JavaScript interface for interacting with the Athena Knowledge Graph API.
 */

class AthenaClient {
  /**
   * Initialize the Athena API client
   * @param {Object} options - Configuration options
   */
  constructor(options = {}) {
    this.baseUrl = options.baseUrl || this._getBaseUrl();
    this.apiPath = options.apiPath || '';
    this.debug = options.debug || false;
  }

  /**
   * Get the base URL for the Athena API from environment variables or default
   * @returns {string} The base URL
   * @private
   */
  _getBaseUrl() {
    // Check for environment variables
    if (window.ENV && window.ENV.ATHENA_API_URL) {
      return window.ENV.ATHENA_API_URL;
    }
    
    // Use Single Port Architecture with standard port assignment
    const port = '8005'; // Standard port for Athena in the Single Port Architecture
    return `http://${window.location.hostname}:${port}`;
  }

  /**
   * Log messages when in debug mode
   * @param {string} message - Debug message
   * @param {*} data - Additional data to log
   * @private
   */
  _debug(message, data = null) {
    if (this.debug) {
      console.log(`[AthenaClient] ${message}`, data || '');
    }
  }

  /**
   * Make a request to the Athena API
   * @param {string} endpoint - API endpoint
   * @param {Object} options - Fetch options
   * @returns {Promise<Object>} API response
   * @private
   */
  async _request(endpoint, options = {}) {
    const url = `${this.baseUrl}${this.apiPath}${endpoint}`;
    
    // Ensure headers exist
    options.headers = options.headers || {};
    
    // Add JSON content type if method is not GET
    if (options.method && options.method !== 'GET' && !options.headers['Content-Type']) {
      options.headers['Content-Type'] = 'application/json';
    }
    
    this._debug(`Request: ${options.method || 'GET'} ${url}`, options.body);
    
    try {
      const response = await fetch(url, options);
      
      // Handle non-2xx responses
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API request failed: ${response.status} ${response.statusText} - ${errorText}`);
      }
      
      // Return JSON response if available, otherwise return text
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        const data = await response.json();
        this._debug('Response:', data);
        return data;
      } else {
        const text = await response.text();
        this._debug('Response (text):', text);
        return text;
      }
    } catch (error) {
      this._debug('Request error:', error);
      throw error;
    }
  }

  /**
   * Get the status of the Athena service
   * @returns {Promise<Object>} Status information
   */
  async getStatus() {
    return this._request('/health');
  }

  /**
   * Get entities with filtering
   * @param {Object} filters - Filter criteria
   * @returns {Promise<Array>} List of entities
   */
  async getEntities(filters = {}) {
    const queryParams = new URLSearchParams();
    
    // Build query parameters from filters
    Object.entries(filters).forEach(([key, value]) => {
      if (Array.isArray(value)) {
        value.forEach(v => queryParams.append(`${key}[]`, v));
      } else if (value !== null && value !== undefined) {
        queryParams.append(key, value);
      }
    });
    
    const queryString = queryParams.toString();
    return this._request(`/entities${queryString ? `?${queryString}` : ''}`);
  }

  /**
   * Get a specific entity by ID
   * @param {string} entityId - Entity ID
   * @returns {Promise<Object>} Entity data
   */
  async getEntity(entityId) {
    return this._request(`/entities/${entityId}`);
  }

  /**
   * Create a new entity
   * @param {Object} entityData - Entity data
   * @returns {Promise<Object>} Created entity
   */
  async createEntity(entityData) {
    return this._request('/entities', {
      method: 'POST',
      body: JSON.stringify(entityData)
    });
  }

  /**
   * Update an existing entity
   * @param {string} entityId - Entity ID
   * @param {Object} entityData - Updated entity data
   * @returns {Promise<Object>} Updated entity
   */
  async updateEntity(entityId, entityData) {
    return this._request(`/entities/${entityId}`, {
      method: 'PUT',
      body: JSON.stringify(entityData)
    });
  }

  /**
   * Delete an entity
   * @param {string} entityId - Entity ID
   * @returns {Promise<Object>} Response data
   */
  async deleteEntity(entityId) {
    return this._request(`/entities/${entityId}`, {
      method: 'DELETE'
    });
  }

  /**
   * Search for entities
   * @param {string} query - Search query
   * @param {string} entityType - Optional entity type filter
   * @param {number} limit - Maximum number of results
   * @returns {Promise<Array>} Matching entities
   */
  async searchEntities(query, entityType = null, limit = 10) {
    const params = new URLSearchParams();
    if (query) params.append('query', query);
    if (entityType) params.append('entity_type', entityType);
    params.append('limit', limit.toString());
    
    return this._request(`/entities?${params.toString()}`);
  }

  /**
   * Get relationships with filtering
   * @param {Object} filters - Filter criteria
   * @returns {Promise<Array>} List of relationships
   */
  async getRelationships(filters = {}) {
    const queryParams = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (Array.isArray(value)) {
        value.forEach(v => queryParams.append(`${key}[]`, v));
      } else if (value !== null && value !== undefined) {
        queryParams.append(key, value);
      }
    });
    
    const queryString = queryParams.toString();
    return this._request(`/relationships${queryString ? `?${queryString}` : ''}`);
  }

  /**
   * Get relationships for a specific entity
   * @param {string} entityId - Entity ID
   * @param {string} relationshipType - Optional relationship type filter
   * @param {string} direction - Relationship direction ('outgoing', 'incoming', or 'both')
   * @returns {Promise<Array>} Entity relationships
   */
  async getEntityRelationships(entityId, relationshipType = null, direction = 'both') {
    const params = new URLSearchParams();
    if (relationshipType) params.append('relationship_type', relationshipType);
    params.append('direction', direction);
    
    return this._request(`/entities/${entityId}/relationships?${params.toString()}`);
  }

  /**
   * Create a new relationship
   * @param {Object} relationshipData - Relationship data
   * @returns {Promise<Object>} Created relationship
   */
  async createRelationship(relationshipData) {
    return this._request('/relationships', {
      method: 'POST',
      body: JSON.stringify(relationshipData)
    });
  }

  /**
   * Find paths between entities
   * @param {string} sourceId - Source entity ID
   * @param {string} targetId - Target entity ID
   * @param {Object} options - Path options
   * @returns {Promise<Array>} Paths between entities
   */
  async findPaths(sourceId, targetId, options = {}) {
    const params = new URLSearchParams();
    if (options.maxDepth) params.append('max_depth', options.maxDepth.toString());
    if (options.relationshipTypes) {
      options.relationshipTypes.forEach(type => 
        params.append('relationship_types[]', type)
      );
    }
    
    return this._request(`/relationships/path/${sourceId}/${targetId}?${params.toString()}`);
  }

  /**
   * Execute a graph query
   * @param {Object} queryRequest - Query request
   * @returns {Promise<Object>} Query results
   */
  async executeQuery(queryRequest) {
    return this._request('/query', {
      method: 'POST',
      body: JSON.stringify(queryRequest)
    });
  }

  /**
   * Execute a Cypher query directly
   * @param {string} cypher - Cypher query
   * @param {Object} parameters - Query parameters
   * @returns {Promise<Object>} Query results
   */
  async executeCypher(cypher, parameters = {}) {
    return this._request('/query/cypher', {
      method: 'POST',
      body: JSON.stringify({
        query: cypher,
        parameters
      })
    });
  }

  /**
   * Extract entities from text
   * @param {string} text - Text to analyze
   * @param {Array<string>} entityTypes - Optional entity types to extract
   * @returns {Promise<Object>} Extraction results
   */
  async extractEntities(text, entityTypes = null) {
    return this._request('/extraction/text', {
      method: 'POST',
      body: JSON.stringify({
        text,
        entity_types: entityTypes
      })
    });
  }

  /**
   * Get visualization data for the graph
   * @param {Object} params - Visualization parameters
   * @returns {Promise<Object>} Visualization data
   */
  async getVisualizationData(params = {}) {
    const queryParams = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        queryParams.append(key, value.toString());
      }
    });
    
    const queryString = queryParams.toString();
    return this._request(`/visualization/graph${queryString ? `?${queryString}` : ''}`);
  }

  /**
   * Get a knowledge-enhanced chat response
   * @param {string} query - User's question
   * @returns {Promise<Object>} Chat response
   */
  async knowledgeChat(query) {
    return this._request('/llm/chat', {
      method: 'POST',
      body: JSON.stringify({
        query
      })
    });
  }

  /**
   * Stream a knowledge-enhanced chat response
   * @param {string} query - User's question
   * @param {Function} onChunk - Callback for each chunk received
   * @returns {Promise<void>}
   */
  async streamKnowledgeChat(query, onChunk) {
    const url = `${this.baseUrl}${this.apiPath}/llm/chat/stream`;
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    });
    
    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }
    
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    let buffer = '';
    
    try {
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          // Process any remaining data in the buffer
          if (buffer) {
            try {
              const chunk = JSON.parse(buffer);
              onChunk(chunk);
            } catch (e) {
              console.error('Error parsing JSON from stream:', e);
            }
          }
          break;
        }
        
        // Decode chunk and add to buffer
        const chunkText = decoder.decode(value, { stream: true });
        buffer += chunkText;
        
        // Process complete JSON objects from buffer
        let newlineIndex;
        while ((newlineIndex = buffer.indexOf('\n')) !== -1) {
          const line = buffer.slice(0, newlineIndex).trim();
          buffer = buffer.slice(newlineIndex + 1);
          
          if (line) {
            try {
              const chunk = JSON.parse(line);
              onChunk(chunk);
            } catch (e) {
              console.error('Error parsing JSON from stream:', e);
            }
          }
        }
      }
    } catch (error) {
      console.error('Error reading stream:', error);
      throw error;
    }
  }
}

// Export the client class
export { AthenaClient };