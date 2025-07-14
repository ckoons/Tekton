/**
 * API Client for Noesis Dashboard
 * Handles all communication with the Noesis backend API
 */

class APIClient extends EventTarget {
    constructor() {
        super();
        this.baseUrl = this.detectBaseUrl();
        this.connected = false;
        this.retryCount = 0;
        this.maxRetries = 3;
        this.retryDelay = 1000;
        
        console.log(`🌐 API Client initialized with base URL: ${this.baseUrl}`);
    }
    
    detectBaseUrl() {
        // Auto-detect the API base URL
        const { protocol, hostname, port } = window.location;
        
        // If we're on the default Noesis port (8005), use that
        if (port === '8005' || !port) {
            return `${protocol}//${hostname}:8005`;
        }
        
        // Otherwise assume we're on the same host/port
        return `${protocol}//${hostname}${port ? ':' + port : ''}`;
    }
    
    async init() {
        try {
            await this.checkConnection();
            this.connected = true;
            this.dispatchEvent(new CustomEvent('connectionChange', { 
                detail: { connected: true } 
            }));
            console.log('✅ API Client connected');
        } catch (error) {
            this.connected = false;
            this.dispatchEvent(new CustomEvent('connectionChange', { 
                detail: { connected: false } 
            }));
            console.error('❌ API Client connection failed:', error);
            throw error;
        }
    }
    
    async makeRequest(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            },
            ...options
        };
        
        let lastError;
        
        for (let attempt = 0; attempt <= this.maxRetries; attempt++) {
            try {
                const response = await fetch(url, defaultOptions);
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const data = await response.json();
                
                // Reset retry count on success
                this.retryCount = 0;
                
                // Update connection status if needed
                if (!this.connected) {
                    this.connected = true;
                    this.dispatchEvent(new CustomEvent('connectionChange', { 
                        detail: { connected: true } 
                    }));
                }
                
                return data;
                
            } catch (error) {
                lastError = error;
                console.warn(`API request failed (attempt ${attempt + 1}/${this.maxRetries + 1}):`, error);
                
                // Update connection status on error
                if (this.connected) {
                    this.connected = false;
                    this.dispatchEvent(new CustomEvent('connectionChange', { 
                        detail: { connected: false } 
                    }));
                }
                
                // Wait before retry (except on last attempt)
                if (attempt < this.maxRetries) {
                    await this.sleep(this.retryDelay * (attempt + 1));
                }
            }
        }
        
        throw lastError;
    }
    
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    // Health and Status APIs
    async checkConnection() {
        return await this.makeRequest('/health');
    }
    
    async getStatus() {
        return await this.makeRequest('/api/status');
    }
    
    async getStreamingHealth() {
        return await this.makeRequest('/streaming/health');
    }
    
    // Streaming Control APIs
    async getStreamingStatus() {
        return await this.makeRequest('/streaming/status');
    }
    
    async startStreaming() {
        const result = await this.makeRequest('/streaming/start', { method: 'POST' });
        return result.status === 'started';
    }
    
    async stopStreaming() {
        const result = await this.makeRequest('/streaming/stop', { method: 'POST' });
        return result.status === 'stopped';
    }
    
    async forcePoll() {
        return await this.makeRequest('/streaming/memory/force-poll', { method: 'POST' });
    }
    
    async forceAnalysisUpdate() {
        return await this.makeRequest('/streaming/analysis/update', { method: 'POST' });
    }
    
    // Data Retrieval APIs
    async getInsights() {
        return await this.makeRequest('/streaming/insights');
    }
    
    async getMemoryAnalysis() {
        return await this.makeRequest('/streaming/memory/analysis');
    }
    
    async getCurrentMemoryState() {
        return await this.makeRequest('/streaming/memory/current');
    }
    
    async getMemoryHistory(limit = 50) {
        return await this.makeRequest(`/streaming/memory/history?limit=${limit}`);
    }
    
    async getStreamingStatistics() {
        return await this.makeRequest('/streaming/statistics');
    }
    
    // Analysis APIs (from analysis endpoints)
    async performManifoldAnalysis(data) {
        return await this.makeRequest('/api/analysis/manifold', {
            method: 'POST',
            body: JSON.stringify({ data })
        });
    }
    
    async performDynamicsAnalysis(data) {
        return await this.makeRequest('/api/analysis/dynamics', {
            method: 'POST',
            body: JSON.stringify({ data })
        });
    }
    
    async performCatastropheAnalysis(data) {
        return await this.makeRequest('/api/analysis/catastrophe', {
            method: 'POST',
            body: JSON.stringify({ data })
        });
    }
    
    async performSynthesisAnalysis(data) {
        return await this.makeRequest('/api/analysis/synthesis', {
            method: 'POST',
            body: JSON.stringify({ data })
        });
    }
    
    // Utility methods for data formatting
    formatError(error) {
        if (error.message) {
            return error.message;
        }
        return String(error);
    }
    
    isConnected() {
        return this.connected;
    }
    
    getBaseUrl() {
        return this.baseUrl;
    }
    
    // Event-driven data fetching
    async subscribeToUpdates(callback, interval = 5000) {
        const updateLoop = async () => {
            try {
                const data = {
                    insights: await this.getInsights(),
                    memoryAnalysis: await this.getMemoryAnalysis().catch(() => null),
                    streamingStats: await this.getStreamingStatistics().catch(() => null),
                    currentState: await this.getCurrentMemoryState().catch(() => null)
                };
                
                callback(data);
            } catch (error) {
                console.error('Update subscription error:', error);
            }
        };
        
        // Initial update
        await updateLoop();
        
        // Schedule periodic updates
        const intervalId = setInterval(updateLoop, interval);
        
        // Return cleanup function
        return () => clearInterval(intervalId);
    }
    
    // Batch data fetching for efficiency
    async fetchDashboardData() {
        try {
            const [
                health,
                insights,
                streamingStatus,
                statistics
            ] = await Promise.allSettled([
                this.getStreamingHealth(),
                this.getInsights(),
                this.getStreamingStatus(),
                this.getStreamingStatistics()
            ]);
            
            const result = {
                health: health.status === 'fulfilled' ? health.value : null,
                insights: insights.status === 'fulfilled' ? insights.value : null,
                streamingStatus: streamingStatus.status === 'fulfilled' ? streamingStatus.value : null,
                statistics: statistics.status === 'fulfilled' ? statistics.value : null,
                errors: []
            };
            
            // Collect any errors
            [health, insights, streamingStatus, statistics].forEach((settled, index) => {
                if (settled.status === 'rejected') {
                    const names = ['health', 'insights', 'streamingStatus', 'statistics'];
                    result.errors.push({
                        endpoint: names[index],
                        error: settled.reason.message || String(settled.reason)
                    });
                }
            });
            
            return result;
            
        } catch (error) {
            console.error('Batch data fetch failed:', error);
            throw error;
        }
    }
    
    // Advanced data fetching with caching
    createCachedFetcher(fetchFunction, cacheTime = 5000) {
        let cache = null;
        let lastFetch = 0;
        
        return async (...args) => {
            const now = Date.now();
            
            if (cache && (now - lastFetch) < cacheTime) {
                return cache;
            }
            
            try {
                cache = await fetchFunction.apply(this, args);
                lastFetch = now;
                return cache;
            } catch (error) {
                // Return cached data if available, otherwise throw
                if (cache) {
                    console.warn('Using cached data due to fetch error:', error);
                    return cache;
                }
                throw error;
            }
        };
    }
    
    // Create cached versions of common endpoints
    getCachedInsights = this.createCachedFetcher(this.getInsights);
    getCachedMemoryAnalysis = this.createCachedFetcher(this.getMemoryAnalysis);
    getCachedStatistics = this.createCachedFetcher(this.getStreamingStatistics);
}

export { APIClient };