/**
 * Metis Service
 * 
 * Service for interacting with the Metis API for task management functionality.
 * Handles API requests, WebSocket connections, and data transformations.
 */

import { getAppConfig } from '../env.js';

export class MetisService {
  constructor() {
    this.apiUrl = null;
    this.wsConnection = null;
    this.eventHandlers = {
      'TASK_CREATED': [],
      'TASK_UPDATED': [],
      'TASK_DELETED': [],
      'DEPENDENCY_ADDED': [],
      'DEPENDENCY_REMOVED': [],
      'COMPLEXITY_UPDATED': []
    };
    
    this.initService();
  }

  async initService() {
    try {
      const config = await getAppConfig();
      const metisPort = window.METIS_PORT || 8011;
      this.apiUrl = config.metisApiUrl || `http://localhost:${metisPort}/api/v1`;
      this.wsUrl = config.metisWsUrl || `ws://localhost:${metisPort}/ws`;
      console.log('Metis service initialized with API URL:', this.apiUrl);
    } catch (error) {
      console.error('Failed to initialize Metis service:', error);
    }
  }

  async connectWebSocket() {
    if (!this.wsUrl) {
      console.error('WebSocket URL not configured');
      return;
    }

    try {
      this.wsConnection = new WebSocket(this.wsUrl);
      
      this.wsConnection.onopen = () => {
        console.log('Connected to Metis WebSocket');
      };
      
      this.wsConnection.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.handleWebSocketMessage(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
      
      this.wsConnection.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
      
      this.wsConnection.onclose = () => {
        console.log('WebSocket connection closed, reconnecting in 5 seconds...');
        setTimeout(() => this.connectWebSocket(), 5000);
      };
    } catch (error) {
      console.error('Failed to connect to WebSocket:', error);
      setTimeout(() => this.connectWebSocket(), 5000);
    }
  }

  handleWebSocketMessage(data) {
    const eventType = data.event;
    const payload = data.payload;
    
    if (this.eventHandlers[eventType]) {
      this.eventHandlers[eventType].forEach(handler => {
        try {
          handler(payload);
        } catch (error) {
          console.error(`Error in ${eventType} handler:`, error);
        }
      });
    }
  }

  addEventListener(eventType, handler) {
    if (this.eventHandlers[eventType]) {
      this.eventHandlers[eventType].push(handler);
    } else {
      console.warn(`Unknown event type: ${eventType}`);
    }
  }

  removeEventListener(eventType, handler) {
    if (this.eventHandlers[eventType]) {
      this.eventHandlers[eventType] = this.eventHandlers[eventType].filter(h => h !== handler);
    }
  }

  async fetchWithErrorHandling(url, options = {}) {
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        }
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API request failed: ${response.status} ${response.statusText} - ${errorText}`);
      }
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API request error:', error);
      throw error;
    }
  }

  // Tasks API

  async getTasks(filters = {}) {
    const queryParams = new URLSearchParams();
    
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        queryParams.append(key, value);
      }
    });
    
    const url = `${this.apiUrl}/tasks${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
    return this.fetchWithErrorHandling(url);
  }

  async getTask(taskId) {
    return this.fetchWithErrorHandling(`${this.apiUrl}/tasks/${taskId}`);
  }

  async createTask(taskData) {
    return this.fetchWithErrorHandling(`${this.apiUrl}/tasks`, {
      method: 'POST',
      body: JSON.stringify(taskData)
    });
  }

  async updateTask(taskId, taskData) {
    return this.fetchWithErrorHandling(`${this.apiUrl}/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(taskData)
    });
  }

  async deleteTask(taskId) {
    return this.fetchWithErrorHandling(`${this.apiUrl}/tasks/${taskId}`, {
      method: 'DELETE'
    });
  }

  // Dependencies API

  async getTaskDependencies(taskId) {
    return this.fetchWithErrorHandling(`${this.apiUrl}/tasks/${taskId}/dependencies`);
  }

  async addDependency(taskId, dependencyId) {
    return this.fetchWithErrorHandling(`${this.apiUrl}/tasks/${taskId}/dependencies`, {
      method: 'POST',
      body: JSON.stringify({ dependency_id: dependencyId })
    });
  }

  async removeDependency(taskId, dependencyId) {
    return this.fetchWithErrorHandling(`${this.apiUrl}/tasks/${taskId}/dependencies/${dependencyId}`, {
      method: 'DELETE'
    });
  }

  // Complexity API

  async analyzeTaskComplexity(taskId) {
    return this.fetchWithErrorHandling(`${this.apiUrl}/tasks/${taskId}/analyze-complexity`, {
      method: 'POST'
    });
  }

  async getComplexityReport() {
    return this.fetchWithErrorHandling(`${this.apiUrl}/tasks/complexity-report`);
  }

  // PRD API

  async parsePRD(fileContent) {
    return this.fetchWithErrorHandling(`${this.apiUrl}/prd/parse`, {
      method: 'POST',
      body: JSON.stringify({ content: fileContent })
    });
  }
}