"""
Professional input validation utilities
"""
from typing import Dict, Any, List, Optional, Tuple
import re
from datetime import datetime


class ValidationError(Exception):
    """Custom validation error"""
    pass


class InputValidator:
    """Professional input validation with comprehensive checks"""
    
    # Validation patterns
    AIRCRAFT_ID_PATTERN = re.compile(r'^aircraft_[1-9]\d*$')
    CALLSIGN_PATTERN = re.compile(r'^[A-Z]{3}\d{2,4}$')
    FREQUENCY_PATTERN = re.compile(r'^\d{3}\.\d{1,3}$')
    
    @staticmethod
    def validate_aircraft_id(aircraft_id: str) -> bool:
        """Validate aircraft ID format"""
        if not isinstance(aircraft_id, str):
            return False
        return bool(InputValidator.AIRCRAFT_ID_PATTERN.match(aircraft_id))
    
    @staticmethod
    def validate_callsign(callsign: str) -> bool:
        """Validate aircraft callsign format"""
        if not isinstance(callsign, str):
            return False
        return bool(InputValidator.CALLSIGN_PATTERN.match(callsign))
    
    @staticmethod
    def validate_coordinates(latitude: float, longitude: float) -> bool:
        """Validate GPS coordinates"""
        try:
            lat = float(latitude)
            lon = float(longitude)
            return -90 <= lat <= 90 and -180 <= lon <= 180
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_altitude(altitude: int) -> bool:
        """Validate aircraft altitude"""
        try:
            alt = int(altitude)
            return -1000 <= alt <= 60000  # Reasonable flight envelope
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_heading(heading: int) -> bool:
        """Validate aircraft heading"""
        try:
            hdg = int(heading)
            return 0 <= hdg <= 360
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_speed(speed: int) -> bool:
        """Validate aircraft speed"""
        try:
            spd = int(speed)
            return 0 <= spd <= 1000  # Reasonable speed range
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_frequency(frequency: float) -> bool:
        """Validate radio frequency"""
        try:
            freq = float(frequency)
            return 108.0 <= freq <= 137.0  # Aviation VHF band
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_control_surface(value: int) -> bool:
        """Validate control surface position"""
        try:
            val = int(value)
            return -90 <= val <= 90
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_throttle(throttle: int) -> bool:
        """Validate throttle setting"""
        try:
            thr = int(throttle)
            return 0 <= thr <= 100
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_attack_request(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate attack simulation request"""
        errors = []
        
        # Required fields
        required_fields = ['system', 'attack_type']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
            elif not isinstance(data[field], str) or not data[field].strip():
                errors.append(f"Invalid {field}: must be non-empty string")
        
        # Validate aircraft_id if provided
        if 'aircraft_id' in data:
            if not InputValidator.validate_aircraft_id(data['aircraft_id']):
                errors.append("Invalid aircraft_id format")
        
        # Validate system type
        valid_systems = ['adsb', 'flight_control', 'communications']
        if 'system' in data and data['system'] not in valid_systems:
            errors.append(f"Invalid system. Must be one of: {', '.join(valid_systems)}")
        
        # Validate attack types per system
        valid_attacks = {
            'adsb': ['spoof_location', 'spoof_altitude', 'mitm_adsb', 'replay_adsb'],
            'flight_control': ['jam_inputs', 'freeze_controls', 'mitm_control', 'replay_control'],
            'communications': ['inject_message', 'jam_radio', 'mitm_comm', 'replay_comm']
        }
        
        if ('system' in data and 'attack_type' in data and 
            data['system'] in valid_attacks and 
            data['attack_type'] not in valid_attacks[data['system']]):
            errors.append(f"Invalid attack_type for {data['system']} system")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_aircraft_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate aircraft system data"""
        errors = []
        
        # Validate ADS-B data
        if 'adsb' in data:
            adsb = data['adsb']
            if 'latitude' in adsb and 'longitude' in adsb:
                if not InputValidator.validate_coordinates(adsb['latitude'], adsb['longitude']):
                    errors.append("Invalid GPS coordinates")
            
            if 'altitude' in adsb and not InputValidator.validate_altitude(adsb['altitude']):
                errors.append("Invalid altitude")
            
            if 'heading' in adsb and not InputValidator.validate_heading(adsb['heading']):
                errors.append("Invalid heading")
            
            if 'speed' in adsb and not InputValidator.validate_speed(adsb['speed']):
                errors.append("Invalid speed")
        
        # Validate flight control data
        if 'flight_control' in data:
            fc = data['flight_control']
            for surface in ['aileron', 'elevator', 'rudder']:
                if surface in fc and not InputValidator.validate_control_surface(fc[surface]):
                    errors.append(f"Invalid {surface} position")
            
            if 'throttle' in fc and not InputValidator.validate_throttle(fc['throttle']):
                errors.append("Invalid throttle setting")
        
        # Validate communications data
        if 'communications' in data:
            comm = data['communications']
            if 'frequency' in comm and not InputValidator.validate_frequency(comm['frequency']):
                errors.append("Invalid radio frequency")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def sanitize_message(message: str, max_length: int = 200) -> str:
        """Sanitize communication message"""
        if not isinstance(message, str):
            return ""
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', message)
        
        # Limit length
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length] + "..."
        
        return sanitized.strip()
    
    @staticmethod
    def validate_defense_action(action: str, system_name: str) -> Tuple[bool, str]:
        """Validate defense system action"""
        valid_actions = ['enable', 'disable', 'reset', 'analyze']
        valid_systems = ['intrusion_detection', 'data_validation', 'encryption', 'backup_systems']
        
        if action not in valid_actions:
            return False, f"Invalid action. Must be one of: {', '.join(valid_actions)}"
        
        if system_name and system_name not in valid_systems:
            return False, f"Invalid system. Must be one of: {', '.join(valid_systems)}"
        
        return True, "Valid"


class SecurityValidator:
    """Security-focused validation utilities"""
    
    @staticmethod
    def validate_session_data(data: Dict[str, Any]) -> bool:
        """Validate session data integrity"""
        required_fields = ['timestamp', 'aircraft_selection']
        return all(field in data for field in required_fields)
    
    @staticmethod
    def check_rate_limit(request_count: int, time_window: int, limit: int) -> bool:
        """Check if request is within rate limit"""
        return request_count <= limit
    
    @staticmethod
    def validate_api_request_size(data: Dict[str, Any], max_size: int = 10000) -> bool:
        """Validate API request size"""
        import json
        try:
            request_size = len(json.dumps(data))
            return request_size <= max_size
        except (TypeError, ValueError):
            return False
    
    @staticmethod
    def sanitize_log_entry(entry: str) -> str:
        """Sanitize log entries to prevent injection"""
        if not isinstance(entry, str):
            return ""
        
        # Remove control characters and limit length
        sanitized = ''.join(char for char in entry if ord(char) >= 32 or char in '\n\t')
        return sanitized[:1000]  # Limit log entry length