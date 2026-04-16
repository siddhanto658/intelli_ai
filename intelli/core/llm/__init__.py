"""
INTELLI AI - LLM Module
Modular Language Model with swappable providers.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Generator


class LLMProvider(ABC):
    """Base class for all LLM providers."""
    
    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = None) -> Optional[str]:
        """Generate response from prompt."""
        pass
    
    @abstractmethod
    def generate_stream(self, prompt: str, system_prompt: str = None) -> Generator[str, None, None]:
        """Generate streaming response."""
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
    def models(self) -> List[str]:
        """Available models."""
        return []


class LLMManager:
    """Manages LLM providers and provides unified interface."""
    
    def __init__(self):
        self._providers: Dict[str, LLMProvider] = {}
        self._active_provider: Optional[LLMProvider] = None
        self._default_provider = "groq"
    
    def register(self, name: str, provider: LLMProvider):
        """Register a provider."""
        self._providers[name] = provider
    
    def set_active(self, name: str):
        """Set active provider."""
        if name in self._providers:
            self._active_provider = self._providers[name]
    
    def get_active(self) -> Optional[LLMProvider]:
        """Get active provider."""
        return self._active_provider
    
    def generate(self, prompt: str, system_prompt: str = None) -> Optional[str]:
        """Generate using active provider."""
        if self._active_provider is None:
            self.set_active(self._default_provider)
        return self._active_provider.generate(prompt, system_prompt) if self._active_provider else None
    
    def generate_stream(self, prompt: str, system_prompt: str = None) -> Generator[str, None, None]:
        """Generate streaming using active provider."""
        if self._active_provider is None:
            self.set_active(self._default_provider)
        if self._active_provider:
            yield from self._active_provider.generate_stream(prompt, system_prompt)
    
    def get_available_providers(self) -> Dict[str, Any]:
        """Get all available providers and their status."""
        return {
            name: {
                "available": provider.is_available(),
                "offline": provider.supports_offline,
                "name": provider.name,
                "models": provider.models
            }
            for name, provider in self._providers.items()
        }