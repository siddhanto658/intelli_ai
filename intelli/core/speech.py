import os
import sys
import time
import subprocess
import re

# Configurable from the Settings panel via command.py → updateVoiceSettings()
VOICE_NAME = "en-US-AriaNeural"
VOICE_SPEED = "+15%"

def create_tts_engine():
    return None

def set_voice_preference(gender: str):
    pass

def clean_text_for_speech(text: str) -> str:
    # 1. Strip markdown characters like * _ ` # ~
    text = re.sub(r'[*_`#~|]+', '', text)
    # 2. Strip markdown links [text](url) -> text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    # 3. Strip bare URLs
    text = re.sub(r'https?://\S+', '', text)
    # 4. Strip emojis and non-ASCII symbols — keep only printable ASCII
    text = text.encode('ascii', 'ignore').decode('ascii')
    # 5. Collapse bullet markers like "- " at start of lines
    text = re.sub(r'^\s*[-*]\s+', '', text, flags=re.MULTILINE)
    # 6. Collapse extra whitespaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def speak_text(text: str, engine=None) -> None:
    if not text:
        return
        
    try:
        clean_text = clean_text_for_speech(text)
        if not clean_text:
            return
            
        filename = f"speech_{int(time.time()*1000)}.mp3"
        filepath = os.path.join(os.getcwd(), filename)
        
        # Use ultra-fast edge-tts with AriaNeural voice, boosted rate for natural flow
        edge_binary = os.path.join(os.path.dirname(sys.executable), "edge-tts")
        
        edge_cmd = [
            edge_binary,
            "--text", clean_text,
            "--voice", VOICE_NAME,
            "--rate", VOICE_SPEED,
            "--write-media", filepath
        ]
        
        result = subprocess.run(edge_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30)
        
        if result.returncode != 0 or not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
            # Fallback: if edge-tts failed, just skip audio
            if os.path.exists(filepath):
                os.remove(filepath)
            print(f"edge-tts failed (returncode={result.returncode})")
            return
        
        # Play using native Linux player
        subprocess.run(["mpg123", "-q", filepath], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
        
        if os.path.exists(filepath):
            os.remove(filepath)
            
    except Exception as e:
        print(f"Female TTS failed: {e}")
