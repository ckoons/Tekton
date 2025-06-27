/**
 * DEPRECATED: This file will be removed after CSS-first migration is verified
 * Component Utilities
 * 
 * Shared utilities for components in Hephaestus UI
 * These utilities provide common functionality across components:
 * - Notification System
 * - Loading Indicators
 * - Component Lifecycle Management
 * - Base Service Pattern
 */

class ComponentUtils {
    constructor() {
        this.initialized = false;
    }
    
    /**
     * Initialize all component utilities
     */
    init() {
        if (this.initialized) return;
        
        // Create utility namespace in global tektonUI
        window.tektonUI = window.tektonUI || {};
        window.tektonUI.componentUtils = {};
        window.tektonUI.services = window.tektonUI.services || {};
        
        // Initialize all utility modules
        this._initNotificationSystem();
        this._initLoadingIndicator();
        this._initLifecycleManagement();
        this._initDomHelpers();
        this._initBaseService();
        
        this.initialized = true;
        console.log('Component utilities initialized');
        
        return this;
    }
    
    /**
     * Initialize the notification system
     */
    _initNotificationSystem() {
        // Notification System
        window.tektonUI.componentUtils.notifications = {
            /**
             * Show a notification within a component
             * 
             * @param {Object} component - The component context
             * @param {string} title - Notification title
             * @param {string} message - Notification message
             * @param {string} type - Notification type (success, error, warning, info)
             * @param {number} duration - Auto-hide duration in ms (0 to disable)
             * @returns {HTMLElement} - The created notification element
             */
            show: function(component, title, message, type = 'info', duration = 3000) {
                // Remove existing notifications of the same type
                const existingNotifications = component.root.querySelectorAll(`.component-notification--${type}`);
                existingNotifications.forEach(notification => {
                    notification.remove();
                });
                
                // Create notification element
                const notification = document.createElement('div');
                notification.className = `component-notification component-notification--${type}`;
                notification.innerHTML = `
                    <button class="component-notification__close">&times;</button>
                    <h4 class="component-notification__title">${title}</h4>
                    <p class="component-notification__message">${message}</p>
                `;
                
                // Add notification styles if not already present
                if (!component.root.querySelector('#component-notification-styles')) {
                    const styleElement = document.createElement('style');
                    styleElement.id = 'component-notification-styles';
                    styleElement.textContent = `
                        .component-notification {
                            position: fixed;
                            bottom: 20px;
                            right: 20px;
                            padding: 15px 20px;
                            border-radius: var(--border-radius-md, 8px);
                            background-color: var(--bg-card, #2d2d2d);
                            color: var(--text-primary, #f0f0f0);
                            box-shadow: var(--box-shadow-md, 0 4px 8px rgba(0, 0, 0, 0.1));
                            z-index: 1000;
                            max-width: 360px;
                            opacity: 0;
                            transform: translateY(20px);
                            transition: opacity 0.3s ease, transform 0.3s ease;
                        }
                        
                        .component-notification--visible {
                            opacity: 1;
                            transform: translateY(0);
                        }
                        
                        .component-notification__title {
                            margin: 0 0 8px 0;
                            font-size: var(--font-size-md, 1rem);
                            font-weight: 600;
                        }
                        
                        .component-notification__message {
                            margin: 0;
                            font-size: var(--font-size-sm, 0.875rem);
                            line-height: 1.4;
                        }
                        
                        .component-notification__close {
                            position: absolute;
                            top: 10px;
                            right: 10px;
                            background: none;
                            border: none;
                            font-size: 1.2rem;
                            color: var(--text-secondary, #aaa);
                            cursor: pointer;
                            padding: 0;
                            line-height: 1;
                        }
                        
                        .component-notification--success {
                            border-left: 4px solid var(--color-success, #28a745);
                        }
                        
                        .component-notification--error {
                            border-left: 4px solid var(--color-danger, #dc3545);
                        }
                        
                        .component-notification--warning {
                            border-left: 4px solid var(--color-warning, #ffc107);
                        }
                        
                        .component-notification--info {
                            border-left: 4px solid var(--color-info, #17a2b8);
                        }
                        
                        .component-notification--success .component-notification__title {
                            color: var(--color-success, #28a745);
                        }
                        
                        .component-notification--error .component-notification__title {
                            color: var(--color-danger, #dc3545);
                        }
                        
                        .component-notification--warning .component-notification__title {
                            color: var(--color-warning, #ffc107);
                        }
                        
                        .component-notification--info .component-notification__title {
                            color: var(--color-info, #17a2b8);
                        }
                    `;
                    component.root.appendChild(styleElement);
                }
                
                // Append notification to component root
                component.root.appendChild(notification);
                
                // Show notification with a small delay for animation
                setTimeout(() => {
                    notification.classList.add('component-notification--visible');
                }, 10);
                
                // Add close button functionality
                const closeButton = notification.querySelector('.component-notification__close');
                if (closeButton) {
                    closeButton.addEventListener('click', () => {
                        this.hide(notification);
                    });
                }
                
                // Auto-hide after duration (if specified)
                if (duration > 0) {
                    setTimeout(() => {
                        this.hide(notification);
                    }, duration);
                }
                
                return notification;
            },
            
            /**
             * Hide a notification
             * 
             * @param {HTMLElement} notification - The notification element to hide
             */
            hide: function(notification) {
                if (!notification) return;
                
                notification.classList.remove('component-notification--visible');
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.remove();
                    }
                }, 300);
            }
        };
    }
    
    /**
     * Initialize the loading indicator
     */
    _initLoadingIndicator() {
        // Loading Indicator
        window.tektonUI.componentUtils.loading = {
            /**
             * Show a loading indicator within a component
             * 
             * @param {Object} component - The component context
             * @param {string} message - Loading message (optional)
             * @returns {HTMLElement} - The created loading element
             */
            show: function(component, message = 'Loading...') {
                // Remove existing loading indicators
                this.hide(component);
                
                // Create loading element
                const loadingElement = document.createElement('div');
                loadingElement.className = 'component-loading';
                loadingElement.innerHTML = `
                    <div class="component-loading__spinner"></div>
                    <div class="component-loading__message">${message}</div>
                `;
                
                // Add loading styles if not already present
                if (!component.root.querySelector('#component-loading-styles')) {
                    const styleElement = document.createElement('style');
                    styleElement.id = 'component-loading-styles';
                    styleElement.textContent = `
                        .component-loading {
                            position: fixed;
                            top: 0;
                            left: 0;
                            right: 0;
                            bottom: 0;
                            display: flex;
                            flex-direction: column;
                            align-items: center;
                            justify-content: center;
                            background-color: rgba(0, 0, 0, 0.5);
                            z-index: 1000;
                        }
                        
                        .component-loading__spinner {
                            width: 40px;
                            height: 40px;
                            border: 4px solid rgba(255, 255, 255, 0.3);
                            border-radius: 50%;
                            border-top-color: var(--color-primary, #007bff);
                            animation: component-loading-spin 1s linear infinite;
                        }
                        
                        .component-loading__message {
                            margin-top: 16px;
                            color: var(--text-primary, #f0f0f0);
                            font-size: var(--font-size-md, 1rem);
                        }
                        
                        @keyframes component-loading-spin {
                            to { transform: rotate(360deg); }
                        }
                    `;
                    component.root.appendChild(styleElement);
                }
                
                // Append loading element to component root
                component.root.appendChild(loadingElement);
                
                return loadingElement;
            },
            
            /**
             * Hide the loading indicator
             * 
             * @param {Object} component - The component context
             */
            hide: function(component) {
                const loadingElement = component.root.querySelector('.component-loading');
                if (loadingElement) {
                    loadingElement.remove();
                }
            }
        };
    }
    
    /**
     * Initialize the component lifecycle management helpers
     */
    _initLifecycleManagement() {
        // Component Lifecycle Management
        window.tektonUI.componentUtils.lifecycle = {
            /**
             * Register a cleanup function for when component is unmounted
             * Wraps component's built-in registerCleanup for consistency
             * 
             * @param {Object} component - The component context
             * @param {Function} cleanupFn - The cleanup function
             */
            registerCleanup: function(component, cleanupFn) {
                component.registerCleanup(cleanupFn);
            },
            
            /**
             * Register an event handler with automatic cleanup
             * 
             * @param {Object} component - The component context
             * @param {HTMLElement} element - The element to add the listener to
             * @param {string} eventType - The event type (e.g., 'click')
             * @param {Function} handler - The event handler function
             */
            registerEventHandler: function(component, element, eventType, handler) {
                // Add the event listener
                element.addEventListener(eventType, handler);
                
                // Register cleanup to remove it when component unmounts
                this.registerCleanupTask(component, () => {
                    element.removeEventListener(eventType, handler);
                });
            },
            
            /**
             * Register multiple cleanup tasks at once
             * 
             * @param {Object} component - The component context
             * @param {Function[]} tasks - Array of cleanup functions
             */
            registerCleanupTasks: function(component, tasks) {
                // Create a single cleanup function that calls all tasks
                component.registerCleanup(() => {
                    tasks.forEach(task => {
                        if (typeof task === 'function') {
                            try {
                                task();
                            } catch (error) {
                                console.error('Error in cleanup task:', error);
                            }
                        }
                    });
                });
            },
            
            /**
             * Register a single cleanup task
             * 
             * @param {Object} component - The component context
             * @param {Function} task - Cleanup function
             */
            registerCleanupTask: function(component, task) {
                // Get any existing cleanup handler
                const existingHandler = window.__componentCleanupHandlers && 
                    window.__componentCleanupHandlers[component.id];
                
                if (existingHandler) {
                    // If there's already a handler, wrap it with the new task
                    component.registerCleanup(() => {
                        try {
                            task();
                        } catch (error) {
                            console.error('Error in cleanup task:', error);
                        }
                        existingHandler();
                    });
                } else {
                    // Otherwise, register the new task directly
                    component.registerCleanup(task);
                }
            }
        };
    }
    
    /**
     * Initialize DOM helper utilities
     */
    _initDomHelpers() {
        // Element Creation Helper
        window.tektonUI.componentUtils.dom = {
            /**
             * Create an HTML element with attributes and content
             * 
             * @param {string} tagName - Element tag name
             * @param {Object} attributes - Element attributes
             * @param {string|HTMLElement|Array} content - Element content
             * @returns {HTMLElement} The created element
             */
            createElement: function(tagName, attributes = {}, content = null) {
                const element = document.createElement(tagName);
                
                // Add attributes
                Object.entries(attributes).forEach(([key, value]) => {
                    if (key === 'className') {
                        element.className = value;
                    } else if (key === 'style' && typeof value === 'object') {
                        Object.entries(value).forEach(([prop, val]) => {
                            element.style[prop] = val;
                        });
                    } else if (key.startsWith('on') && typeof value === 'function') {
                        element.addEventListener(key.substring(2).toLowerCase(), value);
                    } else {
                        element.setAttribute(key, value);
                    }
                });
                
                // Add content
                if (content !== null) {
                    if (typeof content === 'string') {
                        element.innerHTML = content;
                    } else if (content instanceof HTMLElement) {
                        element.appendChild(content);
                    } else if (Array.isArray(content)) {
                        content.forEach(item => {
                            if (typeof item === 'string') {
                                element.innerHTML += item;
                            } else if (item instanceof HTMLElement) {
                                element.appendChild(item);
                            }
                        });
                    }
                }
                
                return element;
            },
            
            /**
             * Create a form field with label and input
             * 
             * @param {Object} options - Field options
             * @returns {HTMLElement} The created form field
             */
            createFormField: function(options) {
                const field = document.createElement('div');
                field.className = options.fieldClass || 'component-field';
                
                // Create label if specified
                if (options.label) {
                    const label = document.createElement('div');
                    label.className = options.labelClass || 'component-field__label';
                    label.textContent = options.label;
                    if (options.id) {
                        label.setAttribute('for', options.id);
                    }
                    field.appendChild(label);
                }
                
                // Create description if specified
                if (options.description) {
                    const description = document.createElement('div');
                    description.className = options.descriptionClass || 'component-field__description';
                    description.textContent = options.description;
                    field.appendChild(description);
                }
                
                // Create control wrapper
                const control = document.createElement('div');
                control.className = options.controlClass || 'component-field__control';
                
                // Create input element
                const input = document.createElement(options.element || 'input');
                input.className = options.inputClass || 'component-input';
                
                // Add input attributes
                if (options.id) input.id = options.id;
                if (options.type) input.type = options.type;
                if (options.name) input.name = options.name;
                if (options.placeholder) input.placeholder = options.placeholder;
                if (options.value) input.value = options.value;
                if (options.required) input.required = options.required;
                if (options.disabled) input.disabled = options.disabled;
                if (options.readonly) input.readOnly = options.readonly;
                if (options.pattern) input.pattern = options.pattern;
                if (options.min) input.min = options.min;
                if (options.max) input.max = options.max;
                if (options.step) input.step = options.step;
                if (options.autocomplete) input.autocomplete = options.autocomplete;
                if (options.checked !== undefined) input.checked = options.checked;
                
                // Add event listeners
                if (options.onChange) {
                    input.addEventListener('change', options.onChange);
                }
                if (options.onInput) {
                    input.addEventListener('input', options.onInput);
                }
                if (options.onFocus) {
                    input.addEventListener('focus', options.onFocus);
                }
                if (options.onBlur) {
                    input.addEventListener('blur', options.onBlur);
                }
                
                // Special handling for select elements
                if (options.element === 'select' && options.options) {
                    options.options.forEach(optionData => {
                        const option = document.createElement('option');
                        option.value = optionData.value;
                        option.textContent = optionData.label;
                        if (optionData.selected) {
                            option.selected = true;
                        }
                        if (optionData.disabled) {
                            option.disabled = true;
                        }
                        input.appendChild(option);
                    });
                }
                
                // Special handling for textarea
                if (options.element === 'textarea' && options.rows) {
                    input.rows = options.rows;
                }
                
                // Add input to control wrapper
                control.appendChild(input);
                
                // Add any additional controls
                if (options.additionalControls) {
                    options.additionalControls.forEach(ctrl => {
                        control.appendChild(ctrl);
                    });
                }
                
                // Add control wrapper to field
                field.appendChild(control);
                
                // Add error message container if validation is needed
                if (options.validation) {
                    const errorContainer = document.createElement('div');
                    errorContainer.className = 'component-field__error';
                    errorContainer.style.display = 'none';
                    errorContainer.id = `${options.id}-error`;
                    field.appendChild(errorContainer);
                    
                    // Add validation logic
                    input.addEventListener('blur', () => {
                        const validationResult = options.validation(input.value);
                        if (!validationResult.valid) {
                            errorContainer.textContent = validationResult.message;
                            errorContainer.style.display = 'block';
                            input.classList.add('component-input--error');
                        } else {
                            errorContainer.style.display = 'none';
                            input.classList.remove('component-input--error');
                        }
                    });
                }
                
                return field;
            }
        };
        
        // Initialize the dialog system
        this._initDialogSystem();
        
        // Initialize the tabs system
        this._initTabsSystem();
        
        // Initialize the form validation utilities
        this._initFormValidation();
    }
    
    /**
     * Initialize the dialog system
     */
    _initDialogSystem() {
        window.tektonUI.componentUtils.dialogs = {
            /**
             * Show a dialog within a component
             * 
             * @param {Object} component - The component context
             * @param {Object} options - Dialog options
             * @returns {HTMLElement} The created dialog element
             */
            show: function(component, options) {
                // Remove any existing dialogs
                this.hideAll(component);
                
                // Create dialog styles if not already present
                if (!component.root.querySelector('#component-dialog-styles')) {
                    const styleElement = document.createElement('style');
                    styleElement.id = 'component-dialog-styles';
                    styleElement.textContent = `
                        .component-dialog {
                            position: fixed;
                            top: 0;
                            left: 0;
                            right: 0;
                            bottom: 0;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            background-color: rgba(0, 0, 0, 0.5);
                            z-index: 1000;
                            opacity: 0;
                            visibility: hidden;
                            transition: opacity 0.3s ease, visibility 0.3s ease;
                        }
                        
                        .component-dialog--visible {
                            opacity: 1;
                            visibility: visible;
                        }
                        
                        .component-dialog__content {
                            background-color: var(--bg-card, #2d2d2d);
                            border-radius: var(--border-radius-md, 8px);
                            width: 90%;
                            max-width: 500px;
                            max-height: 90vh;
                            overflow-y: auto;
                            box-shadow: var(--box-shadow-lg, 0 8px 16px rgba(0, 0, 0, 0.1));
                        }
                        
                        .component-dialog__header {
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            padding: var(--spacing-md, 16px);
                            border-bottom: 1px solid var(--border-color, #444444);
                        }
                        
                        .component-dialog__title {
                            margin: 0;
                            font-size: var(--font-size-lg, 1.25rem);
                            color: var(--text-primary, #f0f0f0);
                        }
                        
                        .component-dialog__close {
                            background: none;
                            border: none;
                            font-size: var(--font-size-xl, 1.5rem);
                            color: var(--text-secondary, #aaaaaa);
                            cursor: pointer;
                            padding: 0;
                            line-height: 1;
                        }
                        
                        .component-dialog__body {
                            padding: var(--spacing-md, 16px);
                            color: var(--text-primary, #f0f0f0);
                        }
                        
                        .component-dialog__footer {
                            display: flex;
                            justify-content: flex-end;
                            gap: var(--spacing-sm, 8px);
                            padding: var(--spacing-md, 16px);
                            border-top: 1px solid var(--border-color, #444444);
                        }
                        
                        .component-dialog__button {
                            padding: var(--spacing-sm, 8px) var(--spacing-md, 16px);
                            border-radius: var(--border-radius-sm, 4px);
                            font-size: var(--font-size-sm, 0.875rem);
                            cursor: pointer;
                            transition: all 0.2s ease;
                        }
                        
                        .component-dialog__button--primary {
                            background-color: var(--color-primary, #007bff);
                            color: white;
                            border: none;
                        }
                        
                        .component-dialog__button--primary:hover {
                            background-color: var(--color-primary-hover, #0056b3);
                        }
                        
                        .component-dialog__button--secondary {
                            background-color: var(--bg-tertiary, #333333);
                            color: var(--text-primary, #f0f0f0);
                            border: 1px solid var(--border-color, #444444);
                        }
                        
                        .component-dialog__button--secondary:hover {
                            background-color: var(--bg-hover, #3a3a3a);
                        }
                    `;
                    component.root.appendChild(styleElement);
                }
                
                // Create the dialog element
                const dialog = component.utils.dom.createElement('div', { 
                    className: 'component-dialog',
                    id: options.id || 'component-dialog'
                }, `
                    <div class="component-dialog__content">
                        <div class="component-dialog__header">
                            <h3 class="component-dialog__title">${options.title || 'Dialog'}</h3>
                            <button class="component-dialog__close" aria-label="Close">&times;</button>
                        </div>
                        <div class="component-dialog__body">
                            ${options.content || ''}
                        </div>
                        <div class="component-dialog__footer">
                            ${options.secondaryButton ? 
                                `<button class="component-dialog__button component-dialog__button--secondary" id="dialog-secondary">${options.secondaryButton}</button>` : ''}
                            <button class="component-dialog__button component-dialog__button--primary" id="dialog-primary">${options.primaryButton || 'OK'}</button>
                        </div>
                    </div>
                `);
                
                // Add dialog to component root
                component.root.appendChild(dialog);
                
                // Set up event listeners
                const closeButton = dialog.querySelector('.component-dialog__close');
                if (closeButton) {
                    closeButton.addEventListener('click', () => {
                        this.hide(component, dialog);
                        if (options.onClose) {
                            options.onClose();
                        }
                    });
                }
                
                const primaryButton = dialog.querySelector('#dialog-primary');
                if (primaryButton) {
                    primaryButton.addEventListener('click', () => {
                        if (options.onPrimary) {
                            options.onPrimary();
                        }
                        this.hide(component, dialog);
                    });
                }
                
                const secondaryButton = dialog.querySelector('#dialog-secondary');
                if (secondaryButton) {
                    secondaryButton.addEventListener('click', () => {
                        if (options.onSecondary) {
                            options.onSecondary();
                        }
                        this.hide(component, dialog);
                    });
                }
                
                // Register dialog for cleanup
                component.utils.lifecycle.registerCleanupTask(component, () => {
                    if (dialog.parentNode) {
                        dialog.remove();
                    }
                });
                
                // Show the dialog after a small delay for animation
                setTimeout(() => {
                    dialog.classList.add('component-dialog--visible');
                }, 10);
                
                return dialog;
            },
            
            /**
             * Hide a dialog
             * 
             * @param {Object} component - The component context
             * @param {HTMLElement} dialog - The dialog element to hide
             */
            hide: function(component, dialog) {
                if (!dialog) {
                    dialog = component.root.querySelector('.component-dialog');
                }
                
                if (dialog) {
                    dialog.classList.remove('component-dialog--visible');
                    
                    // Remove dialog after transition
                    setTimeout(() => {
                        if (dialog.parentNode) {
                            dialog.remove();
                        }
                    }, 300);
                }
            },
            
            /**
             * Hide all dialogs in the component
             * 
             * @param {Object} component - The component context
             */
            hideAll: function(component) {
                const dialogs = component.root.querySelectorAll('.component-dialog');
                dialogs.forEach(dialog => {
                    this.hide(component, dialog);
                });
            },
            
            /**
             * Show a confirmation dialog
             * 
             * @param {Object} component - The component context
             * @param {string} message - The confirmation message
             * @param {Function} onConfirm - Function to call when confirmed
             * @param {Function} onCancel - Function to call when cancelled
             * @returns {HTMLElement} The created dialog element
             */
            confirm: function(component, message, onConfirm, onCancel) {
                return this.show(component, {
                    title: 'Confirm',
                    content: `<p>${message}</p>`,
                    primaryButton: 'Confirm',
                    secondaryButton: 'Cancel',
                    onPrimary: onConfirm,
                    onSecondary: onCancel
                });
            },
            
            /**
             * Show an alert dialog
             * 
             * @param {Object} component - The component context
             * @param {string} message - The alert message
             * @param {Function} onClose - Function to call when closed
             * @returns {HTMLElement} The created dialog element
             */
            alert: function(component, message, onClose) {
                return this.show(component, {
                    title: 'Alert',
                    content: `<p>${message}</p>`,
                    primaryButton: 'OK',
                    onPrimary: onClose
                });
            }
        };
    }
    
    /**
     * Initialize the tabs system
     */
    _initTabsSystem() {
        window.tektonUI.componentUtils.tabs = {
            /**
             * Initialize tabs within a component
             * 
             * @param {Object} component - The component context
             * @param {Object} options - Tabs options
             * @returns {Object} Tabs API
             */
            init: function(component, options = {}) {
                const containerId = options.containerId || 'tabs-container';
                const containerClass = options.containerClass || 'component-tabs';
                const activeClass = options.activeClass || 'component-tabs__tab--active';
                const tabClass = options.tabClass || 'component-tabs__tab';
                const contentClass = options.contentClass || 'component-tabs__content';
                const panelClass = options.panelClass || 'component-tabs__panel';
                const activePanelClass = options.activePanelClass || 'component-tabs__panel--active';
                
                // Create tabs styles if not already present
                if (!component.root.querySelector('#component-tabs-styles')) {
                    const styleElement = document.createElement('style');
                    styleElement.id = 'component-tabs-styles';
                    styleElement.textContent = `
                        .component-tabs {
                            display: flex;
                            flex-direction: column;
                        }
                        
                        .component-tabs__list {
                            display: flex;
                            border-bottom: 1px solid var(--border-color, #444444);
                            margin-bottom: var(--spacing-md, 16px);
                        }
                        
                        .component-tabs__tab {
                            padding: var(--spacing-sm, 8px) var(--spacing-md, 16px);
                            color: var(--text-secondary, #aaaaaa);
                            cursor: pointer;
                            transition: all 0.2s ease;
                            border-bottom: 2px solid transparent;
                            margin-bottom: -1px;
                        }
                        
                        .component-tabs__tab:hover {
                            color: var(--text-primary, #f0f0f0);
                        }
                        
                        .component-tabs__tab--active {
                            color: var(--color-primary, #007bff);
                            border-bottom-color: var(--color-primary, #007bff);
                            font-weight: 500;
                        }
                        
                        .component-tabs__panel {
                            display: none;
                        }
                        
                        .component-tabs__panel--active {
                            display: block;
                        }
                    `;
                    component.root.appendChild(styleElement);
                }
                
                const initialize = () => {
                    const container = component.$(`#${containerId}`);
                    if (!container) {
                        console.error(`Tabs container #${containerId} not found`);
                        return null;
                    }
                    
                    // Get tabs and panels elements
                    const tabsElement = container.querySelector(`.${containerClass}__list`);
                    const tabs = Array.from(tabsElement.querySelectorAll(`.${tabClass}`));
                    const panels = Array.from(container.querySelectorAll(`.${panelClass}`));
                    
                    // Set up click handlers for tabs
                    tabs.forEach((tab, index) => {
                        tab.addEventListener('click', () => {
                            // Deactivate all tabs
                            tabs.forEach(t => t.classList.remove(activeClass));
                            
                            // Deactivate all panels
                            panels.forEach(p => p.classList.remove(activePanelClass));
                            
                            // Activate clicked tab
                            tab.classList.add(activeClass);
                            
                            // Activate corresponding panel
                            if (panels[index]) {
                                panels[index].classList.add(activePanelClass);
                            }
                            
                            // Call onChange callback if provided
                            if (options.onChange) {
                                options.onChange(index, tab.getAttribute('data-tab-id'));
                            }
                        });
                    });
                    
                    // Initialize with first tab active unless otherwise specified
                    const defaultTabIndex = options.defaultTabIndex || 0;
                    if (tabs[defaultTabIndex]) {
                        tabs[defaultTabIndex].click();
                    }
                    
                    // Return API for tabs
                    return {
                        /**
                         * Activate a tab by index
                         * @param {number} index - Tab index
                         */
                        activateTab: function(index) {
                            if (tabs[index]) {
                                tabs[index].click();
                            }
                        },
                        
                        /**
                         * Activate a tab by ID
                         * @param {string} tabId - Tab ID
                         */
                        activateTabById: function(tabId) {
                            const tab = tabs.find(t => t.getAttribute('data-tab-id') === tabId);
                            if (tab) {
                                tab.click();
                            }
                        },
                        
                        /**
                         * Get the active tab index
                         * @returns {number} Active tab index
                         */
                        getActiveTabIndex: function() {
                            return tabs.findIndex(t => t.classList.contains(activeClass));
                        },
                        
                        /**
                         * Get the active tab ID
                         * @returns {string} Active tab ID
                         */
                        getActiveTabId: function() {
                            const activeTab = tabs.find(t => t.classList.contains(activeClass));
                            return activeTab ? activeTab.getAttribute('data-tab-id') : null;
                        }
                    };
                };
                
                // Initialize immediately if container exists, or wait for it
                const tabsContainer = component.$(`#${containerId}`);
                if (tabsContainer) {
                    return initialize();
                } else {
                    console.warn(`Tabs container #${containerId} not found, will initialize when available`);
                    
                    // Return a promise-like API that will initialize when container is available
                    return {
                        _initialized: false,
                        _api: null,
                        _initCheck: null,
                        
                        _checkForContainer: function() {
                            const container = component.$(`#${containerId}`);
                            if (container) {
                                this._api = initialize();
                                this._initialized = true;
                                clearInterval(this._initCheck);
                            }
                        },
                        
                        activateTab: function(index) {
                            if (this._initialized && this._api) {
                                this._api.activateTab(index);
                            } else if (!this._initCheck) {
                                this._initCheck = setInterval(() => this._checkForContainer(), 100);
                            }
                        },
                        
                        activateTabById: function(tabId) {
                            if (this._initialized && this._api) {
                                this._api.activateTabById(tabId);
                            } else if (!this._initCheck) {
                                this._initCheck = setInterval(() => this._checkForContainer(), 100);
                            }
                        },
                        
                        getActiveTabIndex: function() {
                            return this._initialized && this._api ? this._api.getActiveTabIndex() : -1;
                        },
                        
                        getActiveTabId: function() {
                            return this._initialized && this._api ? this._api.getActiveTabId() : null;
                        }
                    };
                }
            }
        };
    }
    
    /**
     * Initialize form validation utilities
     */
    _initFormValidation() {
        window.tektonUI.componentUtils.validation = {
            /**
             * Create an email validator
             * @param {string} message - Error message
             * @returns {Function} Validator function
             */
            email: function(message = 'Please enter a valid email address') {
                return function(value) {
                    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                    return {
                        valid: emailRegex.test(value),
                        message: message
                    };
                };
            },
            
            /**
             * Create a required field validator
             * @param {string} message - Error message
             * @returns {Function} Validator function
             */
            required: function(message = 'This field is required') {
                return function(value) {
                    return {
                        valid: value && value.trim().length > 0,
                        message: message
                    };
                };
            },
            
            /**
             * Create a minimum length validator
             * @param {number} minLength - Minimum length
             * @param {string} message - Error message
             * @returns {Function} Validator function
             */
            minLength: function(minLength, message) {
                return function(value) {
                    return {
                        valid: value && value.length >= minLength,
                        message: message || `Must be at least ${minLength} characters`
                    };
                };
            },
            
            /**
             * Create a maximum length validator
             * @param {number} maxLength - Maximum length
             * @param {string} message - Error message
             * @returns {Function} Validator function
             */
            maxLength: function(maxLength, message) {
                return function(value) {
                    return {
                        valid: !value || value.length <= maxLength,
                        message: message || `Must be no more than ${maxLength} characters`
                    };
                };
            },
            
            /**
             * Create a pattern validator
             * @param {RegExp} regex - Regular expression
             * @param {string} message - Error message
             * @returns {Function} Validator function
             */
            pattern: function(regex, message = 'Invalid format') {
                return function(value) {
                    return {
                        valid: regex.test(value),
                        message: message
                    };
                };
            },
            
            /**
             * Create a custom validator
             * @param {Function} validateFn - Validation function
             * @param {string} message - Error message
             * @returns {Function} Validator function
             */
            custom: function(validateFn, message = 'Invalid value') {
                return function(value) {
                    return {
                        valid: validateFn(value),
                        message: message
                    };
                };
            },
            
            /**
             * Combine multiple validators
             * @param {...Function} validators - Validators to combine
             * @returns {Function} Combined validator function
             */
            combine: function(...validators) {
                return function(value) {
                    for (const validator of validators) {
                        const result = validator(value);
                        if (!result.valid) {
                            return result;
                        }
                    }
                    return { valid: true };
                };
            },
            
            /**
             * Validate a form
             * @param {Object} component - The component context
             * @param {string} formSelector - Selector for the form
             * @param {Object} validations - Field validations
             * @returns {boolean} True if valid
             */
            validateForm: function(component, formSelector, validations) {
                const form = component.$(formSelector);
                if (!form) {
                    console.error(`Form ${formSelector} not found`);
                    return false;
                }
                
                let isValid = true;
                
                // Clear previous validation messages
                const errorElements = form.querySelectorAll('.component-field__error');
                errorElements.forEach(el => {
                    el.style.display = 'none';
                    el.textContent = '';
                });
                
                const errorInputs = form.querySelectorAll('.component-input--error');
                errorInputs.forEach(input => {
                    input.classList.remove('component-input--error');
                });
                
                // Validate each field
                Object.entries(validations).forEach(([fieldName, validator]) => {
                    const field = form.querySelector(`[name="${fieldName}"]`);
                    if (field) {
                        const value = field.value;
                        const result = validator(value);
                        
                        if (!result.valid) {
                            isValid = false;
                            field.classList.add('component-input--error');
                            
                            // Show error message
                            const errorElement = component.$(`#${fieldName}-error`) || 
                                form.querySelector(`.component-field__error[data-for="${fieldName}"]`);
                            
                            if (errorElement) {
                                errorElement.textContent = result.message;
                                errorElement.style.display = 'block';
                            }
                        }
                    }
                });
                
                return isValid;
            }
        };
    }
    
    /**
     * Initialize the Base Service pattern
     */
    _initBaseService() {
        /**
         * Base Service Class
         * Template for creating component services
         */
        class BaseService {
            /**
             * Create a new service
             * 
             * @param {string} name - Service name (used for global registration)
             * @param {string} apiUrl - API endpoint URL
             */
            constructor(name, apiUrl) {
                this.name = name;
                this.apiUrl = apiUrl;
                this.connected = false;
                this.eventListeners = {};
                
                // Register service globally
                if (!window.tektonUI) {
                    window.tektonUI = {};
                }
                
                if (!window.tektonUI.services) {
                    window.tektonUI.services = {};
                }
                
                // Only register if not already registered
                if (!window.tektonUI.services[name]) {
                    window.tektonUI.services[name] = this;
                }
            }
            
            /**
             * Connect to the service
             * @returns {Promise<boolean>} - True if connection succeeded
             */
            async connect() {
                if (this.connected) return true;
                
                try {
                    // Test connection with a ping or similar endpoint
                    // Subclasses should implement specific connection logic
                    this.connected = true;
                    this.dispatchEvent('connected', {});
                    return true;
                } catch (error) {
                    console.error(`Failed to connect to ${this.name} service:`, error);
                    this.connected = false;
                    this.dispatchEvent('connectionFailed', { error });
                    throw error;
                }
            }
            
            /**
             * Disconnect from the service
             */
            disconnect() {
                if (!this.connected) return;
                
                // Subclasses should implement specific disconnection logic
                this.connected = false;
                this.dispatchEvent('disconnected', {});
            }
            
            /**
             * Register an event listener
             * @param {string} event - Event name
             * @param {Function} callback - Callback function
             */
            addEventListener(event, callback) {
                if (!this.eventListeners[event]) {
                    this.eventListeners[event] = [];
                }
                this.eventListeners[event].push(callback);
                return this;
            }
            
            /**
             * Remove an event listener
             * @param {string} event - Event name
             * @param {Function} callback - Callback function to remove
             */
            removeEventListener(event, callback) {
                if (this.eventListeners[event]) {
                    this.eventListeners[event] = this.eventListeners[event].filter(cb => cb !== callback);
                }
                return this;
            }
            
            /**
             * Dispatch an event to all listeners
             * @param {string} event - Event name
             * @param {*} data - Event data
             */
            dispatchEvent(event, data) {
                if (this.eventListeners[event]) {
                    this.eventListeners[event].forEach(callback => {
                        try {
                            callback(data);
                        } catch (e) {
                            console.error(`Error in ${event} event handler:`, e);
                        }
                    });
                }
                return this;
            }
            
            /**
             * Create a fallback object for when service is unavailable
             * @returns {Object} Fallback object
             */
            createFallback() {
                // Subclasses should implement specific fallback logic
                return {
                    connect: async () => Promise.resolve(true),
                    disconnect: () => {}
                };
            }
        }
        
        // Export BaseService as a shared utility
        window.tektonUI.componentUtils.BaseService = BaseService;
    }
}

// Initialize the component utilities on script load
document.addEventListener('DOMContentLoaded', () => {
    // Create and initialize the component utilities
    window.componentUtils = new ComponentUtils().init();
});