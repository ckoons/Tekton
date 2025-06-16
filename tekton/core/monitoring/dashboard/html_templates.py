#!/usr/bin/env python3
"""
HTML Templates Module

This module contains HTML templates for the dashboard UI.
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Tekton Health Dashboard</title>
    <style>
        body { font-family: sans-serif; margin: 0; padding: 20px; }
        h1 { color: #333; }
        .dashboard { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .card { background: #f5f5f5; border-radius: 5px; padding: 15px; }
        .healthy { color: green; }
        .degraded { color: orange; }
        .unhealthy { color: red; }
        .warning { color: orange; }
        .critical { color: red; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f2f2f2; }
        .component-row:hover { background-color: #f0f0f0; }
        .alert { border-left: 4px solid; padding-left: 10px; margin-bottom: 10px; }
        .alert.critical { border-color: #d9534f; background-color: #f9eae9; }
        .alert.warning { border-color: #f0ad4e; background-color: #fcf8e3; }
        .alert.info { border-color: #5bc0de; background-color: #f0f7fd; }
        .tabs { display: flex; margin-bottom: 20px; }
        .tab { padding: 10px 20px; cursor: pointer; border: 1px solid #ddd; 
               border-bottom: none; border-radius: 5px 5px 0 0; margin-right: 5px; }
        .tab.active { background-color: #f5f5f5; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .resource-bar { height: 20px; background-color: #e0e0e0; margin: 5px 0; position: relative; }
        .resource-bar-fill { height: 100%; background-color: #4CAF50; }
        .resource-bar-warning { background-color: #FFA500; }
        .resource-bar-critical { background-color: #FF0000; }
        .resource-bar-label { position: absolute; top: 0; right: 5px; color: #fff; font-weight: bold; }
        .chart-container { height: 200px; position: relative; margin-top: 10px; }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <h1>Tekton Health Dashboard</h1>
    
    <div class="tabs">
        <div class="tab active" data-tab="components">Components</div>
        <div class="tab" data-tab="resources">Resources</div>
        <div class="tab" data-tab="dependencies">Dependencies</div>
    </div>
    
    <div class="tab-content active" id="components-tab">
        <div class="dashboard">
            <div class="card">
                <h2>System Health</h2>
                <div id="system-health"></div>
            </div>
            <div class="card">
                <h2>Active Alerts</h2>
                <div id="alerts"></div>
            </div>
            <div class="card" style="grid-column: span 2;">
                <h2>Component Status</h2>
                <table id="component-table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Type</th>
                            <th>Status</th>
                            <th>Health</th>
                            <th>Metrics</th>
                        </tr>
                    </thead>
                    <tbody id="component-tbody"></tbody>
                </table>
            </div>
        </div>
    </div>
    
    <div class="tab-content" id="resources-tab">
        <div class="dashboard">
            <div class="card">
                <h2>System Resources</h2>
                <div id="resource-metrics">
                    <div>
                        <h3>CPU <span id="cpu-percent"></span></h3>
                        <div class="resource-bar">
                            <div id="cpu-bar" class="resource-bar-fill"></div>
                            <div id="cpu-label" class="resource-bar-label"></div>
                        </div>
                    </div>
                    <div>
                        <h3>Memory <span id="memory-percent"></span></h3>
                        <div class="resource-bar">
                            <div id="memory-bar" class="resource-bar-fill"></div>
                            <div id="memory-label" class="resource-bar-label"></div>
                        </div>
                    </div>
                    <div>
                        <h3>Disk <span id="disk-percent"></span></h3>
                        <div class="resource-bar">
                            <div id="disk-bar" class="resource-bar-fill"></div>
                            <div id="disk-label" class="resource-bar-label"></div>
                        </div>
                    </div>
                    <div>
                        <h3>Network <span id="network-mbps"></span></h3>
                        <div class="resource-bar">
                            <div id="network-bar" class="resource-bar-fill"></div>
                            <div id="network-label" class="resource-bar-label"></div>
                        </div>
                    </div>
                    <div id="gpu-container" style="display:none;">
                        <h3>GPU <span id="gpu-percent"></span></h3>
                        <div class="resource-bar">
                            <div id="gpu-bar" class="resource-bar-fill"></div>
                            <div id="gpu-label" class="resource-bar-label"></div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="card">
                <h2>System Info</h2>
                <div id="system-info"></div>
            </div>
            <div class="card" style="grid-column: span 2;">
                <h2>Resource History</h2>
                <div class="chart-container">
                    <canvas id="resource-chart"></canvas>
                </div>
            </div>
            <div class="card" style="grid-column: span 2;">
                <h2>Component Resources</h2>
                <table id="component-resources-table">
                    <thead>
                        <tr>
                            <th>Component</th>
                            <th>CPU %</th>
                            <th>Memory %</th>
                        </tr>
                    </thead>
                    <tbody id="component-resources-tbody"></tbody>
                </table>
            </div>
        </div>
    </div>
    
    <div class="tab-content" id="dependencies-tab">
        <div class="dashboard">
            <div class="card" style="grid-column: span 2;">
                <h2>Dependency Graph</h2>
                <div id="dependency-graph"></div>
            </div>
        </div>
    </div>
    
    <script>
        // Tab handling
        document.querySelectorAll('.tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                
                tab.classList.add('active');
                document.getElementById(`${tab.dataset.tab}-tab`).classList.add('active');
            });
        });
        
        // Resource chart
        let resourceChart;
        
        function initResourceChart() {
            const ctx = document.getElementById('resource-chart').getContext('2d');
            resourceChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: 'CPU',
                            borderColor: 'rgb(255, 99, 132)',
                            data: []
                        },
                        {
                            label: 'Memory',
                            borderColor: 'rgb(54, 162, 235)',
                            data: []
                        },
                        {
                            label: 'Disk',
                            borderColor: 'rgb(255, 206, 86)',
                            data: []
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            title: {
                                display: true,
                                text: 'Usage %'
                            }
                        }
                    }
                }
            });
        }
        
        // Update component data
        function fetchComponentData() {
            // Fetch system health
            fetch('/api/health')
                .then(response => response.json())
                .then(data => {
                    const systemHealth = document.getElementById('system-health');
                    const metrics = data.metrics;
                    systemHealth.innerHTML = `
                        <p>Components: ${metrics.total_components} total, 
                           <span class="healthy">${metrics.healthy_components} healthy</span>, 
                           <span class="degraded">${metrics.degraded_components} degraded</span>,
                           <span class="unhealthy">${metrics.unhealthy_components} unhealthy</span></p>
                        <p>Average Health: ${metrics.average_health.toFixed(1)}%</p>
                        <p>Active Alerts: ${metrics.alert_count || 0}</p>
                    `;
                    
                    // Update component table
                    const tbody = document.getElementById('component-tbody');
                    tbody.innerHTML = '';
                    for (const component of data.components) {
                        const row = document.createElement('tr');
                        row.className = 'component-row';
                        
                        let metricsHtml = '';
                        if (component.metrics) {
                            const metricsList = [];
                            for (const [key, value] of Object.entries(component.metrics)) {
                                if (typeof value === 'number') {
                                    if (key.includes('percent') || key.includes('usage')) {
                                        metricsList.push(`${key}: ${(value * 100).toFixed(1)}%`);
                                    } else {
                                        metricsList.push(`${key}: ${value.toFixed(1)}`);
                                    }
                                }
                            }
                            metricsHtml = metricsList.join('<br>');
                        }
                        
                        row.innerHTML = `
                            <td>${component.component_name}</td>
                            <td>${component.component_type}</td>
                            <td class="${component.status.toLowerCase()}">${component.status}</td>
                            <td>${component.health ? component.health.toFixed(1) + '%' : 'N/A'}</td>
                            <td>${metricsHtml}</td>
                        `;
                        tbody.appendChild(row);
                    }
                });
                
            // Fetch alerts
            fetch('/api/alerts')
                .then(response => response.json())
                .then(alerts => {
                    const alertsDiv = document.getElementById('alerts');
                    alertsDiv.innerHTML = '';
                    
                    if (alerts.length === 0) {
                        alertsDiv.innerHTML = '<p>No active alerts</p>';
                        return;
                    }
                    
                    // Filter for unresolved alerts
                    const activeAlerts = alerts.filter(alert => !alert.resolved);
                    
                    if (activeAlerts.length === 0) {
                        alertsDiv.innerHTML = '<p>No active alerts</p>';
                        return;
                    }
                    
                    for (const alert of activeAlerts) {
                        const alertDiv = document.createElement('div');
                        alertDiv.className = `alert ${alert.severity.toLowerCase()}`;
                        alertDiv.innerHTML = `
                            <h3>${alert.title}</h3>
                            <p>${alert.description}</p>
                            <small>${new Date(alert.timestamp * 1000).toLocaleString()}</small>
                        `;
                        alertsDiv.appendChild(alertDiv);
                    }
                });
                
            // Fetch dependency graph
            fetch('/api/dependency-graph')
                .then(response => response.json())
                .then(graph => {
                    const graphDiv = document.getElementById('dependency-graph');
                    graphDiv.innerHTML = '';
                    
                    // Simple text representation
                    const dependencies = [];
                    for (const [component, data] of Object.entries(graph)) {
                        if (data.dependencies.length > 0) {
                            dependencies.push(`${component} depends on: ${data.dependencies.join(', ')}`);
                        }
                    }
                    
                    if (dependencies.length === 0) {
                        graphDiv.innerHTML = '<p>No dependencies found</p>';
                        return;
                    }
                    
                    graphDiv.innerHTML = '<ul>' + 
                        dependencies.map(dep => `<li>${dep}</li>`).join('') +
                        '</ul>';
                });
        }
        
        function fetchResourceData() {
            // Fetch current resource metrics
            fetch('/api/resource-metrics')
                .then(response => {
                    if (!response.ok) throw new Error('Resource monitoring not available');
                    return response.json();
                })
                .then(data => {
                    // Update CPU
                    document.getElementById('cpu-percent').textContent = `(${data.cpu_percent.toFixed(1)}%)`;
                    const cpuBar = document.getElementById('cpu-bar');
                    cpuBar.style.width = `${data.cpu_percent}%`;
                    document.getElementById('cpu-label').textContent = `${data.cpu_percent.toFixed(1)}%`;
                    
                    // Set color based on thresholds
                    if (data.cpu_percent >= 90) {
                        cpuBar.className = 'resource-bar-fill resource-bar-critical';
                    } else if (data.cpu_percent >= 70) {
                        cpuBar.className = 'resource-bar-fill resource-bar-warning';
                    } else {
                        cpuBar.className = 'resource-bar-fill';
                    }
                    
                    // Update Memory
                    document.getElementById('memory-percent').textContent = `(${data.memory_percent.toFixed(1)}%)`;
                    const memoryBar = document.getElementById('memory-bar');
                    memoryBar.style.width = `${data.memory_percent}%`;
                    document.getElementById('memory-label').textContent = `${data.memory_percent.toFixed(1)}%`;
                    
                    if (data.memory_percent >= 90) {
                        memoryBar.className = 'resource-bar-fill resource-bar-critical';
                    } else if (data.memory_percent >= 75) {
                        memoryBar.className = 'resource-bar-fill resource-bar-warning';
                    } else {
                        memoryBar.className = 'resource-bar-fill';
                    }
                    
                    // Update Disk (using max disk usage)
                    const diskValues = Object.values(data.disk_percent);
                    const maxDisk = diskValues.length > 0 ? Math.max(...diskValues) : 0;
                    document.getElementById('disk-percent').textContent = `(${maxDisk.toFixed(1)}%)`;
                    const diskBar = document.getElementById('disk-bar');
                    diskBar.style.width = `${maxDisk}%`;
                    document.getElementById('disk-label').textContent = `${maxDisk.toFixed(1)}%`;
                    
                    if (maxDisk >= 95) {
                        diskBar.className = 'resource-bar-fill resource-bar-critical';
                    } else if (maxDisk >= 80) {
                        diskBar.className = 'resource-bar-fill resource-bar-warning';
                    } else {
                        diskBar.className = 'resource-bar-fill';
                    }
                    
                    // Update Network (total across all interfaces)
                    let totalMbps = 0;
                    for (const interface in data.network_mbps) {
                        if (data.network_mbps[interface].total_mbps) {
                            totalMbps += data.network_mbps[interface].total_mbps;
                        }
                    }
                    document.getElementById('network-mbps').textContent = `(${totalMbps.toFixed(1)} Mbps)`;
                    
                    // Network has a different scale
                    const networkPercent = Math.min(100, (totalMbps / 200) * 100);
                    const networkBar = document.getElementById('network-bar');
                    networkBar.style.width = `${networkPercent}%`;
                    document.getElementById('network-label').textContent = `${totalMbps.toFixed(1)} Mbps`;
                    
                    if (totalMbps >= 200) {
                        networkBar.className = 'resource-bar-fill resource-bar-critical';
                    } else if (totalMbps >= 100) {
                        networkBar.className = 'resource-bar-fill resource-bar-warning';
                    } else {
                        networkBar.className = 'resource-bar-fill';
                    }
                    
                    // Update GPU if available
                    if (data.gpu_percent) {
                        document.getElementById('gpu-container').style.display = 'block';
                        
                        // Get max utilization among all GPUs
                        let maxGpuUtil = 0;
                        for (const gpu in data.gpu_percent) {
                            if (data.gpu_percent[gpu].utilization > maxGpuUtil) {
                                maxGpuUtil = data.gpu_percent[gpu].utilization;
                            }
                        }
                        
                        document.getElementById('gpu-percent').textContent = `(${maxGpuUtil.toFixed(1)}%)`;
                        const gpuBar = document.getElementById('gpu-bar');
                        gpuBar.style.width = `${maxGpuUtil}%`;
                        document.getElementById('gpu-label').textContent = `${maxGpuUtil.toFixed(1)}%`;
                        
                        if (maxGpuUtil >= 90) {
                            gpuBar.className = 'resource-bar-fill resource-bar-critical';
                        } else if (maxGpuUtil >= 70) {
                            gpuBar.className = 'resource-bar-fill resource-bar-warning';
                        } else {
                            gpuBar.className = 'resource-bar-fill';
                        }
                    } else {
                        document.getElementById('gpu-container').style.display = 'none';
                    }
                    
                    // Update component resources
                    const tbody = document.getElementById('component-resources-tbody');
                    tbody.innerHTML = '';
                    
                    for (const [componentId, metrics] of Object.entries(data.component_metrics)) {
                        const row = document.createElement('tr');
                        
                        const cpuClass = metrics.cpu_percent >= 90 ? 'critical' : 
                                       metrics.cpu_percent >= 70 ? 'warning' : '';
                                         
                        const memClass = metrics.memory_percent >= 90 ? 'critical' : 
                                       metrics.memory_percent >= 75 ? 'warning' : '';
                        
                        row.innerHTML = `
                            <td>${componentId}</td>
                            <td class="${cpuClass}">${metrics.cpu_percent.toFixed(1)}%</td>
                            <td class="${memClass}">${metrics.memory_percent.toFixed(1)}%</td>
                        `;
                        tbody.appendChild(row);
                    }
                    
                    // Update chart
                    if (resourceChart) {
                        // Add new data point (limited to last 20 points)
                        const timestamp = new Date(data.timestamp);
                        const timeStr = timestamp.toLocaleTimeString();
                        
                        if (resourceChart.data.labels.length >= 20) {
                            resourceChart.data.labels.shift();
                            resourceChart.data.datasets.forEach(dataset => dataset.data.shift());
                        }
                        
                        resourceChart.data.labels.push(timeStr);
                        resourceChart.data.datasets[0].data.push(data.cpu_percent);
                        resourceChart.data.datasets[1].data.push(data.memory_percent);
                        resourceChart.data.datasets[2].data.push(maxDisk);
                        
                        resourceChart.update();
                    }
                })
                .catch(error => {
                    console.error('Error fetching resource metrics:', error);
                });
                
            // Fetch system info (only once)
            if (!window.systemInfoFetched) {
                fetch('/api/system-info')
                    .then(response => {
                        if (!response.ok) throw new Error('System info not available');
                        return response.json();
                    })
                    .then(info => {
                        const infoDiv = document.getElementById('system-info');
                        
                        const infoHtml = [
                            `<p><strong>Hostname:</strong> ${info.hostname}</p>`,
                            `<p><strong>Platform:</strong> ${info.platform}</p>`,
                            `<p><strong>Architecture:</strong> ${info.architecture}</p>`,
                            `<p><strong>CPU:</strong> ${info.cpu_model || 'Unknown'}</p>`,
                            `<p><strong>CPU Cores:</strong> ${info.physical_cpu_count} physical / ${info.cpu_count} logical</p>`,
                            `<p><strong>Memory:</strong> ${info.memory_total_gb.toFixed(1)} GB</p>`,
                            `<p><strong>Boot Time:</strong> ${new Date(info.boot_time).toLocaleString()}</p>`
                        ];
                        
                        if (info.gpus && info.gpus.length > 0) {
                            const gpuInfo = info.gpus.map(gpu => 
                                `${gpu.name || 'Unknown'} (${gpu.memory_total_gb.toFixed(1)} GB)`
                            ).join('<br>');
                            infoHtml.push(`<p><strong>GPUs:</strong><br>${gpuInfo}</p>`);
                        }
                        
                        infoDiv.innerHTML = infoHtml.join('');
                        window.systemInfoFetched = true;
                    })
                    .catch(error => {
                        console.error('Error fetching system info:', error);
                    });
            }
        }

        // Initialize charts
        initResourceChart();
        
        // Initial data fetch
        fetchComponentData();
        fetchResourceData();
        
        // Refresh every 5 seconds
        setInterval(fetchComponentData, 5000);
        setInterval(fetchResourceData, 5000);
    </script>
</body>
</html>
"""