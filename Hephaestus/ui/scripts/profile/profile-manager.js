/**
 * DEPRECATED: This file will be removed after CSS-first migration is verified
 * Profile Manager
 * Manages user profile data for Tekton
 */

console.log('[FILE_TRACE] Loading: profile-manager.js');
class ProfileManager {
    constructor() {
        this.profile = {
            givenName: '',
            familyName: '',
            emails: [''],
            phoneNumber: '',
            socialAccounts: {
                x: '',
                bluesky: '',
                wechat: '',
                whatsapp: '',
                github: ''
            }
        };
        this.eventListeners = {};
        this.initialized = false;
    }
    
    /**
     * Initialize the profile manager
     */
    init() {
        this.load();
        this.initialized = true;
        console.log('Profile manager initialized');
        
        // Dispatch an initialization event
        this.dispatchEvent('initialized', this.profile);
        
        return this;
    }
    
    /**
     * Load profile from storage
     */
    load() {
        if (window.storageManager) {
            const savedProfile = storageManager.getItem('user_profile');
            if (savedProfile) {
                try {
                    const parsed = JSON.parse(savedProfile);
                    // Update profile, preserving defaults for any missing values
                    this.profile = {
                        ...this.profile,
                        ...parsed
                    };
                    
                    // Ensure emails is always an array
                    if (!Array.isArray(this.profile.emails)) {
                        this.profile.emails = this.profile.emails ? [this.profile.emails] : [''];
                    }
                    
                    // Ensure socialAccounts exists
                    if (!this.profile.socialAccounts) {
                        this.profile.socialAccounts = {
                            x: '',
                            bluesky: '',
                            wechat: '',
                            whatsapp: '',
                            github: ''
                        };
                    }
                    
                    console.log('Profile loaded from storage');
                } catch (e) {
                    console.error('Error parsing profile:', e);
                }
            } else {
                console.log('No saved profile found, using defaults');
            }
        }
        return this.profile;
    }
    
    /**
     * Save profile to storage
     */
    save() {
        if (window.storageManager) {
            storageManager.setItem('user_profile', JSON.stringify(this.profile));
            console.log('Profile saved to storage');
            
            // Dispatch event
            this.dispatchEvent('profileSaved', this.profile);
        }
        return this;
    }
    
    /**
     * Update the profile with new data
     * @param {Object} data - Profile data to update
     */
    updateProfile(data) {
        // Update profile with new data
        this.profile = {
            ...this.profile,
            ...data
        };
        
        // Save changes
        this.save();
        
        // Dispatch event
        this.dispatchEvent('profileUpdated', this.profile);
        
        return this;
    }
    
    /**
     * Get the formatted full name from the profile
     * @returns {string} Full name or empty string if no name set
     */
    getFullName() {
        const { givenName, familyName } = this.profile;
        
        if (givenName && familyName) {
            return `${givenName} ${familyName}`;
        } else if (givenName) {
            return givenName;
        } else if (familyName) {
            return familyName;
        } else {
            return '';
        }
    }
    
    /**
     * Get the primary email from the profile
     * @returns {string} Primary email or empty string if none set
     */
    getPrimaryEmail() {
        if (Array.isArray(this.profile.emails) && this.profile.emails.length > 0) {
            return this.profile.emails[0];
        }
        return '';
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
}

// Create and initialize the profile manager when the page loads
document.addEventListener('DOMContentLoaded', () => {
    // Create global instance
    window.profileManager = new ProfileManager();
    
    // Initialize after UI elements are available
    setTimeout(() => {
        window.profileManager.init();
    }, 500);
});