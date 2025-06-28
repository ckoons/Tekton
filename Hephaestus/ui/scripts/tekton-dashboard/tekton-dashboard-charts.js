/**
 * Tekton Dashboard Charts
 * Chart initialization and update functions for the Tekton Dashboard component
 */

console.log('[FILE_TRACE] Loading: tekton-dashboard-charts.js');
(function(component) {
    // Initialize mini charts for the system overview
    function initMiniCharts() {
        // Check if Chart.js is available
        if (typeof Chart === 'undefined') {
            console.error('Chart.js not available for mini charts');
            return;
        }
        
        // Initialize CPU mini chart
        if (elements.charts.cpu) {
            charts.cpu = new Chart(elements.charts.cpu, {
                type: 'line',
                data: {
                    labels: Array(20).fill(''),
                    datasets: [{
                        label: 'CPU Usage',
                        data: Array(20).fill(0),
                        borderColor: 'rgb(75, 192, 192)',
                        borderWidth: 2,
                        fill: true,
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        tension: 0.4
                    }]
                },
                options: getMiniChartOptions('CPU Usage (%)', 100)
            });
        }
        
        // Initialize Memory mini chart
        if (elements.charts.memory) {
            charts.memory = new Chart(elements.charts.memory, {
                type: 'line',
                data: {
                    labels: Array(20).fill(''),
                    datasets: [{
                        label: 'Memory Usage',
                        data: Array(20).fill(0),
                        borderColor: 'rgb(153, 102, 255)',
                        borderWidth: 2,
                        fill: true,
                        backgroundColor: 'rgba(153, 102, 255, 0.2)',
                        tension: 0.4
                    }]
                },
                options: getMiniChartOptions('Memory Usage (MB)')
            });
        }
        
        // Initialize Disk mini chart
        if (elements.charts.disk) {
            charts.disk = new Chart(elements.charts.disk, {
                type: 'doughnut',
                data: {
                    labels: ['Used', 'Free'],
                    datasets: [{
                        data: [0, 100],
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.7)',
                            'rgba(200, 200, 200, 0.2)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: getDoughnutChartOptions('Disk Usage')
            });
        }
        
        // Initialize Network mini chart
        if (elements.charts.network) {
            charts.network = new Chart(elements.charts.network, {
                type: 'bar',
                data: {
                    labels: ['In', 'Out'],
                    datasets: [{
                        label: 'Network I/O',
                        data: [0, 0],
                        backgroundColor: [
                            'rgba(54, 162, 235, 0.7)',
                            'rgba(255, 159, 64, 0.7)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: getBarChartOptions('Network I/O (MB/s)')
            });
        }
    }
    
    // Initialize detailed resource charts
    function initResourceCharts() {
        // Check if Chart.js is available
        if (typeof Chart === 'undefined') {
            console.error('Chart.js not available for resource charts');
            return;
        }
        
        // Initialize CPU history chart
        if (elements.charts.cpuHistory) {
            charts.cpuHistory = new Chart(elements.charts.cpuHistory, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'CPU Usage',
                        data: [],
                        borderColor: 'rgb(75, 192, 192)',
                        borderWidth: 2,
                        fill: true,
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        tension: 0.4
                    }]
                },
                options: getResourceChartOptions('CPU Utilization', '%')
            });
        }
        
        // Initialize Memory history chart
        if (elements.charts.memoryHistory) {
            charts.memoryHistory = new Chart(elements.charts.memoryHistory, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Memory Usage',
                        data: [],
                        borderColor: 'rgb(153, 102, 255)',
                        borderWidth: 2,
                        fill: true,
                        backgroundColor: 'rgba(153, 102, 255, 0.2)',
                        tension: 0.4
                    }]
                },
                options: getResourceChartOptions('Memory Utilization', 'MB')
            });
        }
        
        // Initialize Disk I/O chart
        if (elements.charts.diskIO) {
            charts.diskIO = new Chart(elements.charts.diskIO, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Read',
                        data: [],
                        borderColor: 'rgb(54, 162, 235)',
                        borderWidth: 2,
                        fill: false,
                        tension: 0.4
                    }, {
                        label: 'Write',
                        data: [],
                        borderColor: 'rgb(255, 99, 132)',
                        borderWidth: 2,
                        fill: false,
                        tension: 0.4
                    }]
                },
                options: getResourceChartOptions('Disk I/O', 'MB/s')
            });
        }
        
        // Initialize Network Traffic chart
        if (elements.charts.networkTraffic) {
            charts.networkTraffic = new Chart(elements.charts.networkTraffic, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Received',
                        data: [],
                        borderColor: 'rgb(54, 162, 235)',
                        borderWidth: 2,
                        fill: false,
                        tension: 0.4
                    }, {
                        label: 'Sent',
                        data: [],
                        borderColor: 'rgb(255, 159, 64)',
                        borderWidth: 2,
                        fill: false,
                        tension: 0.4
                    }]
                },
                options: getResourceChartOptions('Network Traffic', 'MB/s')
            });
        }
    }
    
    // Get options for mini charts
    function getMiniChartOptions(title, suggestedMax) {
        return {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: false
                },
                tooltip: {
                    enabled: false
                }
            },
            scales: {
                x: {
                    display: false
                },
                y: {
                    display: false,
                    suggestedMin: 0,
                    suggestedMax: suggestedMax || 100
                }
            },
            elements: {
                point: {
                    radius: 0
                }
            },
            animation: {
                duration: 500
            }
        };
    }
    
    // Get options for doughnut charts
    function getDoughnutChartOptions(title) {
        return {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: false,
                    text: title
                }
            },
            cutout: '70%',
            animation: {
                duration: 500
            }
        };
    }
    
    // Get options for bar charts
    function getBarChartOptions(title) {
        return {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: false,
                    text: title
                }
            },
            scales: {
                y: {
                    display: false,
                    beginAtZero: true
                },
                x: {
                    display: false
                }
            },
            animation: {
                duration: 500
            }
        };
    }
    
    // Get options for resource charts
    function getResourceChartOptions(title, unit) {
        return {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top'
                },
                title: {
                    display: true,
                    text: title,
                    font: {
                        size: 16
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            label += context.parsed.y + ' ' + unit;
                            return label;
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'minute',
                        displayFormats: {
                            minute: 'HH:mm'
                        }
                    },
                    title: {
                        display: true,
                        text: 'Time'
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: unit
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            },
            elements: {
                point: {
                    radius: 0,
                    hoverRadius: 4
                }
            }
        };
    }
    
    // Update all charts with the latest data
    function updateCharts() {
        // Update mini charts
        updateMiniCharts();
    }
    
    // Update mini charts
    function updateMiniCharts() {
        if (!tektonService) return;
        
        // Get the last data points
        const cpuData = tektonService.systemMetrics.cpu;
        const memoryData = tektonService.systemMetrics.memory;
        const diskData = tektonService.systemMetrics.disk;
        const networkData = tektonService.systemMetrics.network;
        
        // Update CPU chart
        if (charts.cpu && cpuData.length > 0) {
            // Get the last 20 data points
            const lastData = cpuData.slice(-20).map(d => d.value);
            
            // Update chart data
            charts.cpu.data.datasets[0].data = lastData;
            charts.cpu.update();
        }
        
        // Update Memory chart
        if (charts.memory && memoryData.length > 0) {
            // Get the last 20 data points
            const lastData = memoryData.slice(-20).map(d => d.value / (1024 * 1024)); // Convert to MB
            
            // Update chart data
            charts.memory.data.datasets[0].data = lastData;
            charts.memory.update();
        }
        
        // Update Disk chart
        if (charts.disk && diskData.length > 0) {
            // Get the latest data point
            const latestData = diskData[diskData.length - 1].value;
            
            // Update chart data
            charts.disk.data.datasets[0].data = [latestData, 100 - latestData];
            charts.disk.update();
        }
        
        // Update Network chart
        if (charts.network && networkData.length > 0) {
            // Get the latest data point - split into IN and OUT if available, otherwise use as total
            const latestData = networkData[networkData.length - 1].value;
            let inData = 0;
            let outData = 0;
            
            if (typeof latestData === 'object' && latestData !== null) {
                inData = (latestData.in || 0) / (1024 * 1024); // Convert to MB/s
                outData = (latestData.out || 0) / (1024 * 1024); // Convert to MB/s
            } else {
                // If not split, assign half to each
                inData = outData = (latestData / 2) / (1024 * 1024); // Convert to MB/s
            }
            
            // Update chart data
            charts.network.data.datasets[0].data = [inData, outData];
            charts.network.update();
        }
    }
    
    // Update resource charts based on time range
    function updateResourceCharts() {
        if (!tektonService) return;
        
        // Get time range from state
        const timeRange = component.state.get('resourceTimeRange');
        
        // Get filtered metrics based on time range
        const cpuMetrics = tektonService.getMetricHistory('cpu', { timeRange });
        const memoryMetrics = tektonService.getMetricHistory('memory', { timeRange });
        const diskMetrics = tektonService.getMetricHistory('disk', { timeRange });
        const networkMetrics = tektonService.getMetricHistory('network', { timeRange });
        
        // Update CPU History chart
        if (charts.cpuHistory) {
            updateTimeSeriesChart(
                charts.cpuHistory, 
                cpuMetrics, 
                d => d.value, 
                d => new Date(d.timestamp)
            );
        }
        
        // Update Memory History chart
        if (charts.memoryHistory) {
            updateTimeSeriesChart(
                charts.memoryHistory, 
                memoryMetrics, 
                d => d.value / (1024 * 1024), // Convert to MB
                d => new Date(d.timestamp)
            );
        }
        
        // Update Disk I/O chart
        if (charts.diskIO) {
            // Check if disk metrics include separate read/write values
            const hasDetailedDiskMetrics = diskMetrics.length > 0 && 
                                       typeof diskMetrics[0].value === 'object' &&
                                       diskMetrics[0].value !== null &&
                                       ('read' in diskMetrics[0].value || 'write' in diskMetrics[0].value);
            
            if (hasDetailedDiskMetrics) {
                // Update with read/write data
                updateMultiTimeSeriesChart(
                    charts.diskIO,
                    [{
                        data: diskMetrics,
                        valueAccessor: d => (d.value.read || 0) / (1024 * 1024), // Convert to MB/s
                        index: 0
                    }, {
                        data: diskMetrics,
                        valueAccessor: d => (d.value.write || 0) / (1024 * 1024), // Convert to MB/s
                        index: 1
                    }],
                    d => new Date(d.timestamp)
                );
            } else {
                // Fallback to just showing the total
                updateTimeSeriesChart(
                    charts.diskIO, 
                    diskMetrics, 
                    d => typeof d.value === 'number' ? d.value / (1024 * 1024) : 0, // Convert to MB/s
                    d => new Date(d.timestamp)
                );
            }
        }
        
        // Update Network Traffic chart
        if (charts.networkTraffic) {
            // Check if network metrics include separate in/out values
            const hasDetailedNetworkMetrics = networkMetrics.length > 0 && 
                                          typeof networkMetrics[0].value === 'object' &&
                                          networkMetrics[0].value !== null &&
                                          ('in' in networkMetrics[0].value || 'out' in networkMetrics[0].value);
            
            if (hasDetailedNetworkMetrics) {
                // Update with in/out data
                updateMultiTimeSeriesChart(
                    charts.networkTraffic,
                    [{
                        data: networkMetrics,
                        valueAccessor: d => (d.value.in || 0) / (1024 * 1024), // Convert to MB/s
                        index: 0
                    }, {
                        data: networkMetrics,
                        valueAccessor: d => (d.value.out || 0) / (1024 * 1024), // Convert to MB/s
                        index: 1
                    }],
                    d => new Date(d.timestamp)
                );
            } else {
                // Fallback to just showing the total
                updateTimeSeriesChart(
                    charts.networkTraffic, 
                    networkMetrics, 
                    d => typeof d.value === 'number' ? d.value / (1024 * 1024) : 0, // Convert to MB/s
                    d => new Date(d.timestamp)
                );
            }
        }
    }
    
    // Update a time series chart with new data
    function updateTimeSeriesChart(chart, data, valueAccessor, timeAccessor) {
        if (!chart || !data || data.length === 0) return;
        
        // Extract data points
        const timestamps = data.map(timeAccessor);
        const values = data.map(valueAccessor);
        
        // Update chart data
        chart.data.labels = timestamps;
        chart.data.datasets[0].data = values;
        
        // Update the chart
        chart.update();
    }
    
    // Update a multi-time series chart with new data
    function updateMultiTimeSeriesChart(chart, dataSets, timeAccessor) {
        if (!chart || !dataSets || dataSets.length === 0) return;
        
        // Extract timestamps from the first dataset (assuming all datasets share the same timestamps)
        const timestamps = dataSets[0].data.map(timeAccessor);
        
        // Update chart labels
        chart.data.labels = timestamps;
        
        // Update each dataset
        dataSets.forEach(dataSet => {
            const values = dataSet.data.map(dataSet.valueAccessor);
            chart.data.datasets[dataSet.index].data = values;
        });
        
        // Update the chart
        chart.update();
    }
    
    // Format utils
    
    // Format byte size to human-readable format
    function formatByteSize(bytes) {
        if (bytes === undefined || bytes === null) return '0 B';
        
        const units = ['B', 'KB', 'MB', 'GB', 'TB'];
        let size = bytes;
        let unitIndex = 0;
        
        while (size >= 1024 && unitIndex < units.length - 1) {
            size /= 1024;
            unitIndex++;
        }
        
        return `${size.toFixed(2)} ${units[unitIndex]}`;
    }
    
    // Format metric value with unit
    function formatMetricValue(value, unit) {
        if (value === undefined || value === null) return '0' + (unit || '');
        
        return `${value.toFixed(2)}${unit || ''}`;
    }
    
    // Format uptime
    function formatUptime(seconds) {
        if (!seconds) return 'N/A';
        
        const days = Math.floor(seconds / 86400);
        const hours = Math.floor((seconds % 86400) / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        
        let result = '';
        if (days > 0) result += `${days}d `;
        if (hours > 0 || days > 0) result += `${hours}h `;
        result += `${minutes}m`;
        
        return result.trim();
    }
    
    // Format date
    function formatDate(dateStr) {
        if (!dateStr) return 'N/A';
        
        const date = new Date(dateStr);
        return date.toLocaleString();
    }
    
    // Get status icon based on status
    function getStatusIcon(status) {
        switch (status) {
            case 'running':
                return '🟢';
            case 'stopped':
                return '🔴';
            case 'error':
                return '⚠️';
            case 'warning':
                return '⚠️';
            case 'starting':
                return '🟡';
            case 'stopping':
                return '🟠';
            default:
                return '⚪';
        }
    }
    
    // Get alert icon based on level
    function getAlertIcon(level) {
        switch (level) {
            case 'error':
                return '🔴';
            case 'warning':
                return '⚠️';
            case 'info':
                return 'ℹ️';
            case 'success':
                return '✅';
            default:
                return 'ℹ️';
        }
    }
    
    // Capitalize first letter of a string
    function capitalizeFirstLetter(string) {
        if (!string) return '';
        return string.charAt(0).toUpperCase() + string.slice(1);
    }
    
    // Expose chart functions and utilities to component scope
    Object.assign(component, {
        initMiniCharts,
        initResourceCharts,
        updateCharts,
        updateMiniCharts,
        updateResourceCharts,
        formatByteSize,
        formatMetricValue,
        formatUptime,
        formatDate,
        getStatusIcon,
        getAlertIcon,
        capitalizeFirstLetter
    });
    
})(component);