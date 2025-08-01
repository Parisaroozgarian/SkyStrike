"""
Professional attack simulation service with comprehensive threat modeling
"""
from datetime import datetime
from typing import Dict, Any, Optional
import logging
from models import (
    FleetManager, ThreatLogEntry, ThreatSeverity, SystemStatus, 
    AttackVector, Aircraft
)

logger = logging.getLogger(__name__)


class AttackService:
    """Professional attack simulation service"""
    
    def __init__(self, fleet_manager: FleetManager):
        self.fleet_manager = fleet_manager
        self.attack_handlers = {
            # ADS-B attacks
            AttackVector.SPOOF_LOCATION: self._handle_location_spoofing,
            AttackVector.SPOOF_ALTITUDE: self._handle_altitude_spoofing,
            AttackVector.MITM_ADSB: self._handle_adsb_mitm,
            AttackVector.REPLAY_ADSB: self._handle_adsb_replay,
            
            # Flight control attacks
            AttackVector.JAM_INPUTS: self._handle_control_jamming,
            AttackVector.FREEZE_CONTROLS: self._handle_control_freeze,
            AttackVector.MITM_CONTROL: self._handle_control_mitm,
            AttackVector.REPLAY_CONTROL: self._handle_control_replay,
            
            # Communication attacks
            AttackVector.INJECT_MESSAGE: self._handle_message_injection,
            AttackVector.JAM_RADIO: self._handle_radio_jamming,
            AttackVector.MITM_COMM: self._handle_comm_mitm,
            AttackVector.REPLAY_COMM: self._handle_comm_replay
        }
    
    def execute_attack(self, attack_vector: AttackVector, aircraft_id: str, 
                      parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a cyber attack on specified aircraft system"""
        aircraft = self.fleet_manager.get_aircraft(aircraft_id)
        if not aircraft:
            return {'status': 'error', 'message': 'Invalid aircraft ID'}
        
        try:
            # Execute attack handler
            handler = self.attack_handlers.get(attack_vector)
            if not handler:
                return {'status': 'error', 'message': 'Unknown attack vector'}
            
            result = handler(aircraft, parameters or {})
            
            # Trigger defense systems
            self._trigger_defense_systems(aircraft, attack_vector)
            
            # Log attack execution
            logger.info(f"Attack {attack_vector.value} executed on {aircraft.callsign}")
            
            return {
                'status': 'success',
                'attack_vector': attack_vector.value,
                'aircraft': aircraft.callsign,
                'result': result
            }
            
        except Exception as e:
            logger.error(f"Attack execution failed: {str(e)}")
            return {'status': 'error', 'message': f'Attack execution failed: {str(e)}'}
    
    def _handle_location_spoofing(self, aircraft: Aircraft, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle GPS location spoofing attack"""
        # Default to London coordinates or use provided coordinates
        spoofed_lat = params.get('latitude', 51.5074)
        spoofed_lon = params.get('longitude', -0.1278)
        
        original_pos = (aircraft.adsb.latitude, aircraft.adsb.longitude)
        aircraft.adsb.latitude = spoofed_lat
        aircraft.adsb.longitude = spoofed_lon
        aircraft.adsb.status = SystemStatus.COMPROMISED
        aircraft.adsb.compromised = True
        aircraft.adsb.last_update = datetime.now()
        
        # Create threat log entry
        threat_entry = ThreatLogEntry(
            timestamp=datetime.now(),
            system='ADS-B',
            attack='Location Spoofing',
            description=f'{aircraft.callsign} location spoofed from {original_pos} to ({spoofed_lat}, {spoofed_lon})',
            severity=ThreatSeverity.HIGH,
            aircraft_id=aircraft.aircraft_id
        )
        self.fleet_manager.add_threat_log_entry(threat_entry)
        
        return {
            'original_position': original_pos,
            'spoofed_position': (spoofed_lat, spoofed_lon),
            'impact': 'Aircraft appears at false location to ATC and other aircraft'
        }
    
    def _handle_altitude_spoofing(self, aircraft: Aircraft, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle altitude spoofing attack"""
        spoofed_altitude = params.get('altitude', 5000)  # Dangerous low altitude
        original_altitude = aircraft.adsb.altitude
        
        aircraft.adsb.altitude = spoofed_altitude
        aircraft.adsb.status = SystemStatus.COMPROMISED
        aircraft.adsb.compromised = True
        aircraft.adsb.last_update = datetime.now()
        
        threat_entry = ThreatLogEntry(
            timestamp=datetime.now(),
            system='ADS-B',
            attack='Altitude Spoofing',
            description=f'{aircraft.callsign} altitude spoofed from {original_altitude}ft to {spoofed_altitude}ft',
            severity=ThreatSeverity.CRITICAL,
            aircraft_id=aircraft.aircraft_id
        )
        self.fleet_manager.add_threat_log_entry(threat_entry)
        
        return {
            'original_altitude': original_altitude,
            'spoofed_altitude': spoofed_altitude,
            'impact': 'Critical altitude conflict - potential collision risk'
        }
    
    def _handle_adsb_mitm(self, aircraft: Aircraft, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ADS-B man-in-the-middle attack"""
        # Gradually modify position and heading
        aircraft.adsb.latitude += 0.5
        aircraft.adsb.longitude += 0.5
        aircraft.adsb.heading = (aircraft.adsb.heading + 45) % 360
        aircraft.adsb.speed = max(0, aircraft.adsb.speed - 50)
        aircraft.adsb.status = SystemStatus.COMPROMISED
        aircraft.adsb.compromised = True
        aircraft.adsb.last_update = datetime.now()
        
        threat_entry = ThreatLogEntry(
            timestamp=datetime.now(),
            system='ADS-B',
            attack='Man-in-the-Middle',
            description=f'{aircraft.callsign} ADS-B transponder compromised - intercepting and modifying position data',
            severity=ThreatSeverity.CRITICAL,
            aircraft_id=aircraft.aircraft_id
        )
        self.fleet_manager.add_threat_log_entry(threat_entry)
        
        return {
            'attack_type': 'persistent_modification',
            'impact': 'Continuous position data manipulation - undetectable by pilot'
        }
    
    def _handle_adsb_replay(self, aircraft: Aircraft, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle ADS-B replay attack"""
        # Use old position data
        aircraft.adsb.latitude = 40.7128  # NYC coordinates
        aircraft.adsb.longitude = -74.0060
        aircraft.adsb.altitude = 25000
        aircraft.adsb.heading = 270
        aircraft.adsb.speed = 350
        aircraft.adsb.status = SystemStatus.COMPROMISED
        aircraft.adsb.compromised = True
        aircraft.adsb.last_update = datetime.now()
        
        threat_entry = ThreatLogEntry(
            timestamp=datetime.now(),
            system='ADS-B',
            attack='Replay Attack',
            description=f'{aircraft.callsign} replaying old ADS-B transmissions - appears at previous location',
            severity=ThreatSeverity.HIGH,
            aircraft_id=aircraft.aircraft_id
        )
        self.fleet_manager.add_threat_log_entry(threat_entry)
        
        return {
            'replayed_position': 'New York City (historical data)',
            'impact': 'Aircraft appears at outdated location causing confusion'
        }
    
    def _handle_control_jamming(self, aircraft: Aircraft, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle flight control input jamming"""
        aircraft.flight_control.aileron = -45  # Extreme bank
        aircraft.flight_control.elevator = 30  # Nose up
        aircraft.flight_control.rudder = 20   # Hard rudder
        aircraft.flight_control.status = SystemStatus.COMPROMISED
        aircraft.flight_control.compromised = True
        aircraft.flight_control.last_update = datetime.now()
        
        threat_entry = ThreatLogEntry(
            timestamp=datetime.now(),
            system='Flight Control',
            attack='Control Input Jamming',
            description=f'{aircraft.callsign} flight control inputs overridden with extreme values',
            severity=ThreatSeverity.CRITICAL,
            aircraft_id=aircraft.aircraft_id
        )
        self.fleet_manager.add_threat_log_entry(threat_entry)
        
        return {
            'control_surfaces': 'All surfaces set to extreme positions',
            'impact': 'Immediate flight safety risk - pilot override required'
        }
    
    def _handle_control_freeze(self, aircraft: Aircraft, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle flight control freeze attack"""
        aircraft.flight_control.status = SystemStatus.COMPROMISED
        aircraft.flight_control.compromised = True
        aircraft.flight_control.last_update = datetime.now()
        
        threat_entry = ThreatLogEntry(
            timestamp=datetime.now(),
            system='Flight Control',
            attack='Control Freeze',
            description=f'{aircraft.callsign} flight controls frozen and unresponsive to pilot input',
            severity=ThreatSeverity.HIGH,
            aircraft_id=aircraft.aircraft_id
        )
        self.fleet_manager.add_threat_log_entry(threat_entry)
        
        return {
            'frozen_controls': 'All control surfaces locked in current position',
            'impact': 'Loss of flight control authority'
        }
    
    def _handle_control_mitm(self, aircraft: Aircraft, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle flight control man-in-the-middle attack"""
        aircraft.flight_control.aileron = 15  # Subtle but dangerous bank
        aircraft.flight_control.elevator = -10  # Slight nose down
        aircraft.flight_control.throttle = 90  # Increased throttle
        aircraft.flight_control.status = SystemStatus.COMPROMISED
        aircraft.flight_control.compromised = True
        aircraft.flight_control.last_update = datetime.now()
        
        threat_entry = ThreatLogEntry(
            timestamp=datetime.now(),
            system='Flight Control',
            attack='Man-in-the-Middle',
            description=f'{aircraft.callsign} flight control bus compromised - subtle input modifications',
            severity=ThreatSeverity.CRITICAL,
            aircraft_id=aircraft.aircraft_id
        )
        self.fleet_manager.add_threat_log_entry(threat_entry)
        
        return {
            'modification_type': 'subtle_persistent',
            'impact': 'Gradual flight path deviation - difficult to detect'
        }
    
    def _handle_control_replay(self, aircraft: Aircraft, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle flight control replay attack"""
        aircraft.flight_control.aileron = -20
        aircraft.flight_control.elevator = 5
        aircraft.flight_control.rudder = 10
        aircraft.flight_control.throttle = 60
        aircraft.flight_control.status = SystemStatus.COMPROMISED
        aircraft.flight_control.compromised = True
        aircraft.flight_control.last_update = datetime.now()
        
        threat_entry = ThreatLogEntry(
            timestamp=datetime.now(),
            system='Flight Control',
            attack='Replay Attack',
            description=f'{aircraft.callsign} executing replayed control commands from previous flight segment',
            severity=ThreatSeverity.HIGH,
            aircraft_id=aircraft.aircraft_id
        )
        self.fleet_manager.add_threat_log_entry(threat_entry)
        
        return {
            'replayed_commands': 'Previous maneuver sequence',
            'impact': 'Aircraft executing outdated flight commands'
        }
    
    def _handle_message_injection(self, aircraft: Aircraft, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle communication message injection"""
        malicious_message = params.get('message', "MAYDAY MAYDAY - HIJACK IN PROGRESS")
        aircraft.communications.last_message = malicious_message
        aircraft.communications.status = SystemStatus.COMPROMISED
        aircraft.communications.compromised = True
        aircraft.communications.last_update = datetime.now()
        
        threat_entry = ThreatLogEntry(
            timestamp=datetime.now(),
            system='Communications',
            attack='Message Injection',
            description=f'{aircraft.callsign} fake emergency message injected: "{malicious_message}"',
            severity=ThreatSeverity.HIGH,
            aircraft_id=aircraft.aircraft_id
        )
        self.fleet_manager.add_threat_log_entry(threat_entry)
        
        return {
            'injected_message': malicious_message,
            'impact': 'False emergency declared - resources diverted unnecessarily'
        }
    
    def _handle_radio_jamming(self, aircraft: Aircraft, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle radio communication jamming"""
        aircraft.communications.signal_strength = 0
        aircraft.communications.last_message = "SIGNAL LOST - UNABLE TO COMMUNICATE"
        aircraft.communications.status = SystemStatus.COMPROMISED
        aircraft.communications.compromised = True
        aircraft.communications.last_update = datetime.now()
        
        threat_entry = ThreatLogEntry(
            timestamp=datetime.now(),
            system='Communications',
            attack='Radio Jamming',
            description=f'{aircraft.callsign} all radio communications jammed - complete communication blackout',
            severity=ThreatSeverity.CRITICAL,
            aircraft_id=aircraft.aircraft_id
        )
        self.fleet_manager.add_threat_log_entry(threat_entry)
        
        return {
            'jammed_frequencies': 'All aviation bands',
            'impact': 'Complete loss of air traffic control communication'
        }
    
    def _handle_comm_mitm(self, aircraft: Aircraft, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle communication man-in-the-middle attack"""
        aircraft.communications.last_message = "Roger, cleared for immediate descent to 5000 feet"
        aircraft.communications.frequency = 999.9  # Invalid frequency
        aircraft.communications.signal_strength = max(0, aircraft.communications.signal_strength - 30)
        aircraft.communications.status = SystemStatus.COMPROMISED
        aircraft.communications.compromised = True
        aircraft.communications.last_update = datetime.now()
        
        threat_entry = ThreatLogEntry(
            timestamp=datetime.now(),
            system='Communications',
            attack='Man-in-the-Middle',
            description=f'{aircraft.callsign} communication channel compromised - false ATC instructions',
            severity=ThreatSeverity.CRITICAL,
            aircraft_id=aircraft.aircraft_id
        )
        self.fleet_manager.add_threat_log_entry(threat_entry)
        
        return {
            'false_instructions': 'Dangerous altitude clearance',
            'impact': 'Pilot receiving unauthorized ATC commands'
        }
    
    def _handle_comm_replay(self, aircraft: Aircraft, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle communication replay attack"""
        aircraft.communications.last_message = "Contact departure 124.35, good day"
        aircraft.communications.frequency = 124.35
        aircraft.communications.status = SystemStatus.COMPROMISED
        aircraft.communications.compromised = True
        aircraft.communications.last_update = datetime.now()
        
        threat_entry = ThreatLogEntry(
            timestamp=datetime.now(),
            system='Communications',
            attack='Replay Attack',
            description=f'{aircraft.callsign} replaying old ATC communications - outdated instructions',
            severity=ThreatSeverity.MEDIUM,
            aircraft_id=aircraft.aircraft_id
        )
        self.fleet_manager.add_threat_log_entry(threat_entry)
        
        return {
            'replayed_message': 'Previous ATC handoff',
            'impact': 'Confusion with outdated communication instructions'
        }
    
    def _trigger_defense_systems(self, aircraft: Aircraft, attack_vector: AttackVector):
        """Trigger appropriate defense mechanisms"""
        timestamp = datetime.now()
        
        for defense_name, defense_system in self.fleet_manager.defense_systems.items():
            if not defense_system.enabled:
                continue
                
            defense_system.alerts_triggered += 1
            defense_system.last_alert = timestamp
            
            if defense_name == 'intrusion_detection':
                defense_system.status = SystemStatus.COMPROMISED  # Alert state
            elif defense_name == 'data_validation' and 'spoof' in attack_vector.value:
                defense_system.status = SystemStatus.DEGRADED  # Validating state
            elif defense_name == 'encryption' and 'mitm' in attack_vector.value:
                defense_system.activations += 1
                defense_system.last_activation = timestamp
                defense_system.status = SystemStatus.DEGRADED  # Key rotation
            elif defense_name == 'backup_systems' and attack_vector in [AttackVector.JAM_INPUTS, AttackVector.FREEZE_CONTROLS, AttackVector.JAM_RADIO]:
                defense_system.activations += 1
                defense_system.last_activation = timestamp
                defense_system.status = SystemStatus.NORMAL  # Active backup
            
            # Log defense system response
            defense_entry = ThreatLogEntry(
                timestamp=timestamp,
                system='Defense Systems',
                attack=f'{defense_name.replace("_", " ").title()} Response',
                description=f'{defense_name.replace("_", " ").title()} system responded to {attack_vector.value} attack on {aircraft.callsign}',
                severity=ThreatSeverity.INFO,
                aircraft_id=aircraft.aircraft_id
            )
            self.fleet_manager.add_threat_log_entry(defense_entry)