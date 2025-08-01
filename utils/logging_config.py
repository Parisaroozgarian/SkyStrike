"""
Professional logging configuration with structured logging
"""
import logging
import logging.handlers
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception information if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields from the record
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'lineno', 'funcName', 'created',
                          'msecs', 'relativeCreated', 'thread', 'threadName',
                          'processName', 'process', 'exc_info', 'exc_text', 'stack']:
                log_entry[key] = value
        
        return json.dumps(log_entry, default=str)


class SecurityLogger:
    """Security-focused logging for threat simulation"""
    
    def __init__(self, name: str = 'aviation_security'):
        self.logger = logging.getLogger(name)
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup logging handlers"""
        if self.logger.handlers:
            return  # Already configured
        
        self.logger.setLevel(logging.INFO)
        
        # Console handler with structured format
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = StructuredFormatter()
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # Prevent duplicate logging
        self.logger.propagate = False
    
    def log_attack_simulation(self, aircraft_id: str, attack_type: str, 
                            success: bool, details: Dict[str, Any]):
        """Log attack simulation events"""
        self.logger.info(
            "Attack simulation executed",
            extra={
                'event_type': 'attack_simulation',
                'aircraft_id': aircraft_id,
                'attack_type': attack_type,
                'success': success,
                'details': details
            }
        )
    
    def log_defense_activation(self, defense_system: str, trigger: str, 
                             aircraft_id: Optional[str] = None):
        """Log defense system activations"""
        self.logger.info(
            "Defense system activated",
            extra={
                'event_type': 'defense_activation',
                'defense_system': defense_system,
                'trigger': trigger,
                'aircraft_id': aircraft_id
            }
        )
    
    def log_system_recovery(self, aircraft_id: str, systems_reset: list):
        """Log system recovery events"""
        self.logger.info(
            "System recovery completed",
            extra={
                'event_type': 'system_recovery',
                'aircraft_id': aircraft_id,
                'systems_reset': systems_reset
            }
        )
    
    def log_threat_analysis(self, analysis_results: Dict[str, Any]):
        """Log threat analysis results"""
        self.logger.info(
            "Threat analysis completed",
            extra={
                'event_type': 'threat_analysis',
                'results': analysis_results
            }
        )
    
    def log_security_event(self, event_type: str, severity: str, 
                          description: str, **kwargs):
        """Log general security events"""
        self.logger.log(
            getattr(logging, severity.upper(), logging.INFO),
            description,
            extra={
                'event_type': event_type,
                'severity': severity,
                **kwargs
            }
        )


class ApplicationLogger:
    """Application-wide logging configuration"""
    
    @staticmethod
    def setup_logging(debug: bool = False):
        """Setup application-wide logging"""
        # Root logger configuration
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG if debug else logging.INFO)
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG if debug else logging.INFO)
        
        # Format for console output
        if debug:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        else:
            formatter = StructuredFormatter()
        
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # Suppress noisy third-party loggers
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        
        return root_logger


# Global security logger instance
security_logger = SecurityLogger()


class AuditLogger:
    """Audit logging for compliance and analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger('aviation_audit')
        self._setup_audit_handlers()
    
    def _setup_audit_handlers(self):
        """Setup audit-specific handlers"""
        if self.logger.handlers:
            return
        
        self.logger.setLevel(logging.INFO)
        
        # Structured audit formatter
        audit_formatter = StructuredFormatter()
        
        # Console audit handler
        audit_handler = logging.StreamHandler(sys.stdout)
        audit_handler.setLevel(logging.INFO)
        audit_handler.setFormatter(audit_formatter)
        self.logger.addHandler(audit_handler)
        
        self.logger.propagate = False
    
    def log_user_action(self, action: str, details: Dict[str, Any]):
        """Log user actions for audit trail"""
        self.logger.info(
            f"User action: {action}",
            extra={
                'audit_type': 'user_action',
                'action': action,
                'timestamp': datetime.utcnow().isoformat(),
                'details': details
            }
        )
    
    def log_system_change(self, change_type: str, before: Any, after: Any, 
                         initiated_by: str = 'system'):
        """Log system state changes"""
        self.logger.info(
            f"System change: {change_type}",
            extra={
                'audit_type': 'system_change',
                'change_type': change_type,
                'before_state': before,
                'after_state': after,
                'initiated_by': initiated_by,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
    
    def log_security_incident(self, incident_type: str, severity: str, 
                            description: str, affected_systems: list):
        """Log security incidents"""
        self.logger.warning(
            f"Security incident: {incident_type}",
            extra={
                'audit_type': 'security_incident',
                'incident_type': incident_type,
                'severity': severity,
                'description': description,
                'affected_systems': affected_systems,
                'timestamp': datetime.utcnow().isoformat()
            }
        )


# Global audit logger instance
audit_logger = AuditLogger()