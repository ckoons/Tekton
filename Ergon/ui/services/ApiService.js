/**
 * Ergon API Service
 * 
 * This service provides a JavaScript interface to the Ergon CLI functions,
 * allowing the UI to interact with Ergon functionality.
 */

// Base API URL for Ergon
const API_BASE_URL = '/api/ergon';

/**
 * Get all available agents
 * @returns {Promise<Array>} List of agents
 */
export const getAgents = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/agents`);
    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }
    const data = await response.json();
    return data.agents;
  } catch (error) {
    console.error('Error fetching agents:', error);
    throw error;
  }
};

/**
 * Get a specific agent by ID
 * @param {string|number} agentId Agent ID
 * @returns {Promise<Object>} Agent details
 */
export const getAgentById = async (agentId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/agents/${agentId}`);
    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`Error fetching agent ${agentId}:`, error);
    throw error;
  }
};

/**
 * Create a new agent
 * @param {Object} agentData Agent configuration
 * @returns {Promise<Object>} Created agent
 */
export const createAgent = async (agentData) => {
  try {
    const response = await fetch(`${API_BASE_URL}/agents/create`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(agentData),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error creating agent:', error);
    throw error;
  }
};

/**
 * Delete an agent
 * @param {string|number} agentId Agent ID
 * @param {boolean} force Force deletion
 * @returns {Promise<Object>} Response data
 */
export const deleteAgent = async (agentId, force = false) => {
  try {
    const response = await fetch(`${API_BASE_URL}/agents/delete/${agentId}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ force }),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error deleting agent ${agentId}:`, error);
    throw error;
  }
};

/**
 * Run an agent with optional parameters
 * @param {string|number} agentId Agent ID
 * @param {Object} options Run options (input, interactive, timeout, etc.)
 * @returns {Promise<Object>} Run result
 */
export const runAgent = async (agentId, options = {}) => {
  try {
    const response = await fetch(`${API_BASE_URL}/agents/run/${agentId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(options),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error running agent ${agentId}:`, error);
    throw error;
  }
};

/**
 * Get agent types
 * @returns {Promise<Array>} List of agent types
 */
export const getAgentTypes = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/agent-types`);
    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }
    const data = await response.json();
    return data.types;
  } catch (error) {
    console.error('Error fetching agent types:', error);
    throw error;
  }
};

/**
 * Get settings for Ergon
 * @returns {Promise<Object>} Settings object
 */
export const getSettings = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/settings`);
    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching settings:', error);
    throw error;
  }
};

/**
 * Update settings
 * @param {Object} settings Settings to update
 * @returns {Promise<Object>} Updated settings
 */
export const updateSettings = async (settings) => {
  try {
    const response = await fetch(`${API_BASE_URL}/settings`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(settings),
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error updating settings:', error);
    throw error;
  }
};

// Export all functions as a service object
export default {
  getAgents,
  getAgentById,
  createAgent,
  deleteAgent,
  runAgent,
  getAgentTypes,
  getSettings,
  updateSettings
};