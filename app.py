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

# Threat log storage
threat_log = []

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
