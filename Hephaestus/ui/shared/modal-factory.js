// Tekton Modal Factory - HTML injection pattern with promise-based API
// CSS-first approach with minimal JavaScript

window.TektonModal = (function() {
    'use strict';
    
    // Track active modals for cleanup
    let activeModals = [];
    let modalIdCounter = 0;
    
    // Generate unique modal ID
    function generateModalId() {
        return `tekton-modal-${++modalIdCounter}`;
    }
    
    // Close modal by ID
    function closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.remove();
            activeModals = activeModals.filter(id => id !== modalId);
        }
    }
    
    // Close all modals
    function closeAllModals() {
        activeModals.forEach(id => {
            const modal = document.getElementById(id);
            if (modal) modal.remove();
        });
        activeModals = [];
    }
    
    // Handle escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && activeModals.length > 0) {
            // Close the most recent modal
            const lastModalId = activeModals[activeModals.length - 1];
            closeModal(lastModalId);
        }
    });
    
    // Main show function with HTML injection
    function show(options) {
        const defaults = {
            title: 'Notification',
            message: '',
            type: 'default', // default, success, error, warning, info
            size: 'medium', // small, medium, large, fullscreen
            buttons: ['OK'],
            showClose: true,
            closeOnBackdrop: true
        };
        
        const config = Object.assign({}, defaults, options);
        const modalId = generateModalId();
        
        // Get icon based on type
        let iconHTML = '';
        if (config.type !== 'default') {
            iconHTML = `<span class="tekton-modal-icon tekton-modal-icon--${config.type}"></span>`;
        }
        
        // Build buttons HTML
        const buttonsHTML = config.buttons.map((btn, index) => {
            const isPrimary = index === config.buttons.length - 1;
            const btnClass = isPrimary ? 'tekton-modal-btn--primary' : 'tekton-modal-btn--secondary';
            return `<button class="tekton-modal-btn ${btnClass}" data-button-index="${index}">${btn}</button>`;
        }).join('');
        
        // Build close button if needed
        const closeButtonHTML = config.showClose 
            ? `<button class="tekton-modal-close" data-close="true">×</button>` 
            : '';
        
        // Create modal with HTML injection
        const modalOverlay = document.createElement('div');
        modalOverlay.className = 'tekton-modal-backdrop';
        modalOverlay.id = modalId;
        
        // Handle backdrop click if enabled
        if (config.closeOnBackdrop) {
            modalOverlay.setAttribute('data-close-on-backdrop', 'true');
        }
        
        // Inject HTML structure
        modalOverlay.innerHTML = `
            <div class="tekton-modal tekton-modal--${config.size} tekton-modal--${config.type}" tabindex="-1">
                <div class="tekton-modal-header">
                    <h3 class="tekton-modal-title">
                        ${iconHTML}
                        ${config.title}
                    </h3>
                    ${closeButtonHTML}
                </div>
                <div class="tekton-modal-body">
                    <div class="tekton-modal-message">${config.message}</div>
                </div>
                <div class="tekton-modal-footer">
                    ${buttonsHTML}
                </div>
            </div>
        `;
        
        // Append to body
        document.body.appendChild(modalOverlay);
        activeModals.push(modalId);
        
        // Focus on modal for accessibility
        const modalElement = modalOverlay.querySelector('.tekton-modal');
        if (modalElement) {
            modalElement.focus();
        }
        
        // Return promise for async operations
        return new Promise((resolve) => {
            // Event delegation for buttons
            modalOverlay.addEventListener('click', function(e) {
                // Handle backdrop click
                if (e.target === modalOverlay && config.closeOnBackdrop) {
                    closeModal(modalId);
                    resolve(null);
                    return;
                }
                
                // Handle close button
                if (e.target.hasAttribute('data-close')) {
                    closeModal(modalId);
                    resolve(null);
                    return;
                }
                
                // Handle action buttons
                if (e.target.hasAttribute('data-button-index')) {
                    const buttonIndex = parseInt(e.target.getAttribute('data-button-index'));
                    closeModal(modalId);
                    resolve(buttonIndex);
                }
            });
        });
    }
    
    // Alert replacement - simple notification
    function alert(message, title = 'Alert') {
        return show({
            title: title,
            message: message,
            type: 'info',
            buttons: ['OK']
        });
    }
    
    // Confirm replacement - returns promise resolving to boolean
    async function confirm(message, title = 'Confirm') {
        const result = await show({
            title: title,
            message: message,
            type: 'warning',
            buttons: ['Cancel', 'Confirm']
        });
        return result === 1; // Returns true if Confirm was clicked
    }
    
    // Success modal with green accent
    function success(message, title = 'Success') {
        return show({
            title: title,
            message: message,
            type: 'success',
            buttons: ['OK']
        });
    }
    
    // Error modal with red accent
    function error(message, title = 'Error') {
        return show({
            title: title,
            message: message,
            type: 'error',
            buttons: ['OK']
        });
    }
    
    // Warning modal with orange accent
    function warning(message, title = 'Warning') {
        return show({
            title: title,
            message: message,
            type: 'warning',
            buttons: ['OK']
        });
    }
    
    // Info modal with blue accent
    function info(message, title = 'Information') {
        return show({
            title: title,
            message: message,
            type: 'info',
            buttons: ['OK']
        });
    }
    
    // Loading modal - special case with spinner
    function loading(message = 'Loading...', title = 'Please Wait') {
        const modalId = generateModalId();
        
        const modalOverlay = document.createElement('div');
        modalOverlay.className = 'tekton-modal-backdrop';
        modalOverlay.id = modalId;
        
        // Loading modal HTML injection
        modalOverlay.innerHTML = `
            <div class="tekton-modal tekton-modal--small tekton-modal--loading" tabindex="-1">
                <div class="tekton-modal-header">
                    <h3 class="tekton-modal-title">${title}</h3>
                </div>
                <div class="tekton-modal-body">
                    <div class="tekton-modal-spinner"></div>
                    <div class="tekton-modal-loading-text">${message}</div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modalOverlay);
        activeModals.push(modalId);
        
        // Return close function for loading modal
        return function() {
            closeModal(modalId);
        };
    }
    
    // Prompt modal - returns promise with input value
    async function prompt(message, title = 'Input Required', defaultValue = '') {
        const modalId = generateModalId();
        
        const modalOverlay = document.createElement('div');
        modalOverlay.className = 'tekton-modal-backdrop';
        modalOverlay.id = modalId;
        
        // Prompt modal HTML injection
        modalOverlay.innerHTML = `
            <div class="tekton-modal tekton-modal--medium" tabindex="-1">
                <div class="tekton-modal-header">
                    <h3 class="tekton-modal-title">${title}</h3>
                    <button class="tekton-modal-close" data-close="true">×</button>
                </div>
                <div class="tekton-modal-body">
                    <div class="tekton-modal-message">${message}</div>
                    <input type="text" class="tekton-modal-input" value="${defaultValue}" 
                           style="width: 100%; padding: 8px; margin-top: 12px; 
                                  background: var(--bg-tertiary, #333345); 
                                  border: 1px solid var(--border-color, #444444); 
                                  color: var(--text-primary, #f0f0f0); 
                                  border-radius: 4px;">
                </div>
                <div class="tekton-modal-footer">
                    <button class="tekton-modal-btn tekton-modal-btn--secondary" data-action="cancel">Cancel</button>
                    <button class="tekton-modal-btn tekton-modal-btn--primary" data-action="submit">Submit</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modalOverlay);
        activeModals.push(modalId);
        
        // Focus on input
        const inputElement = modalOverlay.querySelector('.tekton-modal-input');
        if (inputElement) {
            inputElement.focus();
            inputElement.select();
        }
        
        return new Promise((resolve) => {
            // Handle events
            modalOverlay.addEventListener('click', function(e) {
                if (e.target.hasAttribute('data-close') || 
                    e.target.getAttribute('data-action') === 'cancel') {
                    closeModal(modalId);
                    resolve(null);
                } else if (e.target.getAttribute('data-action') === 'submit') {
                    const value = inputElement.value;
                    closeModal(modalId);
                    resolve(value);
                }
            });
            
            // Handle enter key in input
            inputElement.addEventListener('keydown', function(e) {
                if (e.key === 'Enter') {
                    const value = inputElement.value;
                    closeModal(modalId);
                    resolve(value);
                }
            });
        });
    }
    
    // Public API
    return {
        show: show,
        alert: alert,
        confirm: confirm,
        success: success,
        error: error,
        warning: warning,
        info: info,
        loading: loading,
        prompt: prompt,
        closeAll: closeAllModals
    };
})();

// Make individual functions available for convenience
window.TektonAlert = TektonModal.alert;
window.TektonConfirm = TektonModal.confirm;
window.TektonSuccess = TektonModal.success;
window.TektonError = TektonModal.error;