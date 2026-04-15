import datetime
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

@eel.expose
def playAssistantSound():
    music_dir = os.path.join(os.getcwd(), "www", "assets", "audio", "start_sound.mp3")
    try:
        subprocess.Popen(["mpg123", "-q", music_dir], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"Audio launch skipped: {e}")

    
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
        except:
            speak("some thing went wrong")

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
    current_time = datetime.datetime.now()
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
    porcupine=None
    paud=None
    audio_stream=None
    try:
       
        # pre trained keywords    
        porcupine=pvporcupine.create(keywords=['ok google', 'jarvis', 'blueberry', 'pico clock', 'porcupine', 
                                               'computer', 'americano', 'grasshopper', 'hey google', 'grapefruit', 'bumblebee', 
                                               'picovoice', 'terminator', 'hey siri', 'alexa']) 
        paud=pyaudio.PyAudio()
        audio_stream=paud.open(rate=porcupine.sample_rate,channels=1,format=pyaudio.paInt16,input=True,frames_per_buffer=porcupine.frame_length)
        
        # loop for streaming
        while True:
            keyword=audio_stream.read(porcupine.frame_length)
            keyword=struct.unpack_from("h"*porcupine.frame_length,keyword)

            # processing keyword comes from mic 
            keyword_index=porcupine.process(keyword)

            # checking first keyword detetcted for not
            if keyword_index>=0:
                print("hotword detected")

                # pressing shorcut key win+j
                import pyautogui as autogui
                modifier_key = "win" if platform.system().lower() == "windows" else "super"
                autogui.keyDown(modifier_key)
                autogui.press("j")
                time.sleep(2)
                autogui.keyUp(modifier_key)
                
    except:
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if paud is not None:
            paud.terminate()


