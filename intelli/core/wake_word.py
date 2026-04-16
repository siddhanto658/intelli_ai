"""
INTELLI AI - Wake Word Detection Module
Uses pyaudio with speech recognition for wake word detection.
Simple and free - no paid Porcupine required.
"""
import threading
import time
import logging
import speech_recognition as sr

logger = logging.getLogger(__name__)


class WakeWordDetector:
    """
    Simple wake word detection using speech recognition.
    Listens for audio, recognizes speech, and checks for wake words.
    """
    
    def __init__(self, keywords=None):
        self.keywords = keywords or ['intelli', 'computer', 'hey intelli', 'hey computer']
        self._running = False
        self._thread = None
        self._recognizer = None
        
    def start(self, callback):
        """Start listening for wake words."""
        self._running = True
        self._thread = threading.Thread(target=self._listen_loop, args=(callback,), daemon=True)
        self._thread.start()
        logger.info("Wake word detection started")
    
    def _listen_loop(self, callback):
        """Main listening loop using speech recognition."""
        self._recognizer = sr.Recognizer()
        self._recognizer.energy_threshold = 3000
        self._recognizer.dynamic_energy_threshold = True
        
        logger.info("Listening for wake words...")
        
        while self._running:
            try:
                with sr.Microphone() as source:
                    self._recognizer.adjust_for_ambient_noise(source, duration=1)
                    logger.info("Waiting for speech...")
                    audio = self._recognizer.listen(source, timeout=10, phrase_time_limit=4)
                
                logger.info("Processing audio...")
                query = self._recognizer.recognize_google(audio, language='en-in').lower()
                logger.info(f"Heard: '{query}'")
                
                # Check for wake word match
                for wake_word in self.keywords:
                    if wake_word in query:
                        logger.info(f">>> WAKE WORD DETECTED: '{wake_word}' <<<")
                        callback()
                        time.sleep(1.5)  # Debounce
                        break
                        
            except sr.WaitTimeoutError:
                pass
            except sr.UnknownValueError:
                logger.debug("Could not understand audio")
            except sr.RequestError as e:
                logger.error(f"Speech recognition error: {e}")
            except Exception as e:
                if self._running:
                    logger.error(f"Wake word detection error: {e}")
                continue
    
    def stop(self):
        """Stop listening for wake words."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=3)
        logger.info("Wake word detection stopped")


# Singleton instance
_wake_word_detector = None

def get_wake_word_detector():
    """Get or create wake word detector singleton."""
    global _wake_word_detector
    if _wake_word_detector is None:
        _wake_word_detector = WakeWordDetector()
    return _wake_word_detector

def start_wake_word_detection(callback):
    """Start wake word detection with callback."""
    detector = get_wake_word_detector()
    detector.start(callback)

def stop_wake_word_detection():
    """Stop wake word detection."""
    global _wake_word_detector
    if _wake_word_detector:
        _wake_word_detector.stop()
        _wake_word_detector = None
