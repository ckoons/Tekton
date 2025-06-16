/**
 * Profile Service
 * Manages user profile data for Tekton using the BaseService pattern
 */

class ProfileService extends window.tektonUI.componentUtils.BaseService {
    constructor() {
        super('profileService', '/api/profile');
        
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
        
        this.initialized = false;
    }
    
    /**
     * Initialize the profile service
     * @returns {ProfileService} The service instance
     */
    init() {
        this.load();
        this.initialized = true;
        console.log('Profile service initialized');
        
        // Dispatch initialization event
        this.dispatchEvent('initialized', this.profile);
        
        return this;
    }
    
    /**
     * Connect to the service
     * @returns {Promise<boolean>} True if connection succeeded
     */
    async connect() {
        if (this.connected) return true;
        
        try {
            // In a future implementation, this would connect to an actual API
            // For now, we're just using local storage via storageManager
            this.connected = true;
            this.dispatchEvent('connected', {});
            return true;
        } catch (error) {
            console.error('Failed to connect to profile service:', error);
            this.connected = false;
            this.dispatchEvent('connectionFailed', { error });
            throw error;
        }
    }
    
    /**
     * Load profile from storage
     * @returns {Object} The loaded profile
     */
    load() {
        if (window.storageManager) {
            const savedProfile = window.storageManager.getItem('user_profile');
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
                    this.dispatchEvent('profileLoaded', this.profile);
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
     * @returns {ProfileService} The service instance
     */
    save() {
        if (window.storageManager) {
            window.storageManager.setItem('user_profile', JSON.stringify(this.profile));
            console.log('Profile saved to storage');
            
            // Dispatch event
            this.dispatchEvent('profileSaved', this.profile);
        }
        return this;
    }
    
    /**
     * Update the profile with new data
     * @param {Object} data - Profile data to update
     * @returns {ProfileService} The service instance
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
     * Create a new instance or return existing one
     * Singleton pattern to ensure only one profile service exists
     * @returns {ProfileService} The profile service instance
     */
    static getInstance() {
        if (window.tektonUI?.services?.profileService) {
            return window.tektonUI.services.profileService;
        }
        
        const service = new ProfileService();
        service.init();
        return service;
    }
}

// Create a global instance if it doesn't exist yet
if (!window.tektonUI?.services?.profileService) {
    window.tektonUI = window.tektonUI || {};
    window.tektonUI.services = window.tektonUI.services || {};
    window.tektonUI.services.profileService = new ProfileService();
    
    // Initialize after UI elements are available
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(() => {
            window.tektonUI.services.profileService.init();
        }, 500);
    });
}