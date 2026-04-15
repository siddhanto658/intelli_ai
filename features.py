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
# Playing assiatnt sound function
import pywhatkit as kit
import pvporcupine

from helper import extract_yt_term, remove_words
try:
    from hugchat import hugchat
except Exception:
    hugchat = None
from intelli.core.config import get_settings
from intelli.core.platform import PlatformAdapter

con = sqlite3.connect("INTELLI.db")
cursor = con.cursor()
platform_adapter = PlatformAdapter()

# Hotword control flag
_hotword_active = True

@eel.expose
def playAssistantSound():
    music_dir = os.path.join(os.getcwd(), "www", "assets", "audio", "start_sound.mp3")
    try:
        # Try playsound first (cross-platform)
        playsound(music_dir)
    except Exception as e:
        try:
            # Fallback to Windows media player
            import winsound
            winsound.PlaySound(music_dir, winsound.SND_FILENAME)
        except Exception as e2:
            print(f"Audio launch skipped: {e2}")

    
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
            print(f"Error opening command: {e}")
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
    print("Current time: ", hour, ":", minute)
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
    import speech_recognition as sr
    import sys
    
    print("INTELLI hotword listening started...")
    print("Say 'INTELLI' or similar words to activate!")
    
    global _hotword_active
    sys.stdout.flush()
    
    while _hotword_active:
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 3000  # Lower threshold for better detection
        recognizer.dynamic_energy_threshold = True
        
        try:
            print("\n[ HOTWORD ] Listening...", end="")
            sys.stdout.flush()
            
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(source, timeout=8, phrase_time_limit=4)
            
            print(" Got audio! Recognizing...", end="")
            sys.stdout.flush()
            
            query = recognizer.recognize_google(audio, language='en-in').lower()
            print(f"\n[ HOTWORD ] Heard: '{query}'")
            sys.stdout.flush()
            
            # Check for matches - more flexible matching
            wake_words = [
                'intelli', 'tally', 'bently', 'gentle', 'dental', 'intel',
                'inteli', 'intalli', 'intilly', 'telly', 'belle', 'twenty',
                'intel', 'intell', 'tally', 'tally', 'bently', 'gentle'
            ]
            
            query_words = query.split()
            match_found = False
            
            for qw in query_words:
                for ww in wake_words:
                    # Fuzzy match - if word is similar enough
                    if ww in qw or qw in ww:
                        match_found = True
                        print(f"[ HOTWORD ] MATCH FOUND! '{qw}' matched '{ww}'")
                        break
                    # Check first 4-5 chars
                    if len(qw) >= 4 and len(ww) >= 4:
                        if qw[:4] == ww[:4] or qw[:5] == ww[:5]:
                            match_found = True
                            print(f"[ HOTWORD ] MATCH FOUND! '{qw}' similar to '{ww}'")
                            break
                if match_found:
                    break
            
            if match_found:
                print("[ HOTWORD ] >>> WAKE WORD DETECTED! <<<")
                sys.stdout.flush()
                _trigger_wake_word()
                
        except sr.WaitTimeoutError:
            print(".", end="")
            sys.stdout.flush()
        except sr.UnknownValueError:
            pass
        except Exception as e:
            print(f"\n[ HOTWORD ] Error: {e}")
            sys.stdout.flush()
            import time
            time.sleep(2)


def _trigger_wake_word():
    """Called when wake word is detected - triggers welcome message."""
    import eel
    import threading
    from command import speak
    
    def _welcome():
        try:
            eel.ShowHood()
            eel.DisplayMessage("Hello! I'm listening...")
            speak("Hello! I'm INTELLI. How can I help you?")
            
            from command import allCommands
            allCommands(1)
        except Exception as e:
            print(f"Welcome message error: {e}")
    
    thread = threading.Thread(target=_welcome)
    thread.start()


