import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify
import logging

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "aviation_simulator_secret_key")

# Multi-aircraft system states storage
aircraft_fleet = {
    "aircraft_1": {
        "callsign": "AAL123",
        "model": "Boeing 737",
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
    },
    "aircraft_2": {
        "callsign": "UAL456",
        "model": "Airbus A320",
        "adsb": {
            "status": "normal",
            "latitude": 41.8781,
            "longitude": -87.6298,
            "altitude": 32000,
            "heading": 180,
            "speed": 420,
            "compromised": False
        },
        "flight_control": {
            "status": "normal",
            "aileron": 0,
            "elevator": 0,
            "rudder": 0,
            "throttle": 70,
            "compromised": False
        },
        "communications": {
            "status": "normal",
            "frequency": 122.8,
            "last_message": "Chicago approach, level 320",
            "signal_strength": 90,
            "compromised": False
        }
    },
    "aircraft_3": {
        "callsign": "DLH789",
        "model": "Boeing 777",
        "adsb": {
            "status": "normal",
            "latitude": 51.4700,
            "longitude": -0.4543,
            "altitude": 41000,
            "heading": 270,
            "speed": 480,
            "compromised": False
        },
        "flight_control": {
            "status": "normal",
            "aileron": 0,
            "elevator": 0,
            "rudder": 0,
            "throttle": 80,
            "compromised": False
        },
        "communications": {
            "status": "normal",
            "frequency": 118.5,
            "last_message": "London control, crossing waypoint TIGER",
            "signal_strength": 88,
            "compromised": False
        }
    }
}

# Current selected aircraft for single-aircraft view compatibility
current_aircraft = "aircraft_1"

# Legacy system states for backward compatibility
system_states = aircraft_fleet[current_aircraft]

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
        'threat_log': threat_log[-10:],  # Last 10 entries
        'aircraft_fleet': aircraft_fleet,
        'current_aircraft': current_aircraft
    })

@app.route('/api/fleet_status')
def get_fleet_status():
    """API endpoint to get all aircraft fleet status"""
    return jsonify({
        'aircraft_fleet': aircraft_fleet,
        'defense_systems': defense_systems,
        'threat_log': threat_log[-20:],  # More entries for fleet view
        'current_aircraft': current_aircraft
    })

@app.route('/api/select_aircraft', methods=['POST'])
def select_aircraft():
    """API endpoint to select a specific aircraft for detailed view"""
    global current_aircraft, system_states
    data = request.get_json()
    aircraft_id = data.get('aircraft_id')
    
    if aircraft_id in aircraft_fleet:
        current_aircraft = aircraft_id
        system_states = aircraft_fleet[current_aircraft]
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        threat_log.append({
            'timestamp': timestamp,
            'system': 'Flight Operations',
            'attack': 'Aircraft Selection',
            'description': f'Switched monitoring to {aircraft_fleet[aircraft_id]["callsign"]} ({aircraft_fleet[aircraft_id]["model"]})',
            'severity': 'Info'
        })
        
        return jsonify({'status': 'success', 'message': f'Selected {aircraft_fleet[aircraft_id]["callsign"]}'})
    
    return jsonify({'status': 'error', 'message': 'Invalid aircraft ID'})

@app.route('/api/simulate_attack', methods=['POST'])
def simulate_attack():
    """API endpoint to simulate cyber attacks"""
    data = request.get_json()
    system = data.get('system')
    attack_type = data.get('attack_type')
    target_aircraft = data.get('aircraft_id', current_aircraft)  # Allow targeting specific aircraft
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Get target aircraft data
    if target_aircraft not in aircraft_fleet:
        return jsonify({'status': 'error', 'message': 'Invalid aircraft ID'})
    
    target_systems = aircraft_fleet[target_aircraft]
    aircraft_info = f"{target_systems['callsign']} ({target_systems['model']})"
    
    if system == 'adsb':
        if attack_type == 'spoof_location':
            target_systems['adsb']['latitude'] = 51.5074  # London coordinates
            target_systems['adsb']['longitude'] = -0.1278
            target_systems['adsb']['status'] = 'compromised'
            target_systems['adsb']['compromised'] = True
            
            threat_log.append({
                'timestamp': timestamp,
                'system': 'ADS-B',
                'attack': 'Location Spoofing',
                'description': f'{aircraft_info} location spoofed to London coordinates',
                'severity': 'High'
            })
            
        elif attack_type == 'spoof_altitude':
            target_systems['adsb']['altitude'] = 5000  # Dangerous low altitude
            target_systems['adsb']['status'] = 'compromised'
            target_systems['adsb']['compromised'] = True
            
            threat_log.append({
                'timestamp': timestamp,
                'system': 'ADS-B',
                'attack': 'Altitude Spoofing',
                'description': f'{aircraft_info} altitude spoofed to dangerous low level',
                'severity': 'Critical'
            })
            
        elif attack_type == 'mitm_adsb':
            # Man-in-the-middle attack on ADS-B data
            original_lat = target_systems['adsb']['latitude']
            original_lon = target_systems['adsb']['longitude']
            target_systems['adsb']['latitude'] = original_lat + 0.5  # Slight position shift
            target_systems['adsb']['longitude'] = original_lon + 0.5
            target_systems['adsb']['heading'] = (target_systems['adsb']['heading'] + 45) % 360
            target_systems['adsb']['status'] = 'compromised'
            target_systems['adsb']['compromised'] = True
            
            threat_log.append({
                'timestamp': timestamp,
                'system': 'ADS-B',
                'attack': 'Man-in-the-Middle',
                'description': f'{aircraft_info} ADS-B transponder compromised - intercepting and modifying position data',
                'severity': 'Critical'
            })
            
        elif attack_type == 'replay_adsb':
            # Replay attack using old position data
            target_systems['adsb']['latitude'] = 40.7128  # NYC coordinates (old data)
            target_systems['adsb']['longitude'] = -74.0060
            target_systems['adsb']['altitude'] = 25000
            target_systems['adsb']['heading'] = 270
            target_systems['adsb']['speed'] = 350
            target_systems['adsb']['status'] = 'compromised'
            target_systems['adsb']['compromised'] = True
            
            threat_log.append({
                'timestamp': timestamp,
                'system': 'ADS-B',
                'attack': 'Replay Attack',
                'description': f'{aircraft_info} replaying old ADS-B transmissions - aircraft appears at previous location',
                'severity': 'High'
            })
    
    elif system == 'flight_control':
        if attack_type == 'jam_inputs':
            target_systems['flight_control']['aileron'] = -45  # Extreme bank
            target_systems['flight_control']['elevator'] = 30  # Nose up
            target_systems['flight_control']['status'] = 'compromised'
            target_systems['flight_control']['compromised'] = True
            
            threat_log.append({
                'timestamp': timestamp,
                'system': 'Flight Control',
                'attack': 'Control Input Jamming',
                'description': f'{aircraft_info} flight control inputs jammed with extreme values',
                'severity': 'Critical'
            })
            
        elif attack_type == 'freeze_controls':
            # Controls frozen at current position
            target_systems['flight_control']['status'] = 'compromised'
            target_systems['flight_control']['compromised'] = True
            
            threat_log.append({
                'timestamp': timestamp,
                'system': 'Flight Control',
                'attack': 'Control Freeze',
                'description': f'{aircraft_info} flight controls frozen and unresponsive',
                'severity': 'High'
            })
            
        elif attack_type == 'mitm_control':
            # Man-in-the-middle attack on control systems
            target_systems['flight_control']['aileron'] = 15  # Subtle but dangerous bank
            target_systems['flight_control']['elevator'] = -10  # Slight nose down
            target_systems['flight_control']['throttle'] = 90  # Increased throttle
            target_systems['flight_control']['status'] = 'compromised'
            target_systems['flight_control']['compromised'] = True
            
            threat_log.append({
                'timestamp': timestamp,
                'system': 'Flight Control',
                'attack': 'Man-in-the-Middle',
                'description': f'{aircraft_info} flight control bus compromised - intercepting and modifying pilot inputs',
                'severity': 'Critical'
            })
            
        elif attack_type == 'replay_control':
            # Replay previous control commands
            target_systems['flight_control']['aileron'] = -20
            target_systems['flight_control']['elevator'] = 5
            target_systems['flight_control']['rudder'] = 10
            target_systems['flight_control']['throttle'] = 60
            target_systems['flight_control']['status'] = 'compromised'
            target_systems['flight_control']['compromised'] = True
            
            threat_log.append({
                'timestamp': timestamp,
                'system': 'Flight Control',
                'attack': 'Replay Attack',
                'description': f'{aircraft_info} replaying previous control commands - aircraft executing old maneuvers',
                'severity': 'High'
            })
    
    elif system == 'communications':
        if attack_type == 'inject_message':
            target_systems['communications']['last_message'] = "MAYDAY MAYDAY - HIJACK IN PROGRESS"
            target_systems['communications']['status'] = 'compromised'
            target_systems['communications']['compromised'] = True
            
            threat_log.append({
                'timestamp': timestamp,
                'system': 'Communications',
                'attack': 'Message Injection',
                'description': f'{aircraft_info} fake emergency message injected into radio communications',
                'severity': 'High'
            })
            
        elif attack_type == 'jam_radio':
            target_systems['communications']['signal_strength'] = 0
            target_systems['communications']['last_message'] = "SIGNAL LOST"
            target_systems['communications']['status'] = 'compromised'
            target_systems['communications']['compromised'] = True
            
            threat_log.append({
                'timestamp': timestamp,
                'system': 'Communications',
                'attack': 'Radio Jamming',
                'description': f'{aircraft_info} radio communications jammed - signal lost',
                'severity': 'Medium'
            })
            
        elif attack_type == 'mitm_comms':
            # Man-in-the-middle attack on communications
            target_systems['communications']['last_message'] = "ATC: Proceed to alternate runway 09L [INTERCEPTED]"
            target_systems['communications']['frequency'] = 118.7  # Different frequency
            target_systems['communications']['signal_strength'] = 45  # Reduced signal
            target_systems['communications']['status'] = 'compromised'
            target_systems['communications']['compromised'] = True
            
            threat_log.append({
                'timestamp': timestamp,
                'system': 'Communications',
                'attack': 'Man-in-the-Middle',
                'description': f'{aircraft_info} radio communications intercepted - attacker modifying ATC instructions',
                'severity': 'Critical'
            })
            
        elif attack_type == 'replay_comms':
            # Replay old radio messages
            target_systems['communications']['last_message'] = "ATC: Cleared for takeoff runway 24R [REPLAYED]"
            target_systems['communications']['frequency'] = 120.9
            target_systems['communications']['status'] = 'compromised'
            target_systems['communications']['compromised'] = True
            
            threat_log.append({
                'timestamp': timestamp,
                'system': 'Communications',
                'attack': 'Replay Attack',
                'description': f'{aircraft_info} replaying old ATC clearances - aircraft receiving outdated instructions',
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

@app.route('/api/fleet_attack', methods=['POST'])
def fleet_attack():
    """API endpoint for coordinated fleet-wide attacks"""
    data = request.get_json()
    attack_scenario = data.get('attack_scenario')
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    affected_aircraft = []
    
    if attack_scenario == 'coordinated_jamming':
        # Jam radio communications for all aircraft
        for aircraft_id in aircraft_fleet.keys():
            aircraft_fleet[aircraft_id]['communications']['signal_strength'] = 0
            aircraft_fleet[aircraft_id]['communications']['last_message'] = "SIGNAL LOST - COORDINATED JAMMING"
            aircraft_fleet[aircraft_id]['communications']['status'] = 'compromised'
            aircraft_fleet[aircraft_id]['communications']['compromised'] = True
            affected_aircraft.append(f"{aircraft_fleet[aircraft_id]['callsign']}")
        
        threat_log.append({
            'timestamp': timestamp,
            'system': 'Fleet Communications',
            'attack': 'Coordinated Radio Jamming',
            'description': f'Simultaneous radio jamming attack targeting entire fleet: {", ".join(affected_aircraft)}',
            'severity': 'Critical'
        })
        
    elif attack_scenario == 'adsb_spoofing_campaign':
        # Spoof ADS-B data for all aircraft
        import random
        for aircraft_id in aircraft_fleet.keys():
            aircraft_fleet[aircraft_id]['adsb']['latitude'] += random.uniform(-0.5, 0.5)
            aircraft_fleet[aircraft_id]['adsb']['longitude'] += random.uniform(-0.5, 0.5)
            aircraft_fleet[aircraft_id]['adsb']['altitude'] += random.randint(-2000, 2000)
            aircraft_fleet[aircraft_id]['adsb']['status'] = 'compromised'
            aircraft_fleet[aircraft_id]['adsb']['compromised'] = True
            affected_aircraft.append(f"{aircraft_fleet[aircraft_id]['callsign']}")
        
        threat_log.append({
            'timestamp': timestamp,
            'system': 'Fleet ADS-B',
            'attack': 'Coordinated ADS-B Spoofing',
            'description': f'GPS spoofing campaign creating false positions for entire fleet: {", ".join(affected_aircraft)}',
            'severity': 'Critical'
        })
        
    elif attack_scenario == 'multi_vector_assault':
        # Multi-system attack on all aircraft
        import random
        for aircraft_id in aircraft_fleet.keys():
            # ADS-B compromise
            aircraft_fleet[aircraft_id]['adsb']['latitude'] += random.uniform(-1.0, 1.0)
            aircraft_fleet[aircraft_id]['adsb']['altitude'] += random.randint(-3000, 3000)
            aircraft_fleet[aircraft_id]['adsb']['status'] = 'compromised'
            aircraft_fleet[aircraft_id]['adsb']['compromised'] = True
            
            # Flight control compromise
            aircraft_fleet[aircraft_id]['flight_control']['aileron'] = random.randint(-30, 30)
            aircraft_fleet[aircraft_id]['flight_control']['elevator'] = random.randint(-15, 15)
            aircraft_fleet[aircraft_id]['flight_control']['status'] = 'compromised'
            aircraft_fleet[aircraft_id]['flight_control']['compromised'] = True
            
            # Communications compromise
            aircraft_fleet[aircraft_id]['communications']['signal_strength'] = random.randint(0, 30)
            aircraft_fleet[aircraft_id]['communications']['last_message'] = "MAYDAY - MULTIPLE SYSTEMS COMPROMISED"
            aircraft_fleet[aircraft_id]['communications']['status'] = 'compromised'
            aircraft_fleet[aircraft_id]['communications']['compromised'] = True
            
            affected_aircraft.append(f"{aircraft_fleet[aircraft_id]['callsign']}")
        
        threat_log.append({
            'timestamp': timestamp,
            'system': 'Fleet-Wide',
            'attack': 'Multi-Vector Assault',
            'description': f'Advanced persistent threat targeting all systems across fleet: {", ".join(affected_aircraft)}',
            'severity': 'Critical'
        })
    
    return jsonify({
        'status': 'success', 
        'message': f'Fleet attack "{attack_scenario}" executed successfully',
        'affected_aircraft': affected_aircraft
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
