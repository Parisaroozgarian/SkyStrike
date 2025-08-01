"""
Configuration management for Aircraft Systems Threat Simulator
Professional configuration with environment-based settings and validation
"""
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class Environment(Enum):
    """Environment types for configuration management"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


@dataclass
class DatabaseConfig:
    """Database configuration settings"""
    url: str
    pool_size: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False


@dataclass
class SecurityConfig:
    """Security-related configuration"""
    secret_key: str
    session_timeout: int = 3600
    csrf_protection: bool = True
    rate_limit_per_minute: int = 100


@dataclass
class SimulatorConfig:
    """Simulator-specific configuration"""
    update_interval: int = 2000  # milliseconds
    max_threat_log_entries: int = 1000
    defense_system_timeout: int = 300  # seconds
    max_concurrent_attacks: int = 5


class Config:
    """Main configuration class with environment-specific settings"""
    
    def __init__(self, environment: Optional[str] = None):
        env_value = environment or os.getenv('FLASK_ENV', 'development')
        self.environment = Environment(env_value)
        self._load_config()
        self._validate_config()
    
    def _load_config(self):
        """Load configuration based on environment"""
        # Database configuration
        self.database = DatabaseConfig(
            url=os.getenv('DATABASE_URL', 'sqlite:///aviation_simulator.db'),
            pool_size=int(os.getenv('DB_POOL_SIZE', '10')),
            echo=self.environment == Environment.DEVELOPMENT
        )
        
        # Security configuration
        self.security = SecurityConfig(
            secret_key=os.getenv('SESSION_SECRET', self._generate_default_secret()),
            session_timeout=int(os.getenv('SESSION_TIMEOUT', '3600')),
            rate_limit_per_minute=int(os.getenv('RATE_LIMIT', '100'))
        )
        
        # Simulator configuration
        self.simulator = SimulatorConfig(
            update_interval=int(os.getenv('UPDATE_INTERVAL', '2000')),
            max_threat_log_entries=int(os.getenv('MAX_LOG_ENTRIES', '1000')),
            defense_system_timeout=int(os.getenv('DEFENSE_TIMEOUT', '300'))
        )
        
        # Application settings
        self.debug = self.environment == Environment.DEVELOPMENT
        self.testing = self.environment == Environment.TESTING
        self.host = os.getenv('HOST', '0.0.0.0')
        self.port = int(os.getenv('PORT', '5000'))
    
    def _generate_default_secret(self) -> str:
        """Generate a default secret key for development"""
        if self.environment == Environment.PRODUCTION:
            raise ValueError("SESSION_SECRET environment variable must be set in production")
        return "dev-secret-key-change-in-production"
    
    def _validate_config(self):
        """Validate configuration settings"""
        if not self.security.secret_key:
            raise ValueError("Secret key cannot be empty")
        
        if self.simulator.update_interval < 1000:
            raise ValueError("Update interval must be at least 1000ms")
        
        if self.simulator.max_threat_log_entries < 100:
            raise ValueError("Maximum log entries must be at least 100")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for JSON serialization"""
        return {
            'environment': self.environment.value,
            'debug': self.debug,
            'database': {
                'pool_size': self.database.pool_size,
                'pool_timeout': self.database.pool_timeout
            },
            'simulator': {
                'update_interval': self.simulator.update_interval,
                'max_threat_log_entries': self.simulator.max_threat_log_entries,
                'defense_system_timeout': self.simulator.defense_system_timeout
            }
        }


# Global configuration instance
config = Config()