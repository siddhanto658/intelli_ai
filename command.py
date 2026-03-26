import datetime
import os
import random
import webbrowser
from bs4 import BeautifulSoup
import pyautogui
import pyttsx3
import requests
import speech_recognition as sr
import eel
import time
import speedtest_cli
from HandGesture import Handgesture
from config import ASSISTANT_NAME
from helper import remove_words
import pywhatkit as kit
from logger import logger
import traceback

selected_mic_index = 0
speech_rate = 174

def load_settings():
    global selected_mic_index, speech_rate
    try:
        import json
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as f:
                settings = json.load(f)
                selected_mic_index = settings.get("mic_index", 0)
                speech_rate = settings.get("speech_rate", 174)
                logger.info(f"Settings loaded: mic={selected_mic_index}, rate={speech_rate}")
    except Exception as e:
        logger.warning(f"Could not load settings: {e}")

def save_settings():
    try:
        import json
        settings = {"mic_index": selected_mic_index, "speech_rate": speech_rate}
        with open("settings.json", "w") as f:
            json.dump(settings, f)
        logger.info("Settings saved")
    except Exception as e:
        logger.warning(f"Could not save settings: {e}")

load_settings()

def get_available_mics():
    mics = []
    try:
        for i, microphone in enumerate(sr.Microphone.list_microphone_names()):
            mics.append({"index": i, "name": microphone})
    except Exception as e:
        logger.error(f"Error getting microphones: {e}")
    return mics

def set_mic_index(index):
    global selected_mic_index
    selected_mic_index = index
    save_settings()

def set_speech_rate(rate):
    global speech_rate
    speech_rate = rate
    save_settings()

@eel.expose
def get_available_mics():
    mics = []
    try:
        for i, microphone in enumerate(sr.Microphone.list_microphone_names()):
            mics.append({"index": i, "name": microphone})
    except Exception as e:
        logger.error(f"Error getting microphones: {e}")
    return mics

@eel.expose
def set_mic_index(index):
    global selected_mic_index
    selected_mic_index = index
    save_settings()
    logger.info(f"Microphone index set to: {index}")

@eel.expose
def set_speech_rate(rate):
    global speech_rate
    speech_rate = rate
    save_settings()
    logger.info(f"Speech rate set to: {rate}")

@eel.expose
def test_microphone(index):
    try:
        logger.info(f"Testing microphone index: {index}")
        r = sr.Recognizer()
        mic = sr.Microphone(device_index=index)
        with mic as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
        logger.info("Microphone test successful")
        return "success"
    except Exception as e:
        logger.error(f"Microphone test failed: {e}")
        return "failed"

@eel.expose
def get_settings():
    return {"mic_index": selected_mic_index, "speech_rate": speech_rate}

def speak(text):
    try:
        text = str(text)
        engine = pyttsx3.init('sapi5')
        voices = engine.getProperty('voices') 
        engine.setProperty('voice', voices[1].id)
        engine.setProperty('rate', speech_rate)
        eel.DisplayMessage(text)
        engine.say(text)
        eel.receiverText(text)
        engine.runAndWait()
    except Exception as e:
        logger.error(f"TTS Error: {e}")
        eel.DisplayMessage(text)

def takecommand():

    r = sr.Recognizer()
    r.dynamic_energy_threshold = True
    r.energy_threshold = 4000

    try:
        microphone = sr.Microphone(device_index=selected_mic_index)
        logger.info(f"Using microphone index: {selected_mic_index}")
    except Exception as e:
        logger.warning(f"Could not use selected mic, using default: {e}")
        microphone = sr.Microphone()

    with microphone as source:
        logger.info("Listening...")
        print('listening....')
        eel.DisplayMessage('listening....')
        r.pause_threshold = 1.5
        r.dynamic_energy_threshold = True
        
        try:
            r.adjust_for_ambient_noise(source, duration=1)
        except Exception as e:
            logger.warning(f"Could not adjust for ambient noise: {e}")
        
        try:
            audio = r.listen(source, timeout=10, phrase_time_limit=15)
        except sr.WaitTimeoutError:
            logger.info("No speech detected within timeout")
            eel.DisplayMessage("No speech detected")
            return ""
        except Exception as e:
            logger.error(f"Error listening: {e}")
            return ""

    try:
        logger.info("Recognizing speech...")
        print('recognizing')
        eel.DisplayMessage('recognizing....')
        query = r.recognize_google(audio, language='en-in')
        print(f"user said: {query}")
        eel.DisplayMessage(query)
        logger.info(f"User said: {query}")
        time.sleep(2)
       
    except sr.UnknownValueError:
        logger.warning("Could not understand audio")
        eel.DisplayMessage("Could not understand. Please try again.")
        return ""
    except sr.RequestError as e:
        logger.error(f"Speech recognition service error: {e}")
        eel.DisplayMessage("Speech service unavailable. Please check internet connection.")
        return ""
    except Exception as e:
        logger.error(f"Error in speech recognition: {e}")
        return ""
    
    return query.lower()

@eel.expose
def allCommands(message=1):
    try:
        if message == 1:
            query = takecommand()
            print(query)
            eel.senderText(query)
        else:
            query = message
            eel.senderText(query)
        
        logger.info(f"Processing command: {query}")

        if "open" in query:
            from features import openCommand
            openCommand(query)

        elif "launch" in query:
                        query = query.replace("launch","")
                        query = query.replace("intelli","")
                        speak("Launching " +(query))
                        pyautogui.press("super")
                        pyautogui.typewrite(query)
                        pyautogui.sleep(2)
                        pyautogui.press("enter") 

        elif "on youtube" in query:
            from features import PlayYoutube
            PlayYoutube(query)

        elif "hello" in query or "hii" in query or "good morning" in query or "good afternoon" in query or "good evening" in query:
            from features import greetuser
            greetuser()

        elif "your name" in query:
            speak("My name is INTELLI, How can I help you today!")
            eel.display("My name is INTELLI, How can I help you today!")

        elif "google" in query:
            from features import searchGoogle
            searchGoogle(query)
        
        elif "how are you" in query or "how r u" in query:
            speak("I'm Doing great!, Just hanging out in the cloud, eagerly awaiting the next question or conversation. How’s your day going so far?!")
            eel.display("I'm Doing great!, Just hanging out in the cloud, eagerly awaiting the next question or conversation. How’s your day going so far?!")

        elif "introduce yourself" in query:
            speak("Sure!!  Hey there, everyone! My name is INTELLI, and I’m an AI designed to be a friendly and helpful conversation partner. You can think of me as a digital assistant that you can chat with about pretty much anything. I’m here to help! ")
            eel.display("Sure!!  Hey there, everyone! My name is INTELLI, and I’m an AI designed to be a friendly and helpful conversation partner. You can think of me as a digital assistant that you can chat with about pretty much anything. I’m here to help! ")
        
        elif "your birthday" in query or "you born" in query:
            speak("I don't really have a birthday since I wasn't born in the traditional sense. I was created by a group of 5 engineering students, and they may have a specific date when I was activated or started running, but I don't have that information. But I can help you to do your tasks better!")
            eel.display("I don't really have a birthday since I wasn't born in the traditional sense. I was created by a group of 5 engineering students, and they may have a specific date when I was activated or started running, but I don't have that information. But I can help you to do your tasks better!")
       
        elif "temperature" in query:
            try:
                # Extract location from query
                location = query.replace("temperature", "").replace("in", "").replace("what is", "").strip()
                if not location:
                    location = "delhi"
                
                # Use wttr.in for weather (free, no API key)
                url = f"https://wttr.in/{location}?format=%t"
                r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                r.encoding = 'utf-8'
                if r.status_code == 200:
                    temp = r.text.strip()
                    if "cuttack" in query.lower() or "cuttack" in location.lower():
                        speak(f"Current temperature here is {temp}")
                    else:
                        speak(f"Current temperature in {location} is {temp}")
                else:
                    speak(f"Sorry, I couldn't find temperature for {location}")
            except Exception as e:
                logger.error(f"Temperature error: {e}")
                speak("Sorry, I couldn't fetch the temperature right now.")

        elif "weather" in query:
            try:
                # Extract location from query
                location = query.replace("weather", "").replace("in", "").replace("what is", "").strip()
                if not location:
                    location = "delhi"
                
                # Use wttr.in for weather (free, no API key)
                url = f"https://wttr.in/{location}?format=%c+%t"
                r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                r.encoding = 'utf-8'
                if r.status_code == 200:
                    weather = r.text.strip()
                    if "cuttack" in query.lower() or "cuttack" in location.lower():
                        speak(f"Current weather here: {weather}")
                    else:
                        speak(f"Current weather in {location}: {weather}")
                else:
                    speak(f"Sorry, I couldn't find weather for {location}")
            except Exception as e:
                logger.error(f"Weather error: {e}")
                speak("Sorry, I couldn't fetch the weather right now.")

        elif "speed test" in query or "internet speed" in query:
             wifi = speedtest_cli.Speedtest()
             upload_net = wifi.upload()/1048576
             download_net = wifi.download()/1048576
             upload_net = int(upload_net)
             download_net = int(download_net)
             print("Wifi Upload speed is" , upload_net)
             print("Wifi Download speed is" , download_net)
             speak(f"Your download speed is  {download_net} MB per second")
             speak(f"Your upload speed is  {upload_net} MB per second")
        
        elif "handsfree" in query or "hands free" in query or "hand free" in query:
             speak("Activating Hands free mode!")
             Handgesture()

        elif "add my task" in query:
            from task import add_task
            add_task()
        elif "view my task" in query:
            from task import view_task
            view_task()
        elif "update my task" in query:
            from task import update_task
            update_task()
        elif "delete my task" in query:
            from task import delete_task
            delete_task()

        elif "my routine" in query:
                tasks = [] #Empty list 
                speak("Do you want to clear old tasks (Plz speak YES or NO)")
                query = takecommand().lower()
                if "yes" in query:
                    file = open("tasks.txt","w")
                    file.write(f"")
                    file.close()
                    speak("How many tasks?")
                    no_tasks = takecommand()
                    try:
                        no_tasks = int(no_tasks)
                    except:
                        no_tasks = 3
                    i = 0
                    for i in range(no_tasks):
                        speak("Tell me the task")
                        task = takecommand()
                        tasks.append(task)
                        file = open("tasks.txt","a")
                        file.write(f"{i}. {tasks[i]}\n")
                        file.close()
                elif "no" in query:
                    i = 0
                    speak("How many tasks?")
                    no_tasks = takecommand()
                    try:
                        no_tasks = int(no_tasks)
                    except:
                        no_tasks = 3
                    for i in range(no_tasks):
                        speak("Tell me the task")
                        task = takecommand()
                        tasks.append(task)
                        file = open("tasks.txt","a")
                        file.write(f"{i}. {tasks[i]}\n")
                        file.close()

        elif "time" in query:
            strTime = datetime.datetime.now().strftime("%I:%M %p")
            speak(f"The time is {strTime}")
            eel.display(f"The time is {strTime}")
        elif "date" in query:
            strDate = datetime.datetime.now().strftime("%B %d, %Y")
            speak(f"The date is {strDate}")
            eel.display(f"The date is {strDate}")

        elif "remember that" in query:
            removewords = [ASSISTANT_NAME,'remember', 'that']
            query = remove_words(query, removewords)
            rememberMessage = query
            # rememberMessage = query.replace('I', 'you')
            rememberMessage = query.replace('i', 'you').replace('my', 'your')
            print(rememberMessage)
            speak("ok I remember that " + rememberMessage)
            remember = open("Remember.txt", "a")
            remember.write(rememberMessage +" \n")
            remember.close()
                                
        elif "what do you remember" in query:
            remember = open("Remember.txt","r")
            speak("You told me to remember that " +remember.read())
                                                               
        elif "news" in query:
            from NewsRead import latestnews
            latestnews(query)

        elif "calculate" in query:
            from calculate import Calc
            query = query.replace("calculate","")
            query = query.replace("intelli","")
            Calc(query)

        elif "shutdown the system" in query:
            speak("Are You sure you want to shutdown, Say Yes or No!")
            shutdown = takecommand()
            if shutdown == "yes":
                speak("ok sir, I am shutting down the system")
                os.system("shutdown /s /t 1")
            elif shutdown == "no":
                speak("ok sir, I am not shutting down the system")
            pass
                                        
        elif "screenshot" in query:
            speak("ok sir, taking screenshot")
            im = pyautogui.screenshot()
            im.save("screenshot by AI.jpg")
        
        elif "tired" in query:
                                speak("I’ve got some great ideas! What would you like! watching a movie, music video, comedy video or informational video ")
                                relax = takecommand().lower()
                                if "music" in relax or "songs" in relax:
                                    speak("Playing your favourite songs,")
                                    a = (1,2,3,4,5)
                                    b = random.choice(a)
                                    if b==1:
                                        webbrowser.open('https://www.youtube.com/watch?v=w_EbL-rkNgs&list=PLJ0ixiQcQtGKcczK9dSNjIy2kUh5xkyiu')
                                    elif b==2:
                                        webbrowser.open('https://www.youtube.com/watch?v=_GWKkqNoyEA&list=PLJ0ixiQcQtGKcczK9dSNjIy2kUh5xkyiu&index=3')
                                    elif b==3:
                                        webbrowser.open("https://www.youtube.com/watch?v=Hq5rXS0iIPU&list=PLJ0ixiQcQtGKcczK9dSNjIy2kUh5xkyiu&index=8")
                                    elif b==4:
                                        webbrowser.open("https://www.youtube.com/watch?v=vTMAa6zZ7jY&list=PLJ0ixiQcQtGKcczK9dSNjIy2kUh5xkyiu&index=40")
                                    elif b==5:
                                        webbrowser.open("https://www.youtube.com/watch?v=K1FlAphL2p8&list=PLJ0ixiQcQtGKcczK9dSNjIy2kUh5xkyiu&index=62")

                                elif "comedy" in relax or "funny" in relax:
                                     speak("Playing a funny video on YouTube! I hope you'd like")
                                     search_term = 'stand up comedy'
                                     kit.playonyt(search_term)
                                     PlayYoutube(query)
                                elif "movie" in relax or "movies" in relax:
                                    speak("Playing a movie trailer on YouTube! I hope you'd like")
                                    search_term = 'latest movie trailers'
                                    kit.playonyt(search_term)
                                    PlayYoutube(query)
                                elif "information" in relax or "informational" in relax:
                                     speak("Playing a informational video on youtube! I hope it helps")
                                     search_term = 'current affairs long video'
                                     kit.playonyt(search_term)
                                     PlayYoutube(query)
                                else:
                                     speak("Sorry! I didn't recognized. Please try again")
                                        
        elif "click my photo" in query:
            speak("ok sir, clicking your photo")
            pyautogui.press("super")
            pyautogui.typewrite("camera")
            pyautogui.press("enter")
            pyautogui.sleep(2)
            speak("SMILE please")
            pyautogui.press("enter")

        elif "message" in query or "phone call" in query or "video call" in query:
            from features import findContact, whatsApp
            flag = ""
            contact_no, name = findContact(query)
            if(contact_no != 0):

                if "message" in query:
                    flag = 'message'
                    speak("what message to send")
                    query = takecommand()
                    
                elif "phone call" in query:
                    flag = 'call'

                else:
                    flag = 'video call'
                    
                whatsApp(contact_no, query, flag, name)
        else:
            from features import chatBot
            chatBot(query)
    except Exception as e:
        logger.error(f"Error processing command: {e}")
        traceback.print_exc()
        speak("Sorry, I encountered an error. Please try again.")
        eel.DisplayMessage("Error occurred. Please try again.")
    
    eel.ShowHood()