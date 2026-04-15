import datetime
import pyautogui
import speech_recognition as sr
import eel
import time
try:
    from HandGesture import Handgesture
except Exception as e:
    print(f"Warning: HandGesture module failed to load. Hand gestures disabled. {e}")
    Handgesture = None
from config import ASSISTANT_NAME
from helper import remove_words
from intelli.core.capabilities import detect_capabilities
from intelli.core.platform import PlatformAdapter
from intelli.core.router import IntentRouter
from intelli.core.safety import ask_voice_permission
from intelli.core.speech import create_tts_engine, speak_text
from intelli.core.brain import HybridBrain
from intelli.core.memory import MemoryManager
from intelli.handlers.basic import BasicHandlers
from intelli.handlers.media_info import MediaInfoHandlers
from intelli.handlers.registry import build_router
from intelli.handlers.social import SocialHandlers
from intelli.handlers.utility import UtilityHandlers

# from calculate import Calc

platform_adapter = PlatformAdapter()
_tts_engine = create_tts_engine()
intent_router = IntentRouter()
_capabilities = detect_capabilities(platform_adapter)

ai_brain = HybridBrain()
ai_memory = MemoryManager()


def speak(text):
    text = str(text)
    eel.DisplayMessage(text)
    eel.receiverText(text)
    speak_text(text, _tts_engine)


def _spoken_number_to_int(text):
    try:
        return int(text)
    except ValueError:
        pass

    word_map = {
        "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
        "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
    }
    return word_map.get(text.strip().lower())


def takecommand():

    r = sr.Recognizer()

    with sr.Microphone() as source:
        print('listening....')
        eel.DisplayMessage('listening....')
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        
        audio = r.listen(source, 10, 6)

    try:
        print('recognizing')
        eel.DisplayMessage('recognizing....')
        query = r.recognize_google(audio, language='en-in')
        print(f"user said: {query}")
        eel.DisplayMessage(query)
        time.sleep(2)
       
    except Exception as e:
        return ""
    
    return query.lower()


def _check_permission(action_name: str) -> bool:
    return ask_voice_permission(action_name, speak, takecommand)


_basic_handlers = BasicHandlers(
    speak=speak,
    takecommand=takecommand,
    platform_adapter=platform_adapter,
    pyautogui_module=pyautogui,
    permission_checker=_check_permission,
)
_utility_handlers = UtilityHandlers(
    speak=speak,
    takecommand=takecommand,
    spoken_number_to_int=_spoken_number_to_int,
    eel_module=eel,
    remove_words=remove_words,
    assistant_name=ASSISTANT_NAME,
)
_social_handlers = SocialHandlers(
    speak=speak,
    takecommand=takecommand,
    permission_checker=_check_permission,
    brain=ai_brain,
    memory=ai_memory,
)
from intelli.handlers.generation import GenerationHandlers

from intelli.handlers.communications import CommunicationsHandlers

_media_info_handlers = MediaInfoHandlers(
    speak=speak,
    takecommand=takecommand,
    eel_module=eel,
    pyautogui_module=pyautogui,
    handgesture_func=Handgesture,
    platform_adapter=platform_adapter,
    permission_checker=_check_permission,
)
_generation_handlers = GenerationHandlers(
    speak=speak,
    brain=ai_brain,
)
_communications_handlers = CommunicationsHandlers(
    speak=speak,
    takecommand=takecommand,
    permission_checker=_check_permission,
    platform_adapter=platform_adapter,
    assistant_name=ASSISTANT_NAME,
)
build_router(
    intent_router,
    _basic_handlers,
    _utility_handlers,
    _social_handlers,
    _media_info_handlers,
    _generation_handlers,
    _communications_handlers,
)

@eel.expose
def allCommands(message=1):

    if message == 1:
        query = takecommand()
        print(query)
        eel.senderText(query)
    else:
        query = message
        eel.senderText(query)
    try:
        if intent_router.dispatch(query):
            eel.ShowHood()
            return
        _social_handlers.handle_chat_fallback(query)
    except Exception as exc:
        print(f"error: {exc}")
    
    eel.ShowHood()


@eel.expose
def getSystemCapabilities():
    return {
        "os_name": _capabilities.os_name,
        "can_hotword": _capabilities.can_hotword,
        "can_screenshot": _capabilities.can_screenshot,
        "can_shutdown": _capabilities.can_shutdown,
        "has_camera_launcher": _capabilities.has_camera_launcher,
        "has_whatsapp_web": _capabilities.has_whatsapp_web,
    }

@eel.expose
def toggleScreenRecording():
    if platform_adapter._is_recording:
        platform_adapter.stop_screen_recording()
        return "stopped"
    else:
        # Default save path inside current directory
        import os
        from datetime import datetime
        now_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        out_path = os.path.join(os.getcwd(), f"recording_{now_str}.avi")
        if platform_adapter.start_screen_recording(out_path):
            return "recording"
        return "error"

@eel.expose
def updateVoiceSettings(voice_name, voice_speed):
    """Receive voice settings from frontend and update the speech module."""
    from intelli.core import speech
    speech.VOICE_NAME = voice_name
    speech.VOICE_SPEED = voice_speed
    print(f"Voice settings updated: voice={voice_name}, speed={voice_speed}")