/**
 * Professional Aviation Threat Simulator - Master's Level JavaScript
 * Advanced client-side functionality with professional features
 */

class ProfessionalSimulator {
    constructor() {
        this.updateInterval = null;
        this.fleetView = false;
        this.currentAircraft = 'aircraft_1';
        this.threatChart = null;
        this.lastUpdateTime = null;
        this.connectionStatus = 'connected';
        this.analytics = {
            totalAttacks: 0,
            defenseActivations: 0,
            systemUptime: 100
        };
    }

    initialize() {
        this.setupEventListeners();
        this.initializeCharts();
        this.startUpdates();
        this.initializeTooltips();
        this.setupKeyboardShortcuts();
        console.log('Professional Aviation Threat Simulator initialized');
    }

    setupEventListeners() {
        // Aircraft selection
        const aircraftSelector = document.getElementById('aircraftSelector');
        if (aircraftSelector) {
            aircraftSelector.addEventListener('change', (e) => {
                this.selectAircraft(e.target.value);
            });
        }

        // Fleet view toggle
        const fleetViewBtn = document.getElementById('fleetViewBtn');
        if (fleetViewBtn) {
            fleetViewBtn.addEventListener('click', () => {
                this.toggleFleetView();
            });
        }

        // System controls
        const resetAllBtn = document.getElementById('resetAllBtn');
        if (resetAllBtn) {
            resetAllBtn.addEventListener('click', () => {
                this.resetAllSystems();
            });
        }

        const clearLogBtn = document.getElementById('clearLogBtn');
        if (clearLogBtn) {
            clearLogBtn.addEventListener('click', () => {
                this.clearThreatLog();
            });
        }

        // Connection status monitoring
        window.addEventListener('online', () => {
            this.updateConnectionStatus('connected');
        });

        window.addEventListener('offline', () => {
            this.updateConnectionStatus('disconnected');
        });
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + R: Reset all systems
            if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
                e.preventDefault();
                this.resetAllSystems();
            }
            
            // Ctrl/Cmd + F: Toggle fleet view
            if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
                e.preventDefault();
                this.toggleFleetView();
            }
            
            // Ctrl/Cmd + L: Clear log
            if ((e.ctrlKey || e.metaKey) && e.key === 'l') {
                e.preventDefault();
                this.clearThreatLog();
            }
        });
    }

    initializeCharts() {
        const chartCanvas = document.getElementById('fleetThreatChart');
        if (chartCanvas) {
            const ctx = chartCanvas.getContext('2d');
            this.threatChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Threat Level',
                        data: [],
                        borderColor: '#dc3545',
                        backgroundColor: 'rgba(220, 53, 69, 0.1)',
                        tension: 0.4,
                        fill: true
                    }, {
                        label: 'Defense Response',
                        data: [],
                        borderColor: '#28a745',
                        backgroundColor: 'rgba(40, 167, 69, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: {
                                color: '#ffffff'
                            }
                        }
                    },
                    scales: {
                        x: {
                            ticks: { color: '#ffffff' },
                            grid: { color: 'rgba(255, 255, 255, 0.1)' }
                        },
                        y: {
                            ticks: { color: '#ffffff' },
                            grid: { color: 'rgba(255, 255, 255, 0.1)' }
                        }
                    }
                }
            });
        }
    }

    initializeTooltips() {
        // Initialize Bootstrap tooltips
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    startUpdates() {
        // Update system status every 2 seconds
        this.updateInterval = setInterval(() => {
            if (this.fleetView) {
                this.updateFleetStatus();
            } else {
                this.updateSystemStatus();
            }
            this.updateConnectionIndicator();
        }, 2000);
    }

    stopUpdates() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
            this.updateInterval = null;
        }
    }

    async updateSystemStatus() {
        try {
            const response = await fetch('/api/system_status', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.updateSystemDisplays(data.systems);
                this.updateDefenseDisplays(data.defense_systems);
                this.updateThreatLog(data.threat_log);
                this.updateSignalStrength(data.systems);
                this.lastUpdateTime = new Date();
                this.updateConnectionStatus('connected');
            } else {
                console.warn('API returned error status:', data.message);
                this.updateConnectionStatus('error');
            }
            
        } catch (error) {
            console.error('Error updating system status:', error);
            this.updateConnectionStatus('error');
        }
    }

    async updateFleetStatus() {
        try {
            const response = await fetch('/api/fleet_status');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.updateFleetGrid(data.aircraft);
                this.updateThreatChart(data.threat_log);
                this.updateFleetAnalytics(data.analytics);
                this.lastUpdateTime = new Date();
                this.updateConnectionStatus('connected');
            }
            
        } catch (error) {
            console.error('Error updating fleet status:', error);
            this.updateConnectionStatus('error');
        }
    }

    updateSystemDisplays(systems) {
        // Update ADS-B system
        if (systems.adsb) {
            this.updateElement('adsb-position', `${systems.adsb.latitude.toFixed(4)}, ${systems.adsb.longitude.toFixed(4)}`);
            this.updateElement('adsb-alt', `${systems.adsb.altitude} ft`);
            this.updateElement('adsb-heading', `${systems.adsb.heading}°`);
            this.updateElement('adsb-speed', `${systems.adsb.speed} kts`);
            this.updateSystemStatus('adsb', systems.adsb.status, systems.adsb.compromised);
        }

        // Update Flight Control system
        if (systems.flight_control) {
            this.updateElement('fc-aileron', `${systems.flight_control.aileron}°`);
            this.updateElement('fc-elevator', `${systems.flight_control.elevator}°`);
            this.updateElement('fc-rudder', `${systems.flight_control.rudder}°`);
            this.updateElement('fc-throttle', `${systems.flight_control.throttle}%`);
            this.updateSystemStatus('flight-control', systems.flight_control.status, systems.flight_control.compromised);
        }

        // Update Communications system
        if (systems.communications) {
            this.updateElement('comm-frequency', `${systems.communications.frequency} MHz`);
            this.updateElement('comm-signal-strength', `${systems.communications.signal_strength}%`);
            this.updateElement('comm-message', systems.communications.last_message);
            this.updateSystemStatus('communications', systems.communications.status, systems.communications.compromised);
        }
    }

    updateDefenseDisplays(defenseSystems) {
        Object.entries(defenseSystems).forEach(([name, system]) => {
            const defenseElement = document.getElementById(`defense-${name}`);
            if (defenseElement) {
                const statusBadge = defenseElement.querySelector('.defense-badge');
                const alertsSpan = defenseElement.querySelector('.defense-alerts');
                const activationsSpan = defenseElement.querySelector('.defense-activations');
                
                if (statusBadge) {
                    statusBadge.textContent = system.status.charAt(0).toUpperCase() + system.status.slice(1);
                    statusBadge.setAttribute('data-status', system.status);
                }
                
                if (alertsSpan) alertsSpan.textContent = system.alerts_triggered;
                if (activationsSpan) activationsSpan.textContent = system.activations;
            }
        });
    }

    updateThreatLog(threats) {
        const threatLog = document.getElementById('threat-log');
        const threatCount = document.getElementById('threat-count');
        
        if (threatCount) threatCount.textContent = threats.length;
        
        if (threatLog) {
            threatLog.innerHTML = '';
            
            threats.slice(-15).reverse().forEach(threat => {
                const entry = document.createElement('div');
                entry.className = `threat-entry severity-${threat.severity.toLowerCase()} slide-in`;
                
                entry.innerHTML = `
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="threat-info">
                            <div class="threat-system">${threat.system}</div>
                            <div class="threat-timestamp">${threat.timestamp}</div>
                        </div>
                        <span class="badge severity-badge-${threat.severity.toLowerCase()}">${threat.severity}</span>
                    </div>
                    <div class="threat-attack">${threat.attack}</div>
                    <div class="threat-description">${threat.description}</div>
                `;
                
                threatLog.appendChild(entry);
            });
        }
    }

    updateSignalStrength(systems) {
        // Update ADS-B signal strength
        if (systems.adsb) {
            const adsbSignal = document.getElementById('adsb-signal');
            if (adsbSignal) {
                this.setSignalStrength(adsbSignal, systems.adsb.compromised ? 25 : 100);
            }
        }

        // Update Communications signal strength
        if (systems.communications) {
            const commSignal = document.getElementById('comm-signal');
            if (commSignal) {
                this.setSignalStrength(commSignal, systems.communications.signal_strength);
            }
        }
    }

    setSignalStrength(element, strength) {
        element.className = 'signal-strength';
        if (strength < 30) {
            element.classList.add('weak');
        } else if (strength < 70) {
            element.classList.add('moderate');
        }
    }

    updateSystemStatus(systemId, status, compromised) {
        const card = document.getElementById(`${systemId}-card`);
        const statusBadge = document.getElementById(`${systemId}-status`);
        
        if (card && statusBadge) {
            // Update card appearance
            card.className = card.className.replace(/\b(success-state|error-state|loading)\b/g, '');
            
            if (compromised) {
                card.classList.add('error-state');
                statusBadge.textContent = 'Compromised';
                statusBadge.className = 'status-badge badge bg-danger';
            } else {
                card.classList.add('success-state');
                statusBadge.textContent = 'Normal';
                statusBadge.className = 'status-badge badge bg-success';
            }
        }
    }

    updateFleetGrid(aircraft) {
        const fleetGrid = document.getElementById('fleetGrid');
        if (!fleetGrid) return;
        
        fleetGrid.innerHTML = '';
        
        Object.entries(aircraft).forEach(([aircraftId, aircraftData]) => {
            const col = document.createElement('div');
            col.className = 'col-md-4 mb-3';
            
            const compromisedCount = [
                aircraftData.adsb.compromised,
                aircraftData.flight_control.compromised,
                aircraftData.communications.compromised
            ].filter(Boolean).length;
            
            const statusClass = compromisedCount === 0 ? 'success-state' : 'error-state';
            const threatLevel = compromisedCount === 0 ? 'LOW' : 
                               compromisedCount === 1 ? 'MEDIUM' : 
                               compromisedCount === 2 ? 'HIGH' : 'CRITICAL';
            
            col.innerHTML = `
                <div class="card professional-card ${statusClass}">
                    <div class="card-header">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <h6 class="mb-0">${aircraftData.callsign}</h6>
                                <small class="text-muted">${aircraftData.model}</small>
                            </div>
                            <span class="badge bg-${threatLevel === 'LOW' ? 'success' : threatLevel === 'MEDIUM' ? 'warning' : 'danger'}">${threatLevel}</span>
                        </div>
                    </div>
                    <div class="card-body">
                        <div class="row text-center">
                            <div class="col-4">
                                <div class="system-status ${aircraftData.adsb.compromised ? 'compromised' : 'normal'}">
                                    <i class="fas fa-satellite"></i>
                                    <div class="small">ADS-B</div>
                                </div>
                            </div>
                            <div class="col-4">
                                <div class="system-status ${aircraftData.flight_control.compromised ? 'compromised' : 'normal'}">
                                    <i class="fas fa-cogs"></i>
                                    <div class="small">Flight</div>
                                </div>
                            </div>
                            <div class="col-4">
                                <div class="system-status ${aircraftData.communications.compromised ? 'compromised' : 'normal'}">
                                    <i class="fas fa-broadcast-tower"></i>
                                    <div class="small">Comm</div>
                                </div>
                            </div>
                        </div>
                        <button class="btn btn-sm btn-outline-primary w-100 mt-2" 
                                onclick="professionalSimulator.selectAircraftFromFleet('${aircraftId}')">
                            <i class="fas fa-crosshairs me-1"></i>Focus Aircraft
                        </button>
                    </div>
                </div>
            `;
            
            fleetGrid.appendChild(col);
        });
    }

    updateThreatChart(threats) {
        if (!this.threatChart) return;
        
        const now = new Date();
        const timeLabel = now.toLocaleTimeString();
        
        // Calculate threat level (0-100)
        const recentThreats = threats.slice(-10);
        const threatLevel = Math.min(recentThreats.length * 10, 100);
        
        // Calculate defense response (0-100)
        const defenseResponses = recentThreats.filter(t => t.system === 'Defense Systems').length;
        const defenseLevel = Math.min(defenseResponses * 20, 100);
        
        // Add new data point
        this.threatChart.data.labels.push(timeLabel);
        this.threatChart.data.datasets[0].data.push(threatLevel);
        this.threatChart.data.datasets[1].data.push(defenseLevel);
        
        // Keep only last 20 data points
        if (this.threatChart.data.labels.length > 20) {
            this.threatChart.data.labels.shift();
            this.threatChart.data.datasets[0].data.shift();
            this.threatChart.data.datasets[1].data.shift();
        }
        
        this.threatChart.update('none');
    }

    updateFleetAnalytics(analytics) {
        if (analytics) {
            this.updateElement('system-uptime', `${analytics.uptime_percentage || 100}%`);
            this.updateElement('active-threats', analytics.total_attacks_simulated || 0);
            this.analytics = { ...this.analytics, ...analytics };
        }
    }

    updateConnectionStatus(status) {
        this.connectionStatus = status;
        // Could add visual connection indicator if needed
    }

    updateConnectionIndicator() {
        const now = new Date();
        if (this.lastUpdateTime && (now - this.lastUpdateTime) > 10000) {
            this.updateConnectionStatus('stale');
        }
    }

    toggleFleetView() {
        this.fleetView = !this.fleetView;
        const fleetOverview = document.getElementById('fleetOverview');
        const individualView = document.getElementById('individualView');
        const fleetViewBtn = document.getElementById('fleetViewBtn');
        
        if (this.fleetView) {
            fleetOverview.style.display = 'block';
            individualView.style.display = 'none';
            fleetViewBtn.innerHTML = '<i class="fas fa-plane me-1"></i>Individual View';
            this.updateFleetStatus();
        } else {
            fleetOverview.style.display = 'none';
            individualView.style.display = 'block';
            fleetViewBtn.innerHTML = '<i class="fas fa-list me-1"></i>Fleet Overview';
            this.updateSystemStatus();
        }
    }

    async selectAircraft(aircraftId) {
        try {
            const response = await fetch('/api/select_aircraft', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ aircraft_id: aircraftId })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.currentAircraft = aircraftId;
                this.showNotification('Aircraft selected: ' + data.message, 'success');
                this.updateSystemStatus();
            } else {
                this.showNotification('Failed to select aircraft: ' + data.message, 'error');
            }
            
        } catch (error) {
            console.error('Error selecting aircraft:', error);
            this.showNotification('Error selecting aircraft', 'error');
        }
    }

    selectAircraftFromFleet(aircraftId) {
        this.selectAircraft(aircraftId);
        this.toggleFleetView(); // Switch back to individual view
    }

    async resetAllSystems() {
        if (!confirm('Are you sure you want to reset all systems across the fleet?')) {
            return;
        }
        
        try {
            const response = await fetch('/api/reset_all', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.showNotification('All systems reset successfully', 'success');
                this.updateSystemStatus();
            } else {
                this.showNotification('Failed to reset systems: ' + data.message, 'error');
            }
            
        } catch (error) {
            console.error('Error resetting systems:', error);
            this.showNotification('Error resetting systems', 'error');
        }
    }

    async clearThreatLog() {
        if (!confirm('Are you sure you want to clear the threat log?')) {
            return;
        }
        
        try {
            const response = await fetch('/api/clear_log', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.showNotification('Threat log cleared', 'success');
                this.updateSystemStatus();
            } else {
                this.showNotification('Failed to clear log: ' + data.message, 'error');
            }
            
        } catch (error) {
            console.error('Error clearing log:', error);
            this.showNotification('Error clearing log', 'error');
        }
    }

    async analyzeThreats() {
        try {
            const response = await fetch('/api/threat_analysis');
            const data = await response.json();
            
            if (data.status === 'success') {
                this.showThreatAnalysis(data.analysis);
            } else {
                this.showNotification('Threat analysis failed: ' + data.message, 'error');
            }
            
        } catch (error) {
            console.error('Error analyzing threats:', error);
            this.showNotification('Error performing threat analysis', 'error');
        }
    }

    async activateCountermeasure(countermeasure) {
        try {
            const response = await fetch('/api/activate_countermeasure', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin',
                body: JSON.stringify({
                    countermeasure: countermeasure,
                    aircraft_id: this.currentAircraft
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.showNotification(`Countermeasure activated: ${countermeasure}`, 'success');
                this.updateSystemStatus();
            } else {
                this.showNotification(`Countermeasure failed: ${data.message}`, 'error');
            }
            
        } catch (error) {
            console.error('Error activating countermeasure:', error);
            this.showNotification('Error activating countermeasure', 'error');
        }
    }

    async simulateFleetAttack(attackScenario) {
        try {
            const response = await fetch('/api/fleet_attack', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin',
                body: JSON.stringify({
                    attack_scenario: attackScenario
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.showNotification(`Fleet attack executed: ${attackScenario}`, 'warning');
                if (this.fleetView) {
                    this.updateFleetStatus();
                } else {
                    this.updateSystemStatus();
                }
            } else {
                this.showNotification(`Fleet attack failed: ${data.message}`, 'error');
            }
            
        } catch (error) {
            console.error('Error executing fleet attack:', error);
            this.showNotification('Error executing fleet attack', 'error');
        }
    }

    showThreatAnalysis(analysis) {
        const modal = new bootstrap.Modal(document.createElement('div'));
        // Could implement a professional threat analysis modal here
        this.showNotification(`Threat Level: ${analysis.threat_level} - ${analysis.recommendations.length} recommendations`, 'info');
    }

    showNotification(message, type = 'info') {
        // Create professional toast notification
        const toast = document.createElement('div');
        toast.className = `alert alert-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info'} position-fixed`;
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        toast.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
                ${message}
                <button type="button" class="btn-close ms-auto" onclick="this.parentElement.parentElement.remove()"></button>
            </div>
        `;
        
        document.body.appendChild(toast);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (toast.parentElement) {
                toast.remove();
            }
        }, 5000);
    }

    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }
}

// Global functions for template compatibility
async function simulateAttack(system, attackType) {
    try {
        const simulator = window.professionalSimulator || professionalSimulator;
        const response = await fetch('/api/simulate_attack', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin',
            body: JSON.stringify({
                system: system,
                attack_type: attackType,
                aircraft_id: simulator ? simulator.currentAircraft : 'aircraft_1'
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.status === 'success') {
            if (simulator) {
                simulator.showNotification(`Attack executed: ${attackType} on ${data.aircraft}`, 'warning');
                // Trigger immediate update
                simulator.updateSystemStatus();
            }
        } else {
            if (simulator) {
                simulator.showNotification(`Attack failed: ${data.message}`, 'error');
            }
        }
        
    } catch (error) {
        console.error('Error simulating attack:', error);
        const simulator = window.professionalSimulator || professionalSimulator;
        if (simulator) {
            simulator.showNotification('Error simulating attack', 'error');
        }
    }
}

async function resetSystem(system) {
    try {
        const simulator = window.professionalSimulator || professionalSimulator;
        const response = await fetch('/api/reset_system', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin',
            body: JSON.stringify({
                system: system,
                aircraft_id: simulator ? simulator.currentAircraft : 'aircraft_1'
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (data.status === 'success') {
            if (simulator) {
                simulator.showNotification(`${system} system reset successfully`, 'success');
                // Trigger immediate update
                simulator.updateSystemStatus();
            }
        } else {
            if (simulator) {
                simulator.showNotification(`Reset failed: ${data.message}`, 'error');
            }
        }
        
    } catch (error) {
        console.error('Error resetting system:', error);
        const simulator = window.professionalSimulator || professionalSimulator;
        if (simulator) {
            simulator.showNotification('Error resetting system', 'error');
        }
    }
}

async function analyzeThreats() {
    const simulator = window.professionalSimulator || professionalSimulator;
    if (simulator) {
        await simulator.analyzeThreats();
    }
}

// Additional global functions for template compatibility
async function activateCountermeasure(countermeasure) {
    const simulator = window.professionalSimulator || professionalSimulator;
    if (simulator) {
        await simulator.activateCountermeasure(countermeasure);
    }
}

function selectAircraftFromFleet(aircraftId) {
    const simulator = window.professionalSimulator || professionalSimulator;
    if (simulator) {
        simulator.selectAircraft(aircraftId);
        simulator.toggleFleetView(); // Switch back to individual view
    }
}

async function simulateFleetAttack(attackScenario) {
    const simulator = window.professionalSimulator || professionalSimulator;
    if (simulator) {
        await simulator.simulateFleetAttack(attackScenario);
    }
}

// Global instance
let professionalSimulator;