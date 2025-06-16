/**
 * Storage Manager
 * Handles localStorage operations for UI state persistence
 */

class StorageManager {
    constructor() {
        this.prefix = 'tekton_';
        this.initialized = this.checkStorage();
    }
    
    /**
     * Check if localStorage is available
     * @returns {boolean} Whether localStorage is available
     */
    checkStorage() {
        try {
            const test = 'test';
            localStorage.setItem(test, test);
            localStorage.removeItem(test);
            return true;
        } catch (e) {
            console.error('localStorage not available:', e);
            return false;
        }
    }
    
    /**
     * Get an item from localStorage
     * @param {string} key - Storage key
     * @returns {string|null} Stored value or null if not found
     */
    getItem(key) {
        if (!this.initialized) return null;
        return localStorage.getItem(this.prefix + key);
    }
    
    /**
     * Set an item in localStorage
     * @param {string} key - Storage key
     * @param {string} value - Value to store
     */
    setItem(key, value) {
        if (!this.initialized) return;
        try {
            localStorage.setItem(this.prefix + key, value);
        } catch (e) {
            console.error('Error storing data:', e);
            // Try to clear some space
            this.pruneOldItems();
        }
    }
    
    /**
     * Remove an item from localStorage
     * @param {string} key - Storage key to remove
     */
    removeItem(key) {
        if (!this.initialized) return;
        localStorage.removeItem(this.prefix + key);
    }
    
    /**
     * Get input context for a specific component
     * @param {string} componentId - Component ID
     * @returns {string} Saved input text or empty string
     */
    getInputContext(componentId) {
        return this.getItem('input_' + componentId) || '';
    }
    
    /**
     * Save input context for a specific component
     * @param {string} componentId - Component ID
     * @param {string} text - Input text to save
     */
    setInputContext(componentId, text) {
        this.setItem('input_' + componentId, text);
    }
    
    /**
     * Remove old or unused items to free up space
     */
    pruneOldItems() {
        if (!this.initialized) return;
        
        try {
            // Get all keys that start with our prefix
            const keys = [];
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                if (key.startsWith(this.prefix)) {
                    keys.push(key);
                }
            }
            
            // Sort by length (longer values first)
            keys.sort((a, b) => {
                const lenA = localStorage.getItem(a).length;
                const lenB = localStorage.getItem(b).length;
                return lenB - lenA;
            });
            
            // Remove the 10% largest items
            const toRemove = Math.max(1, Math.floor(keys.length * 0.1));
            for (let i = 0; i < toRemove; i++) {
                localStorage.removeItem(keys[i]);
            }
            
            console.log(`Pruned ${toRemove} items from localStorage to free space`);
        } catch (e) {
            console.error('Error pruning storage:', e);
        }
    }
    
    /**
     * Clear all Tekton-related items
     */
    clearAll() {
        if (!this.initialized) return;
        
        try {
            const keys = [];
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                if (key.startsWith(this.prefix)) {
                    keys.push(key);
                }
            }
            
            keys.forEach(key => {
                localStorage.removeItem(key);
            });
            
            console.log(`Cleared ${keys.length} items from localStorage`);
        } catch (e) {
            console.error('Error clearing storage:', e);
        }
    }
}