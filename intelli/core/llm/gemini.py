"""
Gemini LLM Provider - Backup AI
Google's Gemini API as backup.
"""
import os
import logging
from typing import Optional, List
from intelli.core.llm import LLMProvider

logger = logging.getLogger(__name__)

# Try to import Google AI
try:
    import google.genai as genai
    GEMINI_NEW_SDK = True
except ImportError:
    try:
        import google.generativeai as genai
        GEMINI_NEW_SDK = False
    except ImportError:
        genai = None
        GEMINI_NEW_SDK = None
        logger.warning("Google AI SDK not installed")


class GeminiLLM(LLMProvider):
    """Google Gemini LLM provider."""
    
    def __init__(self, api_key: str = None, model: str = "gemini-2.0-flash"):
        self._api_key = api_key or os.getenv("GEMINI_API_KEY", "").strip()
        self._model = model
        self._client = None
        self._using_new_sdk = GEMINI_NEW_SDK
        
        if genai and self._api_key and self._api_key != "your_gemini_api_key_here":
            try:
                if GEMINI_NEW_SDK:
                    genai.configure(api_key=self._api_key)
                    self._client = genai.Client()
                else:
                    genai.configure(api_key=self._api_key)
                    self._client = genai.GenerativeModel(model)
                logger.info(f"Gemini initialized with model: {model}")
            except Exception as e:
                logger.error(f"Gemini init error: {e}")
        else:
            logger.warning("Gemini API key not found")
    
    @property
    def name(self) -> str:
        return "Google Gemini"
    
    @property
    def supports_offline(self) -> bool:
        return False
    
    @property
    def models(self) -> List[str]:
        return [
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
        ]
    
    def is_available(self) -> bool:
        return genai is not None and bool(self._api_key) and self._api_key != "your_gemini_api_key_here"
    
    def set_model(self, model: str):
        """Set the model to use."""
        self._model = model
    
    def generate(self, prompt: str, system_prompt: str = None) -> Optional[str]:
        """Generate response."""
        if not self.is_available():
            return None
        
        try:
            if self._using_new_sdk:
                full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
                response = self._client.models.generate_content(
                    model=self._model,
                    contents=full_prompt
                )
                return response.text
            else:
                if system_prompt:
                    self._client.system_prompt = system_prompt
                response = self._client.generate_content(prompt)
                return response.text
                
        except Exception as e:
            logger.error(f"Gemini generate error: {e}")
            return None
    
    def generate_stream(self, prompt: str, system_prompt: str = None):
        """Generate streaming response."""
        if not self.is_available():
            return
        
        try:
            if self._using_new_sdk:
                full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
                response = self._client.models.generate_content(
                    model=self._model,
                    contents=full_prompt
                )
                if hasattr(response, 'text'):
                    yield response.text
            else:
                if system_prompt:
                    self._client.system_prompt = system_prompt
                response = self._client.generate_content(prompt, stream=True)
                for chunk in response:
                    if chunk.text:
                        yield chunk.text
                        
        except Exception as e:
            logger.error(f"Gemini stream error: {e}")
            yield f"Error: {str(e)}"


def get_gemini_llm(api_key: str = None, model: str = "gemini-2.0-flash") -> GeminiLLM:
    """Get Gemini LLM instance."""
    return GeminiLLM(api_key=api_key, model=model)