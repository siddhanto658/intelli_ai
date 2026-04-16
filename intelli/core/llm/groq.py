"""
Groq LLM Provider - Default AI Brain
Fast, free tier available.
"""
import os
import logging
from typing import Optional, List
from intelli.core.llm import LLMProvider

logger = logging.getLogger(__name__)

# Try to import groq
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    logger.warning("Groq not installed. Install with: pip install groq")


class GroqLLM(LLMProvider):
    """Groq API LLM provider."""
    
    def __init__(self, api_key: str = None, model: str = "llama-3.3-70b-versatile"):
        self._api_key = api_key or os.getenv("GROQ_API_KEY", "").strip()
        self._model = model
        self._client = None
        
        if GROQ_AVAILABLE and self._api_key:
            self._client = Groq(api_key=self._api_key)
            logger.info(f"Groq initialized with model: {model}")
        else:
            logger.warning("Groq API key not found")
    
    @property
    def name(self) -> str:
        return "Groq"
    
    @property
    def supports_offline(self) -> bool:
        return False
    
    @property
    def models(self) -> List[str]:
        return [
            "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma2-9b-it",
        ]
    
    def is_available(self) -> bool:
        return GROQ_AVAILABLE and bool(self._api_key) and self._client is not None
    
    def set_model(self, model: str):
        """Set the model to use."""
        self._model = model
    
    def generate(self, prompt: str, system_prompt: str = None) -> Optional[str]:
        """Generate response."""
        if not self.is_available():
            return None
        
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=0.7,
                max_tokens=4096,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Groq generate error: {e}")
            return None
    
    def generate_stream(self, prompt: str, system_prompt: str = None):
        """Generate streaming response."""
        if not self.is_available():
            return
        
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=0.7,
                max_tokens=4096,
                stream=True,
            )
            
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"Groq stream error: {e}")
            yield f"Error: {str(e)}"


def get_groq_llm(api_key: str = None, model: str = "llama-3.3-70b-versatile") -> GroqLLM:
    """Get Groq LLM instance."""
    return GroqLLM(api_key=api_key, model=model)