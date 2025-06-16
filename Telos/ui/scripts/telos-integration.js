/**
 * Telos Integration with Hephaestus UI
 * 
 * This script handles the integration of the Telos component with the
 * Hephaestus UI system, following the Component Pattern and State Management approach.
 */

import TelosComponent from './telos-component.js';
import TelosService from './telos-service.js';

// Initialize as a singleton
let telosServiceInstance = null;

/**
 * Create or get the singleton Telos service instance
 */
function getTelosService() {
  if (!telosServiceInstance) {
    telosServiceInstance = new TelosService();
  }
  return telosServiceInstance;
}

/**
 * Initialize the Telos component and register it with Hephaestus
 * @param {Object} stateManager - Hephaestus state manager
 */
function initializeTelosComponent(stateManager) {
  // Initialize service
  const telosService = getTelosService();
  telosService.initialize(stateManager);
  
  // Register component state
  stateManager.registerState('projects', {
    list: [],
    selectedProject: null,
    loaded: false
  });
  
  stateManager.registerState('requirements', {
    list: [],
    selected: null,
    loaded: false,
    projectId: null,
    filteredList: []
  });
  
  stateManager.registerState('traces', {
    list: [],
    loaded: false,
    projectId: null,
    requirementId: null
  });
  
  stateManager.registerState('telosUI', {
    view: 'list',
    filters: {
      status: '',
      type: '',
      priority: '',
      search: ''
    },
    dialogs: {
      newProject: false,
      newRequirement: false,
      confirmation: false
    }
  });
  
  // Create and export bindings for UI component
  return {
    // Core data operations
    fetchProjects: telosService.fetchProjects,
    fetchRequirements: telosService.fetchRequirements,
    fetchRequirementDetails: telosService.fetchRequirementDetails,
    fetchTraces: telosService.fetchTraces,
    
    // Project operations
    createProject: telosService.createProject,
    updateProject: telosService.updateProject,
    deleteProject: telosService.deleteProject,
    
    // Requirement operations
    createRequirement: telosService.createRequirement,
    updateRequirement: telosService.updateRequirement,
    deleteRequirement: telosService.deleteRequirement,
    validateRequirement: telosService.validateRequirement,
    refineRequirement: telosService.refineRequirement,
    
    // Trace operations
    createTrace: telosService.createTrace,
    updateTrace: telosService.updateTrace,
    deleteTrace: telosService.deleteTrace,
    
    // Import/Export
    exportProject: telosService.exportProject,
    importProject: telosService.importProject,
    
    // Component class
    TelosComponent
  };
}

/**
 * Register the Telos component with Hephaestus
 */
function registerWithHephaestus() {
  // Check if Hephaestus is available
  if (!window.Hephaestus) {
    console.error('Hephaestus UI not available - Telos component registration failed');
    return;
  }
  
  // Register component with Hephaestus
  window.Hephaestus.registerComponent('telos', {
    name: 'Telos Requirements Manager',
    description: 'Requirements management, tracing, and validation',
    version: '1.0.0',
    icon: '/Telos/images/icon.jpg',
    initializer: initializeTelosComponent,
    requires: ['stateManager'],
    template: '/Telos/ui/telos-component.html',
    element: 'telos-component'
  });
  
  console.log('Telos component successfully registered with Hephaestus');
}

// Auto-register with Hephaestus when the script loads
document.addEventListener('DOMContentLoaded', registerWithHephaestus);

// Export the module for direct use
export {
  initializeTelosComponent,
  registerWithHephaestus,
  TelosComponent,
  TelosService,
  getTelosService
};