"""
Environment configuration

Provides environment-based configuration support.
"""

import os
from enum import Enum
from typing import Optional


class Profile(Enum):
    """Application profiles"""
    DEVELOPMENT = "dev"
    PRODUCTION = "prod"
    TEST = "test"


class Environment:
    """
    Environment configuration manager
    
    Manages application profiles and environment-specific settings.
    Similar to Spring Boot's @Profile and Environment.
    """
    
    def __init__(self, active_profile: Optional[Profile] = None):
        self._active_profile = active_profile or self._detect_profile()
    
    def _detect_profile(self) -> Profile:
        """Detect active profile from environment"""
        profile_str = os.environ.get('STARSPRING_PROFILE', 'dev').lower()
        
        for profile in Profile:
            if profile.value == profile_str:
                return profile
        
        return Profile.DEVELOPMENT
    
    @property
    def active_profile(self) -> Profile:
        """Get the active profile"""
        return self._active_profile
    
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self._active_profile == Profile.DEVELOPMENT
    
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self._active_profile == Profile.PRODUCTION
    
    def is_test(self) -> bool:
        """Check if running in test mode"""
        return self._active_profile == Profile.TEST
    
    def get_env(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get environment variable"""
        return os.environ.get(key, default)
    
    def set_profile(self, profile: Profile) -> None:
        """Set the active profile"""
        self._active_profile = profile


# Global environment instance
_environment: Optional[Environment] = None


def get_environment() -> Environment:
    """Get the global environment instance"""
    global _environment
    if _environment is None:
        _environment = Environment()
    return _environment


def set_environment(env: Environment) -> None:
    """Set the global environment instance"""
    global _environment
    _environment = env
