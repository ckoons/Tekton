/**
 * Budget Chart Utilities
 * 
 * Handles creation and configuration of chart visualizations
 * Part of the Budget UI Update Sprint implementation
 */
class BudgetChartUtils {
    /**
     * Create a new chart utilities instance
     */
    constructor() {
        // Default chart colors
        this.colors = {
            blue: '#3B82F6',
            gray: '#94A3B8',
            green: '#34A853',
            yellow: '#FFA500',
            red: '#E53935',
            purple: '#7356BF',
            teal: '#10A283',
            orange: '#FF6600',
            background: '#252535',
            gridLines: '#444444'
        };
        
        // Chart instances for later reference
        this.charts = {};
    }
    
    /**
     * Get color for a provider
     * @param {string} provider - Provider name
     * @returns {string} Color code
     */
    getProviderColor(provider) {
        return window.BudgetModels.getProviderColor(provider);
    }
    
    /**
     * Format currency value
     * @param {number} value - Value to format
     * @returns {string} Formatted currency
     */
    formatCurrency(value) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(value);
    }
    
    /**
     * Format token count with appropriate scaling
     * @param {number} count - Token count
     * @returns {string} Formatted token count
     */
    formatTokens(count) {
        if (count >= 1000000) {
            return (count / 1000000).toFixed(1) + 'M';
        } else if (count >= 1000) {
            return (count / 1000).toFixed(1) + 'K';
        } else {
            return count.toString();
        }
    }
    
    /**
     * Create a usage trend chart
     * @param {string} elementId - Target element ID
     * @param {Array} data - Chart data
     * @param {Object} options - Chart options
     */
    createTrendChart(elementId, data, options = {}) {
        // Get the canvas element
        const canvas = document.getElementById(elementId);
        if (!canvas) {
            console.error(`[BUDGET CHART] Cannot find element with ID ${elementId}`);
            return;
        }
        
        // Clear any existing chart
        if (this.charts[elementId]) {
            this.charts[elementId].destroy();
        }
        
        // Format dates for labels
        const labels = data.map(item => {
            const date = new Date(item.date);
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        });
        
        // Create datasets
        const datasets = [
            {
                label: 'Spend',
                data: data.map(item => item.amount),
                borderColor: this.colors.blue,
                backgroundColor: this.colors.blue + '33', // Add transparency
                borderWidth: 2,
                pointRadius: 3,
                pointBackgroundColor: this.colors.blue,
                fill: true,
                tension: 0.2 // Slight curve for the line
            },
            {
                label: 'Budget Limit',
                data: data.map(item => item.limit),
                borderColor: this.colors.gray,
                borderWidth: 2,
                borderDash: [5, 5], // Dashed line
                pointRadius: 0,
                fill: false
            }
        ];
        
        // Create chart configuration
        const config = {
            type: 'line',
            data: {
                labels,
                datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false // We'll use custom legend
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
                                label += new Intl.NumberFormat('en-US', {
                                    style: 'currency',
                                    currency: 'USD'
                                }).format(context.parsed.y);
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: this.colors.gridLines + '33', // Lighter grid lines
                            tickLength: 0
                        },
                        ticks: {
                            color: '#f0f0f0',
                            autoSkip: true,
                            maxRotation: 0
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: this.colors.gridLines + '33', // Lighter grid lines
                        },
                        ticks: {
                            color: '#f0f0f0',
                            callback: function(value) {
                                return '$' + value;
                            }
                        }
                    }
                },
                ...options
            }
        };
        
        // Create the chart
        this.charts[elementId] = new Chart(canvas, config);
        
        return this.charts[elementId];
    }
    
    /**
     * Create a distribution pie chart
     * @param {string} elementId - Target element ID
     * @param {Array} data - Chart data
     * @param {Object} options - Chart options
     */
    createDistributionChart(elementId, data, options = {}) {
        // Get the canvas element
        const canvas = document.getElementById(elementId);
        if (!canvas) {
            console.error(`[BUDGET CHART] Cannot find element with ID ${elementId}`);
            return;
        }
        
        // Clear any existing chart
        if (this.charts[elementId]) {
            this.charts[elementId].destroy();
        }
        
        // Prepare data for chart
        const labels = data.map(item => item.provider);
        const values = data.map(item => item.amount);
        const colors = data.map(item => this.getProviderColor(item.provider));
        
        // Create chart configuration
        const config = {
            type: 'doughnut',
            data: {
                labels,
                datasets: [{
                    data: values,
                    backgroundColor: colors,
                    borderColor: this.colors.background,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {
                    legend: {
                        display: false // We'll use custom legend
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return [
                                    context.label + ': ' + new Intl.NumberFormat('en-US', {
                                        style: 'currency',
                                        currency: 'USD'
                                    }).format(value),
                                    `${percentage}% of total`
                                ];
                            }
                        }
                    }
                },
                ...options
            }
        };
        
        // Create the chart
        this.charts[elementId] = new Chart(canvas, config);
        
        return this.charts[elementId];
    }
    
    /**
     * Update an existing chart with new data
     * @param {string} elementId - Target element ID
     * @param {Array} data - New chart data
     * @param {string} type - Chart type ('trend' or 'distribution')
     */
    updateChart(elementId, data, type) {
        // Get the chart instance
        const chart = this.charts[elementId];
        if (!chart) {
            console.error(`[BUDGET CHART] No chart found for element ID ${elementId}`);
            
            // Create a new chart if none exists
            if (type === 'trend') {
                return this.createTrendChart(elementId, data);
            } else if (type === 'distribution') {
                return this.createDistributionChart(elementId, data);
            }
            
            return;
        }
        
        // Update the chart based on type
        if (type === 'trend') {
            // Update labels
            chart.data.labels = data.map(item => {
                const date = new Date(item.date);
                return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            });
            
            // Update datasets
            chart.data.datasets[0].data = data.map(item => item.amount);
            chart.data.datasets[1].data = data.map(item => item.limit);
        } else if (type === 'distribution') {
            // Update labels and data
            chart.data.labels = data.map(item => item.provider);
            chart.data.datasets[0].data = data.map(item => item.amount);
            chart.data.datasets[0].backgroundColor = data.map(item => 
                this.getProviderColor(item.provider)
            );
        }
        
        // Update the chart
        chart.update();
        
        return chart;
    }
    
    /**
     * Create a placeholder for a chart that isn't loaded yet
     * @param {string} elementId - Target element ID
     * @param {string} message - Message to display
     */
    createPlaceholder(elementId, message = 'Loading chart data...') {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        // Clear any existing content
        element.innerHTML = '';
        
        // Create placeholder elements
        const placeholderDiv = document.createElement('div');
        placeholderDiv.className = 'budget__chart-placeholder';
        
        const messageDiv = document.createElement('div');
        messageDiv.textContent = message;
        
        // Create loading spinner
        const spinnerDiv = document.createElement('div');
        spinnerDiv.className = 'budget__spinner';
        
        // Append elements
        placeholderDiv.appendChild(spinnerDiv);
        placeholderDiv.appendChild(messageDiv);
        element.appendChild(placeholderDiv);
    }
    
    /**
     * Replace a placeholder with a canvas for chart rendering
     * @param {string} elementId - Target element ID
     * @returns {HTMLCanvasElement} The created canvas
     */
    createCanvasForChart(elementId) {
        const element = document.getElementById(elementId);
        if (!element) return null;
        
        // Clear any existing content
        element.innerHTML = '';
        
        // Create canvas
        const canvas = document.createElement('canvas');
        canvas.id = `${elementId}-canvas`;
        
        // Set canvas attributes for chart
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        
        // Append canvas to container
        element.appendChild(canvas);
        
        return canvas;
    }
    
    /**
     * Format data for chart display
     * @param {Object} rawData - Raw API data
     * @param {string} chartType - Type of chart
     * @returns {Array} Formatted chart data
     */
    formatDataForChart(rawData, chartType) {
        if (!rawData) return [];
        
        switch (chartType) {
            case 'providerDistribution':
                // Format provider distribution data
                return this.formatProviderDistribution(rawData);
                
            case 'spendTrend':
                // Format spend trend data
                return this.formatSpendTrend(rawData);
                
            case 'modelDistribution':
                // Format model distribution data
                return this.formatModelDistribution(rawData);
                
            case 'componentDistribution':
                // Format component distribution data
                return this.formatComponentDistribution(rawData);
                
            default:
                console.error(`[BUDGET CHART] Unknown chart type: ${chartType}`);
                return [];
        }
    }
    
    /**
     * Format provider distribution data
     * @param {Object} rawData - Raw API data
     * @returns {Array} Formatted provider distribution data
     */
    formatProviderDistribution(rawData) {
        if (!rawData || !rawData.providers) return [];
        
        return rawData.providers.map(provider => ({
            provider: provider.name,
            amount: provider.total_cost || 0,
            percentage: provider.percentage || 0
        }));
    }
    
    /**
     * Format spend trend data
     * @param {Object} rawData - Raw API data
     * @returns {Array} Formatted spend trend data
     */
    formatSpendTrend(rawData) {
        if (!rawData || !rawData.daily_spend) return [];
        
        return rawData.daily_spend.map(day => ({
            date: new Date(day.date),
            amount: day.cost || 0,
            limit: day.limit || 0
        }));
    }
    
    /**
     * Format model distribution data
     * @param {Object} rawData - Raw API data
     * @returns {Array} Formatted model distribution data
     */
    formatModelDistribution(rawData) {
        if (!rawData || !rawData.models) return [];
        
        return rawData.models.map(model => ({
            provider: model.provider,
            model: model.name,
            amount: model.cost || 0,
            percentage: model.percentage || 0
        }));
    }
    
    /**
     * Format component distribution data
     * @param {Object} rawData - Raw API data
     * @returns {Array} Formatted component distribution data
     */
    formatComponentDistribution(rawData) {
        if (!rawData || !rawData.components) return [];
        
        return rawData.components.map(component => ({
            component: component.name,
            amount: component.cost || 0,
            percentage: component.percentage || 0
        }));
    }
}

// Export as global class
window.BudgetChartUtils = BudgetChartUtils;