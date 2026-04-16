import datetime
import pyautogui
import speech_recognition as sr
import eel
import time
import threading
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
from intelli.core.speech import create_tts_engine, speak_text, stop_speech
from intelli.core.brain import HybridBrain
from intelli.core.logger import log_info, log_warning, log_error, logger
from intelli.core.thread_safe import stop_listening, is_speaking, is_listening
from intelli.handlers.basic import BasicHandlers
from intelli.handlers.media_info import MediaInfoHandlers
from intelli.handlers.registry import build_router
from intelli.handlers.social import SocialHandlers
from intelli.handlers.utility import UtilityHandlers
from intelli.handlers.generation import GenerationHandlers
from intelli.handlers.communications import CommunicationsHandlers


def show_notification(toast_type: str, title: str, message: str, duration: int = 4000):
    """Show a toast notification in the UI."""
    try:
        eel.showToast(toast_type, title, message, duration)
    except Exception as e:
        log_warning(f"Could not show toast: {e}")


platform_adapter = PlatformAdapter()
_tts_engine = create_tts_engine()
intent_router = IntentRouter()
_capabilities = detect_capabilities(platform_adapter)

ai_brain = HybridBrain()

_current_ai_model = "gemini"
_current_groq_model = "llama-3.3-70b-versatile"

# Multi-turn conversation mode
_conversation_mode = False
_streaming_active = False
_current_stream_text = ""


def _listen_for_stop():
    """Background thread to listen for stop command while AI is speaking."""
    r = sr.Recognizer()
    log_info("Stop-listener thread started")
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.3)
            while not stop_listening.is_set():  # Fixed: was incorrectly using .is_set as a property
                try:
                    audio = r.listen(source, timeout=1, phrase_time_limit=2)
                    query = r.recognize_google(audio, language='en-in').lower()
                    stop_words = ['stop', 'quiet', 'shut up', 'enough', 'pause', 'wait', 'cancel', 'be quiet', 'exit', 'done', 'thank you']
                    if any(word in query for word in stop_words):
                        log_info("Stop command detected - interrupting")
                        stop_speech()
                        global _conversation_mode
                        _conversation_mode = False
                        break
                except:
                    continue
    except Exception as e:
        log_error(f"Stop-listener error: {e}")
    finally:
        stop_listening.clear()
        is_speaking.clear()
        log_info("Stop-listener thread ended")


# Track if we're already in speak() to prevent nested calls
_speaking = False

def speak(text, start_listening=False):
    global _speaking
    
    text = str(text)
    log_info(f"Speaking: {text[:50]}...")
    
    if _speaking:
        log_warning("Already speaking, skipping duplicate call")
        return
    
    _speaking = True
    
    try:
        try:
            eel.receiverText(text)
        except Exception as e:
            log_warning(f"eel display error: {e}")
        
        # No background stop-listener - stop via button/keyboard only
        speak_text(text, _tts_engine)
        
    finally:
        _speaking = False
    
    if start_listening:
        time.sleep(0.3)
        allCommands(1)


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
    lang_code = 'en-in'
    
    try:
        is_listening.set()
        
        # Show listening UI
        try:
            eel.showListeningVisual()
            eel.updateListeningText("Listening...")
        except:
            pass
        
        with sr.Microphone() as source:
            log_info("Listening for voice command...")
            r.pause_threshold = 2.0
            r.adjust_for_ambient_noise(source, duration=0.5)
            
            # Update UI to show we're waiting for speech
            try:
                eel.updateListeningText("Speak now...")
            except:
                pass
            
            audio = r.listen(source, 5, 4)

        log_info("Recognizing speech...")
        
        # Show processing
        try:
            eel.updateListeningText("Processing...")
        except:
            pass
        
        query = r.recognize_google(audio, language=lang_code)
        log_info(f"User said: {query}")
        
        # Show what was heard
        try:
            eel.updateTranscript(query)
        except:
            pass
        
        query = ai_brain.preprocess_multilingual(query.lower())
        is_listening.clear()
        return query.lower()
        
    except sr.WaitTimeoutError:
        log_warning("No speech detected (timeout)")
        is_listening.clear()
        return ""
    except sr.UnknownValueError:
        log_warning("Could not understand audio")
        is_listening.clear()
        return ""
    except Exception as e:
        log_error(f"Speech recognition error: {e}")
        is_listening.clear()
        return ""


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
)

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


def _streaming_callback(token: str):
    """Callback for streaming tokens - sends to frontend."""
    global _current_stream_text, _streaming_active
    _current_stream_text += token
    try:
        eel.streamToken(token)
    except:
        pass


def _handle_ai_response(query: str, use_streaming: bool = True):
    """Handle AI response with optional streaming."""
    global _conversation_mode, _streaming_active, _current_stream_text
    global stop_listening, is_speaking
    
    _streaming_active = True
    _current_stream_text = ""
    
    # Check for stop words in query
    stop_commands = ['exit', 'quit', 'stop', 'done', 'thank you', 'that\'s all', 'bye', 'goodbye']
    should_end_conversation = any(cmd in query.lower() for cmd in stop_commands)
    
    if use_streaming:
        try:
            eel.startStream()
        except:
            pass
        
        # Generate streaming response
        result = ai_brain.generate_stream(query, _streaming_callback)
        
        _streaming_active = False
        stop_listening.clear()
        is_speaking.clear()
        
        if result:
            # Speak the response
            speak(result)
        else:
            try:
                eel.endStream("")
            except:
                pass
    else:
        # Non-streaming fallback
        try:
            eel.receiverText("Thinking...")
        except:
            pass
        
        if intent_router.dispatch(query):
            return
        _social_handlers.handle_chat_fallback(query)
    
    # Handle conversation mode
    if _conversation_mode and not should_end_conversation and not stop_listening.is_set:
        # Continue conversation
        try:
            eel.receiverText("Listening for follow-up...")
        except:
            pass
        
        follow_up = takecommand()
        if follow_up:
            _handle_ai_response(follow_up, use_streaming=True)
        else:
            _conversation_mode = False
            try:
                eel.ShowHood()
            except:
                pass
    else:
        _conversation_mode = False
        try:
            eel.ShowHood()
        except:
            pass


@eel.expose
def allCommands(message=1):
    global _conversation_mode
    try:
        if message == 1:
            try:
                eel.receiverText("Listening...")
            except:
                pass
            query = takecommand()
            if not query:
                log_warning("No voice input detected")
                try:
                    eel.ShowHood()
                except:
                    pass
                return
            log_info(f"Command received: {query}")
            try:
                eel.senderText(query)
            except:
                pass
        else:
            query = message
            log_info(f"Text input: {query}")
            try:
                eel.senderText(query)
            except:
                pass
        
        if not query.strip():
            try:
                eel.ShowHood()
            except:
                pass
            return
        
        # Check if it's a command or chat
        if intent_router.dispatch(query):
            _conversation_mode = False
            try:
                eel.ShowHood()
            except:
                pass
            return
        
        # AI Chat - use streaming and enable multi-turn
        _conversation_mode = True
        _handle_ai_response(query, use_streaming=True)
        
    except KeyboardInterrupt:
        log_info("Command interrupted by user")
        _conversation_mode = False
        try:
            eel.ShowHood()
        except:
            pass
    except Exception as exc:
        log_error(f"Command error: {exc}", exc_info=True)
        _conversation_mode = False
        try:
            eel.showToast('error', 'Error', 'Something went wrong.')
        except:
            pass
        try:
            speak("Sorry, I encountered an error. Please try again.")
        except:
            pass
        try:
            eel.ShowHood()
        except:
            pass


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
        import os
        from datetime import datetime
        now_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        out_path = os.path.join(os.getcwd(), f"recording_{now_str}.avi")
        if platform_adapter.start_screen_recording(out_path):
            return "recording"
        return "error"


@eel.expose
def updateVoiceSettings(voice_name, voice_speed):
    from intelli.core import speech
    speech.VOICE_NAME = voice_name
    speech.VOICE_SPEED = voice_speed
    log_info(f"Voice settings updated: voice={voice_name}, speed={voice_speed}")


@eel.expose
def updateAiSettings(model, groq_model):
    global _current_ai_model, _current_groq_model
    _current_ai_model = model
    _current_groq_model = groq_model
    ai_brain.set_preferred_model(model, groq_model)
    log_info(f"AI settings updated: model={model}, groq_model={groq_model}")


@eel.expose
def checkApiKeysStatus():
    from intelli.core.config import get_settings
    settings = get_settings()
    return {
        "gemini": bool(settings.gemini_api_key),
        "groq": bool(settings.groq_api_key),
    }


@eel.expose
def clearChat():
    """Clear chat messages and AI memory."""
    ai_brain.clear_history()
    try:
        eel.clearChat()
    except:
        pass


@eel.expose
def stopCurrentAction():
    global _conversation_mode, _streaming_active
    log_info("Stop action requested")
    _conversation_mode = False
    _streaming_active = False
    
    # Don't stop audio - let it finish naturally
    # Stop button only handles UI state
    
    stop_listening.clear()
    is_speaking.clear()
    
    try:
        eel.stopTypewriterDisplay()
    except:
        pass
    try:
        eel.endStream(_current_stream_text)
    except:
        pass
    try:
        eel.ShowHood()
    except:
        pass
    return "stopped"


@eel.expose
def endSession():
    log_info("Ending session...")
    global _conversation_mode
    _conversation_mode = False
    stop_listening.clear()
    
    try:
        stop_speech()
    except:
        pass
    try:
        log_info("Session ended. Closing window...")
        eel.close_window()
    except Exception as e:
        log_warning(f"Could not close window: {e}")
    import sys
    sys.exit(0)


@eel.expose
def stopTypewriterDisplay():
    """Stop the typewriter animation."""
    pass
