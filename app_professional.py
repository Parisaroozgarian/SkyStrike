"""
Professional Aircraft Systems Threat Simulator - Master's Level Implementation
Enterprise-grade application with comprehensive security, monitoring, and analysis
"""
import os
from flask import Flask, render_template, session, request, jsonify
from datetime import datetime
import logging

# Professional imports
from config import config
from models import fleet_manager
from api.routes import api_bp
from utils.logging_config import ApplicationLogger, security_logger
from services.attack_service import AttackService
from services.defense_service import DefenseService

# Initialize professional logging
ApplicationLogger.setup_logging(debug=config.debug)
logger = logging.getLogger(__name__)

def create_app():
    """Professional application factory pattern"""
    app = Flask(__name__)
    
    # Configuration
    app.config.update({
        'SECRET_KEY': config.security.secret_key,
        'SESSION_COOKIE_SECURE': not config.debug,
        'SESSION_COOKIE_HTTPONLY': True,
        'SESSION_COOKIE_SAMESITE': 'Lax',
        'PERMANENT_SESSION_LIFETIME': config.security.session_timeout,
        'JSON_SORT_KEYS': False,
        'JSONIFY_PRETTYPRINT_REGULAR': config.debug
    })
    
    # Register blueprints
    app.register_blueprint(api_bp)
    
    # Initialize services (store in app config for access)
    app.config['ATTACK_SERVICE'] = AttackService(fleet_manager)
    app.config['DEFENSE_SERVICE'] = DefenseService(fleet_manager)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register routes
    register_routes(app)
    
    # Initialize session defaults
    @app.before_request
    def before_request():
        if 'current_aircraft' not in session:
            session['current_aircraft'] = 'aircraft_1'
            session['session_start'] = datetime.now().isoformat()
    
    # Security headers
    @app.after_request
    def after_request(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        if not config.debug:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response
    
    logger.info(f"Aviation Threat Simulator initialized - Environment: {config.environment.value}")
    return app


def register_error_handlers(app):
    """Register professional error handlers"""
    
    @app.errorhandler(404)
    def not_found(error):
        logger.warning(f"404 error: {request.url}")
        return render_template('error.html', 
                             error_code=404, 
                             error_message="Page not found"), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500 error: {str(error)}", exc_info=True)
        return render_template('error.html', 
                             error_code=500, 
                             error_message="Internal server error"), 500
    
    @app.errorhandler(403)
    def forbidden(error):
        logger.warning(f"403 error: {request.url}")
        return render_template('error.html', 
                             error_code=403, 
                             error_message="Access forbidden"), 403


def register_routes(app):
    """Register main application routes"""
    
    @app.route('/')
    def index():
        """Enhanced main dashboard with professional features"""
        try:
            aircraft_id = session.get('current_aircraft', 'aircraft_1')
            aircraft = fleet_manager.get_aircraft(aircraft_id)
            
            if not aircraft:
                # Fallback to first available aircraft
                aircraft_id = list(fleet_manager.aircraft.keys())[0]
                aircraft = fleet_manager.get_aircraft(aircraft_id)
                session['current_aircraft'] = aircraft_id
            
            # Enhanced context for template
            context = {
                'system_states': aircraft.to_dict() if aircraft else {},
                'threat_log': [entry.to_dict() for entry in fleet_manager.threat_log[-10:]],
                'fleet_manager': fleet_manager,
                'config': config.to_dict(),
                'current_aircraft': aircraft_id,
                'session_info': {
                    'start_time': session.get('session_start'),
                    'current_time': datetime.now().isoformat()
                }
            }
            
            # Log page access
            security_logger.log_security_event(
                'page_access', 'info', 
                f'Dashboard accessed for aircraft {aircraft.callsign if aircraft else "unknown"}'
            )
            
            return render_template('index_professional.html', **context)
            
        except Exception as e:
            logger.error(f"Error loading dashboard: {str(e)}")
            return render_template('error.html', 
                                 error_code=500, 
                                 error_message="Dashboard loading failed"), 500
    
    @app.route('/analytics')
    def analytics():
        """Professional analytics dashboard"""
        try:
            # Get comprehensive analytics
            fleet_status = fleet_manager.get_fleet_status()
            
            defense_service = app.config['DEFENSE_SERVICE']
            analytics_data = {
                'fleet_status': fleet_status,
                'threat_analysis': defense_service.analyze_threat_patterns(),
                'system_health': defense_service._assess_system_health(),
                'performance_metrics': {
                    'total_aircraft': len(fleet_manager.aircraft),
                    'active_threats': len([t for t in fleet_manager.threat_log[-50:] if not t.resolved]),
                    'defense_effectiveness': _calculate_defense_effectiveness(),
                    'system_availability': _calculate_system_availability()
                }
            }
            
            return render_template('analytics.html', **analytics_data)
            
        except Exception as e:
            logger.error(f"Error loading analytics: {str(e)}")
            return render_template('error.html', 
                                 error_code=500, 
                                 error_message="Analytics loading failed"), 500
    
    @app.route('/documentation')
    def documentation():
        """Professional API and system documentation"""
        try:
            return render_template('documentation.html', config=config.to_dict())
        except Exception as e:
            logger.error(f"Error loading documentation: {str(e)}")
            return render_template('error.html', 
                                 error_code=500, 
                                 error_message="Documentation loading failed"), 500
    
    @app.route('/health')
    def health_check():
        """Professional health check endpoint"""
        try:
            health_status = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'version': '2.0.0',
                'environment': config.environment.value,
                'services': {
                    'fleet_manager': 'operational',
                    'attack_service': 'operational',
                    'defense_service': 'operational'
                },
                'metrics': {
                    'total_aircraft': len(fleet_manager.aircraft),
                    'threat_log_entries': len(fleet_manager.threat_log),
                    'active_defenses': sum(1 for d in fleet_manager.defense_systems.values() if d.enabled)
                }
            }
            
            return jsonify(health_status)
            
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500


def _calculate_defense_effectiveness() -> float:
    """Calculate defense system effectiveness percentage"""
    try:
        total_attacks = len([t for t in fleet_manager.threat_log if t.system != 'Defense Systems'])
        if total_attacks == 0:
            return 100.0
        
        defense_responses = len([t for t in fleet_manager.threat_log if t.system == 'Defense Systems'])
        effectiveness = (defense_responses / total_attacks) * 100
        return round(min(effectiveness, 100.0), 2)
        
    except:
        return 0.0


def _calculate_system_availability() -> float:
    """Calculate overall system availability"""
    try:
        total_systems = len(fleet_manager.aircraft) * 3  # 3 systems per aircraft
        operational_systems = sum(
            sum([
                not aircraft.adsb.compromised,
                not aircraft.flight_control.compromised,
                not aircraft.communications.compromised
            ])
            for aircraft in fleet_manager.aircraft.values()
        )
        
        availability = (operational_systems / total_systems) * 100
        return round(availability, 2)
        
    except:
        return 0.0


# Create application instance
app = create_app()

if __name__ == '__main__':
    # Professional development server configuration
    app.run(
        host=config.host,
        port=config.port,
        debug=config.debug,
        threaded=True
    )