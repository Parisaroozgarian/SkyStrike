// Aircraft Systems Threat Simulator JavaScript

class AviationSimulator {
    constructor() {
        this.updateInterval = null;
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
    }

    startUpdates() {
        // Update system status every 2 seconds
        this.updateInterval = setInterval(() => {
            this.updateSystemStatus();
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
}

// Global functions for onclick handlers
function simulateAttack(system, attackType) {
    window.aviationSimulator.simulateAttack(system, attackType);
}

function resetSystem(system) {
    window.aviationSimulator.resetSystem(system);
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
