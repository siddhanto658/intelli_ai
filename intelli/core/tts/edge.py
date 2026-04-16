"""
Edge TTS - Default TTS Provider
Free, excellent quality, natural voice.
"""
import os
import sys
import subprocess
import time
import platform
import logging
from typing import Dict
from intelli.core.tts import TTSProvider

logger = logging.getLogger(__name__)

# Configurable from settings
DEFAULT_VOICE = "en-US-AriaNeural"
DEFAULT_RATE = "+15%"


class EdgeTTS(TTSProvider):
    """Microsoft Edge TTS provider."""
    
    def __init__(self, voice: str = DEFAULT_VOICE, rate: str = DEFAULT_RATE):
        self._voice = voice
        self._rate = rate
    
    @property
    def name(self) -> str:
        return "Microsoft Edge TTS"
    
    @property
    def supports_offline(self) -> bool:
        return False
    
    @property
    def voices(self) -> Dict[str, str]:
        return {
            "en-US-AriaNeural": "Aria (US)",
            "en-US-JennyNeural": "Jenny (US)",
            "en-GB-SoniaNeural": "Sonia (UK)",
            "en-IN-NeerjaNeural": "Neerja (IN)",
            "en-US-GuyNeural": "Guy (US)",
            "en-AU-NatashaNeural": "Natasha (AU)",
        }
    
    def is_available(self) -> bool:
        """Check if Edge TTS is available."""
        # Check if edge-tts is installed
        try:
            result = subprocess.run(
                [sys.executable, "-m", "edge_tts", "--help"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def set_voice(self, voice_name: str):
        """Set voice."""
        self._voice = voice_name
    
    def set_rate(self, rate: str):
        """Set speech rate."""
        self._rate = rate
    
    def speak(self, text: str) -> bool:
        """Speak the given text."""
        if not text:
            return False
        
        try:
            # Clean text
            text = self._clean_text(text)
            if not text:
                return False
            
            # Generate audio file
            filename = f"speech_{int(time.time()*1000)}.mp3"
            filepath = os.path.join(os.getcwd(), filename)
            
            edge_cmd = [
                sys.executable, "-m", "edge_tts",
                "--text", text,
                "--voice", self._voice,
                "--rate", self._rate,
                "--write-media", filepath
            ]
            
            creation_flags = subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
            
            result = subprocess.run(
                edge_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=30,
                creationflags=creation_flags
            )
            
            if result.returncode != 0 or not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
                if os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                    except:
                        pass
                logger.error("Edge TTS failed to generate audio")
                return False
            
            # Play audio
            self._play_audio(filepath)
            
            # Cleanup
            try:
                os.remove(filepath)
            except:
                pass
            
            return True
            
        except subprocess.TimeoutExpired:
            logger.error("Edge TTS timeout")
            return False
        except Exception as e:
            logger.error(f"Edge TTS error: {e}")
            return False
    
    def _clean_text(self, text: str) -> str:
        """Clean text for speech."""
        import re
        text = re.sub(r'[*_`#~|]+', '', text)
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        text = re.sub(r'https?://\S+', '', text)
        text = text.encode('ascii', 'ignore').decode('ascii')
        text = re.sub(r'^\s*[-*]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def _play_audio(self, filepath: str):
        """Play audio file."""
        try:
            if platform.system() == "Windows":
                # Use PowerShell for blocking playback
                ps_script = f'''
                $file = "{filepath.replace("\\", "\\\\")}"
                $player = New-Object System.Media.SoundPlayer $file
                $player.PlaySync()
                $player.Dispose()
                '''
                subprocess.run(
                    ['powershell', '-Command', ps_script],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                # Linux/Mac
                subprocess.run(['aplay', filepath], check=False, timeout=60)
        except Exception as e:
            logger.error(f"Play error: {e}")
            # Fallback
            try:
                os.startfile(filepath)
            except:
                pass


def get_edge_tts(voice: str = DEFAULT_VOICE, rate: str = DEFAULT_RATE) -> EdgeTTS:
    """Get Edge TTS instance."""
    return EdgeTTS(voice=voice, rate=rate)