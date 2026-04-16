"""
INTELLI AI - Voice Activity Detection (VAD) Module
Detects when user stops speaking for better voice command handling.
"""
import threading
import time
import logging
import collections

logger = logging.getLogger(__name__)

# Try to import webrtcvad for better VAD
try:
    import webrtcvad
    _WEBRTC_AVAILABLE = True
except ImportError:
    logger.warning("webrtcvad not installed. Using simple VAD.")
    logger.warning("Install with: pip install webrtcvad")
    _WEBRTC_AVAILABLE = False
    webrtcvad = None


class VoiceActivityDetector:
    """
    Voice Activity Detection using WebRTC VAD or simple energy-based detection.
    Helps detect when user stops speaking.
    """
    
    def __init__(self, sample_rate=16000, frame_duration_ms=30, aggressiveness=2):
        """
        Initialize VAD.
        
        Args:
            sample_rate: Audio sample rate (8000, 16000, 32000, 48000)
            frame_duration_ms: Frame duration in milliseconds (10, 20, 30)
            aggressiveness: VAD aggressiveness 0-3 (higher = more filtering)
        """
        self.sample_rate = sample_rate
        self.frame_duration_ms = frame_duration_ms
        self.aggressiveness = aggressiveness
        
        self._vad = None
        self._running = False
        self._thread = None
        self._callback = None
        self._audio_buffer = collections.deque(maxlen=100)
        
        if _WEBRTC_AVAILABLE:
            self._init_webrtc_vad()
        else:
            self._init_simple_vad()
    
    def _init_webrtc_vad(self):
        """Initialize WebRTC VAD."""
        try:
            self._vad = webrtcvad.Vad(aggressiveness)
            logger.info(f"WebRTC VAD initialized (aggressiveness: {aggressiveness})")
        except Exception as e:
            logger.error(f"Failed to init WebRTC VAD: {e}")
            self._vad = None
    
    def _init_simple_vad(self):
        """Initialize simple energy-based VAD."""
        self._energy_threshold = 3000
        logger.info("Simple VAD initialized")
    
    def is_speech(self, audio_frame) -> bool:
        """Check if audio frame contains speech."""
        if self._vad and _WEBRTC_AVAILABLE:
            try:
                return self._vad.is_speech(audio_frame, self.sample_rate)
            except:
                return self._detect_energy(audio_frame)
        else:
            return self._detect_energy(audio_frame)
    
    def _detect_energy(self, audio_frame) -> bool:
        """Simple energy-based speech detection."""
        try:
            import struct
            # Calculate RMS energy
            count = len(audio_frame) // 2
            shorts = struct.unpack(f"{count}h", audio_frame)
            energy = sum(abs(s) for s in shorts) / count
            return energy > self._energy_threshold
        except:
            return False
    
    def start(self, audio_source, on_speech_end=None):
        """
        Start VAD on audio source.
        
        Args:
            audio_source: Audio source (microphone stream)
            on_speech_end: Callback when speech ends
        """
        self._audio_source = audio_source
        self._callback = on_speech_end
        self._running = True
        self._thread = threading.Thread(target=self._vad_loop, daemon=True)
        self._thread.start()
        logger.info("VAD started")
    
    def _vad_loop(self):
        """Main VAD loop."""
        try:
            import pyaudio
            pa = pyaudio.PyAudio()
            stream = pa.open(
                rate=self.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                start=False
            )
            stream.start_stream()
            
            frame_size = int(self.sample_rate * self.frame_duration_ms / 1000) * 2  # 16-bit
            
            silence_frames = 0
            speech_frames = 0
            in_speech = False
            min_speech_frames = 10  # Minimum frames to consider as speech
            silence_threshold = 30  # Frames of silence to end speech
            
            while self._running:
                try:
                    frame = stream.read(frame_size, exception_on_overflow=False)
                    
                    if self.is_speech(frame):
                        speech_frames += 1
                        silence_frames = 0
                        if not in_speech and speech_frames >= min_speech_frames:
                            in_speech = True
                    else:
                        silence_frames += 1
                        if in_speech and silence_frames >= silence_threshold:
                            in_speech = False
                            speech_frames = 0
                            if self._callback:
                                self._callback()
                
                except Exception as e:
                    logger.error(f"VAD loop error: {e}")
            
            stream.stop_stream()
            stream.close()
            pa.terminate()
            
        except Exception as e:
            logger.error(f"VAD error: {e}")
    
    def stop(self):
        """Stop VAD."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        logger.info("VAD stopped")


class SmartListener:
    """
    Smart voice listener with VAD and timeout.
    Automatically detects when user stops speaking.
    """
    
    def __init__(self):
        self.timeout = 5.0  # Max seconds to listen
        self.speech_timeout = 2.0  # Seconds of silence to stop listening
        self._listening = False
    
    def listen(self, recognizer, source) -> str:
        """
        Listen with automatic silence detection.
        
        Returns:
            Recognized text or empty string
        """
        import speech_recognition as sr
        
        self._listening = True
        audio_data = []
        last_speech_time = time.time()
        
        try:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            while self._listening:
                # Check timeout
                if time.time() - last_speech_time > self.timeout:
                    break
                
                try:
                    chunk = recognizer.listen(source, timeout=1.0, phrase_time_limit=3.0)
                    audio_data.append(chunk)
                    last_speech_time = time.time()
                except sr.WaitTimeoutError:
                    # Check if too long since last speech
                    if time.time() - last_speech_time > self.speech_timeout:
                        break
                    continue
            
            # Combine and recognize
            if audio_data:
                audio = sr.AudioData(b''.join(a.get_wav_data() for a in audio_data), 
                                     source.SAMPLE_RATE, 
                                     source.SAMPLE_WIDTH)
                text = recognizer.recognize_google(audio, language='en-in')
                return text
                
        except Exception as e:
            logger.error(f"SmartListener error: {e}")
        finally:
            self._listening = False
        
        return ""
    
    def stop(self):
        """Stop listening."""
        self._listening = False


# Singleton
_smart_listener = None

def get_smart_listener():
    """Get smart listener singleton."""
    global _smart_listener
    if _smart_listener is None:
        _smart_listener = SmartListener()
    return _smart_listener
