import os
import sys
import time
import subprocess
import re
import platform
import threading
import ctypes

# Configurable from the Settings panel via command.py -> updateVoiceSettings()
VOICE_NAME = "en-US-AriaNeural"
VOICE_SPEED = "+15%"

# Stop flag for interrupting speech
_stop_speech = False
_speech_lock = threading.Lock()

def stop_speech():
    """Stop any ongoing speech immediately."""
    global _stop_speech
    with _speech_lock:
        _stop_speech = True

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
    global _stop_speech
    
    if not text:
        return
    
    with _speech_lock:
        _stop_speech = False
        
    try:
        clean_text = clean_text_for_speech(text)
        if not clean_text:
            return
            
        filename = f"speech_{int(time.time()*1000)}.mp3"
        filepath = os.path.join(os.getcwd(), filename)
        
        # Use edge-tts command line tool
        edge_cmd = [
            sys.executable, "-m", "edge_tts",
            "--text", clean_text,
            "--voice", VOICE_NAME,
            "--rate", VOICE_SPEED,
            "--write-media", filepath
        ]
        
        result = subprocess.run(edge_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30)
        
        if result.returncode != 0 or not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
            if os.path.exists(filepath):
                os.remove(filepath)
            print(f"edge-tts failed (returncode={result.returncode})")
            return
        
        # Play audio with stop capability - Windows compatible
        if platform.system() == "Windows":
            try:
                from playsound import playsound
                
                def play_with_check():
                    try:
                        playsound(filepath)
                    except Exception as e:
                        print(f"playsound error: {e}")
                
                play_thread = threading.Thread(target=play_with_check)
                play_thread.start()
                
                # Check stop flag while playing
                while play_thread.is_alive():
                    with _speech_lock:
                        if _stop_speech:
                            # Kill the process forcefully
                            try:
                                import winsound
                                winsound.PlaySound(None, winsound.SND_PURGE)
                            except:
                                pass
                            break
                    time.sleep(0.1)
                    
                play_thread.join(timeout=1)
                
            except Exception as e:
                print(f"playsound error: {e}")
        
        if os.path.exists(filepath):
            os.remove(filepath)
            
    except Exception as e:
        print(f"TTS failed: {e}")
