"""
Ollama LLM Provider - Offline AI
100% offline, runs locally.
"""
import logging
import requests
from typing import Optional, List
from intelli.core.llm import LLMProvider

logger = logging.getLogger(__name__)

# Try to import ollama
try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logger.warning("Ollama not installed. Install with: pip install ollama")


class OllamaLLM(LLMProvider):
    """Ollama local LLM provider."""
    
    def __init__(self, model: str = "llama3.2", host: str = "http://localhost:11434"):
        self._model = model
        self._host = host
        self._client = None
        
        if OLLAMA_AVAILABLE:
            try:
                # Test connection
                response = requests.get(f"{host}/api/tags", timeout=2)
                if response.status_code == 200:
                    self._client = ollama
                    logger.info(f"Ollama connected with model: {model}")
                else:
                    logger.warning(f"Ollama not responding: {response.status_code}")
            except Exception as e:
                logger.warning(f"Ollama not available: {e}")
    
    @property
    def name(self) -> str:
        return "Ollama (Local)"
    
    @property
    def supports_offline(self) -> bool:
        return True
    
    @property
    def models(self) -> List[str]:
        """Get available models."""
        if not self.is_available():
            return []
        
        try:
            response = requests.get(f"{self._host}/api/tags", timeout=5)
            data = response.json()
            return [m['name'] for m in data.get('models', [])]
        except:
            return [self._model]
    
    def is_available(self) -> bool:
        """Check if Ollama is running."""
        if not OLLAMA_AVAILABLE:
            return False
        
        try:
            response = requests.get(f"{self._host}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
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
            
            response = ollama.chat(
                model=self._model,
                messages=messages,
                stream=False
            )
            
            return response['message']['content']
            
        except Exception as e:
            logger.error(f"Ollama generate error: {e}")
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
            
            response = ollama.chat(
                model=self._model,
                messages=messages,
                stream=True
            )
            
            for chunk in response:
                if chunk['message']['content']:
                    yield chunk['message']['content']
                    
        except Exception as e:
            logger.error(f"Ollama stream error: {e}")
            yield f"Error: {str(e)}"
    
    def download_model(self, model: str = "llama3.2"):
        """Download a model."""
        try:
            logger.info(f"Downloading model: {model}")
            ollama.pull(model)
            return True
        except Exception as e:
            logger.error(f"Download error: {e}")
            return False


def get_ollama_llm(model: str = "llama3.2", host: str = "http://localhost:11434") -> OllamaLLM:
    """Get Ollama LLM instance."""
    return OllamaLLM(model=model, host=host)