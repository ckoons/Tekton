/**
 * Profile Service
 * Manages user profile data for Tekton using the BaseService pattern
 */

console.log('[FILE_TRACE] Loading: profile-service.js');
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
    async init() {
        await this.load();
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
     * Load profile from backend
     * @returns {Object} The loaded profile
     */
    async load() {
        try {
            // Fetch profile from backend
            const response = await fetch('/api/profile', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Cache-Control': 'no-cache'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.profile = data;
                
                // Ensure emails is always an array
                if (!Array.isArray(this.profile.emails)) {
                    this.profile.emails = this.profile.emails ? [this.profile.emails] : [''];
                }
                
                // Also save to localStorage for caching
                if (window.storageManager) {
                    window.storageManager.setItem('user_profile', JSON.stringify(this.profile));
                }
                
                console.log('Profile loaded from backend');
                this.dispatchEvent('profileLoaded', this.profile);
            } else {
                console.error('Failed to load profile from backend:', response.status);
                // Fall back to localStorage if available
                this.loadFromLocalStorage();
            }
        } catch (error) {
            console.error('Error loading profile from backend:', error);
            // Fall back to localStorage if available
            this.loadFromLocalStorage();
        }
        return this.profile;
    }
    
    /**
     * Load profile from localStorage (fallback)
     */
    loadFromLocalStorage() {
        if (window.storageManager) {
            const savedProfile = window.storageManager.getItem('user_profile');
            if (savedProfile) {
                try {
                    const parsed = JSON.parse(savedProfile);
                    this.profile = {
                        ...this.profile,
                        ...parsed
                    };
                    console.log('Profile loaded from localStorage (fallback)');
                } catch (e) {
                    console.error('Error parsing profile from localStorage:', e);
                }
            }
        }
    }
    
    /**
     * Save profile to backend
     * @returns {ProfileService} The service instance
     */
    async save() {
        try {
            // Save to backend
            const response = await fetch('/api/profile', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.profile)
            });
            
            if (response.ok) {
                console.log('Profile saved to backend');
                
                // Also update localStorage cache
                if (window.storageManager) {
                    window.storageManager.setItem('user_profile', JSON.stringify(this.profile));
                }
                
                // Dispatch event
                this.dispatchEvent('profileSaved', this.profile);
            } else {
                console.error('Failed to save profile to backend:', response.status);
                throw new Error(`Failed to save profile: ${response.status}`);
            }
        } catch (error) {
            console.error('Error saving profile:', error);
            throw error;
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