/**
 * Engram Component - Minimal JavaScript for CSS-first UI
 * 
 * Provides simple API integration for the Engram memory system.
 * No DOM manipulation - uses CSS for all UI state management.
 */

console.log('[FILE_TRACE] Loading: engram-component.js');

// Simple namespace for Engram functions
window.engram = window.engram || {};
console.log('[ENGRAM] Script loaded, window.engram initialized');

/**
 * Switch between Memory panel modes (Browse, Create, Search, Timeline)
 */
window.engram.switchMemoryMode = function(mode) {
    // Update tab states
    const tabs = document.querySelectorAll('.memories__mode-tab');
    tabs.forEach(tab => {
        if (tab.getAttribute('data-mode') === mode) {
            tab.classList.add('active');
        } else {
            tab.classList.remove('active');
        }
    });
    
    // Update content visibility
    const contents = document.querySelectorAll('.memories__mode-content');
    contents.forEach(content => {
        if (content.getAttribute('data-mode-content') === mode) {
            content.classList.add('active');
            content.style.display = 'block';
        } else {
            content.classList.remove('active');
            content.style.display = 'none';
        }
    });
    
    console.log(`[ENGRAM] Switched to ${mode} mode`);
};

// Initialize visualizations when tabs are clicked
document.addEventListener('change', (e) => {
    if (e.target.id === 'engram-tab-cognition' && e.target.checked) {
        console.log('[ENGRAM] Cognition tab selected, initializing 3D brain');
        setTimeout(() => {
            if (typeof initializeCognitionBrain3D === 'function') {
                initializeCognitionBrain3D();
            }
        }, 100);
    }
    if (e.target.id === 'engram-tab-patterns' && e.target.checked) {
        console.log('[ENGRAM] Patterns tab selected, initializing patterns');
        setTimeout(() => {
            if (typeof initializePatternsDiscovery === 'function') {
                initializePatternsDiscovery();
            }
        }, 100);
    }
});

/**
 * Load memories for browse tab
 */
window.engram.loadMemories = async function(type = 'all', sharing = 'all', page = 1) {
    const container = document.getElementById('memory-cards-container');
    const limit = 10; // Reduced from 20 to prevent memory issues
    const offset = (page - 1) * limit;
    
    try {
        // Show loading state
        container.innerHTML = '<div class="engram__loading">Loading memories...</div>';
        
        // Build query params
        const params = new URLSearchParams();
        if (type && type !== 'all') params.append('type', type);
        if (sharing && sharing !== 'all') params.append('sharing', sharing);
        params.append('limit', limit);
        params.append('offset', offset);
        
        // Fetch memories
        const response = await fetch(engramUrl(`/api/v1/memory/browse?${params}`));
        const data = await response.json();
        
        // Clear loading state
        container.innerHTML = '';
        
        // Render memory cards
        if (data.memories && data.memories.length > 0) {
            data.memories.forEach(memory => {
                const card = createMemoryCard(memory);
                container.insertAdjacentHTML('beforeend', card);
            });
        } else {
            container.innerHTML = '<div class="engram__empty-state">No memories found</div>';
        }
        
        // Update pagination
        updatePagination(page, Math.ceil(data.total / limit));
        
    } catch (error) {
        console.error('Error loading memories:', error);
        container.innerHTML = '<div class="engram__error">Error loading memories</div>';
    }
};

/**
 * Create HTML for a memory card
 */
function createMemoryCard(memory) {
    const tagsHtml = memory.tags ? memory.tags.map(tag => 
        `<span class="engram__card-tag">${tag}</span>`
    ).join('') : '';
    
    return `
        <div class="engram__card" data-memory-id="${memory.id}">
            <div class="engram__card-header">
                <h3 class="engram__card-title">${memory.title || 'Untitled'}</h3>
                <div class="engram__card-meta">
                    <span class="engram__card-type">${memory.type}</span>
                    <span class="engram__card-date">${memory.created_at}</span>
                </div>
            </div>
            <p class="engram__card-preview">${memory.preview || ''}</p>
            <div class="engram__card-footer">
                <div class="engram__card-tags">${tagsHtml}</div>
                <div class="engram__card-actions">
                    <button class="engram__card-action" onclick="engram.viewMemory('${memory.id}')">View</button>
                    <button class="engram__card-action" onclick="engram.editMemory('${memory.id}')">Edit</button>
                </div>
            </div>
        </div>
    `;
}

/**
 * Update pagination controls
 */
function updatePagination(currentPage, totalPages) {
    const pagination = document.getElementById('memory-pagination');
    if (!pagination) return;
    
    let html = '';
    
    // Previous button
    if (currentPage > 1) {
        html += `<button class="engram__page-btn" onclick="engram.loadMemories(null, null, ${currentPage - 1})">Previous</button>`;
    }
    
    // Page numbers
    for (let i = 1; i <= totalPages; i++) {
        if (i === currentPage) {
            html += `<span class="engram__page-current">${i}</span>`;
        } else {
            html += `<button class="engram__page-btn" onclick="engram.loadMemories(null, null, ${i})">${i}</button>`;
        }
    }
    
    // Next button
    if (currentPage < totalPages) {
        html += `<button class="engram__page-btn" onclick="engram.loadMemories(null, null, ${currentPage + 1})">Next</button>`;
    }
    
    pagination.innerHTML = html;
}

/**
 * Handle file upload in create tab
 */
window.engram.uploadMemory = async function(event) {
    event.preventDefault();
    
    const form = document.getElementById('create-memory-form');
    const formData = new FormData();
    
    // Get file
    const fileInput = document.getElementById('memory-file');
    if (!fileInput || !fileInput.files || !fileInput.files[0]) {
        alert('Please select a file');
        return;
    }
    
    formData.append('file', fileInput.files[0]);
    
    // Add metadata as JSON
    const metadata = {
        title: document.getElementById('memory-title').value,
        type: document.getElementById('memory-type').value,
        tags: document.getElementById('memory-tags').value.split(',').map(t => t.trim()).filter(t => t),
        description: document.getElementById('memory-content').value,
        sharing: document.getElementById('memory-sharing').value
    };
    
    try {
        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Uploading...';
        
        // Upload file
        const response = await fetch(engramUrl('/api/v1/memory/upload'), {
            method: 'POST',
            body: formData,
            headers: {
                'X-Metadata': JSON.stringify(metadata)
            }
        });
        
        if (!response.ok) {
            throw new Error(`Upload failed: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        // Reset form
        form.reset();
        
        // Show success message
        alert(`Memory uploaded successfully! ID: ${result.id}`);
        
        // Switch to browse tab to see the new memory
        document.getElementById('engram-tab-browse').checked = true;
        engram.loadMemories();
        
    } catch (error) {
        console.error('Error uploading memory:', error);
        alert('Error uploading memory: ' + error.message);
    } finally {
        // Reset button
        const submitBtn = form.querySelector('button[type="submit"]');
        submitBtn.disabled = false;
        submitBtn.textContent = 'Upload Memory';
    }
};

/**
 * Search memories
 */
window.engram.searchMemories = async function() {
    const query = document.getElementById('memory-search').value;
    const collection = document.getElementById('search-collection') ? document.getElementById('search-collection').value : 'all';
    const tags = document.getElementById('search-tags') ? document.getElementById('search-tags').value : '';
    
    if (!query) {
        alert('Please enter a search query');
        return;
    }
    
    const resultsContainer = document.getElementById('search-results');
    
    try {
        // Show loading state
        resultsContainer.innerHTML = '<div class="engram__loading">Searching...</div>';
        
        // Build search request
        const searchData = {
            query: query,
            namespace: collection || 'all',
            limit: 20
        };
        
        // Add tag filtering if provided
        if (tags) {
            searchData.metadata = {
                tags: tags.split(',').map(t => t.trim()).filter(t => t)
            };
        }
        
        // Search memories
        const response = await fetch(engramUrl('/api/v1/search'), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(searchData)
        });
        
        const data = await response.json();
        
        // Clear loading state
        resultsContainer.innerHTML = '';
        
        // Render results
        if (data.results && data.results.length > 0) {
            resultsContainer.innerHTML = `<h3 class="engram__search-header">Found ${data.count} results</h3>`;
            
            data.results.forEach(result => {
                const resultHtml = `
                    <div class="engram__search-result">
                        <h4 class="engram__result-title">${result.metadata?.title || 'Untitled'}</h4>
                        <p class="engram__result-content">${result.content}</p>
                        <div class="engram__result-meta">
                            <span class="engram__result-score">Score: ${result.score?.toFixed(2) || 'N/A'}</span>
                            <span class="engram__result-namespace">${result.namespace}</span>
                        </div>
                    </div>
                `;
                resultsContainer.insertAdjacentHTML('beforeend', resultHtml);
            });
        } else {
            resultsContainer.innerHTML = '<div class="engram__empty-state">No results found</div>';
        }
        
    } catch (error) {
        console.error('Error searching memories:', error);
        resultsContainer.innerHTML = '<div class="engram__error">Error searching memories</div>';
    }
};

/**
 * Load insights
 */
window.engram.loadInsights = async function() {
    const container = document.getElementById('insights-container');
    
    try {
        // Show loading state
        container.innerHTML = '<div class="engram__loading">Loading insights...</div>';
        
        // Fetch insights
        const response = await fetch(engramUrl('/api/v1/insights'));
        const data = await response.json();
        
        // Clear loading state
        container.innerHTML = '';
        
        // Render insights
        if (data.insights && data.insights.length > 0) {
            const insightsHtml = data.insights.map(insight => `
                <div class="engram__insight-card" onclick="engram.viewInsight('${insight.name}')">
                    <div class="engram__insight-header">
                        <span class="engram__insight-emoji">${insight.emoji}</span>
                        <h3 class="engram__insight-name">${insight.name}</h3>
                    </div>
                    <div class="engram__insight-stats">
                        <div class="engram__insight-count">${insight.count} memories</div>
                        <div class="engram__insight-percentage">${insight.percentage}%</div>
                    </div>
                    <div class="engram__insight-keywords">
                        ${insight.keywords.map(k => `<span class="engram__keyword">${k}</span>`).join('')}
                    </div>
                </div>
            `).join('');
            
            container.innerHTML = `
                <div class="engram__insights-summary">
                    <h3>Emotional Patterns in ${data.total_memories} Memories</h3>
                </div>
                <div class="engram__insights-grid">
                    ${insightsHtml}
                </div>
            `;
        } else {
            container.innerHTML = '<div class="engram__empty-state">No insights available</div>';
        }
        
    } catch (error) {
        console.error('Error loading insights:', error);
        container.innerHTML = '<div class="engram__error">Error loading insights</div>';
    }
};

/**
 * Apply selected filter
 */
window.engram.applySelectedFilter = function(filterType) {
    const typeFilter = document.getElementById('memory-type-filter');
    const sharingFilter = document.getElementById('memory-sharing-filter');
    
    if (!filterType) return;
    
    switch(filterType) {
        case 'type':
            engram.loadMemories(typeFilter.value, 'all');
            break;
        case 'sharing':
            engram.loadMemories('all', sharingFilter.value);
            break;
        case 'all':
            engram.loadMemories(typeFilter.value, sharingFilter.value);
            break;
    }
    
    // Reset dropdown
    document.getElementById('filter-action').value = '';
};

/**
 * View memories for a specific insight
 */
window.engram.viewInsight = async function(insightName) {
    try {
        // Switch to search tab to show filtered results
        document.getElementById('engram-tab-search').checked = true;
        const resultsContainer = document.getElementById('search-results');
        
        // Show loading state
        resultsContainer.innerHTML = '<div class="engram__loading">Loading memories for insight: ' + insightName + '...</div>';
        
        // Get insight keywords from the insights configuration
        const insightsResponse = await fetch(engramUrl('/api/v1/insights'));
        const insightsData = await insightsResponse.json();
        
        // Find the keywords for this insight
        let keywords = [];
        if (insightsData.insights) {
            const insight = insightsData.insights.find(i => i.name === insightName);
            if (insight && insight.keywords) {
                keywords = insight.keywords;
            }
        }
        
        // Search for memories containing these keywords
        const searchData = {
            query: keywords.join(' OR '),
            namespace: 'all',
            limit: 50
        };
        
        const response = await fetch(engramUrl('/api/v1/search'), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(searchData)
        });
        
        const data = await response.json();
        
        // Display results
        resultsContainer.innerHTML = `
            <div class="engram__insight-results">
                <h3 class="engram__search-header">
                    <span class="engram__insight-emoji">${getInsightEmoji(insightName)}</span>
                    Memories with "${insightName}" emotion
                    <span class="engram__result-count">(${data.results?.length || 0} found)</span>
                </h3>
                <div class="engram__insight-keywords">
                    Keywords: ${keywords.join(', ')}
                </div>
            </div>
        `;
        
        if (data.results && data.results.length > 0) {
            data.results.forEach(result => {
                const resultHtml = `
                    <div class="engram__search-result engram__search-result--${insightName}">
                        <h4 class="engram__result-title">${result.metadata?.title || 'Untitled'}</h4>
                        <p class="engram__result-content">${result.content}</p>
                        <div class="engram__result-meta">
                            <span class="engram__result-score">Score: ${result.score?.toFixed(2) || 'N/A'}</span>
                            <span class="engram__result-namespace">${result.namespace}</span>
                            <span class="engram__result-date">${result.metadata?.created_at || ''}</span>
                        </div>
                    </div>
                `;
                resultsContainer.insertAdjacentHTML('beforeend', resultHtml);
            });
        } else {
            // No results, show sample data for demonstration
            resultsContainer.innerHTML += `
                <div class="engram__empty-state">
                    <p>No memories found with "${insightName}" emotion.</p>
                    <p>Sample memories would appear here once you create memories with keywords like: ${keywords.join(', ')}</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error viewing insight memories:', error);
        const resultsContainer = document.getElementById('search-results');
        resultsContainer.innerHTML = `
            <div class="engram__error">
                Error loading memories for insight "${insightName}": ${error.message}
            </div>
        `;
    }
};

function getInsightEmoji(insightName) {
    const emojiMap = {
        'joy': '😊',
        'frustration': '😤',
        'confusion': '🤔',
        'insight': '💡',
        'curiosity': '🔍',
        'achievement': '🏆',
        'learning': '📚',
        'problem': '⚠️',
        'solution': '✅',
        'collaboration': '🤝'
    };
    return emojiMap[insightName] || '📊';
}

/**
 * View a specific memory
 */
window.engram.viewMemory = async function(memoryId) {
    try {
        const response = await fetch(engramUrl(`/api/v1/memory/${memoryId}`));
        
        if (!response.ok) {
            throw new Error(`Failed to load memory: ${response.statusText}`);
        }
        
        const memory = await response.json();
        
        // Handle the actual memory data structure
        const title = memory.title || memory.metadata?.title || 'Untitled';
        const type = memory.type || memory.metadata?.type || 'Unknown';
        const created = memory.created_at || memory.metadata?.created_at || 'Unknown';
        const content = memory.content || memory.preview || 'No content available';
        const tags = memory.tags || memory.metadata?.tags || [];
        
        // Create a simple modal or alert with full memory content
        const displayContent = `
Title: ${title}
Type: ${type}
Created: ${created}

Content:
${content}

Tags: ${Array.isArray(tags) ? tags.join(', ') : 'None'}
        `;
        
        alert(displayContent);
    } catch (error) {
        console.error('Error viewing memory:', error);
        alert('Error loading memory details: ' + error.message);
    }
};

/**
 * Edit a specific memory
 */
window.engram.editMemory = async function(memoryId) {
    // Switch to create tab and populate with existing data
    document.getElementById('engram-tab-create').checked = true;
    
    try {
        const response = await fetch(engramUrl(`/api/v1/memory/${memoryId}`));
        
        if (!response.ok) {
            throw new Error(`Failed to load memory: ${response.statusText}`);
        }
        
        const memory = await response.json();
        
        // Handle the actual memory data structure - check both top level and metadata
        const title = memory.title || memory.metadata?.title || '';
        const type = memory.type || memory.metadata?.type || 'note';
        const tags = memory.tags || memory.metadata?.tags || [];
        const content = memory.content || memory.preview || '';
        const sharing = memory.sharing || memory.metadata?.sharing || 'private';
        
        // Populate form fields
        document.getElementById('memory-title').value = title;
        document.getElementById('memory-type').value = type;
        document.getElementById('memory-tags').value = Array.isArray(tags) ? tags.join(', ') : '';
        document.getElementById('memory-content').value = content;
        
        // Check if sharing radio buttons exist, otherwise use select
        const privateRadio = document.querySelector('input[name="memory-sharing"][value="private"]');
        if (privateRadio) {
            const sharingRadio = document.querySelector(`input[name="memory-sharing"][value="${sharing}"]`);
            if (sharingRadio) sharingRadio.checked = true;
        } else if (document.getElementById('memory-sharing')) {
            document.getElementById('memory-sharing').value = sharing;
        }
        
        // Change form to update mode
        const form = document.getElementById('create-memory-form');
        form.dataset.mode = 'edit';
        form.dataset.memoryId = memoryId;
        
        // Change button text
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.textContent = 'Update Memory';
        }
    } catch (error) {
        console.error('Error loading memory for edit:', error);
        alert('Error loading memory for editing: ' + error.message);
    }
};

/**
 * Delete a memory
 */
window.engram.deleteMemory = async function(memoryId) {
    if (!confirm('Are you sure you want to delete this memory?')) {
        return;
    }
    
    try {
        const response = await fetch(engramUrl(`/api/v1/memory/${memoryId}`), {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            throw new Error(`Delete failed: ${response.statusText}`);
        }
        
        const result = await response.json();
        alert('Memory deleted successfully');
        
        // Reload the browse view
        engram.loadMemories();
        
    } catch (error) {
        console.error('Error deleting memory:', error);
        alert('Error deleting memory: ' + error.message);
    }
};

/**
 * Initialize component when DOM is ready
 */
document.addEventListener('DOMContentLoaded', function() {
    // Only load initial data if the Engram tab is active
    const engramTab = document.getElementById('engram-tab-browse');
    if (engramTab && engramTab.checked) {
        engram.loadMemories();
    } else {
        console.log('[ENGRAM] Browse tab not active, deferring memory load');
        // Add listener to load when tab becomes active
        if (engramTab) {
            engramTab.addEventListener('change', function() {
                if (this.checked && !window.engram._memoriesLoaded) {
                    window.engram._memoriesLoaded = true;
                    engram.loadMemories();
                }
            }, { once: true });
        }
    }
    
    // Set up filter change handlers
    const typeFilter = document.getElementById('memory-type-filter');
    const sharingFilter = document.getElementById('memory-sharing-filter');
    
    if (typeFilter) {
        typeFilter.addEventListener('change', function() {
            engram.loadMemories(this.value, sharingFilter?.value);
        });
    }
    
    if (sharingFilter) {
        sharingFilter.addEventListener('change', function() {
            engram.loadMemories(typeFilter?.value, this.value);
        });
    }
    
    // Load insights when tab is selected
    const insightsTab = document.getElementById('engram-tab-insights');
    if (insightsTab) {
        insightsTab.addEventListener('change', function() {
            if (this.checked) {
                engram.loadInsights();
            }
        });
    }
    
    // Also handle the content type change for file upload
    const contentTextarea = document.getElementById('memory-content');
    const fileInput = document.getElementById('memory-file');
    
    // If we're loading this for the first time, initialize insights if that tab is active
    if (document.getElementById('engram-tab-insights').checked) {
        engram.loadInsights();
    }
});