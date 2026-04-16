from datetime import datetime
import os
import platform
import sqlite3
import struct
import subprocess
import time
import webbrowser
from playsound import playsound
import eel
import pyaudio
import pyautogui
from command import speak
from config import ASSISTANT_NAME
import pywhatkit as kit

from helper import extract_yt_term, remove_words
from intelli.core.config import get_settings
from intelli.core.platform import PlatformAdapter
from intelli.core.logger import log_info, log_warning, log_error
from intelli.core.thread_safe import hotword_active
from intelli.core.wake_word import start_wake_word_detection, stop_wake_word_detection

con = sqlite3.connect("INTELLI.db")
cursor = con.cursor()
platform_adapter = PlatformAdapter()


def stop_hotword():
    """Stop the hotword listener."""
    hotword_active.clear()
    stop_wake_word_detection()
    log_info("Hotword listener stopped")


@eel.expose
def playAssistantSound():
    music_dir = os.path.join(os.getcwd(), "www", "assets", "audio", "start_sound.mp3")
    try:
        playsound(music_dir)
        log_info("Assistant sound played")
    except Exception as e:
        try:
            import winsound
            winsound.PlaySound(music_dir, winsound.SND_FILENAME)
        except Exception as e2:
            log_warning(f"Audio launch skipped: {e2}")


def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("open", "")
    query = query.lower()

    app_name = query.strip()

    if app_name != "":
        try:
            cursor.execute(
                'SELECT path FROM sys_command WHERE name IN (?)', (app_name,))
            results = cursor.fetchall()

            if len(results) != 0:
                speak("Opening "+query)
                if not platform_adapter.open_app(results[0][0]):
                    speak("not found")

            elif len(results) == 0: 
                cursor.execute(
                'SELECT url FROM web_command WHERE name IN (?)', (app_name,))
                results = cursor.fetchall()
                
                if len(results) != 0:
                    speak("Opening "+query)
                    webbrowser.open(results[0][0])

                else:
                    speak("Opening "+query)
                    if not platform_adapter.open_app(query):
                        speak("not found")
        except Exception as e:
            log_error(f"Error opening command: {e}")
            speak("something went wrong")


def searchGoogle(query):
    if "google" in query:
        import wikipedia as googleScrap
        query = query.replace("intelli","")
        query = query.replace("google search","")
        query = query.replace("google","")
        speak("This is what I found on google")

        try:
            kit.search(query)
            result = googleScrap.summary(query,2)
            speak(result)

        except:
            speak("No speakable output available")
            
            
def greetuser():
    current_time = datetime.now()
    hour = current_time.hour
    minute = current_time.minute
    log_info(f"Current time: {hour}:{minute}")
    if hour>=0 and hour<12:
        speak("Good Morning")
    elif hour >=12 and hour<=15:
        speak("Good Afternoon ")
    else:
        speak("Good Evening")
    speak("Please tell me, How can I help you?")
    

def PlayYoutube(query):
    search_term = extract_yt_term(query)
    speak("Playing "+search_term+" on YouTube")
    kit.playonyt(search_term)


def hotword():
    """
    Start wake word detection using Porcupine or fallback.
    This function is called by run.py to start listening.
    """
    log_info("INTELLI hotword listening started...")
    log_info("Say 'INTELLI' or 'Computer' to activate!")
    
    def on_wake_word():
        """Callback when wake word is detected."""
        log_info(">>> WAKE WORD DETECTED! <<<")
        _trigger_wake_word()
    
    # Start wake word detection
    start_wake_word_detection(on_wake_word)
    
    # Keep the thread alive
    while hotword_active.is_set:
        time.sleep(0.5)
    
    log_info("Hotword listener ended")


def _trigger_wake_word():
    """Called when wake word is detected - triggers welcome message."""
    import threading
    from command import speak
    
    def _welcome():
        try:
            log_info("Wake word triggered - starting welcome sequence")
            speak("Hello! How can I help you?", start_listening=True)
        except Exception as e:
            log_error(f"Welcome message error: {e}")
            try:
                eel.ShowHood()
            except:
                pass
    
    try:
        thread = threading.Thread(target=_welcome)
        thread.start()
    except Exception as e:
        log_error(f"Failed to start welcome thread: {e}")
