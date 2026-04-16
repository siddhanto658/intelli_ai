import os
import sys
import time
import subprocess
import re
import platform
import threading
from intelli.core.thread_safe import stop_listening, ThreadSafeFlag

# Configurable from the Settings panel via command.py -> updateVoiceSettings()
VOICE_NAME = "en-US-AriaNeural"
VOICE_SPEED = "+15%"

# Speech-specific stop flag
_speech_stopped = ThreadSafeFlag(False)
_speaking = False

def stop_speech():
    """Stop any ongoing speech immediately."""
    global _speaking
    _speech_stopped.set()
    _speaking = False
    stop_listening.set()

def create_tts_engine():
    return None

def set_voice_preference(gender: str):
    pass

def clean_text_for_speech(text: str) -> str:
    text = re.sub(r'[*_`#~|]+', '', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'https?://\S+', '', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'^\s*[-*]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def speak_text(text: str, engine=None) -> None:
    global _speaking
    
    if not text:
        return
    
    if _speech_stopped.is_set:
        _speech_stopped.clear()
        return
    
    _speaking = True
    _speech_stopped.clear()
    stop_listening.set()
    
    try:
        clean_text = clean_text_for_speech(text)
        if not clean_text:
            return
            
        filename = f"speech_{int(time.time()*1000)}.mp3"
        filepath = os.path.join(os.getcwd(), filename)
        
        # Generate speech using edge-tts
        edge_cmd = [
            sys.executable, "-m", "edge_tts",
            "--text", clean_text,
            "--voice", VOICE_NAME,
            "--rate", VOICE_SPEED,
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
            print(f"edge-tts failed (returncode={result.returncode})")
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except:
                    pass
            _speak_fallback(clean_text)
            return
        
        # Play audio and wait for it to finish
        _play_audio(filepath)
        
    except subprocess.TimeoutExpired:
        print("TTS timeout")
    except Exception as e:
        print(f"TTS error: {e}")
        try:
            _speak_fallback(clean_text)
        except:
            pass
    finally:
        _speaking = False
        stop_listening.clear()


def _play_audio(filepath: str):
    """Play audio file and wait for completion."""
    if _speech_stopped.is_set:
        return
    
    try:
        if platform.system() == "Windows":
            # Use PowerShell to play audio - blocks until finished
            # This is more reliable than playsound
            ps_script = f'''
            $file = "{filepath.replace("\\", "\\\\")}"
            $player = New-Object System.Media.SoundPlayer $file
            $player.PlaySync()
            $player.Dispose()
            '''
            proc = subprocess.Popen(
                ['powershell', '-Command', ps_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Wait for playback to finish or stop signal
            while proc.poll() is None:
                if _speech_stopped.is_set:
                    proc.terminate()
                    break
                time.sleep(0.1)
                
        else:
            # Linux/Mac - use aplay or similar
            subprocess.run(['aplay', filepath], check=False, timeout=60)
            
    except Exception as e:
        print(f"Play error: {e}")
        # Simple fallback - cross-platform
        try:
            if platform.system() == "Windows":
                os.startfile(filepath)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", filepath], check=False)
            else:  # Linux
                subprocess.run(["xdg-open", filepath], check=False)
        except:
            pass


def _speak_fallback(text: str):
    """Fallback TTS using pyttsx3."""
    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty('rate', 180)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Fallback TTS failed: {e}")