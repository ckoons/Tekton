/**
 * Profile UI Handler
 * Manages the profile UI and connects it to the Profile Manager
 */

class ProfileUI {
    constructor() {
        this.initialized = false;
        this.container = null;
        this.profileManager = window.profileManager;
    }
    
    /**
     * Initialize the profile UI
     */
    init() {
        console.log('Initializing Profile UI...');
        
        // Make sure profile manager exists
        if (!window.profileManager) {
            console.error('Profile Manager not found, creating a new one');
            window.profileManager = new ProfileManager().init();
            this.profileManager = window.profileManager;
        }
        
        // Find the HTML panel - the standard for Clean Slate architecture
        this.container = document.getElementById('html-panel');
        if (!this.container) {
            console.error('HTML panel not found for Profile UI');
            return;
        }
        
        // Set up event listeners for the profile manager
        this.profileManager.addEventListener('profileUpdated', () => {
            this.updateProfileUI();
        });
        
        // Load the profile component if not already loaded
        // this.loadProfileComponent();
        
        return this;
    }
    
    /**
     * Load the profile component HTML
     */
    loadProfileComponent() {
        console.log('Loading profile component...');
        
        // Use the standard Clean Slate approach to load component with absolute path
        fetch('/components/profile/profile-component.html')
            .then(response => response.text())
            .then(html => {
                this.container.innerHTML = html;
                console.log('Profile component loaded');
                
                // Now that the component is loaded, finish initialization
                this.setupEventListeners();
                this.updateProfileUI();
            })
            .catch(error => {
                console.error('Error loading profile component:', error);
                // Create an error message
                this.container.innerHTML = `
                    <div class="profile-container">
                        <div class="profile__header">
                            <h2 class="profile__title">User Profile</h2>
                        </div>
                        <div class="profile__section">
                            <div class="profile__error">
                                <div class="profile__error-message">Error loading profile component: ${error.message}</div>
                            </div>
                        </div>
                    </div>
                `;
            });
    }
    
    /**
     * Set up event listeners for profile controls
     */
    setupEventListeners() {
        // These event listeners are now handled through the profile_switchTab and profile_saveProfile functions
        // directly in the profile-component.html file, following the same pattern as Budget component
    }
    
    /**
     * Update the UI with profile data
     */
    updateProfileUI() {
        if (!this.initialized) return;
        
        // This functionality is now handled in the profile-component.js file
        // following the Clean Slate architecture pattern
    }
    
    /**
     * Show the profile panel using the standard panel activation
     */
    showProfile() {
        // Use the standard activateComponent method from UI Manager
        if (window.uiManager) {
            window.uiManager.activateComponent('profile');
        } else if (window.tektonUI) {
            window.tektonUI.activateComponent('profile');
        }
    }
}

// Initialize the profile UI when the page loads
document.addEventListener('DOMContentLoaded', () => {
    // Create global instance
    window.profileUI = new ProfileUI();
    
    // Initialize after UI elements are available
    setTimeout(() => {
        window.profileUI.init();
    }, 1000);
});