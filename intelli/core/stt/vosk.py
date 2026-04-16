"""
Vosk - Offline STT Provider
100% offline, no internet required.
"""
import os
import logging
from typing import Optional
from intelli.core.stt import STTProvider

logger = logging.getLogger(__name__)

# Try to import vosk
try:
    from vosk import Model, KaldiRecognizer
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False
    logger.warning("Vosk not installed. Install with: pip3 install vosk")


class VoskSTT(STTProvider):
    """Vosk offline speech recognition."""
    
    def __init__(self, model_path: str = None, language: str = "en"):
        self._model_path = model_path or self._get_default_model_path()
        self._model = None
        self._recognizer = None
        self._language = language
        
        if VOSK_AVAILABLE:
            self._init_model()
    
    def _get_default_model_path(self) -> str:
        """Get default model path."""
        # Look for model in common locations
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        model_dirs = [
            os.path.join(base_dir, "models", "vosk-model-en"),
            os.path.join(base_dir, "vosk-model-en"),
            "models/vosk-model-en",
            "vosk-model-en",
        ]
        
        for path in model_dirs:
            if os.path.exists(path):
                return path
        
        # Return default to download
        return "models/vosk-model-en"
    
    def _init_model(self):
        """Initialize Vosk model."""
        if not os.path.exists(self._model_path):
            logger.warning(f"Vosk model not found at: {self._model_path}")
            logger.info("Download model from: https://alphacephei.com/vosk/models")
            return
        
        try:
            self._model = Model(self._model_path)
            sample_rate = 16000
            self._recognizer = KaldiRecognizer(self._model, sample_rate)
            logger.info(f"Vosk model loaded from: {self._model_path}")
        except Exception as e:
            logger.error(f"Failed to load Vosk model: {e}")
    
    @property
    def name(self) -> str:
        return "Vosk Offline"
    
    @property
    def supports_offline(self) -> bool:
        return True
    
    def is_available(self) -> bool:
        """Check if Vosk is available."""
        return VOSK_AVAILABLE and self._model is not None
    
    def listen(self, timeout: int = 5) -> Optional[str]:
        """Listen and transcribe speech."""
        if not self.is_available():
            logger.error("Vosk not available")
            return None
        
        try:
            import pyaudio
            
            p = pyaudio.PyAudio()
            stream = p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=4096
            )
            
            logger.info("Listening (offline)...")
            
            # Listen for audio
            frames = []
            import time
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                data = stream.read(4096, exception_on_overflow=False)
                if self._recognizer.AcceptWaveform(data):
                    result = self._recognizer.Result()
                    stream.stop_stream()
                    stream.close()
                    p.terminate()
                    
                    import json
                    result_dict = json.loads(result)
                    text = result_dict.get("text", "")
                    if text:
                        logger.info(f"Transcribed: {text}")
                        return text.lower()
                    return None
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            logger.warning("No speech detected (timeout)")
            return None
            
        except Exception as e:
            logger.error(f"Vosk listen error: {e}")
            return None
    
    def download_model(self, language: str = "en"):
        """Download model for language."""
        models = {
            "en": "vosk-model-en-us-0.22",
            "en-in": "vosk-model-en-in-0.4",
            "hi": "vosk-model-hi-0.22",
        }
        
        model_name = models.get(language, "vosk-model-en-us-0.22")
        logger.info(f"Download from: https://alphacephei.com/vosk/models/{model_name}.zip")
        return model_name


def get_vosk_stt(model_path: str = None) -> VoskSTT:
    """Get Vosk STT instance."""
    return VoskSTT(model_path=model_path)