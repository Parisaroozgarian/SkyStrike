"""
Professional defense system service with automated threat response
"""
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging
from models import FleetManager, ThreatLogEntry, ThreatSeverity, SystemStatus

logger = logging.getLogger(__name__)


class DefenseService:
    """Advanced defense system management"""
    
    def __init__(self, fleet_manager: FleetManager):
        self.fleet_manager = fleet_manager
        self.auto_recovery_enabled = True
        self.threat_correlation_window = timedelta(minutes=5)
        self.max_threat_threshold = 3
    
    def reset_aircraft_systems(self, aircraft_id: str) -> Dict[str, Any]:
        """Reset all systems for specific aircraft"""
        aircraft = self.fleet_manager.get_aircraft(aircraft_id)
        if not aircraft:
            return {'status': 'error', 'message': 'Aircraft not found'}
        
        try:
            # Reset ADS-B system
            aircraft.adsb.status = SystemStatus.NORMAL
            aircraft.adsb.compromised = False
            aircraft.adsb.last_update = datetime.now()
            
            # Reset flight control system
            aircraft.flight_control.status = SystemStatus.NORMAL
            aircraft.flight_control.compromised = False
            aircraft.flight_control.last_update = datetime.now()
            
            # Reset communications system
            aircraft.communications.status = SystemStatus.NORMAL
            aircraft.communications.compromised = False
            aircraft.communications.last_update = datetime.now()
            
            # Log recovery action
            recovery_entry = ThreatLogEntry(
                timestamp=datetime.now(),
                system='Defense Systems',
                attack='System Recovery',
                description=f'All systems reset for {aircraft.callsign} - manual recovery initiated',
                severity=ThreatSeverity.INFO,
                aircraft_id=aircraft_id,
                resolved=True
            )
            self.fleet_manager.add_threat_log_entry(recovery_entry)
            
            logger.info(f"Systems reset for aircraft {aircraft.callsign}")
            
            return {
                'status': 'success',
                'message': f'All systems reset for {aircraft.callsign}',
                'aircraft': aircraft.to_dict()
            }
            
        except Exception as e:
            logger.error(f"System reset failed for {aircraft_id}: {str(e)}")
            return {'status': 'error', 'message': f'Reset failed: {str(e)}'}
    
    def reset_all_systems(self) -> Dict[str, Any]:
        """Reset all systems across entire fleet"""
        try:
            reset_count = 0
            for aircraft_id in self.fleet_manager.aircraft.keys():
                result = self.reset_aircraft_systems(aircraft_id)
                if result['status'] == 'success':
                    reset_count += 1
            
            # Reset defense systems
            for defense_system in self.fleet_manager.defense_systems.values():
                defense_system.status = SystemStatus.NORMAL
                defense_system.alerts_triggered = 0
                defense_system.activations = 0
                defense_system.last_alert = None
                defense_system.last_activation = None
            
            # Log fleet-wide recovery
            fleet_recovery_entry = ThreatLogEntry(
                timestamp=datetime.now(),
                system='Defense Systems',
                attack='Fleet Recovery',
                description=f'Complete fleet reset - {reset_count} aircraft systems restored',
                severity=ThreatSeverity.INFO,
                resolved=True
            )
            self.fleet_manager.add_threat_log_entry(fleet_recovery_entry)
            
            logger.info(f"Fleet-wide system reset completed for {reset_count} aircraft")
            
            return {
                'status': 'success',
                'message': f'Fleet reset completed - {reset_count} aircraft restored',
                'reset_count': reset_count
            }
            
        except Exception as e:
            logger.error(f"Fleet reset failed: {str(e)}")
            return {'status': 'error', 'message': f'Fleet reset failed: {str(e)}'}
    
    def clear_threat_log(self) -> Dict[str, Any]:
        """Clear threat log with backup"""
        try:
            cleared_count = len(self.fleet_manager.threat_log)
            self.fleet_manager.threat_log.clear()
            
            # Log the clearing action
            clear_entry = ThreatLogEntry(
                timestamp=datetime.now(),
                system='Defense Systems',
                attack='Log Maintenance',
                description=f'Threat log cleared - {cleared_count} entries archived',
                severity=ThreatSeverity.INFO,
                resolved=True
            )
            self.fleet_manager.add_threat_log_entry(clear_entry)
            
            logger.info(f"Threat log cleared - {cleared_count} entries removed")
            
            return {
                'status': 'success',
                'message': f'Threat log cleared - {cleared_count} entries archived',
                'cleared_count': cleared_count
            }
            
        except Exception as e:
            logger.error(f"Threat log clearing failed: {str(e)}")
            return {'status': 'error', 'message': f'Log clearing failed: {str(e)}'}
    
    def analyze_threat_patterns(self) -> Dict[str, Any]:
        """Analyze threat patterns for proactive defense"""
        try:
            now = datetime.now()
            recent_threats = [
                entry for entry in self.fleet_manager.threat_log
                if (now - entry.timestamp) <= self.threat_correlation_window
            ]
            
            # Analyze by system
            system_threats = {}
            aircraft_threats = {}
            severity_distribution = {}
            
            for threat in recent_threats:
                # Count by system
                system_threats[threat.system] = system_threats.get(threat.system, 0) + 1
                
                # Count by aircraft
                if threat.aircraft_id:
                    aircraft_threats[threat.aircraft_id] = aircraft_threats.get(threat.aircraft_id, 0) + 1
                
                # Count by severity
                severity_distribution[threat.severity.value] = severity_distribution.get(threat.severity.value, 0) + 1
            
            # Identify high-risk aircraft
            high_risk_aircraft = [
                aircraft_id for aircraft_id, count in aircraft_threats.items()
                if count >= self.max_threat_threshold
            ]
            
            # Generate recommendations
            recommendations = self._generate_defense_recommendations(
                system_threats, aircraft_threats, high_risk_aircraft
            )
            
            analysis = {
                'analysis_window': f'{self.threat_correlation_window.total_seconds()/60} minutes',
                'total_recent_threats': len(recent_threats),
                'system_breakdown': system_threats,
                'aircraft_breakdown': aircraft_threats,
                'severity_distribution': severity_distribution,
                'high_risk_aircraft': high_risk_aircraft,
                'recommendations': recommendations,
                'threat_level': self._calculate_overall_threat_level(recent_threats)
            }
            
            return {
                'status': 'success',
                'analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"Threat analysis failed: {str(e)}")
            return {'status': 'error', 'message': f'Analysis failed: {str(e)}'}
    
    def _generate_defense_recommendations(
        self, system_threats: Dict[str, int], 
        aircraft_threats: Dict[str, int], 
        high_risk_aircraft: List[str]
    ) -> List[str]:
        """Generate defense recommendations based on threat analysis"""
        recommendations = []
        
        # System-specific recommendations
        if system_threats.get('ADS-B', 0) > 2:
            recommendations.append("Consider implementing enhanced ADS-B validation protocols")
        
        if system_threats.get('Flight Control', 0) > 2:
            recommendations.append("Activate backup flight control systems")
        
        if system_threats.get('Communications', 0) > 2:
            recommendations.append("Switch to secondary communication frequencies")
        
        # Aircraft-specific recommendations
        if high_risk_aircraft:
            aircraft_names = []
            for aircraft_id in high_risk_aircraft:
                aircraft = self.fleet_manager.get_aircraft(aircraft_id)
                if aircraft:
                    aircraft_names.append(aircraft.callsign)
            
            recommendations.append(
                f"Prioritize monitoring for high-risk aircraft: {', '.join(aircraft_names)}"
            )
        
        # General recommendations
        if len(system_threats) > 5:
            recommendations.append("Consider elevating security posture across all systems")
        
        if not recommendations:
            recommendations.append("Current threat level acceptable - maintain standard monitoring")
        
        return recommendations
    
    def _calculate_overall_threat_level(self, recent_threats: List[ThreatLogEntry]) -> str:
        """Calculate overall threat level based on recent activity"""
        if not recent_threats:
            return "LOW"
        
        critical_count = sum(1 for t in recent_threats if t.severity == ThreatSeverity.CRITICAL)
        high_count = sum(1 for t in recent_threats if t.severity == ThreatSeverity.HIGH)
        
        if critical_count >= 3:
            return "CRITICAL"
        elif critical_count >= 1 or high_count >= 3:
            return "HIGH"
        elif len(recent_threats) >= 5:
            return "MEDIUM"
        else:
            return "LOW"
    
    def enable_defense_system(self, system_name: str) -> Dict[str, Any]:
        """Enable specific defense system"""
        if system_name not in self.fleet_manager.defense_systems:
            return {'status': 'error', 'message': 'Unknown defense system'}
        
        defense_system = self.fleet_manager.defense_systems[system_name]
        defense_system.enabled = True
        defense_system.status = SystemStatus.NORMAL
        
        # Log activation
        activation_entry = ThreatLogEntry(
            timestamp=datetime.now(),
            system='Defense Systems',
            attack='System Activation',
            description=f'{system_name.replace("_", " ").title()} defense system enabled',
            severity=ThreatSeverity.INFO,
            resolved=True
        )
        self.fleet_manager.add_threat_log_entry(activation_entry)
        
        return {
            'status': 'success',
            'message': f'{system_name.replace("_", " ").title()} defense system enabled',
            'system_status': defense_system.to_dict()
        }
    
    def disable_defense_system(self, system_name: str) -> Dict[str, Any]:
        """Disable specific defense system"""
        if system_name not in self.fleet_manager.defense_systems:
            return {'status': 'error', 'message': 'Unknown defense system'}
        
        defense_system = self.fleet_manager.defense_systems[system_name]
        defense_system.enabled = False
        defense_system.status = SystemStatus.OFFLINE
        
        # Log deactivation
        deactivation_entry = ThreatLogEntry(
            timestamp=datetime.now(),
            system='Defense Systems',
            attack='System Deactivation',
            description=f'{system_name.replace("_", " ").title()} defense system disabled',
            severity=ThreatSeverity.INFO,
            resolved=True
        )
        self.fleet_manager.add_threat_log_entry(deactivation_entry)
        
        return {
            'status': 'success',
            'message': f'{system_name.replace("_", " ").title()} defense system disabled',
            'system_status': defense_system.to_dict()
        }
    
    def get_defense_status(self) -> Dict[str, Any]:
        """Get comprehensive defense system status"""
        try:
            threat_analysis = self.analyze_threat_patterns()
            
            return {
                'status': 'success',
                'defense_systems': {
                    name: system.to_dict() 
                    for name, system in self.fleet_manager.defense_systems.items()
                },
                'threat_analysis': threat_analysis.get('analysis', {}),
                'auto_recovery_enabled': self.auto_recovery_enabled,
                'system_health': self._assess_system_health()
            }
            
        except Exception as e:
            logger.error(f"Defense status check failed: {str(e)}")
            return {'status': 'error', 'message': f'Status check failed: {str(e)}'}
    
    def _assess_system_health(self) -> Dict[str, str]:
        """Assess overall system health"""
        compromised_aircraft = sum(
            1 for aircraft in self.fleet_manager.aircraft.values() 
            if aircraft.is_compromised()
        )
        
        total_aircraft = len(self.fleet_manager.aircraft)
        
        if compromised_aircraft == 0:
            overall_health = "EXCELLENT"
        elif compromised_aircraft / total_aircraft <= 0.33:
            overall_health = "GOOD"
        elif compromised_aircraft / total_aircraft <= 0.66:
            overall_health = "DEGRADED"
        else:
            overall_health = "CRITICAL"
        
        active_defenses = sum(
            1 for system in self.fleet_manager.defense_systems.values()
            if system.enabled
        )
        
        return {
            'overall_health': overall_health,
            'compromised_aircraft': f"{compromised_aircraft}/{total_aircraft}",
            'active_defenses': f"{active_defenses}/{len(self.fleet_manager.defense_systems)}",
            'recommendation': self._get_health_recommendation(overall_health)
        }
    
    def _get_health_recommendation(self, health_status: str) -> str:
        """Get recommendation based on system health"""
        recommendations = {
            'EXCELLENT': 'All systems operating normally - maintain current posture',
            'GOOD': 'Minor issues detected - continue monitoring',
            'DEGRADED': 'Multiple systems compromised - consider immediate action',
            'CRITICAL': 'Fleet-wide compromise detected - initiate emergency protocols'
        }
        return recommendations.get(health_status, 'Unknown status - manual assessment required')