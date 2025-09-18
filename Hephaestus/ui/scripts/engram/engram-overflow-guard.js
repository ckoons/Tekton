/**
 * Engram Overflow Guard
 *
 * CRITICAL: This prevents the memory overflow that crashes Greek Chorus CIs.
 * Intercepts and limits ALL Engram responses before they reach JSON.parse()
 */

(function() {
    'use strict';

    console.warn('[ENGRAM GUARD] Memory overflow protection active');

    // Maximum allowed response size (64KB)
    const MAX_RESPONSE_SIZE = 64 * 1024;

    // Store original fetch
    const originalFetch = window.fetch;

    // Override fetch to intercept Engram responses
    window.fetch = async function(...args) {
        const [url, options] = args;

        // Check if this is an Engram request
        const isEngramRequest =
            (typeof url === 'string' && url.includes('8901')) ||
            (typeof url === 'string' && url.includes('engram'));

        // Call original fetch
        const response = await originalFetch.apply(this, args);

        // If not Engram, return as-is
        if (!isEngramRequest) {
            return response;
        }

        // For Engram requests, wrap response to check size
        return new Proxy(response, {
            get(target, prop) {
                // Intercept json() method
                if (prop === 'json') {
                    return async function() {
                        // Get text first to check size
                        const clonedResponse = target.clone();
                        const text = await clonedResponse.text();

                        // Check size
                        if (text.length > MAX_RESPONSE_SIZE) {
                            console.error(`[ENGRAM GUARD] BLOCKED ${text.length} byte response!`);
                            console.error('[ENGRAM GUARD] This would have crashed the Greek Chorus');

                            // Return safe empty response
                            return {
                                items: [],
                                memories: [],
                                total: 0,
                                error: 'Response too large - blocked by overflow guard',
                                size: text.length,
                                limit: MAX_RESPONSE_SIZE
                            };
                        }

                        // Safe to parse
                        try {
                            return JSON.parse(text);
                        } catch (e) {
                            console.error('[ENGRAM GUARD] JSON parse error:', e);
                            return {
                                items: [],
                                memories: [],
                                error: 'JSON parse failed'
                            };
                        }
                    };
                }

                // Intercept text() method
                if (prop === 'text') {
                    return async function() {
                        const text = await target.text();

                        if (text.length > MAX_RESPONSE_SIZE) {
                            console.warn(`[ENGRAM GUARD] Text response ${text.length} bytes`);
                            // Still return it for text, but warn
                        }

                        return text;
                    };
                }

                // Pass through other properties/methods
                return target[prop];
            }
        });
    };

    // Also override JSON.parse to catch any direct parsing
    const originalJSONParse = JSON.parse;
    JSON.parse = function(text, reviver) {
        // Check if this looks like Engram data (has memories or items)
        if (typeof text === 'string' && text.length > MAX_RESPONSE_SIZE) {
            if (text.includes('"memories"') || text.includes('"items"') || text.includes('"landmarks"')) {
                console.error(`[ENGRAM GUARD] BLOCKED direct JSON.parse of ${text.length} bytes!`);
                console.error('[ENGRAM GUARD] Engram data too large, returning empty');

                return {
                    items: [],
                    memories: [],
                    total: 0,
                    error: 'Data too large - blocked by JSON.parse guard'
                };
            }
        }

        // Call original JSON.parse
        return originalJSONParse.call(this, text, reviver);
    };

    console.log('[ENGRAM GUARD] Protection installed:');
    console.log('  - fetch() wrapped to check response size');
    console.log('  - JSON.parse() protected against large Engram data');
    console.log(`  - Maximum size: ${MAX_RESPONSE_SIZE} bytes (64KB)`);

})();