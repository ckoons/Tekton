/**
 * Sophia Recommendations Implementation
 * 
 * This script provides functionality for the recommendations view in the Sophia dashboard,
 * including recommendation cards, filtering, status management, and implementation tracking.
 */

// Load Tekton config if available
if (typeof window.TektonConfig === 'undefined' && document.querySelector('script[src*="tekton-config.js"]') === null) {
  const script = document.createElement('script');
  script.src = '/scripts/shared/tekton-config.js';
  document.head.appendChild(script);
}

// Initialize the recommendations system when the DOM is loaded
document.addEventListener('DOMContentLoaded', initRecommendations);

// Global state for recommendations
const recommendationsState = {
  recommendations: [],
  filters: {
    status: '',
    priority: '',
    component: ''
  },
  selectedRecommendation: null
};

/**
 * Initialize the recommendations functionality
 */
function initRecommendations() {
  console.log('Initializing Sophia recommendations...');
  
  // Set up filter event listeners
  setupRecommendationFilters();
  
  // Set up modal event listeners
  setupRecommendationModals();
  
  console.log('Sophia recommendations initialized');
}

/**
 * Set up recommendation filters
 */
function setupRecommendationFilters() {
  // Status filter
  const statusFilter = document.getElementById('sophia-recommendations-status-filter');
  if (statusFilter) {
    statusFilter.addEventListener('change', function() {
      recommendationsState.filters.status = this.value;
      updateRecommendationsList();
    });
  }
  
  // Priority filter
  const priorityFilter = document.getElementById('sophia-recommendations-priority-filter');
  if (priorityFilter) {
    priorityFilter.addEventListener('change', function() {
      recommendationsState.filters.priority = this.value;
      updateRecommendationsList();
    });
  }
  
  // Component filter
  const componentFilter = document.getElementById('sophia-recommendations-component-filter');
  if (componentFilter) {
    componentFilter.addEventListener('change', function() {
      recommendationsState.filters.component = this.value;
      updateRecommendationsList();
    });
  }
}

/**
 * Set up recommendation modal event listeners
 */
function setupRecommendationModals() {
  // Action button in the recommendation modal
  const actionBtn = document.getElementById('sophia-recommendation-action-btn');
  if (actionBtn) {
    actionBtn.addEventListener('click', handleRecommendationAction);
  }
}

/**
 * Handle recommendation action button click
 */
function handleRecommendationAction() {
  const recommendation = recommendationsState.selectedRecommendation;
  if (!recommendation) return;
  
  // Get action based on current status
  let nextStatus = '';
  let actionText = '';
  
  switch (recommendation.status) {
    case 'pending':
      nextStatus = 'approved';
      actionText = 'Approve';
      break;
    case 'approved':
      nextStatus = 'in_progress';
      actionText = 'Start Implementation';
      break;
    case 'in_progress':
      nextStatus = 'implemented';
      actionText = 'Mark as Implemented';
      break;
    case 'implemented':
      nextStatus = 'verified';
      actionText = 'Verify';
      break;
    default:
      nextStatus = 'pending';
      actionText = 'Reset';
  }
  
  // Update the recommendation status
  updateRecommendationStatus(recommendation.id, nextStatus)
    .then(() => {
      // Close the modal
      const modal = document.getElementById('sophia-recommendation-modal');
      if (modal && typeof bootstrap !== 'undefined') {
        const bsModal = bootstrap.Modal.getInstance(modal);
        if (bsModal) {
          bsModal.hide();
        }
      }
      
      // Refresh recommendations
      loadRecommendations();
    })
    .catch(error => {
      console.error('Error updating recommendation status:', error);
      showNotification('Error updating recommendation status', 'error');
    });
}

/**
 * Load recommendations from the API
 * @returns {Promise} A promise that resolves when recommendations are loaded
 */
function loadRecommendations() {
  // Reset selection
  recommendationsState.selectedRecommendation = null;
  
  // Build query parameters based on filters
  const params = new URLSearchParams();
  
  if (recommendationsState.filters.status) {
    params.append('status', recommendationsState.filters.status);
  }
  
  if (recommendationsState.filters.priority) {
    params.append('priority', recommendationsState.filters.priority);
  }
  
  if (recommendationsState.filters.component) {
    params.append('target_components', recommendationsState.filters.component);
  }
  
  // Add pagination parameters
  params.append('limit', '100');
  params.append('offset', '0');
  
  // Fetch recommendations from API
  const baseUrl = window.TektonConfig ? window.TektonConfig.getSophiaUrl('/api') : (window.env?.SOPHIA_API_URL || 'http://localhost:8114/api');
  return fetch(`${baseUrl}/recommendations?${params.toString()}`)
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      recommendationsState.recommendations = data.items || [];
      updateRecommendationsList();
      return data;
    })
    .catch(error => {
      console.error('Error loading recommendations:', error);
      showNotification('Error loading recommendations', 'error');
      return [];
    });
}

/**
 * Update the recommendations list UI
 */
function updateRecommendationsList() {
  const tbody = document.getElementById('sophia-recommendations-tbody');
  if (!tbody) return;
  
  // Clear the table body
  tbody.innerHTML = '';
  
  // Check if we have recommendations
  if (recommendationsState.recommendations.length === 0) {
    const row = document.createElement('tr');
    const cell = document.createElement('td');
    cell.setAttribute('colspan', '6');
    cell.textContent = 'No recommendations found';
    cell.style.textAlign = 'center';
    row.appendChild(cell);
    tbody.appendChild(row);
    return;
  }
  
  // Add rows for each recommendation
  recommendationsState.recommendations.forEach(recommendation => {
    const row = document.createElement('tr');
    tbody.appendChild(row);
    
    // Title
    const titleCell = document.createElement('td');
    titleCell.textContent = recommendation.title;
    row.appendChild(titleCell);
    
    // Type
    const typeCell = document.createElement('td');
    typeCell.textContent = recommendation.recommendation_type || '-';
    row.appendChild(typeCell);
    
    // Priority
    const priorityCell = document.createElement('td');
    priorityCell.textContent = recommendation.priority || '-';
    // Add color based on priority
    if (recommendation.priority === 'critical') {
      priorityCell.style.color = 'red';
      priorityCell.style.fontWeight = 'bold';
    } else if (recommendation.priority === 'high') {
      priorityCell.style.color = 'orange';
      priorityCell.style.fontWeight = 'bold';
    }
    row.appendChild(priorityCell);
    
    // Components
    const componentsCell = document.createElement('td');
    if (recommendation.target_components && recommendation.target_components.length > 0) {
      componentsCell.textContent = recommendation.target_components.join(', ');
    } else {
      componentsCell.textContent = 'All';
    }
    row.appendChild(componentsCell);
    
    // Status
    const statusCell = document.createElement('td');
    const statusBadge = document.createElement('span');
    statusBadge.className = 'badge';
    
    // Set badge class based on status
    switch (recommendation.status) {
      case 'pending':
        statusBadge.classList.add('bg-secondary');
        break;
      case 'approved':
        statusBadge.classList.add('bg-primary');
        break;
      case 'in_progress':
        statusBadge.classList.add('bg-info');
        break;
      case 'implemented':
        statusBadge.classList.add('bg-warning');
        break;
      case 'verified':
        statusBadge.classList.add('bg-success');
        break;
      case 'rejected':
        statusBadge.classList.add('bg-danger');
        break;
      default:
        statusBadge.classList.add('bg-secondary');
    }
    
    statusBadge.textContent = recommendation.status || 'Unknown';
    statusCell.appendChild(statusBadge);
    row.appendChild(statusCell);
    
    // Actions
    const actionsCell = document.createElement('td');
    
    // View button
    const viewBtn = document.createElement('button');
    viewBtn.className = 'btn btn-sm btn-outline-primary me-1';
    viewBtn.textContent = 'View';
    viewBtn.addEventListener('click', () => showRecommendationDetails(recommendation));
    actionsCell.appendChild(viewBtn);
    
    // Action button (changes based on status)
    const actionBtn = document.createElement('button');
    actionBtn.className = 'btn btn-sm btn-primary';
    
    // Set action text based on status
    switch (recommendation.status) {
      case 'pending':
        actionBtn.textContent = 'Approve';
        break;
      case 'approved':
        actionBtn.textContent = 'Start';
        break;
      case 'in_progress':
        actionBtn.textContent = 'Complete';
        break;
      case 'implemented':
        actionBtn.textContent = 'Verify';
        break;
      case 'verified':
        actionBtn.textContent = 'View';
        break;
      case 'rejected':
        actionBtn.textContent = 'Reconsider';
        break;
      default:
        actionBtn.textContent = 'Update';
    }
    
    actionBtn.addEventListener('click', () => showRecommendationDetails(recommendation, true));
    actionsCell.appendChild(actionBtn);
    
    row.appendChild(actionsCell);
  });
}

/**
 * Show recommendation details in a modal
 * @param {Object} recommendation - The recommendation object
 * @param {boolean} showAction - Whether to show the action button
 */
function showRecommendationDetails(recommendation, showAction = false) {
  // Store selected recommendation
  recommendationsState.selectedRecommendation = recommendation;
  
  // Get modal elements
  const modal = document.getElementById('sophia-recommendation-modal');
  const title = modal?.querySelector('.modal-title');
  const details = document.getElementById('sophia-recommendation-details');
  const actionBtn = document.getElementById('sophia-recommendation-action-btn');
  
  if (!modal || !title || !details || !actionBtn) {
    console.error('Modal elements not found');
    return;
  }
  
  // Set modal title
  title.textContent = recommendation.title;
  
  // Build details HTML
  let detailsHtml = `
    <div class="recommendation-header">
      <div class="recommendation-meta">
        <span class="badge ${getBadgeClass(recommendation.priority)}">${recommendation.priority || 'Unknown'}</span>
        <span class="badge ${getStatusBadgeClass(recommendation.status)}">${recommendation.status || 'Unknown'}</span>
      </div>
      <div class="recommendation-components mt-2">
        <strong>Target Components:</strong> ${recommendation.target_components?.join(', ') || 'All Components'}
      </div>
    </div>
    
    <div class="recommendation-body mt-3">
      <h5>Description</h5>
      <p>${recommendation.description || 'No description provided'}</p>
      
      <h5 class="mt-3">Rationale</h5>
      <p>${recommendation.rationale || 'No rationale provided'}</p>
      
      <div class="row mt-3">
        <div class="col-md-6">
          <h5>Expected Impact</h5>
          <ul>
  `;
  
  // Add expected impact items
  if (recommendation.expected_impact && typeof recommendation.expected_impact === 'object') {
    Object.entries(recommendation.expected_impact).forEach(([key, value]) => {
      detailsHtml += `<li><strong>${key}:</strong> ${value}</li>`;
    });
  } else {
    detailsHtml += `<li>No impact information provided</li>`;
  }
  
  detailsHtml += `
          </ul>
        </div>
        <div class="col-md-6">
          <h5>Implementation Complexity</h5>
          <p>${recommendation.implementation_complexity || 'Unknown'}</p>
          
          <h5 class="mt-3">Implementation Steps</h5>
          <ol>
  `;
  
  // Add implementation steps
  if (recommendation.implementation_steps && Array.isArray(recommendation.implementation_steps)) {
    recommendation.implementation_steps.forEach(step => {
      detailsHtml += `<li>${step}</li>`;
    });
  } else if (recommendation.implementation_steps && typeof recommendation.implementation_steps === 'object') {
    Object.entries(recommendation.implementation_steps).forEach(([key, value]) => {
      detailsHtml += `<li><strong>${key}:</strong> ${value}</li>`;
    });
  } else {
    detailsHtml += `<li>No implementation steps provided</li>`;
  }
  
  detailsHtml += `
          </ol>
        </div>
      </div>
    `;
  
  // Add supporting evidence if available
  if (recommendation.supporting_evidence) {
    detailsHtml += `
      <div class="recommendation-evidence mt-3">
        <h5>Supporting Evidence</h5>
        <div class="card bg-light">
          <div class="card-body">
    `;
    
    if (typeof recommendation.supporting_evidence === 'string') {
      detailsHtml += `<p>${recommendation.supporting_evidence}</p>`;
    } else if (typeof recommendation.supporting_evidence === 'object') {
      Object.entries(recommendation.supporting_evidence).forEach(([key, value]) => {
        detailsHtml += `<p><strong>${key}:</strong> ${value}</p>`;
      });
    }
    
    detailsHtml += `
          </div>
        </div>
      </div>
    `;
  }
  
  // Add verification results if available and status is verified
  if (recommendation.status === 'verified' && recommendation.verification_results) {
    detailsHtml += `
      <div class="recommendation-verification mt-3">
        <h5>Verification Results</h5>
        <div class="card bg-success text-white">
          <div class="card-body">
    `;
    
    if (typeof recommendation.verification_results === 'string') {
      detailsHtml += `<p>${recommendation.verification_results}</p>`;
    } else if (typeof recommendation.verification_results === 'object') {
      Object.entries(recommendation.verification_results).forEach(([key, value]) => {
        detailsHtml += `<p><strong>${key}:</strong> ${value}</p>`;
      });
    }
    
    detailsHtml += `
          </div>
        </div>
      </div>
    `;
  }
  
  // Set details content
  details.innerHTML = detailsHtml;
  
  // Configure action button
  if (showAction) {
    actionBtn.style.display = 'block';
    
    // Set button text based on status
    switch (recommendation.status) {
      case 'pending':
        actionBtn.textContent = 'Approve';
        break;
      case 'approved':
        actionBtn.textContent = 'Start Implementation';
        break;
      case 'in_progress':
        actionBtn.textContent = 'Mark as Implemented';
        break;
      case 'implemented':
        actionBtn.textContent = 'Verify';
        break;
      case 'verified':
        actionBtn.textContent = 'View Impact';
        break;
      case 'rejected':
        actionBtn.textContent = 'Reconsider';
        break;
      default:
        actionBtn.textContent = 'Update Status';
    }
  } else {
    actionBtn.style.display = 'none';
  }
  
  // Show the modal
  if (typeof bootstrap !== 'undefined') {
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
  } else {
    // Fallback for when Bootstrap is not available
    modal.style.display = 'block';
  }
}

/**
 * Update a recommendation's status
 * @param {string} id - Recommendation ID
 * @param {string} status - New status
 * @returns {Promise} A promise that resolves when the status is updated
 */
function updateRecommendationStatus(id, status) {
  const baseUrl = window.TektonConfig ? window.TektonConfig.getSophiaUrl('/api') : (window.env?.SOPHIA_API_URL || 'http://localhost:8114/api');
  return fetch(`${baseUrl}/recommendations/${id}/status/${status}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    }
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    showNotification(`Recommendation status updated to ${status}`, 'success');
    return data;
  });
}

/**
 * Create a new recommendation
 * @param {Object} recommendation - Recommendation data
 * @returns {Promise} A promise that resolves with the created recommendation
 */
function createRecommendation(recommendation) {
  const baseUrl = window.TektonConfig ? window.TektonConfig.getSophiaUrl('/api') : (window.env?.SOPHIA_API_URL || 'http://localhost:8114/api');
  return fetch(`${baseUrl}/recommendations`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(recommendation)
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    showNotification('New recommendation created', 'success');
    return data;
  });
}

/**
 * Get badge class for priority
 * @param {string} priority - Priority level
 * @returns {string} Badge class
 */
function getBadgeClass(priority) {
  switch (priority) {
    case 'critical':
      return 'bg-danger';
    case 'high':
      return 'bg-warning text-dark';
    case 'medium':
      return 'bg-info text-dark';
    case 'low':
      return 'bg-secondary';
    default:
      return 'bg-light text-dark';
  }
}

/**
 * Get badge class for status
 * @param {string} status - Recommendation status
 * @returns {string} Badge class
 */
function getStatusBadgeClass(status) {
  switch (status) {
    case 'pending':
      return 'bg-secondary';
    case 'approved':
      return 'bg-primary';
    case 'in_progress':
      return 'bg-info text-dark';
    case 'implemented':
      return 'bg-warning text-dark';
    case 'verified':
      return 'bg-success';
    case 'rejected':
      return 'bg-danger';
    default:
      return 'bg-secondary';
  }
}

/**
 * Show a notification message
 * @param {string} message - The notification message
 * @param {string} type - Notification type (success, error, info, warning)
 */
function showNotification(message, type = 'info') {
  // Check if notification function is available in parent UI
  if (typeof window.showNotification === 'function') {
    window.showNotification(message, type);
  } else {
    // Fallback to console
    switch (type) {
      case 'error':
        console.error(message);
        break;
      case 'warning':
        console.warn(message);
        break;
      case 'success':
        console.log('%c' + message, 'color: green');
        break;
      default:
        console.log(message);
    }
  }
}

// Export functions for use in other scripts
window.sophiaRecommendations = {
  loadRecommendations,
  updateRecommendationsList,
  createRecommendation,
  updateRecommendationStatus,
  showRecommendationDetails
};