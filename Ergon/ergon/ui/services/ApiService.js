/**
 * API Service for Ergon
 * Provides a wrapper around CLI functions for the GUI
 */

import { execute, sendToProcess, terminateProcess } from '../utils/execute';

/**
 * Service class that wraps Ergon CLI functions for the GUI
 * Acts as a bridge between React components and underlying CLI functionality
 */
class ErgonApiService {
  /**
   * Get a list of all available agents
   * Wraps 'ergon list' CLI command
   */
  async getAgents() {
    try {
      // Format the result from CLI command
      const result = await execute('list_agents');
      
      // The CLI might return the agents in a different format
      // We transform them to match our UI requirements
      if (result.error) {
        throw new Error(result.error);
      }
      
      // Extract agents from the result
      const agents = result.agents || [];
      return agents;
    } catch (error) {
      console.error('Error getting agents:', error);
      throw error;
    }
  }

  /**
   * Create a new agent with specified parameters
   * Wraps 'ergon create' CLI command
   */
  async createAgent({
    name,
    description,
    agentType = 'standard',
    model = null,
  }) {
    try {
      const result = await execute('create_agent', {
        name,
        description,
        agent_type: agentType,
        model
      });
      
      if (result.error) {
        throw new Error(result.error);
      }
      
      return result;
    } catch (error) {
      console.error('Error creating agent:', error);
      throw error;
    }
  }

  /**
   * Run an agent with specific input in non-interactive mode
   * Wraps 'ergon run' CLI command
   */
  async runAgent(agentIdentifier, input, timeout = null, timeoutAction = 'log') {
    try {
      const result = await execute('run_agent', {
        agent_identifier: agentIdentifier,
        input,
        timeout,
        timeout_action: timeoutAction
      });
      
      if (result.error) {
        throw new Error(result.error);
      }
      
      return result;
    } catch (error) {
      console.error('Error running agent:', error);
      throw error;
    }
  }

  /**
   * Delete an agent by ID or name
   * Wraps 'ergon delete' CLI command
   */
  async deleteAgent(agentIdentifier, force = false) {
    try {
      const result = await execute('delete_agent', {
        agent_identifier: agentIdentifier,
        force
      });
      
      if (result.error) {
        throw new Error(result.error);
      }
      
      return result;
    } catch (error) {
      console.error('Error deleting agent:', error);
      throw error;
    }
  }

  /**
   * Start an interactive chat session with an agent
   * This creates a connection to a long-running CLI process
   * Wraps 'ergon run --interactive' CLI command
   */
  async startInteractiveChat(agentIdentifier, options = {}) {
    try {
      // Create a streaming process for interactive chat
      const process = await execute('run_agent', {
        agent_identifier: agentIdentifier,
        timeout: options.timeout || null,
        timeout_action: options.timeoutAction || 'log',
        agent_type: options.agentType || 'standard',
        disable_memory: options.disableMemory || false
      }, { 
        streaming: true
      });
      
      // Set up message handler
      let messageCallback = options.onMessage || (() => {});
      process.on('message', (message) => {
        if (message.type === 'response') {
          messageCallback(message.content);
        } else if (message.type === 'error') {
          console.error('Error in chat process:', message.error);
          if (options.onError) {
            options.onError(message.error);
          }
        } else if (message.type === 'fatal') {
          console.error('Fatal error in chat process:', message.error);
          if (options.onError) {
            options.onError(message.error);
          }
        }
      });
      
      // Set up close handler
      process.on('close', (code) => {
        console.log(`Chat process closed with code ${code}`);
        if (options.onClose) {
          options.onClose(code);
        }
      });
      
      // Return session object
      return {
        processId: process.id,
        sendMessage: (message) => {
          process.send(message);
          return true;
        },
        endChat: () => {
          return terminateProcess(process.id);
        },
        onMessage: (callback) => {
          messageCallback = callback;
        }
      };
    } catch (error) {
      console.error('Error starting interactive chat:', error);
      throw error;
    }
  }

  /**
   * Preload documents for knowledge retrieval
   * Wraps 'ergon preload-docs' CLI command
   */
  async preloadDocuments(path, recursive = true) {
    try {
      const result = await execute('preload_docs_command', {
        path,
        recursive
      });
      
      if (result.error) {
        throw new Error(result.error);
      }
      
      return result;
    } catch (error) {
      console.error('Error preloading documents:', error);
      throw error;
    }
  }
}

export default new ErgonApiService();