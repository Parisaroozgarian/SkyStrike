"""
Data models for Aircraft Systems Threat Simulator
Professional data structures with validation and persistence
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import json


class SystemStatus(Enum):
    """System status enumeration"""
    NORMAL = "normal"
    COMPROMISED = "compromised"
    DEGRADED = "degraded"
    OFFLINE = "offline"


class ThreatSeverity(Enum):
    """Threat severity levels"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AttackVector(Enum):
    """Available attack vectors"""
    SPOOF_LOCATION = "spoof_location"
    SPOOF_ALTITUDE = "spoof_altitude"
    MITM_ADSB = "mitm_adsb"
    REPLAY_ADSB = "replay_adsb"
    JAM_INPUTS = "jam_inputs"
    FREEZE_CONTROLS = "freeze_controls"
    MITM_CONTROL = "mitm_control"
    REPLAY_CONTROL = "replay_control"
    INJECT_MESSAGE = "inject_message"
    JAM_RADIO = "jam_radio"
    MITM_COMM = "mitm_comm"
    REPLAY_COMM = "replay_comm"


@dataclass
class ADSBSystem:
    """ADS-B system data model"""
    status: SystemStatus = SystemStatus.NORMAL
    latitude: float = 0.0
    longitude: float = 0.0
    altitude: int = 0
    heading: int = 0
    speed: int = 0
    compromised: bool = False
    last_update: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'status': self.status.value,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'altitude': self.altitude,
            'heading': self.heading,
            'speed': self.speed,
            'compromised': self.compromised,
            'last_update': self.last_update.isoformat()
        }


@dataclass
class FlightControlSystem:
    """Flight control system data model"""
    status: SystemStatus = SystemStatus.NORMAL
    aileron: int = 0
    elevator: int = 0
    rudder: int = 0
    throttle: int = 0
    compromised: bool = False
    last_update: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'status': self.status.value,
            'aileron': self.aileron,
            'elevator': self.elevator,
            'rudder': self.rudder,
            'throttle': self.throttle,
            'compromised': self.compromised,
            'last_update': self.last_update.isoformat()
        }


@dataclass
class CommunicationSystem:
    """Communication system data model"""
    status: SystemStatus = SystemStatus.NORMAL
    frequency: float = 121.5
    last_message: str = ""
    signal_strength: int = 0
    compromised: bool = False
    last_update: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'status': self.status.value,
            'frequency': self.frequency,
            'last_message': self.last_message,
            'signal_strength': self.signal_strength,
            'compromised': self.compromised,
            'last_update': self.last_update.isoformat()
        }


@dataclass
class DefenseSystem:
    """Defense system data model"""
    status: SystemStatus = SystemStatus.NORMAL
    enabled: bool = True
    alerts_triggered: int = 0
    last_alert: Optional[datetime] = None
    activations: int = 0
    last_activation: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'status': self.status.value,
            'enabled': self.enabled,
            'alerts_triggered': self.alerts_triggered,
            'last_alert': self.last_alert.isoformat() if self.last_alert else None,
            'activations': self.activations,
            'last_activation': self.last_activation.isoformat() if self.last_activation else None
        }


@dataclass
class ThreatLogEntry:
    """Threat log entry data model"""
    timestamp: datetime
    system: str
    attack: str
    description: str
    severity: ThreatSeverity
    aircraft_id: Optional[str] = None
    resolved: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'system': self.system,
            'attack': self.attack,
            'description': self.description,
            'severity': self.severity.value,
            'aircraft_id': self.aircraft_id,
            'resolved': self.resolved
        }


@dataclass
class Aircraft:
    """Aircraft data model with all systems"""
    aircraft_id: str
    callsign: str
    model: str
    adsb: ADSBSystem = field(default_factory=ADSBSystem)
    flight_control: FlightControlSystem = field(default_factory=FlightControlSystem)
    communications: CommunicationSystem = field(default_factory=CommunicationSystem)
    last_update: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Initialize default system values"""
        if not hasattr(self.adsb, 'last_update'):
            self.adsb.last_update = datetime.now()
        if not hasattr(self.flight_control, 'last_update'):
            self.flight_control.last_update = datetime.now()
        if not hasattr(self.communications, 'last_update'):
            self.communications.last_update = datetime.now()
    
    def is_compromised(self) -> bool:
        """Check if any system is compromised"""
        return (self.adsb.compromised or 
                self.flight_control.compromised or 
                self.communications.compromised)
    
    def get_overall_status(self) -> SystemStatus:
        """Get overall aircraft status"""
        if self.is_compromised():
            return SystemStatus.COMPROMISED
        return SystemStatus.NORMAL
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'aircraft_id': self.aircraft_id,
            'callsign': self.callsign,
            'model': self.model,
            'adsb': self.adsb.to_dict(),
            'flight_control': self.flight_control.to_dict(),
            'communications': self.communications.to_dict(),
            'last_update': self.last_update.isoformat(),
            'is_compromised': self.is_compromised(),
            'overall_status': self.get_overall_status().value
        }


class FleetManager:
    """Professional fleet management with data validation"""
    
    def __init__(self):
        self.aircraft: Dict[str, Aircraft] = {}
        self.defense_systems: Dict[str, DefenseSystem] = {}
        self.threat_log: List[ThreatLogEntry] = []
        self._initialize_default_fleet()
        self._initialize_defense_systems()
    
    def _initialize_default_fleet(self):
        """Initialize default aircraft fleet"""
        default_aircraft = [
            {
                'aircraft_id': 'aircraft_1',
                'callsign': 'AAL123',
                'model': 'Boeing 737',
                'adsb': ADSBSystem(latitude=40.7128, longitude=-74.0060, altitude=35000, heading=90, speed=450),
                'flight_control': FlightControlSystem(throttle=75),
                'communications': CommunicationSystem(frequency=121.5, last_message="All systems nominal", signal_strength=85)
            },
            {
                'aircraft_id': 'aircraft_2',
                'callsign': 'UAL456',
                'model': 'Airbus A320',
                'adsb': ADSBSystem(latitude=41.8781, longitude=-87.6298, altitude=32000, heading=180, speed=420),
                'flight_control': FlightControlSystem(throttle=70),
                'communications': CommunicationSystem(frequency=122.8, last_message="Chicago approach, level 320", signal_strength=90)
            },
            {
                'aircraft_id': 'aircraft_3',
                'callsign': 'DLH789',
                'model': 'Boeing 777',
                'adsb': ADSBSystem(latitude=51.4700, longitude=-0.4543, altitude=41000, heading=270, speed=480),
                'flight_control': FlightControlSystem(throttle=80),
                'communications': CommunicationSystem(frequency=118.5, last_message="London control, crossing waypoint TIGER", signal_strength=88)
            }
        ]
        
        for aircraft_data in default_aircraft:
            aircraft = Aircraft(**aircraft_data)
            self.aircraft[aircraft.aircraft_id] = aircraft
    
    def _initialize_defense_systems(self):
        """Initialize defense systems"""
        self.defense_systems = {
            'intrusion_detection': DefenseSystem(status=SystemStatus.NORMAL),
            'data_validation': DefenseSystem(status=SystemStatus.NORMAL),
            'encryption': DefenseSystem(status=SystemStatus.NORMAL),
            'backup_systems': DefenseSystem(status=SystemStatus.NORMAL)
        }
    
    def add_threat_log_entry(self, entry: ThreatLogEntry):
        """Add entry to threat log with size management"""
        self.threat_log.append(entry)
        # Keep only the last 1000 entries
        if len(self.threat_log) > 1000:
            self.threat_log = self.threat_log[-1000:]
    
    def get_aircraft(self, aircraft_id: str) -> Optional[Aircraft]:
        """Get aircraft by ID with validation"""
        return self.aircraft.get(aircraft_id)
    
    def get_fleet_status(self) -> Dict[str, Any]:
        """Get comprehensive fleet status"""
        return {
            'aircraft': {aid: aircraft.to_dict() for aid, aircraft in self.aircraft.items()},
            'defense_systems': {name: system.to_dict() for name, system in self.defense_systems.items()},
            'threat_log': [entry.to_dict() for entry in self.threat_log[-20:]],
            'fleet_summary': {
                'total_aircraft': len(self.aircraft),
                'compromised_aircraft': sum(1 for aircraft in self.aircraft.values() if aircraft.is_compromised()),
                'active_threats': sum(1 for entry in self.threat_log[-50:] if not entry.resolved),
                'defense_systems_active': sum(1 for system in self.defense_systems.values() if system.enabled)
            }
        }


# Global fleet manager instance
fleet_manager = FleetManager()