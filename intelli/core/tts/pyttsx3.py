"""
pyttsx3 - Offline TTS Provider
100% offline, no internet required.
"""
import logging
from typing import Dict
from intelli.core.tts import TTSProvider

logger = logging.getLogger(__name__)

# Try to import pyttsx3
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    logger.warning("pyttsx3 not installed. Install with: pip install pyttsx3")


class Pyttsx3TTS(TTSProvider):
    """pyttsx3 offline TTS provider."""
    
    def __init__(self, rate: int = 180, voice_id: int = None):
        self._engine = None
        self._rate = rate
        self._voice_id = voice_id
        self._voices = {}
        
        if PYTTSX3_AVAILABLE:
            self._init_engine()
    
    def _init_engine(self):
        """Initialize pyttsx3 engine."""
        try:
            self._engine = pyttsx3.init()
            
            # Get available voices
            voices = self._engine.getProperty('voices')
            for i, voice in enumerate(voices):
                self._voices[voice.name] = str(i)
            
            # Set rate
            self._engine.setProperty('rate', self._rate)
            
            # Set voice if specified
            if self._voice_id is not None:
                self._engine.setProperty('voice', voices[self._voice_id].id)
            else:
                # Try to find English voice
                for voice in voices:
                    if 'english' in voice.name.lower():
                        self._engine.setProperty('voice', voice.id)
                        break
            
            logger.info("pyttsx3 initialized")
        except Exception as e:
            logger.error(f"Failed to initialize pyttsx3: {e}")
    
    @property
    def name(self) -> str:
        return "pyttsx3 Offline"
    
    @property
    def supports_offline(self) -> bool:
        return True
    
    @property
    def voices(self) -> Dict[str, str]:
        return self._voices
    
    def is_available(self) -> bool:
        return PYTTSX3_AVAILABLE and self._engine is not None
    
    def set_voice(self, voice_name: str):
        """Set voice by name."""
        if self._engine and voice_name in self._voices:
            voice_id = self._voices[voice_name]
            voices = self._engine.getProperty('voices')
            self._engine.setProperty('voice', voices[int(voice_id)].id)
    
    def set_rate(self, rate: str):
        """Set rate from string like '+15%'."""
        # Parse rate like '+15%' or '-10%'
        if rate.startswith('+') or rate.startswith('-'):
            base = 180
            try:
                percent = int(rate.strip('%+'))
                self._rate = base + (base * percent // 100)
                if self._engine:
                    self._engine.setProperty('rate', self._rate)
            except ValueError:
                pass
        else:
            try:
                self._rate = int(rate)
                if self._engine:
                    self._engine.setProperty('rate', self._rate)
            except ValueError:
                pass
    
    def speak(self, text: str) -> bool:
        """Speak the given text."""
        if not text or not self.is_available():
            return False
        
        try:
            self._engine.say(text)
            self._engine.runAndWait()
            return True
        except Exception as e:
            logger.error(f"pyttsx3 speak error: {e}")
            return False
    
    def stop(self):
        """Stop speaking."""
        if self._engine:
            try:
                self._engine.stop()
            except:
                pass


def get_pyttsx3_tts(rate: int = 180, voice_id: int = None) -> Pyttsx3TTS:
    """Get pyttsx3 TTS instance."""
    return Pyttsx3TTS(rate=rate, voice_id=voice_id)