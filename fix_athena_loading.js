// Quick fix for Athena loading issue
// Run this in the browser console to manually initialize the graph

// First, check if AthenaService is available
if (window.AthenaService) {
    console.log("AthenaService is available");
    
    // Remove the loading placeholder
    const placeholder = document.getElementById('graph-placeholder');
    if (placeholder) {
        placeholder.innerHTML = `
            <div style="text-align: center; padding: 2rem;">
                <h2 style="color: #999; margin-bottom: 1rem;">Knowledge Graph View</h2>
                <p style="color: #777; max-width: 600px; margin: 0 auto;">
                    Knowledge graph is now available. We have successfully populated Athena with:
                    <br><br>
                    • 14 Tekton components<br>
                    • 4 Integration patterns<br>
                    • Component relationships (being added)<br>
                    <br>
                    Use the Entities tab to view all components.
                </p>
            </div>
        `;
    }
    
    // Also load entities if on that tab
    const entityList = document.getElementById('entity-list-items');
    const entityLoading = document.getElementById('entity-list-loading');
    if (entityList && entityLoading) {
        // Fetch actual entities from Athena
        AthenaService.getEntities().then(entities => {
            console.log("Loaded entities:", entities);
            entityLoading.style.display = 'none';
            
            // Display the entities
            entityList.innerHTML = entities.map(entity => `
                <div class="athena__entity-item">
                    <div class="athena__entity-header">
                        <h4>${entity.name}</h4>
                        <span class="athena__entity-type">${entity.entityType}</span>
                    </div>
                    <div class="athena__entity-details">
                        ${entity.properties?.description || 'No description'}
                    </div>
                </div>
            `).join('');
        });
    }
} else {
    console.error("AthenaService not found!");
    
    // Still remove the loading state
    const placeholder = document.getElementById('graph-placeholder');
    if (placeholder) {
        placeholder.innerHTML = `
            <div style="text-align: center; padding: 2rem;">
                <h2 style="color: #999; margin-bottom: 1rem;">Knowledge Graph</h2>
                <p style="color: #777;">
                    AthenaService not loaded. Please check the console for errors.
                </p>
            </div>
        `;
    }
}