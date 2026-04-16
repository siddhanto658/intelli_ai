"""
INTELLI AI - Provider Configuration Loader
Loads provider settings from YAML config file.
"""
import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Try to import yaml
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    logger.warning("PyYAML not installed. Install with: pip install pyyaml")


class Config:
    """Configuration manager for INTELLI providers."""
    
    def __init__(self, config_path: str = None):
        self._config_path = config_path or self._get_default_config_path()
        self._config = {}
        self._load_config()
    
    def _get_default_config_path(self) -> str:
        """Get default config path."""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        return os.path.join(base_dir, "config", "providers.yaml")
    
    def _load_config(self):
        """Load configuration from YAML file."""
        if not YAML_AVAILABLE:
            logger.warning("YAML not available, using defaults")
            self._set_defaults()
            return
        
        if not os.path.exists(self._config_path):
            logger.warning(f"Config file not found: {self._config_path}")
            self._set_defaults()
            return
        
        try:
            with open(self._config_path, 'r') as f:
                self._config = yaml.safe_load(f)
            logger.info(f"Config loaded from: {self._config_path}")
        except Exception as e:
            logger.error(f"Config load error: {e}")
            self._set_defaults()
    
    def _set_defaults(self):
        """Set default configuration."""
        self._config = {
            'stt': {'active': 'google'},
            'tts': {'active': 'edge'},
            'llm': {'active': 'groq', 'fallback': 'gemini'},
            'memory': {
                'rag_enabled': True,
                'prompt_protection_enabled': True
            },
            'offline': {'enabled': True},
            'features': {
                'streaming': True,
                'multi_turn': True,
                'multilingual': True
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get config value."""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    def get_stt_config(self) -> Dict:
        """Get STT configuration."""
        return self._config.get('stt', {})
    
    def get_tts_config(self) -> Dict:
        """Get TTS configuration."""
        return self._config.get('tts', {})
    
    def get_llm_config(self) -> Dict:
        """Get LLM configuration."""
        return self._config.get('llm', {})
    
    def get_memory_config(self) -> Dict:
        """Get memory configuration."""
        return self._config.get('memory', {})
    
    def get_offline_config(self) -> Dict:
        """Get offline configuration."""
        return self._config.get('offline', {})
    
    def get_active_stt(self) -> str:
        """Get active STT provider."""
        return self.get('stt.active', 'google')
    
    def get_active_tts(self) -> str:
        """Get active TTS provider."""
        return self.get('tts.active', 'edge')
    
    def get_active_llm(self) -> str:
        """Get active LLM provider."""
        return self.get('llm.active', 'groq')
    
    def get_fallback_llm(self) -> str:
        """Get fallback LLM provider."""
        return self.get('llm.fallback', 'gemini')
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if feature is enabled."""
        return self.get(f'features.{feature}', True)
    
    def is_offline_enabled(self) -> bool:
        """Check if offline mode is enabled."""
        return self.get('offline.enabled', True)


# Global config instance
_config = None

def get_provider_config() -> Config:
    """Get global config instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def reload_config():
    """Reload configuration."""
    global _config
    _config = Config()