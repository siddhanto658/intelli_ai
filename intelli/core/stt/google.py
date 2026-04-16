"""
Google Speech Recognition - Default STT Provider
"""
import speech_recognition as sr
from typing import Optional
import logging
from intelli.core.stt import STTProvider

logger = logging.getLogger(__name__)


class GoogleSTT(STTProvider):
    """Google Speech Recognition provider."""
    
    def __init__(self, language: str = "en-in"):
        self._recognizer = sr.Recognizer()
        self._language = language
        self._recognizer.pause_threshold = 2.0
    
    @property
    def name(self) -> str:
        return "Google Speech Recognition"
    
    @property
    def supports_offline(self) -> bool:
        return False
    
    def is_available(self) -> bool:
        """Check if Google STT is available."""
        try:
            # Just check if we can create a recognizer
            r = sr.Recognizer()
            return True
        except Exception:
            return False
    
    def listen(self, timeout: int = 5) -> Optional[str]:
        """Listen and transcribe speech."""
        try:
            with sr.Microphone() as source:
                self._recognizer.adjust_for_ambient_noise(source, duration=0.5)
                logger.info("Listening...")
                audio = self._recognizer.listen(source, timeout=timeout, phrase_time_limit=4)
            
            logger.info("Transcribing...")
            text = self._recognizer.recognize_google(audio, language=self._language)
            logger.info(f"Transcribed: {text}")
            return text.lower()
            
        except sr.WaitTimeoutError:
            logger.warning("No speech detected (timeout)")
            return None
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Google STT request error: {e}")
            return None
        except Exception as e:
            logger.error(f"STT error: {e}")
            return None
    
    def adjust_threshold(self, energy_threshold: int = 3000):
        """Adjust microphone energy threshold."""
        self._recognizer.energy_threshold = energy_threshold


def get_google_stt() -> GoogleSTT:
    """Get Google STT instance."""
    return GoogleSTT()