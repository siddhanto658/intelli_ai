import datetime
import os
from urllib.parse import quote
import re
import sqlite3
import struct
import subprocess
import time
import webbrowser
from playsound import playsound
import eel
import pyaudio
import pyautogui
from command import speak, logger
from config import ASSISTANT_NAME
# Playing assiatnt sound function
import pywhatkit as kit
import pvporcupine

from helper import extract_yt_term, remove_words
from hugchat import hugchat

try:
    con = sqlite3.connect("INTELLI.db")
    cursor = con.cursor()
except Exception as e:
    logger.error(f"Database connection error: {e}")
    con = None
    cursor = None

@eel.expose
def playAssistantSound():
    try:
        music_dir = "www\\assets\\audio\\start_sound.mp3"
        playsound(music_dir)
        logger.info("Assistant sound played")
    except Exception as e:
        logger.warning(f"Could not play assistant sound: {e}")

    
def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("open", "")
    query.lower()

    app_name = query.strip()

    if app_name != "":
        try:
            if cursor is None:
                speak("Database not available")
                return
                
            cursor.execute(
                'SELECT path FROM sys_command WHERE name = ?', (app_name,))
            results = cursor.fetchall()

            if len(results) != 0:
                speak("Opening "+query)
                os.startfile(results[0][0])
                logger.info(f"Opened application: {app_name}")

            elif len(results) == 0: 
                cursor.execute(
                'SELECT url FROM web_command WHERE name = ?', (app_name,))
                results = cursor.fetchall()
                
                if len(results) != 0:
                    speak("Opening "+query)
                    webbrowser.open(results[0][0])
                    logger.info(f"Opened URL: {app_name}")

                else:
                    speak("Opening "+query)
                    try:
                        os.system('start '+query)
                        logger.info(f"Opened via system: {app_name}")
                    except Exception as e:
                        logger.warning(f"Could not open {app_name}: {e}")
                        speak("not found")
        except Exception as e:
            logger.error(f"Error in openCommand: {e}")
            speak("Something went wrong while opening")

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
    elif hour >=12 and hour<=17:
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
                autogui.keyDown("win")
                autogui.press("j")
                time.sleep(2)
                autogui.keyUp("win")
                
    except:
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if paud is not None:
            paud.terminate()



# find contacts
def findContact(query):
    
    words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'whatsapp', 'video']
    query = remove_words(query, words_to_remove)

    try:
        query = query.strip().lower()
        cursor.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
        results = cursor.fetchall()
        print(results[0][0])
        mobile_number_str = str(results[0][0])

        if not mobile_number_str.startswith('+91'):
            mobile_number_str = '+91' + mobile_number_str

        return mobile_number_str, query
    except:
        speak('not exist in contacts')
        return 0, 0
    
def whatsApp(mobile_no, message, flag, name):
    

    if flag == 'message':
        target_tab = 12
        INTELLI_message = "message send successfully to "+name

    elif flag == 'call':
        target_tab = 7
        message = ''
        INTELLI_message = "calling to "+name

    else:
        target_tab = 6
        message = ''
        INTELLI_message = "staring video call with "+name


    # Encode the message for URL
    encoded_message = quote(message)
    print(encoded_message) 
    # Construct the URL
    whatsapp_url = f"whatsapp://send?phone={mobile_no}&text={encoded_message}"

    # Construct the full command
    full_command = f'start "" "{whatsapp_url}"'

    # Open WhatsApp with the constructed URL using cmd.exe
    subprocess.run(full_command, shell=True)
    time.sleep(5)
    subprocess.run(full_command, shell=True)
    
    pyautogui.hotkey('ctrl', 'f')

    for i in range(1, target_tab):
        pyautogui.hotkey('tab')

    pyautogui.hotkey('enter')
    speak(INTELLI_message)

# chat bot 
def chatBot(query):
    try:
        user_input = query.lower()
        logger.info(f"ChatBot query: {user_input}")
        
        chatbot = hugchat.ChatBot(cookie_path="cookies.json")
        id = chatbot.new_conversation()
        chatbot.change_conversation(id)
        response =  chatbot.chat(user_input)
        print(response)
        speak(response)
        logger.info(f"ChatBot response: {response[:100]}...")
        return response
    except Exception as e:
        logger.error(f"ChatBot error: {e}")
        speak("I'm sorry, I couldn't process that right now. Please try again.")
        return "Sorry, I encountered an error."