"""
Professional API routes with comprehensive error handling and validation
"""
from flask import Blueprint, request, jsonify, session
from datetime import datetime
from typing import Dict, Any
import logging

from models import fleet_manager, AttackVector, ThreatSeverity
from services.attack_service import AttackService
from services.defense_service import DefenseService
from utils.validators import InputValidator, ValidationError
from utils.logging_config import security_logger, audit_logger

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Initialize services
attack_service = AttackService(fleet_manager)
defense_service = DefenseService(fleet_manager)

logger = logging.getLogger(__name__)


@api_bp.errorhandler(ValidationError)
def handle_validation_error(e):
    """Handle validation errors"""
    logger.warning(f"Validation error: {str(e)}")
    return jsonify({
        'status': 'error',
        'error_type': 'validation_error',
        'message': str(e)
    }), 400


@api_bp.errorhandler(Exception)
def handle_general_error(e):
    """Handle general API errors"""
    logger.error(f"API error: {str(e)}", exc_info=True)
    return jsonify({
        'status': 'error',
        'error_type': 'internal_error',
        'message': 'An internal error occurred'
    }), 500


@api_bp.route('/system_status', methods=['GET'])
def get_system_status():
    """Get current system status for selected aircraft"""
    try:
        aircraft_id = session.get('current_aircraft', 'aircraft_1')
        aircraft = fleet_manager.get_aircraft(aircraft_id)
        
        if not aircraft:
            return jsonify({
                'status': 'error',
                'message': 'Aircraft not found'
            }), 404
        
        response_data = {
            'status': 'success',
            'systems': aircraft.to_dict(),
            'defense_systems': {name: system.to_dict() for name, system in fleet_manager.defense_systems.items()},
            'threat_log': [entry.to_dict() for entry in fleet_manager.threat_log[-10:]],
            'aircraft_fleet': {aid: aircraft.to_dict() for aid, aircraft in fleet_manager.aircraft.items()},
            'current_aircraft': aircraft_id
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve system status'
        }), 500


@api_bp.route('/fleet_status', methods=['GET'])
def get_fleet_status():
    """Get comprehensive fleet status"""
    try:
        fleet_status = fleet_manager.get_fleet_status()
        
        # Add fleet-wide analytics
        fleet_status['analytics'] = {
            'total_attacks_simulated': len([
                entry for entry in fleet_manager.threat_log 
                if 'attack' in entry.attack.lower() and entry.system != 'Defense Systems'
            ]),
            'defense_activations': len([
                entry for entry in fleet_manager.threat_log 
                if entry.system == 'Defense Systems'
            ]),
            'uptime_percentage': _calculate_fleet_uptime(),
            'threat_level': _assess_current_threat_level()
        }
        
        return jsonify({
            'status': 'success',
            **fleet_status
        })
        
    except Exception as e:
        logger.error(f"Error getting fleet status: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve fleet status'
        }), 500


@api_bp.route('/select_aircraft', methods=['POST'])
def select_aircraft():
    """Select aircraft for detailed monitoring"""
    try:
        data = request.get_json()
        if not data:
            raise ValidationError("No data provided")
        
        aircraft_id = data.get('aircraft_id')
        if not aircraft_id:
            raise ValidationError("aircraft_id is required")
        
        if not InputValidator.validate_aircraft_id(aircraft_id):
            raise ValidationError("Invalid aircraft_id format")
        
        aircraft = fleet_manager.get_aircraft(aircraft_id)
        if not aircraft:
            raise ValidationError("Aircraft not found")
        
        # Update session
        session['current_aircraft'] = aircraft_id
        
        # Log aircraft selection
        audit_logger.log_user_action('aircraft_selection', {
            'aircraft_id': aircraft_id,
            'callsign': aircraft.callsign,
            'model': aircraft.model
        })
        
        return jsonify({
            'status': 'success',
            'message': f'Selected {aircraft.callsign}',
            'aircraft': aircraft.to_dict()
        })
        
    except ValidationError as e:
        raise e
    except Exception as e:
        logger.error(f"Error selecting aircraft: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to select aircraft'
        }), 500


@api_bp.route('/simulate_attack', methods=['POST'])
def simulate_attack():
    """Execute cyber attack simulation"""
    try:
        data = request.get_json()
        if not data:
            raise ValidationError("No attack data provided")
        
        # Validate attack request
        is_valid, errors = InputValidator.validate_attack_request(data)
        if not is_valid:
            raise ValidationError(f"Invalid attack request: {'; '.join(errors)}")
        
        # Extract attack parameters
        system = data['system']
        attack_type = data['attack_type']
        aircraft_id = data.get('aircraft_id', session.get('current_aircraft', 'aircraft_1'))
        parameters = data.get('parameters', {})
        
        # Validate aircraft exists
        if not fleet_manager.get_aircraft(aircraft_id):
            raise ValidationError("Target aircraft not found")
        
        # Convert attack type to enum
        try:
            attack_vector = AttackVector(attack_type)
        except ValueError:
            raise ValidationError(f"Unknown attack type: {attack_type}")
        
        # Execute attack
        result = attack_service.execute_attack(attack_vector, aircraft_id, parameters)
        
        # Log attack simulation
        security_logger.log_attack_simulation(
            aircraft_id=aircraft_id,
            attack_type=attack_type,
            success=result['status'] == 'success',
            details=result
        )
        
        return jsonify(result)
        
    except ValidationError as e:
        raise e
    except Exception as e:
        logger.error(f"Error simulating attack: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Attack simulation failed'
        }), 500


@api_bp.route('/reset_system', methods=['POST'])
def reset_system():
    """Reset specific aircraft system"""
    try:
        data = request.get_json()
        if not data:
            raise ValidationError("No reset data provided")
        
        system = data.get('system')
        aircraft_id = data.get('aircraft_id', session.get('current_aircraft', 'aircraft_1'))
        
        if not system:
            raise ValidationError("System type is required")
        
        aircraft = fleet_manager.get_aircraft(aircraft_id)
        if not aircraft:
            raise ValidationError("Aircraft not found")
        
        # Reset specific system
        if system == 'adsb':
            aircraft.adsb.status = aircraft.adsb.status.NORMAL
            aircraft.adsb.compromised = False
            aircraft.adsb.last_update = datetime.now()
        elif system == 'flight_control':
            aircraft.flight_control.status = aircraft.flight_control.status.NORMAL
            aircraft.flight_control.compromised = False
            aircraft.flight_control.last_update = datetime.now()
        elif system == 'communications':
            aircraft.communications.status = aircraft.communications.status.NORMAL
            aircraft.communications.compromised = False
            aircraft.communications.last_update = datetime.now()
        else:
            raise ValidationError(f"Unknown system: {system}")
        
        # Log system reset
        security_logger.log_system_recovery(aircraft_id, [system])
        
        return jsonify({
            'status': 'success',
            'message': f'{system.replace("_", " ").title()} system reset for {aircraft.callsign}',
            'aircraft': aircraft.to_dict()
        })
        
    except ValidationError as e:
        raise e
    except Exception as e:
        logger.error(f"Error resetting system: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'System reset failed'
        }), 500


@api_bp.route('/reset_all', methods=['POST'])
def reset_all_systems():
    """Reset all systems across the fleet"""
    try:
        result = defense_service.reset_all_systems()
        
        # Log fleet reset
        audit_logger.log_user_action('fleet_reset', {
            'reset_count': result.get('reset_count', 0),
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error resetting all systems: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Fleet reset failed'
        }), 500


@api_bp.route('/clear_log', methods=['POST'])
def clear_threat_log():
    """Clear threat log"""
    try:
        result = defense_service.clear_threat_log()
        
        # Log threat log clearing
        audit_logger.log_user_action('clear_threat_log', {
            'cleared_count': result.get('cleared_count', 0),
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error clearing threat log: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Log clearing failed'
        }), 500


@api_bp.route('/defense_status', methods=['GET'])
def get_defense_status():
    """Get comprehensive defense system status"""
    try:
        result = defense_service.get_defense_status()
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error getting defense status: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve defense status'
        }), 500


@api_bp.route('/threat_analysis', methods=['GET'])
def get_threat_analysis():
    """Get advanced threat analysis"""
    try:
        analysis = defense_service.analyze_threat_patterns()
        
        # Log threat analysis request
        security_logger.log_threat_analysis(analysis.get('analysis', {}))
        
        return jsonify(analysis)
        
    except Exception as e:
        logger.error(f"Error performing threat analysis: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Threat analysis failed'
        }), 500


@api_bp.route('/config', methods=['GET'])
def get_configuration():
    """Get current application configuration"""
    try:
        from config import config
        
        return jsonify({
            'status': 'success',
            'configuration': config.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error getting configuration: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to retrieve configuration'
        }), 500


def _calculate_fleet_uptime() -> float:
    """Calculate fleet-wide uptime percentage"""
    try:
        total_systems = len(fleet_manager.aircraft) * 3  # 3 systems per aircraft
        compromised_systems = sum(
            sum([aircraft.adsb.compromised, aircraft.flight_control.compromised, aircraft.communications.compromised])
            for aircraft in fleet_manager.aircraft.values()
        )
        
        uptime = ((total_systems - compromised_systems) / total_systems) * 100
        return round(uptime, 2)
        
    except:
        return 100.0


def _assess_current_threat_level() -> str:
    """Assess current threat level across fleet"""
    try:
        recent_threats = fleet_manager.threat_log[-20:]  # Last 20 entries
        
        critical_count = sum(1 for t in recent_threats if t.severity == ThreatSeverity.CRITICAL)
        high_count = sum(1 for t in recent_threats if t.severity == ThreatSeverity.HIGH)
        
        if critical_count >= 3:
            return "CRITICAL"
        elif critical_count >= 1 or high_count >= 3:
            return "HIGH"
        elif len(recent_threats) >= 10:
            return "MEDIUM"
        else:
            return "LOW"
            
    except:
        return "UNKNOWN"