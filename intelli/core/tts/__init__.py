"""
INTELLI AI - TTS Module
Modular Text-to-Speech with swappable providers.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class TTSProvider(ABC):
    """Base class for all TTS providers."""
    
    @abstractmethod
    def speak(self, text: str) -> bool:
        """Speak the given text."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""
        pass
    
    @property
    @abstractmethod
    def supports_offline(self) -> bool:
        """Whether this provider works offline."""
        pass
    
    @property
    def voices(self) -> Dict[str, str]:
        """Available voices."""
        return {}
    
    def set_voice(self, voice_name: str):
        """Set voice."""
        pass
    
    def set_rate(self, rate: str):
        """Set speech rate (e.g., '+15%')."""
        pass


class TTSManager:
    """Manages TTS providers and provides unified interface."""
    
    def __init__(self):
        self._providers: Dict[str, TTSProvider] = {}
        self._active_provider: Optional[TTSProvider] = None
        self._default_provider = "edge"
    
    def register(self, name: str, provider: TTSProvider):
        """Register a provider."""
        self._providers[name] = provider
    
    def set_active(self, name: str):
        """Set active provider."""
        if name in self._providers:
            self._active_provider = self._providers[name]
    
    def get_active(self) -> Optional[TTSProvider]:
        """Get active provider."""
        return self._active_provider
    
    def speak(self, text: str) -> bool:
        """Speak using active provider."""
        if self._active_provider is None:
            self.set_active(self._default_provider)
        return self._active_provider.speak(text) if self._active_provider else False
    
    def get_available_providers(self) -> Dict[str, Any]:
        """Get all available providers and their status."""
        return {
            name: {
                "available": provider.is_available(),
                "offline": provider.supports_offline,
                "name": provider.name,
                "voices": provider.voices
            }
            for name, provider in self._providers.items()
        }