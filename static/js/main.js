// PulseSuperConduit Energy System - Main JavaScript

class PulseSuperConduitApp {
    constructor() {
        this.socket = io();
        this.energyData = [];
        this.maxDataPoints = 100;
        this.init();
    }

    init() {
        this.setupSocketListeners();
        this.setupEventListeners();
        this.setupSliders();
        this.initializeCharts();
        this.loadScenarios();
        this.updateNetworkConfig();
    }

    setupSocketListeners() {
        this.socket.on('connect', () => {
            console.log('Connected to PulseSuperConduit simulation');
        });

        this.socket.on('simulation_update', (data) => {
            this.updateStatus(data);
            this.updateEnergyChart(data);
            this.updateSafetyStatus(data);
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from simulation');
        });
    }

    setupEventListeners() {
        // Start simulation button
        document.getElementById('start-btn').addEventListener('click', () => {
            this.startSimulation();
        });

        // Stop simulation button
        document.getElementById('stop-btn').addEventListener('click', () => {
            this.stopSimulation();
        });

        // Network configuration changes
        ['conduit-length', 'num-conduits', 'active-conduits'].forEach(id => {
            document.getElementById(id).addEventListener('input', () => {
                this.updateNetworkConfig();
            });
        });
    }

    setupSliders() {
        const sliders = [
            { id: 'conduit-length', valueId: 'conduit-length-value' },
            { id: 'num-conduits', valueId: 'num-conduits-value' },
            { id: 'active-conduits', valueId: 'active-conduits-value' },
            { id: 'spin-duration', valueId: 'spin-duration-value' }
        ];

        sliders.forEach(slider => {
            const element = document.getElementById(slider.id);
            const valueElement = document.getElementById(slider.valueId);
            
            element.addEventListener('input', (e) => {
                valueElement.textContent = e.target.value;
                
                // Update active conduits max value based on num-conduits
                if (slider.id === 'num-conduits') {
                    const activeConduits = document.getElementById('active-conduits');
                    activeConduits.max = parseInt(e.target.value) - 1;
                    if (parseInt(activeConduits.value) >= parseInt(e.target.value)) {
                        activeConduits.value = parseInt(e.target.value) - 1;
                        document.getElementById('active-conduits-value').textContent = activeConduits.value;
                    }
                }
            });
        });
    }

    initializeCharts() {
        // Energy Flow Chart
        this.initEnergyChart();
        
        // Performance Chart
        this.initPerformanceChart();
    }

    initEnergyChart() {
        const layout = {
            title: {
                text: 'Energy Flow Over Time',
                font: { color: '#f1f5f9' }
            },
            xaxis: {
                title: 'Time',
                color: '#94a3b8',
                gridcolor: '#334155'
            },
            yaxis: {
                title: 'Power (GW)',
                color: '#94a3b8',
                gridcolor: '#334155'
            },
            plot_bgcolor: '#0f172a',
            paper_bgcolor: '#0f172a',
            font: { color: '#f1f5f9' }
        };

        const trace = {
            x: [],
            y: [],
            type: 'scatter',
            mode: 'lines',
            name: 'Power Output',
            line: { color: '#10b981', width: 3 }
        };

        Plotly.newPlot('energy-flow-chart', [trace], layout, {
            responsive: true,
            displayModeBar: false
        });
    }

    initPerformanceChart() {
        const layout = {
            title: {
                text: 'System Performance Metrics',
                font: { color: '#f1f5f9' }
            },
            plot_bgcolor: '#0f172a',
            paper_bgcolor: '#0f172a',
            font: { color: '#f1f5f9' }
        };

        // Empty chart initially
        Plotly.newPlot('performance-chart', [], layout, {
            responsive: true,
            displayModeBar: false
        });
    }

    async loadScenarios() {
        try {
            const response = await fetch('/api/scenarios');
            const scenarios = await response.json();
            
            // Update performance chart with scenario data
            this.updatePerformanceChart(scenarios);
        } catch (error) {
            console.error('Error loading scenarios:', error);
        }
    }

    updatePerformanceChart(scenarios) {
        const names = Object.keys(scenarios);
        const dailyEnergy = names.map(name => scenarios[name].daily_energy);
        const netEnergy = names.map(name => scenarios[name].net_energy);
        const efficiencyRatio = names.map(name => scenarios[name].efficiency_ratio);

        const trace1 = {
            x: names,
            y: dailyEnergy,
            type: 'bar',
            name: 'Daily Energy (GWh)',
            marker: { color: '#3b82f6' }
        };

        const trace2 = {
            x: names,
            y: netEnergy,
            type: 'bar',
            name: 'Net Energy (GWh)',
            marker: { color: '#10b981' }
        };

        const layout = {
            title: {
                text: 'Energy Generation by Scenario',
                font: { color: '#f1f5f9' }
            },
            xaxis: {
                title: 'Scenarios',
                color: '#94a3b8',
                gridcolor: '#334155'
            },
            yaxis: {
                title: 'Energy (GWh)',
                color: '#94a3b8',
                gridcolor: '#334155'
            },
            plot_bgcolor: '#0f172a',
            paper_bgcolor: '#0f172a',
            font: { color: '#f1f5f9' },
            barmode: 'group'
        };

        Plotly.newPlot('performance-chart', [trace1, trace2], layout, {
            responsive: true,
            displayModeBar: false
        });
    }

    async startSimulation() {
        const scenario = document.getElementById('scenario-select').value;
        const duration = parseInt(document.getElementById('spin-duration').value);

        try {
            const response = await fetch('/api/start_simulation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ scenario, duration })
            });

            const result = await response.json();
            
            if (result.status === 'started') {
                document.getElementById('system-status').textContent = '🟢 ACTIVE';
                document.getElementById('system-status').classList.add('pulse');
                
                // Disable start button, enable stop button
                document.getElementById('start-btn').disabled = true;
                document.getElementById('stop-btn').disabled = false;
            }
        } catch (error) {
            console.error('Error starting simulation:', error);
        }
    }

    async stopSimulation() {
        try {
            const response = await fetch('/api/stop_simulation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const result = await response.json();
            
            if (result.status === 'stopped') {
                document.getElementById('system-status').textContent = '🔴 STANDBY';
                document.getElementById('system-status').classList.remove('pulse');
                
                // Enable start button, disable stop button
                document.getElementById('start-btn').disabled = false;
                document.getElementById('stop-btn').disabled = true;
            }
        } catch (error) {
            console.error('Error stopping simulation:', error);
        }
    }

    updateStatus(data) {
        // Update RPM with animation
        const rpmElement = document.getElementById('core-rpm');
        const currentRpm = parseInt(rpmElement.textContent.replace(/,/g, ''));
        const targetRpm = Math.round(data.rpm);
        
        if (currentRpm !== targetRpm) {
            this.animateNumber(rpmElement, currentRpm, targetRpm, (val) => val.toLocaleString());
        }

        // Update power output
        document.getElementById('power-output').textContent = `${data.power.toFixed(1)} GW`;
        
        // Update kinetic energy
        document.getElementById('kinetic-energy').textContent = `${Math.round(data.kinetic_energy)} GJ`;
    }

    updateEnergyChart(data) {
        const now = new Date();
        this.energyData.push({
            time: now,
            power: data.power
        });

        // Keep only last 100 data points
        if (this.energyData.length > this.maxDataPoints) {
            this.energyData.shift();
        }

        const times = this.energyData.map(d => d.time);
        const powers = this.energyData.map(d => d.power);

        const update = {
            x: [times],
            y: [powers]
        };

        Plotly.restyle('energy-flow-chart', update, [0]);
    }

    updateSafetyStatus(data) {
        const safetyStatus = data.safety_status;
        const safetyIndicator = document.getElementById('safety-indicator');
        const safetyMessage = document.getElementById('safety-message');
        const materialStress = document.getElementById('material-stress');
        const riskLevel = document.getElementById('risk-level');

        // Update safety indicator
        let statusColor = '';
        switch (safetyStatus.level) {
            case 'green':
                statusColor = '🟢';
                break;
            case 'yellow':
                statusColor = '🟡';
                break;
            case 'orange':
                statusColor = '🟠';
                break;
            case 'red':
                statusColor = '🔴';
                break;
        }

        safetyIndicator.textContent = `${statusColor} ${safetyStatus.status}`;
        safetyMessage.textContent = safetyStatus.message;
        materialStress.textContent = `${data.material_stress.toFixed(1)}%`;
        riskLevel.textContent = safetyStatus.status;
    }

    async updateNetworkConfig() {
        const conduitLength = parseInt(document.getElementById('conduit-length').value);
        const numConduits = parseInt(document.getElementById('num-conduits').value);
        const activeConduits = parseInt(document.getElementById('active-conduits').value);

        try {
            const response = await fetch('/api/network_config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    conduit_length: conduitLength,
                    num_conduits: numConduits,
                    active_conduits: activeConduits
                })
            });

            const result = await response.json();
            
            // Update network status display
            document.getElementById('active-conduits-status').textContent = activeConduits;
            document.getElementById('standby-conduits-status').textContent = result.standby_conduits;
            document.getElementById('redundancy-factor').textContent = `${result.redundancy_factor.toFixed(1)}x`;
            document.getElementById('total-capacity').textContent = `${Math.round(result.total_capacity)} GWh`;
            
        } catch (error) {
            console.error('Error updating network config:', error);
        }
    }

    animateNumber(element, start, end, formatter) {
        const duration = 1000; // 1 second
        const startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function for smooth animation
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const current = start + (end - start) * easeOutQuart;
            
            element.textContent = formatter ? formatter(current) : Math.round(current);
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PulseSuperConduitApp();
});

// Handle window resize for responsive charts
window.addEventListener('resize', () => {
    Plotly.Plots.resize('energy-flow-chart');
    Plotly.Plots.resize('performance-chart');
});