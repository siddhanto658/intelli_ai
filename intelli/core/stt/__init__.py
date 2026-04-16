"""
INTELLI AI - STT Module
Modular Speech-to-Text with swappable providers.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class STTProvider(ABC):
    """Base class for all STT providers."""
    
    @abstractmethod
    def listen(self, timeout: int = 5) -> Optional[str]:
        """Listen and return transcribed text."""
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


class STTManager:
    """Manages STT providers and provides unified interface."""
    
    def __init__(self):
        self._providers: Dict[str, STTProvider] = {}
        self._active_provider: Optional[STTProvider] = None
        self._default_provider = "google"
    
    def register(self, name: str, provider: STTProvider):
        """Register a provider."""
        self._providers[name] = provider
    
    def set_active(self, name: str):
        """Set active provider."""
        if name in self._providers:
            self._active_provider = self._providers[name]
    
    def get_active(self) -> Optional[STTProvider]:
        """Get active provider."""
        return self._active_provider
    
    def listen(self, timeout: int = 5) -> Optional[str]:
        """Listen using active provider."""
        if self._active_provider is None:
            # Fallback to default
            self.set_active(self._default_provider)
        return self._active_provider.listen(timeout) if self._active_provider else None
    
    def get_available_providers(self) -> Dict[str, Any]:
        """Get all available providers and their status."""
        return {
            name: {
                "available": provider.is_available(),
                "offline": provider.supports_offline,
                "name": provider.name
            }
            for name, provider in self._providers.items()
        }