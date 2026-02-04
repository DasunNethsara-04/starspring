"""
Application properties management

Provides configuration loading from YAML and properties files.
"""

import os
import yaml
from typing import Any, Dict, Optional
from pathlib import Path


class ApplicationProperties:
    """
    Application properties manager
    
    Loads configuration from application.yaml or application.properties files.
    Similar to Spring Boot's application properties.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self._properties: Dict[str, Any] = {}
        self._config_path = config_path
        
        if config_path:
            self.load(config_path)
    
    def load(self, config_path: str) -> None:
        """
        Load configuration from a file
        
        Args:
            config_path: Path to configuration file (YAML or properties)
        """
        path = Path(config_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        if path.suffix in ['.yaml', '.yml']:
            self._load_yaml(path)
        elif path.suffix == '.properties':
            self._load_properties(path)
        else:
            raise ValueError(f"Unsupported configuration file format: {path.suffix}")
    
    def _load_yaml(self, path: Path) -> None:
        """Load YAML configuration"""
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
            if data:
                self._properties = self._flatten_dict(data)
    
    def _load_properties(self, path: Path) -> None:
        """Load properties file"""
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        self._properties[key.strip()] = value.strip()
    
    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
        """Flatten nested dictionary with dot notation"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a property value
        
        Args:
            key: Property key (supports dot notation)
            default: Default value if key not found
            
        Returns:
            Property value or default
        """
        # Check environment variable override
        env_key = key.upper().replace('.', '_')
        env_value = os.environ.get(env_key)
        if env_value is not None:
            return env_value
        
        return self._properties.get(key, default)
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Get property as integer"""
        value = self.get(key, default)
        return int(value) if value is not None else default
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get property as boolean"""
        value = self.get(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', 'yes', '1', 'on')
        return bool(value)
    
    def get_list(self, key: str, default: list = None) -> list:
        """Get property as list"""
        value = self.get(key, default or [])
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [item.strip() for item in value.split(',')]
        return default or []
    
    def set(self, key: str, value: Any) -> None:
        """Set a property value"""
        self._properties[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """Get all properties"""
        return self._properties.copy()


# Global properties instance
_app_properties: Optional[ApplicationProperties] = None


def get_properties() -> ApplicationProperties:
    """Get the global application properties instance"""
    global _app_properties
    if _app_properties is None:
        _app_properties = ApplicationProperties()
    return _app_properties


def set_properties(properties: ApplicationProperties) -> None:
    """Set the global application properties instance"""
    global _app_properties
    _app_properties = properties


def get_property(key: str, default: Any = None) -> Any:
    """Convenience function to get a property"""
    return get_properties().get(key, default)
