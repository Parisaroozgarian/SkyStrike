// Aircraft Systems Threat Simulator JavaScript

class AviationSimulator {
    constructor() {
        this.updateInterval = null;
        this.fleetView = false;
        this.currentAircraft = 'aircraft_1';
        this.init();
    }

    init() {
        // Start automatic updates
        this.startUpdates();
        
        // Bind event listeners
        this.bindEvents();
        
        // Initialize aircraft position
        this.updateAircraftPosition();
        
        console.log('Aviation Threat Simulator initialized');
    }

    bindEvents() {
        // Reset all systems button
        document.getElementById('resetAllBtn').addEventListener('click', () => {
            this.resetSystem('all');
        });

        // Clear log button
        document.getElementById('clearLogBtn').addEventListener('click', () => {
            this.clearLog();
        });

        // Defense system toggles
        document.querySelectorAll('.defense-toggle').forEach(toggle => {
            toggle.addEventListener('change', (e) => {
                const defenseType = e.target.getAttribute('data-defense');
                const enabled = e.target.checked;
                this.toggleDefense(defenseType, enabled);
            });
        });

        // Aircraft selector
        document.getElementById('aircraftSelector').addEventListener('change', (e) => {
            this.selectAircraft(e.target.value);
        });

        // Fleet view toggle
        document.getElementById('fleetViewBtn').addEventListener('click', () => {
            this.toggleFleetView();
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
            const response = await fetch('/api/system_status');
            const data = await response.json();
            
            this.updateSystemDisplays(data.systems);
            this.updateDefenseDisplays(data.defense_systems);
            this.updateThreatLog(data.threat_log);
            this.updateAircraftPosition(data.systems.adsb);
            
        } catch (error) {
            console.error('Error updating system status:', error);
        }
    }

    updateSystemDisplays(systems) {
        // Update ADS-B system
        this.updateSystemCard('adsb', systems.adsb);
        document.getElementById('adsb-lat').textContent = `${systems.adsb.latitude}°`;
        document.getElementById('adsb-lon').textContent = `${systems.adsb.longitude}°`;
        document.getElementById('adsb-alt').textContent = `${systems.adsb.altitude} ft`;
        document.getElementById('adsb-heading').textContent = `${systems.adsb.heading}°`;
        document.getElementById('adsb-speed').textContent = `${systems.adsb.speed} kts`;

        // Update Flight Control system
        this.updateSystemCard('flight-control', systems.flight_control);
        document.getElementById('fc-aileron').textContent = `${systems.flight_control.aileron}°`;
        document.getElementById('fc-elevator').textContent = `${systems.flight_control.elevator}°`;
        document.getElementById('fc-rudder').textContent = `${systems.flight_control.rudder}°`;
        document.getElementById('fc-throttle').textContent = `${systems.flight_control.throttle}%`;

        // Update Communications system
        this.updateSystemCard('communications', systems.communications);
        document.getElementById('comm-frequency').textContent = `${systems.communications.frequency} MHz`;
        document.getElementById('comm-signal').textContent = `${systems.communications.signal_strength}%`;
        document.getElementById('comm-message').textContent = systems.communications.last_message;
    }

    updateSystemCard(systemId, systemData) {
        const card = document.getElementById(`${systemId}-card`);
        const statusBadge = document.getElementById(`${systemId}-status`);
        
        if (systemData.compromised) {
            card.classList.add('compromised');
            statusBadge.textContent = 'COMPROMISED';
            statusBadge.className = 'badge status-badge compromised';
        } else {
            card.classList.remove('compromised');
            statusBadge.textContent = 'Normal';
            statusBadge.className = 'badge status-badge normal';
        }
    }

    updateThreatLog(threats) {
        const threatLog = document.getElementById('threat-log');
        const threatCount = document.getElementById('threat-count');
        
        threatCount.textContent = threats.length;
        
        // Clear existing entries
        threatLog.innerHTML = '';
        
        // Add new entries (showing last 10)
        threats.slice(-10).reverse().forEach(threat => {
            const entry = document.createElement('div');
            entry.className = `threat-entry severity-${threat.severity.toLowerCase()}`;
            
            entry.innerHTML = `
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <strong>${threat.system}</strong>
                        <small class="text-muted d-block">${threat.timestamp}</small>
                    </div>
                    <span class="badge severity-badge-${threat.severity.toLowerCase()}">${threat.severity}</span>
                </div>
                <div class="attack-type">${threat.attack}</div>
                <div class="attack-description">${threat.description}</div>
            `;
            
            threatLog.appendChild(entry);
        });
    }

    updateDefenseDisplays(defenseData) {
        // Update Intrusion Detection System
        const idsStatus = document.getElementById('ids-status');
        const idsMetric = document.getElementById('ids-metric');
        const idsToggle = document.getElementById('ids-toggle');
        
        if (defenseData.intrusion_detection) {
            idsStatus.textContent = defenseData.intrusion_detection.status.replace('_', ' ').toUpperCase();
            idsStatus.className = `defense-status ${defenseData.intrusion_detection.status}`;
            idsMetric.textContent = `Alerts: ${defenseData.intrusion_detection.alerts_triggered}`;
            idsToggle.checked = defenseData.intrusion_detection.enabled;
        }

        // Update Data Validation System
        const validationStatus = document.getElementById('validation-status');
        const validationMetric = document.getElementById('validation-metric');
        const validationToggle = document.getElementById('validation-toggle');
        
        if (defenseData.data_validation) {
            validationStatus.textContent = defenseData.data_validation.status.replace('_', ' ').toUpperCase();
            validationStatus.className = `defense-status ${defenseData.data_validation.status}`;
            validationMetric.textContent = `Failures: ${defenseData.data_validation.validation_failures}`;
            validationToggle.checked = defenseData.data_validation.enabled;
        }

        // Update Encryption System
        const encryptionStatus = document.getElementById('encryption-status');
        const encryptionMetric = document.getElementById('encryption-metric');
        const encryptionToggle = document.getElementById('encryption-toggle');
        
        if (defenseData.encryption) {
            encryptionStatus.textContent = defenseData.encryption.status.replace('_', ' ').toUpperCase();
            encryptionStatus.className = `defense-status ${defenseData.encryption.status}`;
            encryptionMetric.textContent = `Rotations: ${defenseData.encryption.key_rotations}`;
            encryptionToggle.checked = defenseData.encryption.enabled;
        }

        // Update Backup Systems
        const backupStatus = document.getElementById('backup-status');
        const backupMetric = document.getElementById('backup-metric');
        const backupToggle = document.getElementById('backup-toggle');
        
        if (defenseData.backup_systems) {
            backupStatus.textContent = defenseData.backup_systems.status.replace('_', ' ').toUpperCase();
            backupStatus.className = `defense-status ${defenseData.backup_systems.status}`;
            backupMetric.textContent = `Activations: ${defenseData.backup_systems.activations}`;
            backupToggle.checked = defenseData.backup_systems.enabled;
        }
    }

    async toggleDefense(defenseType, enabled) {
        try {
            const response = await fetch('/api/toggle_defense', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    defense_type: defenseType,
                    enabled: enabled
                })
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                // Force immediate update
                await this.updateSystemStatus();
                
                const action = enabled ? 'enabled' : 'disabled';
                this.showNotification(`Defense system ${action}`, 'info');
            } else {
                this.showNotification('Failed to toggle defense system', 'danger');
            }
            
        } catch (error) {
            console.error('Error toggling defense system:', error);
            this.showNotification('Error toggling defense system', 'danger');
        }
    }

    async activateCountermeasure(countermeasure) {
        try {
            // Disable countermeasure buttons temporarily
            const countermeasureButtons = document.querySelectorAll('.countermeasure-btn');
            countermeasureButtons.forEach(btn => btn.disabled = true);
            
            const response = await fetch('/api/activate_countermeasure', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    countermeasure: countermeasure
                })
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                // Force immediate update
                await this.updateSystemStatus();
                
                this.showNotification(`Countermeasure activated: ${countermeasure.replace('_', ' ')}`, 'warning');
            } else {
                this.showNotification('Failed to activate countermeasure', 'danger');
            }
            
        } catch (error) {
            console.error('Error activating countermeasure:', error);
            this.showNotification('Error activating countermeasure', 'danger');
        } finally {
            // Re-enable countermeasure buttons
            const countermeasureButtons = document.querySelectorAll('.countermeasure-btn');
            countermeasureButtons.forEach(btn => btn.disabled = false);
        }
    }

    updateAircraftPosition(adsbData = null) {
        const aircraftIcon = document.getElementById('aircraft-icon');
        const positionText = document.getElementById('grid-position');
        
        if (adsbData) {
            // Calculate position based on coordinates (simplified for demo)
            const lat = adsbData.latitude;
            const lon = adsbData.longitude;
            const heading = adsbData.heading;
            
            // Convert coordinates to grid position (0-100%)
            const x = Math.max(0, Math.min(100, ((lon + 180) / 360) * 100));
            const y = Math.max(0, Math.min(100, ((lat + 90) / 180) * 100));
            
            aircraftIcon.style.left = `${x}%`;
            aircraftIcon.style.top = `${100 - y}%`;
            aircraftIcon.style.transform = `translate(-50%, -50%) rotate(${heading}deg)`;
            
            // Update position text
            positionText.textContent = `${lat.toFixed(4)}°, ${lon.toFixed(4)}°`;
            
            // Add compromised styling if system is compromised
            if (adsbData.compromised) {
                aircraftIcon.classList.add('compromised');
            } else {
                aircraftIcon.classList.remove('compromised');
            }
        }
    }

    async simulateAttack(system, attackType) {
        try {
            // Disable attack buttons temporarily
            const attackButtons = document.querySelectorAll('.attack-btn');
            attackButtons.forEach(btn => btn.disabled = true);
            
            const response = await fetch('/api/simulate_attack', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    system: system,
                    attack_type: attackType
                })
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                // Force immediate update
                await this.updateSystemStatus();
                
                // Show visual feedback
                this.showNotification(`Attack simulated: ${attackType} on ${system}`, 'warning');
            } else {
                this.showNotification('Failed to simulate attack', 'danger');
            }
            
        } catch (error) {
            console.error('Error simulating attack:', error);
            this.showNotification('Error simulating attack', 'danger');
        } finally {
            // Re-enable attack buttons
            const attackButtons = document.querySelectorAll('.attack-btn');
            attackButtons.forEach(btn => btn.disabled = false);
        }
    }

    async resetSystem(system) {
        try {
            const response = await fetch('/api/reset_system', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    system: system
                })
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                // Force immediate update
                await this.updateSystemStatus();
                
                const systemName = system === 'all' ? 'All Systems' : system.replace('_', ' ').toUpperCase();
                this.showNotification(`${systemName} reset successfully`, 'success');
            } else {
                this.showNotification('Failed to reset system', 'danger');
            }
            
        } catch (error) {
            console.error('Error resetting system:', error);
            this.showNotification('Error resetting system', 'danger');
        }
    }

    async clearLog() {
        try {
            const response = await fetch('/api/clear_log', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                // Force immediate update
                await this.updateSystemStatus();
                this.showNotification('Threat log cleared', 'info');
            } else {
                this.showNotification('Failed to clear log', 'danger');
            }
            
        } catch (error) {
            console.error('Error clearing log:', error);
            this.showNotification('Error clearing log', 'danger');
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }

    async updateFleetStatus() {
        try {
            const response = await fetch('/api/fleet_status');
            const data = await response.json();
            
            this.updateFleetDisplay(data.aircraft_fleet);
            this.updateThreatLog(data.threat_log);
            
        } catch (error) {
            console.error('Error updating fleet status:', error);
        }
    }

    updateFleetDisplay(aircraftFleet) {
        const fleetGrid = document.getElementById('fleetGrid');
        fleetGrid.innerHTML = '';

        Object.keys(aircraftFleet).forEach(aircraftId => {
            const aircraft = aircraftFleet[aircraftId];
            const card = document.createElement('div');
            card.className = 'col-md-4 mb-3';
            
            const compromisedSystems = [
                aircraft.adsb.compromised ? 'ADS-B' : null,
                aircraft.flight_control.compromised ? 'Flight Control' : null,
                aircraft.communications.compromised ? 'Communications' : null
            ].filter(Boolean);

            const statusClass = compromisedSystems.length > 0 ? 'border-danger' : 'border-success';
            const statusBadge = compromisedSystems.length > 0 ? 
                `<span class="badge bg-danger">${compromisedSystems.length} Compromised</span>` :
                `<span class="badge bg-success">All Normal</span>`;

            card.innerHTML = `
                <div class="card h-100 ${statusClass}" style="border-width: 2px;">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h6 class="mb-0">${aircraft.callsign}</h6>
                        ${statusBadge}
                    </div>
                    <div class="card-body">
                        <small class="text-muted d-block mb-2">${aircraft.model}</small>
                        <div class="row">
                            <div class="col-6">
                                <small class="d-block">
                                    <strong>Position:</strong><br>
                                    ${aircraft.adsb.latitude.toFixed(2)}°, ${aircraft.adsb.longitude.toFixed(2)}°
                                </small>
                                <small class="d-block">
                                    <strong>Altitude:</strong><br>
                                    ${aircraft.adsb.altitude} ft
                                </small>
                            </div>
                            <div class="col-6">
                                <small class="d-block">
                                    <strong>Speed:</strong><br>
                                    ${aircraft.adsb.speed} kts
                                </small>
                                <small class="d-block">
                                    <strong>Frequency:</strong><br>
                                    ${aircraft.communications.frequency} MHz
                                </small>
                            </div>
                        </div>
                        ${compromisedSystems.length > 0 ? 
                            `<div class="mt-2"><small class="text-danger">Compromised: ${compromisedSystems.join(', ')}</small></div>` : 
                            ''}
                        <div class="mt-3">
                            <button class="btn btn-sm btn-primary w-100" onclick="selectAircraftFromFleet('${aircraftId}')">
                                <i class="fas fa-crosshairs me-1"></i>Select Aircraft
                            </button>
                        </div>
                    </div>
                </div>
            `;
            
            fleetGrid.appendChild(card);
        });
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
            fleetViewBtn.innerHTML = '<i class="fas fa-list me-1"></i>Fleet View';
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
                body: JSON.stringify({
                    aircraft_id: aircraftId
                })
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                this.currentAircraft = aircraftId;
                document.getElementById('aircraftSelector').value = aircraftId;
                
                // Force immediate update
                await this.updateSystemStatus();
                
                this.showNotification(`Selected ${result.message}`, 'info');
            } else {
                this.showNotification('Failed to select aircraft', 'danger');
            }
            
        } catch (error) {
            console.error('Error selecting aircraft:', error);
            this.showNotification('Error selecting aircraft', 'danger');
        }
    }

    async simulateFleetAttack(attackScenario) {
        try {
            const response = await fetch('/api/fleet_attack', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    attack_scenario: attackScenario
                })
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                this.showNotification(`Fleet attack launched: ${result.affected_aircraft.join(', ')} affected`, 'warning');
                
                // If in fleet view, update immediately
                if (this.fleetView) {
                    this.updateFleetStatus();
                } else {
                    this.updateSystemStatus();
                }
            } else {
                this.showNotification('Fleet attack failed', 'danger');
            }
            
        } catch (error) {
            console.error('Error launching fleet attack:', error);
            this.showNotification('Error launching fleet attack', 'danger');
        }
    }
}

// Global functions for onclick handlers
function simulateAttack(system, attackType) {
    window.aviationSimulator.simulateAttack(system, attackType);
}

function resetSystem(system) {
    window.aviationSimulator.resetSystem(system);
}

function activateCountermeasure(countermeasure) {
    window.aviationSimulator.activateCountermeasure(countermeasure);
}

function selectAircraftFromFleet(aircraftId) {
    window.aviationSimulator.selectAircraft(aircraftId);
    window.aviationSimulator.toggleFleetView(); // Switch back to individual view
}

function simulateFleetAttack(attackScenario) {
    window.aviationSimulator.simulateFleetAttack(attackScenario);
}

// Initialize simulator when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.aviationSimulator = new AviationSimulator();
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (window.aviationSimulator) {
        window.aviationSimulator.stopUpdates();
    }
});
