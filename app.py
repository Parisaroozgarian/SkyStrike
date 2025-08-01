import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify
import logging

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "aviation_simulator_secret_key")

# System states storage
system_states = {
    "adsb": {
        "status": "normal",
        "latitude": 40.7128,
        "longitude": -74.0060,
        "altitude": 35000,
        "heading": 90,
        "speed": 450,
        "compromised": False
    },
    "flight_control": {
        "status": "normal",
        "aileron": 0,
        "elevator": 0,
        "rudder": 0,
        "throttle": 75,
        "compromised": False
    },
    "communications": {
        "status": "normal",
        "frequency": 121.5,
        "last_message": "All systems nominal",
        "signal_strength": 85,
        "compromised": False
    }
}

# Defense system states
defense_systems = {
    "intrusion_detection": {
        "status": "active",
        "enabled": True,
        "alerts_triggered": 0,
        "last_alert": None
    },
    "data_validation": {
        "status": "active", 
        "enabled": True,
        "validation_failures": 0,
        "last_validation": None
    },
    "encryption": {
        "status": "active",
        "enabled": True,
        "key_rotations": 0,
        "last_rotation": None
    },
    "backup_systems": {
        "status": "standby",
        "enabled": True,
        "activations": 0,
        "last_activation": None
    }
}

# Threat log storage
threat_log = []

def trigger_defense_systems(system, attack_type, timestamp):
    """Trigger appropriate defense mechanisms based on the attack"""
    
    # Intrusion Detection System
    if defense_systems['intrusion_detection']['enabled']:
        defense_systems['intrusion_detection']['alerts_triggered'] += 1
        defense_systems['intrusion_detection']['last_alert'] = timestamp
        defense_systems['intrusion_detection']['status'] = 'alert'
        
        threat_log.append({
            'timestamp': timestamp,
            'system': 'Defense Systems',
            'attack': 'Intrusion Detection Alert',
            'description': f'IDS detected {attack_type} attack on {system} system',
            'severity': 'Info'
        })
    
    # Data Validation System
    if defense_systems['data_validation']['enabled'] and 'spoof' in attack_type:
        defense_systems['data_validation']['validation_failures'] += 1
        defense_systems['data_validation']['last_validation'] = timestamp
        defense_systems['data_validation']['status'] = 'validating'
        
        threat_log.append({
            'timestamp': timestamp,
            'system': 'Defense Systems',
            'attack': 'Data Validation Check',
            'description': f'Data validation system flagged suspicious {system} data',
            'severity': 'Info'
        })
    
    # Encryption System Response
    if defense_systems['encryption']['enabled'] and 'mitm' in attack_type:
        defense_systems['encryption']['key_rotations'] += 1
        defense_systems['encryption']['last_rotation'] = timestamp
        defense_systems['encryption']['status'] = 'rotating_keys'
        
        threat_log.append({
            'timestamp': timestamp,
            'system': 'Defense Systems',
            'attack': 'Emergency Key Rotation',
            'description': f'Encryption keys rotated due to detected man-in-the-middle attack',
            'severity': 'Info'
        })
    
    # Backup Systems Activation
    if defense_systems['backup_systems']['enabled'] and attack_type in ['jam_inputs', 'freeze_controls', 'jam_radio']:
        defense_systems['backup_systems']['activations'] += 1
        defense_systems['backup_systems']['last_activation'] = timestamp
        defense_systems['backup_systems']['status'] = 'active'
        
        threat_log.append({
            'timestamp': timestamp,
            'system': 'Defense Systems',
            'attack': 'Backup System Activation',
            'description': f'Backup systems activated due to {system} compromise',
            'severity': 'Info'
        })

@app.route('/')
def index():
    """Main dashboard route"""
    return render_template('index.html', 
                         system_states=system_states, 
                         threat_log=threat_log)

@app.route('/api/system_status')
def get_system_status():
    """API endpoint to get current system status"""
    return jsonify({
        'systems': system_states,
        'defense_systems': defense_systems,
        'threat_log': threat_log[-10:]  # Last 10 entries
    })

@app.route('/api/simulate_attack', methods=['POST'])
def simulate_attack():
    """API endpoint to simulate cyber attacks"""
    data = request.get_json()
    system = data.get('system')
    attack_type = data.get('attack_type')
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if system == 'adsb':
        if attack_type == 'spoof_location':
            system_states['adsb']['latitude'] = 51.5074  # London coordinates
            system_states['adsb']['longitude'] = -0.1278
            system_states['adsb']['status'] = 'compromised'
            system_states['adsb']['compromised'] = True
            
            threat_log.append({
                'timestamp': timestamp,
                'system': 'ADS-B',
                'attack': 'Location Spoofing',
                'description': 'Aircraft location spoofed to London coordinates',
                'severity': 'High'
            })
            
        elif attack_type == 'spoof_altitude':
            system_states['adsb']['altitude'] = 5000  # Dangerous low altitude
            system_states['adsb']['status'] = 'compromised'
            system_states['adsb']['compromised'] = True
            
            threat_log.append({
                'timestamp': timestamp,
                'system': 'ADS-B',
                'attack': 'Altitude Spoofing',
                'description': 'Aircraft altitude spoofed to dangerous low level',
                'severity': 'Critical'
            })
            
        elif attack_type == 'mitm_adsb':
            # Man-in-the-middle attack on ADS-B data
            original_lat = system_states['adsb']['latitude']
            original_lon = system_states['adsb']['longitude']
            system_states['adsb']['latitude'] = original_lat + 0.5  # Slight position shift
            system_states['adsb']['longitude'] = original_lon + 0.5
            system_states['adsb']['heading'] = (system_states['adsb']['heading'] + 45) % 360
            system_states['adsb']['status'] = 'compromised'
            system_states['adsb']['compromised'] = True
            
            threat_log.append({
                'timestamp': timestamp,
                'system': 'ADS-B',
                'attack': 'Man-in-the-Middle',
                'description': 'ADS-B transponder compromised - intercepting and modifying position data',
                'severity': 'Critical'
            })
            
        elif attack_type == 'replay_adsb':
            # Replay attack using old position data
            system_states['adsb']['latitude'] = 40.7128  # NYC coordinates (old data)
            system_states['adsb']['longitude'] = -74.0060
            system_states['adsb']['altitude'] = 25000
            system_states['adsb']['heading'] = 270
            system_states['adsb']['speed'] = 350
            system_states['adsb']['status'] = 'compromised'
            system_states['adsb']['compromised'] = True
            
            threat_log.append({
                'timestamp': timestamp,
                'system': 'ADS-B',
                'attack': 'Replay Attack',
                'description': 'Replaying old ADS-B transmissions - aircraft appears at previous location',
                'severity': 'High'
            })
    
    elif system == 'flight_control':
        if attack_type == 'jam_inputs':
            system_states['flight_control']['aileron'] = -45  # Extreme bank
            system_states['flight_control']['elevator'] = 30  # Nose up
            system_states['flight_control']['status'] = 'compromised'
            system_states['flight_control']['compromised'] = True
            
            threat_log.append({
                'timestamp': timestamp,
                'system': 'Flight Control',
                'attack': 'Control Input Jamming',
                'description': 'Flight control inputs jammed with extreme values',
                'severity': 'Critical'
            })
            
        elif attack_type == 'freeze_controls':
            # Controls frozen at current position
            system_states['flight_control']['status'] = 'compromised'
            system_states['flight_control']['compromised'] = True
            
            threat_log.append({
                'timestamp': timestamp,
                'system': 'Flight Control',
                'attack': 'Control Freeze',
                'description': 'Flight controls frozen and unresponsive',
                'severity': 'High'
            })
            
        elif attack_type == 'mitm_control':
            # Man-in-the-middle attack on control systems
            system_states['flight_control']['aileron'] = 15  # Subtle but dangerous bank
            system_states['flight_control']['elevator'] = -10  # Slight nose down
            system_states['flight_control']['throttle'] = 90  # Increased throttle
            system_states['flight_control']['status'] = 'compromised'
            system_states['flight_control']['compromised'] = True
            
            threat_log.append({
                'timestamp': timestamp,
                'system': 'Flight Control',
                'attack': 'Man-in-the-Middle',
                'description': 'Flight control bus compromised - intercepting and modifying pilot inputs',
                'severity': 'Critical'
            })
            
        elif attack_type == 'replay_control':
            # Replay previous control commands
            system_states['flight_control']['aileron'] = -20
            system_states['flight_control']['elevator'] = 5
            system_states['flight_control']['rudder'] = 10
            system_states['flight_control']['throttle'] = 60
            system_states['flight_control']['status'] = 'compromised'
            system_states['flight_control']['compromised'] = True
            
            threat_log.append({
                'timestamp': timestamp,
                'system': 'Flight Control',
                'attack': 'Replay Attack',
                'description': 'Replaying previous control commands - aircraft executing old maneuvers',
                'severity': 'High'
            })
    
    elif system == 'communications':
        if attack_type == 'inject_message':
            system_states['communications']['last_message'] = "MAYDAY MAYDAY - HIJACK IN PROGRESS"
            system_states['communications']['status'] = 'compromised'
            system_states['communications']['compromised'] = True
            
            threat_log.append({
                'timestamp': timestamp,
                'system': 'Communications',
                'attack': 'Message Injection',
                'description': 'Fake emergency message injected into radio communications',
                'severity': 'High'
            })
            
        elif attack_type == 'jam_radio':
            system_states['communications']['signal_strength'] = 0
            system_states['communications']['last_message'] = "SIGNAL LOST"
            system_states['communications']['status'] = 'compromised'
            system_states['communications']['compromised'] = True
            
            threat_log.append({
                'timestamp': timestamp,
                'system': 'Communications',
                'attack': 'Radio Jamming',
                'description': 'Radio communications jammed - signal lost',
                'severity': 'Medium'
            })
            
        elif attack_type == 'mitm_comms':
            # Man-in-the-middle attack on communications
            system_states['communications']['last_message'] = "ATC: Proceed to alternate runway 09L [INTERCEPTED]"
            system_states['communications']['frequency'] = 118.7  # Different frequency
            system_states['communications']['signal_strength'] = 45  # Reduced signal
            system_states['communications']['status'] = 'compromised'
            system_states['communications']['compromised'] = True
            
            threat_log.append({
                'timestamp': timestamp,
                'system': 'Communications',
                'attack': 'Man-in-the-Middle',
                'description': 'Radio communications intercepted - attacker modifying ATC instructions',
                'severity': 'Critical'
            })
            
        elif attack_type == 'replay_comms':
            # Replay old radio messages
            system_states['communications']['last_message'] = "ATC: Cleared for takeoff runway 24R [REPLAYED]"
            system_states['communications']['frequency'] = 120.9
            system_states['communications']['status'] = 'compromised'
            system_states['communications']['compromised'] = True
            
            threat_log.append({
                'timestamp': timestamp,
                'system': 'Communications',
                'attack': 'Replay Attack',
                'description': 'Replaying old ATC clearances - aircraft receiving outdated instructions',
                'severity': 'High'
            })
    
    # Trigger defense mechanisms based on attack
    trigger_defense_systems(system, attack_type, timestamp)
    
    return jsonify({'status': 'success', 'message': 'Attack simulated successfully'})

@app.route('/api/reset_system', methods=['POST'])
def reset_system():
    """API endpoint to reset a specific system or all systems"""
    data = request.get_json()
    system = data.get('system', 'all')
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if system == 'all' or system == 'adsb':
        system_states['adsb'] = {
            "status": "normal",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "altitude": 35000,
            "heading": 90,
            "speed": 450,
            "compromised": False
        }
    
    if system == 'all' or system == 'flight_control':
        system_states['flight_control'] = {
            "status": "normal",
            "aileron": 0,
            "elevator": 0,
            "rudder": 0,
            "throttle": 75,
            "compromised": False
        }
    
    if system == 'all' or system == 'communications':
        system_states['communications'] = {
            "status": "normal",
            "frequency": 121.5,
            "last_message": "All systems nominal",
            "signal_strength": 85,
            "compromised": False
        }
    
    if system == 'all':
        threat_log.append({
            'timestamp': timestamp,
            'system': 'All Systems',
            'attack': 'System Reset',
            'description': 'All aircraft systems reset to normal operation',
            'severity': 'Info'
        })
    else:
        threat_log.append({
            'timestamp': timestamp,
            'system': system.upper().replace('_', ' '),
            'attack': 'System Reset',
            'description': f'{system.upper().replace("_", " ")} system reset to normal operation',
            'severity': 'Info'
        })
    
    return jsonify({'status': 'success', 'message': 'System reset successfully'})

@app.route('/api/clear_log', methods=['POST'])
def clear_log():
    """API endpoint to clear the threat log"""
    global threat_log
    threat_log = []
    return jsonify({'status': 'success', 'message': 'Threat log cleared'})

@app.route('/api/toggle_defense', methods=['POST'])
def toggle_defense():
    """API endpoint to enable/disable defense systems"""
    data = request.get_json()
    defense_type = data.get('defense_type')
    enabled = data.get('enabled', True)
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if defense_type in defense_systems:
        defense_systems[defense_type]['enabled'] = enabled
        status = 'active' if enabled else 'disabled'
        defense_systems[defense_type]['status'] = status
        
        action = 'enabled' if enabled else 'disabled'
        threat_log.append({
            'timestamp': timestamp,
            'system': 'Defense Systems',
            'attack': f'Defense System {action.title()}',
            'description': f'{defense_type.replace("_", " ").title()} defense system {action}',
            'severity': 'Info'
        })
        
        return jsonify({'status': 'success', 'message': f'Defense system {action}'})
    
    return jsonify({'status': 'error', 'message': 'Invalid defense system'})

@app.route('/api/activate_countermeasure', methods=['POST'])
def activate_countermeasure():
    """API endpoint to manually activate countermeasures"""
    data = request.get_json()
    countermeasure = data.get('countermeasure')
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if countermeasure == 'emergency_protocol':
        # Reset all compromised systems
        for system_key in system_states:
            if system_states[system_key].get('compromised'):
                system_states[system_key]['compromised'] = False
                system_states[system_key]['status'] = 'normal'
        
        # Reset system values to safe defaults
        system_states['adsb']['latitude'] = 40.7128
        system_states['adsb']['longitude'] = -74.0060
        system_states['adsb']['altitude'] = 35000
        system_states['adsb']['heading'] = 90
        system_states['adsb']['speed'] = 450
        
        system_states['flight_control']['aileron'] = 0
        system_states['flight_control']['elevator'] = 0
        system_states['flight_control']['rudder'] = 0
        system_states['flight_control']['throttle'] = 75
        
        system_states['communications']['frequency'] = 121.5
        system_states['communications']['last_message'] = "Emergency protocol activated - systems restored"
        system_states['communications']['signal_strength'] = 85
        
        threat_log.append({
            'timestamp': timestamp,
            'system': 'Defense Systems',
            'attack': 'Emergency Protocol Activated',
            'description': 'All systems reset to safe configuration - manual override engaged',
            'severity': 'Info'
        })
        
    elif countermeasure == 'isolate_systems':
        # Simulate system isolation
        for system_key in system_states:
            system_states[system_key]['status'] = 'isolated'
        
        threat_log.append({
            'timestamp': timestamp,
            'system': 'Defense Systems',
            'attack': 'System Isolation Activated',
            'description': 'All aircraft systems isolated from external networks',
            'severity': 'Info'
        })
        
    elif countermeasure == 'backup_navigation':
        # Activate backup navigation
        defense_systems['backup_systems']['status'] = 'active'
        defense_systems['backup_systems']['activations'] += 1
        defense_systems['backup_systems']['last_activation'] = timestamp
        
        system_states['adsb']['status'] = 'backup_mode'
        
        threat_log.append({
            'timestamp': timestamp,
            'system': 'Defense Systems',
            'attack': 'Backup Navigation Activated',
            'description': 'Primary navigation compromised - switched to backup inertial navigation',
            'severity': 'Info'
        })
    
    return jsonify({'status': 'success', 'message': 'Countermeasure activated'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
