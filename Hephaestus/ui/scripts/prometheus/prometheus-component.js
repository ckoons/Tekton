/**
 * Prometheus Component JavaScript
 * Handles sprint management, timeline visualization, resources, and retrospectives
 */

window.prometheusComponent = {
    state: {
        activeTab: 'dashboard',
        sprints: [],
        resources: {},
        retrospectives: [],
        selectedSprint: null
    },

    init: function() {
        console.log('[PROMETHEUS] Initializing component');
        this.loadTabContent('dashboard');
    },

    loadTabContent: function(tabId) {
        console.log('[PROMETHEUS] Loading content for tab:', tabId);
        
        switch(tabId) {
            case 'dashboard':
                this.loadSprints();
                break;
            case 'plans':
                this.loadTimeline();
                break;
            case 'resources':
                this.loadResources();
                break;
            case 'retrospective':
                this.loadRetrospectives();
                break;
            case 'schedule':
                this.loadScheduleForm();
                break;
        }
    },

    // Dashboard Functions
    loadSprints: async function() {
        const grid = document.getElementById('sprints-grid');
        if (!grid) return;

        try {
            const response = await fetch('/api/prometheus/sprints/list');
            if (!response.ok) throw new Error('Failed to load sprints');
            
            const sprints = await response.json();
            this.state.sprints = sprints;
            
            // Clear loading indicator and display sprints
            grid.innerHTML = '';
            
            if (sprints.length === 0) {
                grid.innerHTML = '<div class="prometheus__empty-state">No sprints found. Sprints will appear here when created.</div>';
                return;
            }
            
            sprints.forEach(sprint => {
                const card = this.createSprintCard(sprint);
                grid.appendChild(card);
            });
        } catch (error) {
            console.error('[PROMETHEUS] Error loading sprints:', error);
            grid.innerHTML = '<div class="prometheus__error">Failed to load sprints. Please try again.</div>';
        }
    },

    createSprintCard: function(sprint) {
        const card = document.createElement('div');
        card.className = 'prometheus__sprint-card';
        card.setAttribute('data-sprint-name', sprint.name);
        
        const statusClass = 'prometheus__sprint-status--' + sprint.status.toLowerCase();
        const displayName = sprint.display_name || sprint.name;
        
        card.innerHTML = `
            <div class="prometheus__sprint-status ${statusClass}">${sprint.status}</div>
            <h3 class="prometheus__sprint-name">${displayName}</h3>
            <p class="prometheus__sprint-description">${sprint.description || 'No description available'}</p>
            <div class="prometheus__sprint-meta">
                <span>Updated: ${new Date(sprint.updated).toLocaleDateString()}</span>
                ${sprint.coder_assignment ? `<span>Assigned: ${sprint.coder_assignment}</span>` : ''}
            </div>
            <div class="prometheus__sprint-actions">
                <button class="prometheus__sprint-action prometheus__sprint-action--view" onclick="prometheusComponent.viewSprint('${sprint.name}')">View</button>
                <button class="prometheus__sprint-action prometheus__sprint-action--edit" onclick="prometheusComponent.editSprint('${sprint.name}')">Edit</button>
                ${sprint.status === 'Complete' ? 
                    `<button class="prometheus__sprint-action prometheus__sprint-action--primary" onclick="prometheusComponent.createRetro('${sprint.name}')">Retrospective</button>` :
                    `<button class="prometheus__sprint-action prometheus__sprint-action--primary" onclick="prometheusComponent.updateStatus('${sprint.name}')">Update</button>`
                }
            </div>
        `;
        
        return card;
    },

    editSprint: function(sprintName) {
        console.log('[PROMETHEUS] Editing sprint:', sprintName);
        const sprint = this.state.sprints.find(s => s.name === sprintName);
        if (!sprint) return;
        
        // Populate edit form
        document.getElementById('edit-sprint-name').value = sprint.name;
        document.getElementById('edit-sprint-display-name').value = sprint.display_name || sprint.name;
        document.getElementById('edit-sprint-description').value = sprint.description || '';
        document.getElementById('edit-sprint-purpose').value = sprint.purpose || '';
        document.getElementById('edit-sprint-criteria').value = sprint.success_criteria ? sprint.success_criteria.join('\n') : '';
        document.getElementById('edit-sprint-coder').value = sprint.coder_assignment || '';
        
        // Show dialog
        document.getElementById('edit-sprint-dialog').style.display = 'flex';
    },

    // Timeline Functions
    loadTimeline: async function() {
        const container = document.getElementById('timeline-container');
        if (!container) return;
        
        try {
            // Get active sprints
            const sprints = this.state.sprints.filter(s => 
                s.status === 'Planning' || s.status === 'Ready' || s.status === 'Building'
            );
            
            if (sprints.length === 0) {
                container.innerHTML = '<div class="prometheus__empty-state">No active sprints to display on timeline.</div>';
                return;
            }
            
            // Create CSS-based timeline
            container.innerHTML = '';
            const timeline = this.createTimeline(sprints);
            container.appendChild(timeline);
        } catch (error) {
            console.error('[PROMETHEUS] Error loading timeline:', error);
            container.innerHTML = '<div class="prometheus__error">Failed to load timeline.</div>';
        }
    },

    createTimeline: function(sprints) {
        const timeline = document.createElement('div');
        timeline.className = 'prometheus__timeline-grid';
        
        // Simple CSS-based timeline visualization
        const now = new Date();
        const monthStart = new Date(now.getFullYear(), now.getMonth(), 1);
        const monthEnd = new Date(now.getFullYear(), now.getMonth() + 1, 0);
        const daysInMonth = monthEnd.getDate();
        
        // Set CSS variables for grid
        timeline.style.setProperty('--sprint-count', sprints.length);
        timeline.style.setProperty('--day-count', daysInMonth);
        
        // Create header row with dates
        const headerRow = document.createElement('div');
        headerRow.className = 'prometheus__timeline-header-row';
        headerRow.innerHTML = '<div class="prometheus__timeline-header-cell">Sprint</div>';
        
        for (let day = 1; day <= daysInMonth; day++) {
            const dayCell = document.createElement('div');
            dayCell.className = 'prometheus__timeline-header-cell';
            dayCell.textContent = day;
            headerRow.appendChild(dayCell);
        }
        timeline.appendChild(headerRow);
        
        // Create sprint rows
        sprints.forEach((sprint, index) => {
            const row = document.createElement('div');
            row.className = 'prometheus__timeline-row';
            
            const nameCell = document.createElement('div');
            nameCell.className = 'prometheus__timeline-sprint-name';
            nameCell.textContent = sprint.display_name || sprint.name;
            row.appendChild(nameCell);
            
            // Create timeline bar based on sprint status
            // Planning: days 1-7, Ready: days 8-14, Building: days 15-28
            let startDay = 1;
            let duration = 7;
            
            if (sprint.status === 'Ready') {
                startDay = 8;
                duration = 7;
            } else if (sprint.status === 'Building') {
                startDay = 15;
                duration = 14;
            }
            
            const bar = document.createElement('div');
            bar.className = 'prometheus__timeline-bar';
            bar.style.gridColumn = `${startDay + 2} / span ${duration}`;
            bar.style.gridRow = index + 2;
            bar.textContent = sprint.status;
            bar.onclick = () => this.viewSprint(sprint.name);
            
            timeline.appendChild(row);
            timeline.appendChild(bar);
        });
        
        return timeline;
    },

    // Resources Functions
    loadResources: async function() {
        const grid = document.getElementById('resource-grid');
        if (!grid) return;
        
        try {
            // First ensure we have the latest sprint data
            if (this.state.sprints.length === 0) {
                await this.loadSprints();
            }
            
            const response = await fetch('/api/prometheus/resources/coders');
            if (!response.ok) throw new Error('Failed to load resources');
            
            const result = await response.json();
            const coders = result.data;
            this.state.resources = coders;
            
            // Clear loading and display resources
            grid.innerHTML = '';
            
            // Add real sprint assignment data
            Object.entries(coders).forEach(([coderName, coderData]) => {
                // Find sprints assigned to this coder
                const assignedSprints = this.state.sprints.filter(s => 
                    s.coder_assignment === coderName && 
                    (s.status === 'Building' || s.status === 'Ready')
                );
                
                // Find unassigned ready sprints for queue
                const queueSprints = this.state.sprints.filter(s => 
                    !s.coder_assignment && s.status === 'Ready'
                );
                
                // Update coder data with real assignments
                coderData.active = assignedSprints.map(s => s.name);
                coderData.queue = queueSprints.slice(0, 3).map(s => s.name); // Show up to 3 in queue
                
                const card = this.createResourceCard(coderName, coderData);
                grid.appendChild(card);
            });
        } catch (error) {
            console.error('[PROMETHEUS] Error loading resources:', error);
            grid.innerHTML = '<div class="prometheus__error">Failed to load resources.</div>';
        }
    },

    createResourceCard: function(name, data) {
        const card = document.createElement('div');
        card.className = 'prometheus__resource-card';
        
        const utilization = (data.active.length / data.capacity) * 100;
        
        card.innerHTML = `
            <h3 class="prometheus__resource-name">${name}</h3>
            <div class="prometheus__resource-capacity">
                <span>Capacity: ${data.active.length}/${data.capacity}</span>
                <span>${utilization.toFixed(0)}%</span>
            </div>
            <div class="prometheus__resource-bar">
                <div class="prometheus__resource-fill" style="width: ${utilization}%"></div>
            </div>
            
            <div class="prometheus__resource-section">
                <h4 class="prometheus__resource-section-title">Active Sprints</h4>
                <div class="prometheus__resource-list">
                    ${data.active.length > 0 ? 
                        data.active.map(sprint => `
                            <div class="prometheus__resource-item">
                                <span>${sprint.replace('_Sprint', '')}</span>
                                <span class="prometheus__resource-move" onclick="prometheusComponent.completeSprint('${name}', '${sprint}')">Complete</span>
                            </div>
                        `).join('') :
                        '<div class="prometheus__resource-item">No active sprints</div>'
                    }
                </div>
            </div>
            
            <div class="prometheus__resource-section">
                <h4 class="prometheus__resource-section-title">Queue</h4>
                <div class="prometheus__resource-list">
                    ${data.queue.length > 0 ?
                        data.queue.map(sprint => `
                            <div class="prometheus__resource-item">
                                <span>${sprint.replace('_Sprint', '')}</span>
                                <span class="prometheus__resource-move" onclick="prometheusComponent.assignSprint('${name}', '${sprint}')">Assign</span>
                            </div>
                        `).join('') :
                        '<div class="prometheus__resource-item">No sprints in queue</div>'
                    }
                </div>
            </div>
        `;
        
        return card;
    },

    // Retrospective Functions
    loadRetrospectives: async function() {
        const completedList = document.getElementById('retro-completed-list');
        const activeList = document.getElementById('retro-active-list');
        
        if (!completedList || !activeList) return;
        
        try {
            // Load active sprints that can be completed
            const activeSprints = this.state.sprints.filter(s => 
                s.status === 'Building' || s.status === 'Ready'
            );
            
            // Display active sprints with Complete buttons
            activeList.innerHTML = '';
            if (activeSprints.length === 0) {
                activeList.innerHTML = '<div class="prometheus__empty-state">No active sprints to complete.</div>';
            } else {
                activeSprints.forEach(sprint => {
                    const item = this.createActiveRetroItem(sprint);
                    activeList.appendChild(item);
                });
            }
            
            // Load completed retrospectives
            const response = await fetch('/api/prometheus/retrospectives/sprints/list-retrospectives');
            if (!response.ok) throw new Error('Failed to load retrospectives');
            
            const result = await response.json();
            const retros = result.data;
            this.state.retrospectives = retros;
            
            // Display completed retrospectives
            completedList.innerHTML = '';
            if (retros.length === 0) {
                completedList.innerHTML = '<div class="prometheus__empty-state">No completed retrospectives found.</div>';
            } else {
                retros.forEach(retro => {
                    const item = this.createRetroItem(retro);
                    completedList.appendChild(item);
                });
            }
        } catch (error) {
            console.error('[PROMETHEUS] Error loading retrospectives:', error);
            if (completedList) completedList.innerHTML = '<div class="prometheus__error">Failed to load retrospectives.</div>';
            if (activeList) activeList.innerHTML = '<div class="prometheus__error">Failed to load active sprints.</div>';
        }
    },
    
    createActiveRetroItem: function(sprint) {
        const item = document.createElement('div');
        item.className = 'prometheus__retro-item prometheus__retro-item--active';
        
        item.innerHTML = `
            <div class="prometheus__retro-info">
                <h4 class="prometheus__retro-title">${sprint.display_name || sprint.name}</h4>
                <div class="prometheus__retro-date">Status: ${sprint.status}</div>
                <div class="prometheus__retro-meta">
                    ${sprint.coder_assignment ? `<span>Assigned: ${sprint.coder_assignment}</span>` : ''}
                    <span>Updated: ${new Date(sprint.updated).toLocaleDateString()}</span>
                </div>
            </div>
            <div class="prometheus__retro-actions">
                <button class="prometheus__sprint-action prometheus__sprint-action--view" onclick="prometheusComponent.viewSprint('${sprint.name}')">View</button>
                <button class="prometheus__sprint-action prometheus__sprint-action--edit" onclick="prometheusComponent.editSprint('${sprint.name}')">Edit</button>
                <button class="prometheus__sprint-action prometheus__sprint-action--complete" onclick="prometheusComponent.completeSprintToRetro('${sprint.name}')">Complete</button>
            </div>
        `;
        
        return item;
    },

    createRetroItem: function(retro) {
        const item = document.createElement('div');
        item.className = 'prometheus__retro-item';
        
        item.innerHTML = `
            <div class="prometheus__retro-info">
                <h4 class="prometheus__retro-title">${retro.sprintName}</h4>
                <div class="prometheus__retro-date">Completed: ${retro.completedDate}</div>
                <div class="prometheus__retro-meta">
                    ${retro.hasTeamChat ? '<span>📝 Has team chat</span>' : ''}
                    ${retro.actionItemCount > 0 ? `<span>✓ ${retro.actionItemCount} action items</span>` : ''}
                </div>
            </div>
            <div class="prometheus__retro-actions">
                <button class="prometheus__sprint-action prometheus__sprint-action--view" onclick="prometheusComponent.viewRetro('${retro.sprintName}')">View</button>
                <button class="prometheus__sprint-action prometheus__sprint-action--edit" onclick="prometheusComponent.editRetro('${retro.sprintName}')">Edit</button>
            </div>
        `;
        
        return item;
    },

    // Schedule Form Functions
    loadScheduleForm: async function() {
        const select = document.getElementById('schedule-sprint-select');
        if (!select) return;
        
        // Clear and populate with sprints
        select.innerHTML = '<option value="">Choose a sprint...</option>';
        
        this.state.sprints.forEach(sprint => {
            const option = document.createElement('option');
            option.value = sprint.name;
            option.textContent = `${sprint.display_name || sprint.name} (${sprint.status})`;
            select.appendChild(option);
        });
    },

    // Action Functions
    updateStatus: async function(sprintName) {
        console.log('[PROMETHEUS] Updating status for:', sprintName);
        // Switch to schedule tab and pre-select the sprint
        document.getElementById('schedule-sprint-select').value = sprintName;
        window.prometheus_switchTab('schedule');
    },

    createRetro: function(sprintName) {
        console.log('[PROMETHEUS] Creating retrospective for:', sprintName);
        document.getElementById('retro-sprint-name').value = sprintName;
        document.getElementById('retro-sprint-display').value = sprintName.replace('_Sprint', '');
        document.getElementById('retro-editor-dialog').style.display = 'flex';
    },

    viewSprint: function(sprintName) {
        console.log('[PROMETHEUS] Viewing sprint details:', sprintName);
        // For now, show an alert with sprint info - could be enhanced with a modal
        const sprint = this.state.sprints.find(s => s.name === sprintName);
        if (sprint) {
            alert(`Sprint: ${sprint.display_name || sprint.name}\nStatus: ${sprint.status}\nDescription: ${sprint.description || 'No description'}`);
        }
    },

    completeSprint: async function(coderName, sprintName) {
        console.log('[PROMETHEUS] Completing sprint:', sprintName, 'for coder:', coderName);
        
        try {
            const response = await fetch(`/api/prometheus/resources/coders/${coderName}/complete`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sprint_name: sprintName })
            });
            
            if (!response.ok) throw new Error('Failed to complete sprint');
            
            // Reload resources
            this.loadResources();
        } catch (error) {
            console.error('[PROMETHEUS] Error completing sprint:', error);
        }
    },

    assignSprint: async function(coderName, sprintName) {
        console.log('[PROMETHEUS] Assigning sprint:', sprintName, 'to coder:', coderName);
        
        try {
            const response = await fetch(`/api/prometheus/resources/coders/${coderName}/assign`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sprint_name: sprintName })
            });
            
            if (!response.ok) throw new Error('Failed to assign sprint');
            
            // Reload resources
            this.loadResources();
        } catch (error) {
            console.error('[PROMETHEUS] Error assigning sprint:', error);
        }
    },
    
    completeSprintToRetro: async function(sprintName) {
        console.log('[PROMETHEUS] Completing sprint and moving to retrospectives:', sprintName);
        
        try {
            // First update status to Complete
            const statusResponse = await fetch(`/api/prometheus/sprints/${sprintName}/status`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    status: 'Complete',
                    updated_by: 'prometheus',
                    notes: 'Sprint completed and ready for retrospective'
                })
            });
            
            if (!statusResponse.ok) throw new Error('Failed to update sprint status');
            
            // Then move to Completed directory
            const moveResponse = await fetch(`/api/prometheus/sprints/${sprintName}/move`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    destination: 'Completed',
                    reason: 'Sprint completed and moved to retrospectives'
                })
            });
            
            if (!moveResponse.ok) throw new Error('Failed to move sprint to Completed');
            
            // Reload sprints and retrospectives
            await this.loadSprints();
            await this.loadRetrospectives();
            
            // Show success message (could be improved with a toast notification)
            alert(`Sprint "${sprintName}" has been completed and moved to the Completed directory.`);
        } catch (error) {
            console.error('[PROMETHEUS] Error completing sprint:', error);
            alert('Failed to complete sprint. Please try again.');
        }
    }
};

// Global functions referenced in HTML
window.refreshSprints = function() {
    prometheusComponent.loadSprints();
};

window.saveSprintEdits = async function() {
    const sprintName = document.getElementById('edit-sprint-name').value;
    const updates = {
        description: document.getElementById('edit-sprint-description').value,
        purpose: document.getElementById('edit-sprint-purpose').value,
        successCriteria: document.getElementById('edit-sprint-criteria').value.split('\n').filter(s => s.trim()),
        coder_assignment: document.getElementById('edit-sprint-coder').value
    };
    
    try {
        const response = await fetch(`/api/prometheus/sprints/${sprintName}/edit`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updates)
        });
        
        if (!response.ok) throw new Error('Failed to save sprint');
        
        window.closeEditDialog();
        prometheusComponent.loadSprints();
    } catch (error) {
        console.error('[PROMETHEUS] Error saving sprint:', error);
        alert('Failed to save sprint changes');
    }
};

window.updateSchedule = async function() {
    const sprintName = document.getElementById('schedule-sprint-select').value;
    const status = document.getElementById('schedule-status-select').value;
    const notes = document.getElementById('schedule-notes').value;
    
    if (!sprintName) {
        alert('Please select a sprint');
        return;
    }
    
    try {
        const response = await fetch(`/api/prometheus/sprints/${sprintName}/status`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                status: status,
                updated_by: 'prometheus',
                notes: notes
            })
        });
        
        if (!response.ok) throw new Error('Failed to update schedule');
        
        // Clear form and reload
        document.getElementById('schedule-notes').value = '';
        prometheusComponent.loadSprints();
        
        // Add to log
        const logEntry = document.createElement('div');
        logEntry.className = 'prometheus__log-entry';
        logEntry.innerHTML = `
            <div class="prometheus__log-time">${new Date().toLocaleString()}</div>
            <div>${sprintName} status changed to ${status}</div>
            ${notes ? `<div>${notes}</div>` : ''}
        `;
        document.getElementById('schedule-entries').prepend(logEntry);
    } catch (error) {
        console.error('[PROMETHEUS] Error updating schedule:', error);
        alert('Failed to update schedule');
    }
};

window.clearScheduleForm = function() {
    document.getElementById('schedule-sprint-select').value = '';
    document.getElementById('schedule-status-select').value = 'Planning';
    document.getElementById('schedule-notes').value = '';
};

window.autoGenerateRetro = async function() {
    console.log('[PROMETHEUS] Auto-generating retrospectives');
    // This would call an API to analyze completed sprints and generate retrospectives
    alert('Auto-generation feature coming soon!');
};

window.createManualRetro = function() {
    document.getElementById('retro-sprint-name').value = '';
    document.getElementById('retro-sprint-display').value = 'Manual Retrospective';
    document.getElementById('retro-editor-dialog').style.display = 'flex';
};

window.saveRetro = async function() {
    const sprintName = document.getElementById('retro-sprint-name').value || 'manual_' + Date.now();
    const retroData = {
        whatWentWell: document.getElementById('retro-went-well').value.split('\n').filter(s => s.trim()),
        whatCouldImprove: document.getElementById('retro-could-improve').value.split('\n').filter(s => s.trim()),
        actionItems: document.getElementById('retro-action-items').value.split('\n').filter(s => s.trim()),
        teamChatTranscript: document.getElementById('retro-chat-transcript').value
    };
    
    try {
        const response = await fetch(`/api/prometheus/retrospectives/sprints/${sprintName}/create`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(retroData)
        });
        
        if (!response.ok) throw new Error('Failed to save retrospective');
        
        window.closeRetroEditor();
        prometheusComponent.loadRetrospectives();
    } catch (error) {
        console.error('[PROMETHEUS] Error saving retrospective:', error);
        alert('Failed to save retrospective');
    }
};

window.prometheusComponent.viewRetro = async function(sprintName) {
    try {
        const response = await fetch(`/api/prometheus/retrospectives/sprints/${sprintName}/retrospective`);
        if (!response.ok) throw new Error('Failed to load retrospective');
        
        const result = await response.json();
        const retro = result.data;
        
        // Populate editor with existing data
        document.getElementById('retro-sprint-name').value = sprintName;
        document.getElementById('retro-sprint-display').value = sprintName;
        document.getElementById('retro-went-well').value = retro.whatWentWell ? retro.whatWentWell.join('\n') : '';
        document.getElementById('retro-could-improve').value = retro.whatCouldImprove ? retro.whatCouldImprove.join('\n') : '';
        document.getElementById('retro-action-items').value = retro.actionItems ? retro.actionItems.join('\n') : '';
        document.getElementById('retro-chat-transcript').value = retro.teamChatTranscript || '';
        
        document.getElementById('retro-editor-dialog').style.display = 'flex';
    } catch (error) {
        console.error('[PROMETHEUS] Error loading retrospective:', error);
        alert('Failed to load retrospective');
    }
};

window.prometheusComponent.editRetro = window.prometheusComponent.viewRetro;