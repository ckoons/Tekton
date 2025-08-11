/**
 * Test script for verifying WebSocket connections to backend services
 * Run this in the browser console to test connections
 */

function testBackendConnections() {
    console.log('[TEST] Starting backend connection tests...');
    console.log('[TEST] Using Tekton environment:', {
        ENGRAM_PORT: window.ENGRAM_PORT,
        RHETOR_PORT: window.RHETOR_PORT,
        APOLLO_PORT: window.APOLLO_PORT,
        TEKTON_HOST: window.TEKTON_HOST || 'localhost'
    });
    
    const services = {
        engram: { endpoint: '/ws/ui' },
        rhetor: { endpoint: '/ws/prompts' },
        apollo: { endpoint: '/ws/patterns' }
    };
    
    const results = {};
    
    Object.entries(services).forEach(([name, config]) => {
        // Use tektonUrl to build proper URLs
        const httpUrl = tektonUrl(name, config.endpoint);
        const wsUrl = httpUrl.replace(/^http/, 'ws');
        console.log(`[TEST] Testing ${name} at ${wsUrl}...`);
        
        try {
            const ws = new WebSocket(wsUrl);
            
            ws.onopen = () => {
                console.log(`✅ ${name}: Connected successfully`);
                results[name] = 'connected';
                
                // Send a test message
                ws.send(JSON.stringify({
                    action: 'ping',
                    timestamp: Date.now()
                }));
            };
            
            ws.onmessage = (event) => {
                console.log(`📥 ${name}: Received message:`, event.data);
            };
            
            ws.onerror = (error) => {
                console.error(`❌ ${name}: Connection error:`, error);
                results[name] = 'error';
            };
            
            ws.onclose = (event) => {
                console.log(`🔌 ${name}: Connection closed (code: ${event.code})`);
                if (!results[name]) {
                    results[name] = 'failed';
                }
            };
            
        } catch (error) {
            console.error(`❌ ${name}: Failed to create WebSocket:`, error);
            results[name] = 'failed';
        }
    });
    
    // Test REST API endpoints
    setTimeout(() => {
        console.log('\n[TEST] Testing REST API endpoints...\n');
        
        // Use tektonUrl for proper API URLs
        Promise.all([
            fetch(tektonUrl('engram', '/api/memories/recent?limit=1'))
                .then(r => ({ service: 'engram', status: r.status, ok: r.ok }))
                .catch(e => ({ service: 'engram', error: e.message })),
            
            fetch(tektonUrl('rhetor', '/api/prompts/templates'))
                .then(r => ({ service: 'rhetor', status: r.status, ok: r.ok }))
                .catch(e => ({ service: 'rhetor', error: e.message })),
            
            fetch(tektonUrl('apollo', '/api/patterns/active'))
                .then(r => ({ service: 'apollo', status: r.status, ok: r.ok }))
                .catch(e => ({ service: 'apollo', error: e.message }))
        ]).then(apiResults => {
            console.log('\n[TEST] API Test Results:');
            apiResults.forEach(result => {
                if (result.error) {
                    console.log(`❌ ${result.service} API: ${result.error}`);
                } else {
                    const icon = result.ok ? '✅' : '⚠️';
                    console.log(`${icon} ${result.service} API: Status ${result.status}`);
                }
            });
            
            console.log('\n[TEST] WebSocket Test Results:', results);
            console.log('\n[TEST] Connection tests complete!');
        });
    }, 2000);
}

// Auto-run if loaded directly
if (typeof window !== 'undefined') {
    window.testBackendConnections = testBackendConnections;
    console.log('[TEST] Backend connection tester loaded. Run testBackendConnections() to test.');
}