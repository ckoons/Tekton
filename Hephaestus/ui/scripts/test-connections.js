/**
 * Test script for verifying WebSocket connections to backend services
 * Run this in the browser console to test connections
 */

function testBackendConnections() {
    console.log('[TEST] Starting backend connection tests...');
    
    const services = {
        engram: { port: 8002, endpoint: '/ws/ui' },
        rhetor: { port: 8005, endpoint: '/ws/prompts' },
        apollo: { port: 8012, endpoint: '/ws/patterns' }
    };
    
    const results = {};
    
    Object.entries(services).forEach(([name, config]) => {
        const wsUrl = `ws://localhost:${config.port}${config.endpoint}`;
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
        
        Promise.all([
            fetch('http://localhost:8002/api/memories/recent?limit=1')
                .then(r => ({ service: 'engram', status: r.status, ok: r.ok }))
                .catch(e => ({ service: 'engram', error: e.message })),
            
            fetch('http://localhost:8005/api/prompts/templates')
                .then(r => ({ service: 'rhetor', status: r.status, ok: r.ok }))
                .catch(e => ({ service: 'rhetor', error: e.message })),
            
            fetch('http://localhost:8012/api/patterns/active')
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