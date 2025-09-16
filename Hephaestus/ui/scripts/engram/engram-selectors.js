// Engram CI Registry Selector Population
console.log('[ENGRAM-SELECTORS] Script file loading...');
try {
    console.log('[ENGRAM-SELECTORS] Script loaded successfully');
} catch(e) {
    console.error('[ENGRAM-SELECTORS] Error:', e);
}

// Function to load CI Registry and populate dropdowns
async function loadEngramCIRegistry() {
    console.log('[ENGRAM-SELECTORS] Starting loadEngramCIRegistry function');
    
    // First check if selectors exist
    const memoriesSelect = document.getElementById('memories-ci-select');
    const cognitionSelect = document.getElementById('cognition-ci-select');
    
    console.log('[ENGRAM-SELECTORS] Memories selector found:', !!memoriesSelect);
    console.log('[ENGRAM-SELECTORS] Cognition selector found:', !!cognitionSelect);
    
    let ciList = [];
    
    try {
        // Fetch from Hephaestus server's CI registry endpoint
        const registryUrl = '/api/ci-registry';
            
        console.log('[ENGRAM-SELECTORS] Fetching CI registry from:', registryUrl);
        const response = await fetch(registryUrl);
        
        if (response.ok) {
            const data = await response.json();
            console.log('[ENGRAM-SELECTORS] Registry data received:', data);
            
            // Log the structure to understand what we're getting
            console.log('[ENGRAM-SELECTORS] Registry keys:', Object.keys(data));
            if (data.active_cis) {
                console.log('[ENGRAM-SELECTORS] active_cis:', Object.keys(data.active_cis));
            }
            if (data.specialists) {
                console.log('[ENGRAM-SELECTORS] specialists:', Object.keys(data.specialists));
            }
            if (data.ci_terminals) {
                console.log('[ENGRAM-SELECTORS] ci_terminals:', Object.keys(data.ci_terminals));
            }
            if (data.project_cis) {
                console.log('[ENGRAM-SELECTORS] project_cis:', Object.keys(data.project_cis));
            }
            
            // The new endpoint returns a flat object with all CIs
            // Process each CI directly
            console.log('[ENGRAM-SELECTORS] Processing registry data with', Object.keys(data).length, 'entries');
            
            Object.entries(data).forEach(([id, info]) => {
                // Clean up the ID (remove -ci suffix if present for CI terminals, but keep for display)
                const cleanId = id;  // Keep original ID to match what aish uses
                
                // Get display name
                const displayName = info.name || id.replace(/[-_]/g, ' ')
                    .split(' ')
                    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                    .join(' ');
                
                // Add to list
                ciList.push({
                    id: cleanId,
                    name: displayName,
                    type: info.type || 'unknown'
                });
                
                console.log(`[ENGRAM-SELECTORS] Added ${cleanId} (${displayName}) type: ${info.type}`);
            });
            
            console.log('[ENGRAM-SELECTORS] Found', ciList.length, 'CIs in registry');
        }
    } catch (error) {
        console.warn('[ENGRAM-SELECTORS] Failed to fetch CI registry:', error);
    }
    
    // If no CIs found or fetch failed, use comprehensive fallback list
    if (ciList.length === 0) {
        console.log('[ENGRAM-SELECTORS] Using fallback CI list');
        // Greek Chorus CIs (from your list)
        const greekChorus = [
            'apollo', 'athena', 'engram', 'ergon', 'harmonia', 
            'hermes', 'metis', 'noesis', 'numa', 'penia',
            'prometheus', 'rhetor', 'sophia', 'synthesis', 'telos',
            'tekton-core', 'terma', 'hephaestus'
        ];
        
        // Known CI Terminals
        const ciTerminals = [
            'Amy', 'Ani', 'Cali'
        ];
        
        // Known Project CIs
        const projectCIs = [
            'archon'
        ];
        
        // Add Greek Chorus
        greekChorus.forEach(id => {
            ciList.push({
                id: id,
                name: id.replace('-', ' ').split(' ')
                    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
                    .join(' '),
                type: 'greek'  // Use the actual type from registry
            });
        });
        
        // Add CI Terminals
        ciTerminals.forEach(id => {
            ciList.push({
                id: id + '-ci',  // Add -ci suffix to match registry format
                name: id,
                type: 'ci_terminal'  // Use the actual type from registry
            });
        });
        
        // Add Project CIs
        projectCIs.forEach(id => {
            ciList.push({
                id: id,
                name: id.charAt(0).toUpperCase() + id.slice(1),
                type: 'ai_specialist'  // Archon is actually an AI specialist
            });
        });
    }
    
    // Group CIs by type for better organization
    const groupedCIs = {
        'Greek Chorus': [],
        'CI Terminals': [],
        'Terminals': [],
        'AI Specialists': [],
        'Other': []
    };
    
    ciList.forEach(ci => {
        if (ci.type === 'ci_terminal') {
            groupedCIs['CI Terminals'].push(ci);
        } else if (ci.type === 'terminal') {
            groupedCIs['Terminals'].push(ci);
        } else if (ci.type === 'greek') {
            groupedCIs['Greek Chorus'].push(ci);
        } else if (ci.type === 'ai_specialist') {
            groupedCIs['AI Specialists'].push(ci);
        } else {
            groupedCIs['Other'].push(ci);
        }
    });
    
    // Sort within each group
    Object.values(groupedCIs).forEach(group => {
        group.sort((a, b) => a.name.localeCompare(b.name));
    });
    
    // Helper function to populate a selector
    function populateSelector(select) {
        // Clear and repopulate
        while (select.options.length > 1) {
            select.remove(1);
        }
        
        // Add CIs by group
        Object.entries(groupedCIs).forEach(([groupName, cis]) => {
            if (cis.length > 0) {
                // Add a separator/group label (disabled option)
                if (select.options.length > 1) {
                    const separator = document.createElement('option');
                    separator.disabled = true;
                    separator.textContent = '──────────';
                    select.appendChild(separator);
                }
                
                const groupLabel = document.createElement('option');
                groupLabel.disabled = true;
                groupLabel.textContent = `── ${groupName} ──`;
                groupLabel.style.fontWeight = 'bold';
                select.appendChild(groupLabel);
                
                // Add CIs in this group
                cis.forEach(ci => {
                    const option = document.createElement('option');
                    option.value = ci.id;
                    option.textContent = `  ${ci.name}`;  // Indent for clarity
                    if (ci.type) {
                        option.setAttribute('data-ci-type', ci.type);
                    }
                    select.appendChild(option);
                });
            }
        });
        
        return ciList.length;
    }
    
    // Populate Memories selector
    if (memoriesSelect) {
        const count = populateSelector(memoriesSelect);
        console.log('[ENGRAM-SELECTORS] Populated memories selector with', count, 'CIs');
    }
    
    // Populate Cognition selector
    if (cognitionSelect) {
        const count = populateSelector(cognitionSelect);
        console.log('[ENGRAM-SELECTORS] Populated cognition selector with', count, 'CIs');
        
        // Add event handler for CI selection
        cognitionSelect.addEventListener('change', (e) => {
            const selectedCI = e.target.value;
            console.log(`[ENGRAM-SELECTORS] CI selected: ${selectedCI}`);
            
            // Update brain visualization if it exists
            if (window.cognitionBrain3D && window.cognitionBrain3D.setActiveCI) {
                window.cognitionBrain3D.setActiveCI(selectedCI);
            }
        });
    }
}

// Try to load immediately
console.log('[ENGRAM-SELECTORS] Attempting immediate load');
loadEngramCIRegistry();

// Also try on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('[ENGRAM-SELECTORS] DOM loaded, loading CI registry');
        loadEngramCIRegistry();
    });
} else {
    // DOM already loaded
    setTimeout(() => {
        console.log('[ENGRAM-SELECTORS] DOM already loaded, loading CI registry with delay');
        loadEngramCIRegistry();
    }, 100);
}

// Export for global access
window.loadEngramCIRegistry = loadEngramCIRegistry;
console.log('[ENGRAM-SELECTORS] Script execution complete');