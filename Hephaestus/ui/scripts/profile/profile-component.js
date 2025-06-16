/**
 * Profile Component
 * Shadow DOM compatible implementation of the Profile UI
 */

(function(component) {
    'use strict';
    
    // Component-specific utilities
    const dom = component.utils.dom;
    const notifications = component.utils.notifications;
    const loading = component.utils.loading;
    const lifecycle = component.utils.lifecycle;
    
    // Service and state references
    let profileService = null;
    
    /**
     * Initialize the component
     */
    function initComponent() {
        console.log('Initializing Profile component...');
        
        // Initialize or get required services
        initServices();
        
        // Set up event listeners
        setupEventListeners();
        
        // Load initial data
        updateProfileUI();
        
        // Register cleanup function
        component.registerCleanup(cleanupComponent);
        
        console.log('Profile component initialized');
    }
    
    /**
     * Initialize required services
     */
    function initServices() {
        // Get or create profile service
        if (window.tektonUI?.services?.profileService) {
            profileService = window.tektonUI.services.profileService;
        } else {
            // Create a new profile service
            profileService = new ProfileService();
            profileService.init();
        }
        
        // Connect to service
        profileService.connect().catch(error => {
            console.error('Failed to connect to profile service:', error);
        });
    }
    
    /**
     * Set up event listeners
     */
    function setupEventListeners() {
        // Save profile button
        component.on('click', '#save-profile', function() {
            saveProfile();
        });
        
        // Add email button
        component.on('click', '#add-email', function(event) {
            event.preventDefault();
            addEmailField();
        });
        
        // Remove email buttons
        component.on('click', '.profile-button--remove', function(event) {
            event.preventDefault();
            if (component.$$('.profile-input--email').length > 1) {
                this.closest('.profile-emails__item').remove();
            }
        });
    }
    
    /**
     * Update the UI with profile data
     */
    function updateProfileUI() {
        if (!profileService || !profileService.profile) return;
        
        const profile = profileService.profile;
        
        // Show loading indicator
        const loader = loading.show(component, 'Loading profile...');
        
        // Update text fields
        component.$('#given-name').value = profile.givenName || '';
        component.$('#family-name').value = profile.familyName || '';
        component.$('#phone-number').value = profile.phoneNumber || '';
        
        // Update social accounts
        component.$('#x-account').value = profile.socialAccounts.x || '';
        component.$('#bluesky-account').value = profile.socialAccounts.bluesky || '';
        component.$('#wechat-account').value = profile.socialAccounts.wechat || '';
        component.$('#whatsapp-account').value = profile.socialAccounts.whatsapp || '';
        component.$('#github-account').value = profile.socialAccounts.github || '';
        
        // Update email fields
        const emailFields = component.$('#email-fields');
        emailFields.innerHTML = '';
        
        // Create fields for each email
        profile.emails.forEach((email) => {
            const emailItem = dom.createElement('div', { className: 'profile-emails__item' }, `
                <input type="email" class="profile-input profile-input--email" placeholder="Email Address" value="${email || ''}">
                <button class="profile-button profile-button--remove">
                    <span class="profile-button__icon">-</span>
                </button>
            `);
            emailFields.appendChild(emailItem);
        });
        
        // If no emails were added, add an empty field
        if (profile.emails.length === 0) {
            addEmailField();
        }
        
        // Hide loading indicator after a short delay
        setTimeout(() => {
            loading.hide(component);
        }, 300);
    }
    
    /**
     * Add a new email input field
     */
    function addEmailField() {
        const emailFields = component.$('#email-fields');
        
        const emailItem = dom.createElement('div', { className: 'profile-emails__item' }, `
            <input type="email" class="profile-input profile-input--email" placeholder="Email Address">
            <button class="profile-button profile-button--remove">
                <span class="profile-button__icon">-</span>
            </button>
        `);
        emailFields.appendChild(emailItem);
        
        // Focus the new input
        emailItem.querySelector('input').focus();
    }
    
    /**
     * Save profile data from UI
     */
    function saveProfile() {
        // Show loading indicator
        const loader = loading.show(component, 'Saving profile...');
        
        const profile = {
            givenName: component.$('#given-name').value,
            familyName: component.$('#family-name').value,
            phoneNumber: component.$('#phone-number').value,
            emails: Array.from(component.$$('.profile-input--email'))
                .map(input => input.value)
                .filter(email => email.trim() !== ''),
            socialAccounts: {
                x: component.$('#x-account').value,
                bluesky: component.$('#bluesky-account').value,
                wechat: component.$('#wechat-account').value,
                whatsapp: component.$('#whatsapp-account').value,
                github: component.$('#github-account').value
            }
        };
        
        // Validate the form
        const validationResult = validateProfileForm(profile);
        if (!validationResult.valid) {
            loading.hide(component);
            showValidationErrors(validationResult.errors);
            return;
        }
        
        // Update profile in service
        profileService.updateProfile(profile);
        
        // Hide loading and show confirmation
        setTimeout(() => {
            loading.hide(component);
            notifications.show(
                component,
                'Success',
                'Profile saved successfully',
                'success',
                3000
            );
        }, 500);
    }
    
    /**
     * Validate the profile form
     * @param {Object} profile - The profile data to validate
     * @returns {Object} Validation result with valid flag and errors array
     */
    function validateProfileForm(profile) {
        const errors = [];
        
        // Validate emails
        if (profile.emails.length > 0) {
            profile.emails.forEach((email, index) => {
                if (email && !isValidEmail(email)) {
                    errors.push(`Email address #${index + 1} is not valid`);
                }
            });
        } else {
            errors.push('At least one email address is required');
        }
        
        // Validate names
        if (!profile.givenName && !profile.familyName) {
            errors.push('At least one name field (Given Name or Family Name) is required');
        }
        
        return {
            valid: errors.length === 0,
            errors: errors
        };
    }
    
    /**
     * Check if an email is valid
     * @param {string} email - The email to validate
     * @returns {boolean} True if email is valid
     */
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    /**
     * Show validation errors in a dialog
     * @param {string[]} errors - Array of error messages
     */
    function showValidationErrors(errors) {
        showDialog({
            title: 'Validation Errors',
            content: `
                <div class="profile-dialog__validation">
                    <p>Please fix the following errors:</p>
                    <ul class="profile-dialog__errors">
                        ${errors.map(error => `<li>${error}</li>`).join('')}
                    </ul>
                </div>
            `,
            primaryButton: {
                text: 'OK',
                action: () => {}
            }
        });
    }
    
    /**
     * Show a dialog with custom content and buttons
     * @param {Object} options - Dialog options
     */
    function showDialog(options) {
        // Remove any existing dialogs
        const existingDialog = component.$('.profile-dialog');
        if (existingDialog) {
            existingDialog.remove();
        }
        
        // Create the dialog
        const dialog = dom.createElement('div', { className: 'profile-dialog' }, `
            <div class="profile-dialog__content">
                <div class="profile-dialog__header">
                    <h3 class="profile-dialog__title">${options.title || 'Dialog'}</h3>
                    <button class="profile-dialog__close">&times;</button>
                </div>
                <div class="profile-dialog__body">
                    ${options.content || ''}
                </div>
                <div class="profile-dialog__footer">
                    ${options.secondaryButton ? 
                        `<button class="profile-button profile-button--secondary" id="dialog-secondary">${options.secondaryButton.text}</button>` : ''}
                    <button class="profile-button profile-button--primary" id="dialog-primary">${options.primaryButton?.text || 'OK'}</button>
                </div>
            </div>
        `);
        
        // Add to component root
        component.root.appendChild(dialog);
        
        // Show dialog after a small delay
        setTimeout(() => {
            dialog.classList.add('profile-dialog--visible');
        }, 10);
        
        // Set up event listeners
        const closeBtn = dialog.querySelector('.profile-dialog__close');
        closeBtn.addEventListener('click', () => hideDialog(dialog));
        
        const primaryBtn = dialog.querySelector('#dialog-primary');
        primaryBtn.addEventListener('click', () => {
            if (options.primaryButton?.action) {
                options.primaryButton.action();
            }
            hideDialog(dialog);
        });
        
        const secondaryBtn = dialog.querySelector('#dialog-secondary');
        if (secondaryBtn && options.secondaryButton?.action) {
            secondaryBtn.addEventListener('click', () => {
                options.secondaryButton.action();
                hideDialog(dialog);
            });
        }
        
        // Register dialog for cleanup
        lifecycle.registerCleanupTask(component, () => {
            if (dialog.parentNode) {
                dialog.remove();
            }
        });
        
        return dialog;
    }
    
    /**
     * Hide a dialog
     * @param {HTMLElement} dialog - The dialog element to hide
     */
    function hideDialog(dialog) {
        dialog.classList.remove('profile-dialog--visible');
        setTimeout(() => {
            if (dialog.parentNode) {
                dialog.remove();
            }
        }, 300);
    }
    
    /**
     * Show a confirmation dialog
     * @param {string} message - The confirmation message
     * @param {Function} onConfirm - Function to call when confirmed
     * @param {Function} onCancel - Function to call when cancelled
     */
    function showConfirmationDialog(message, onConfirm, onCancel = () => {}) {
        return showDialog({
            title: 'Confirmation',
            content: `<p>${message}</p>`,
            primaryButton: {
                text: 'Confirm',
                action: onConfirm
            },
            secondaryButton: {
                text: 'Cancel',
                action: onCancel
            }
        });
    }
    
    /**
     * Clean up component resources
     */
    function cleanupComponent() {
        console.log('Cleaning up Profile component');
        
        // Any specific cleanup needed can be added here
        
        // No need to manually remove listeners that were added with component.on()
        // as they are automatically cleaned up by the component loader
    }
    
    // Initialize the component
    initComponent();
    
})(component);