import eel
import requests
import json
import pyttsx3
from command import takecommand, speech_rate, logger

def speak(text):
    try:
        text = str(text)
        engine = pyttsx3.init('sapi5')
        voices = engine.getProperty('voices') 
        engine.setProperty('voice', voices[1].id)
        engine.setProperty('rate', speech_rate)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        logger.error(f"TTS error in NewsRead: {e}")
@eel.expose
def latestnews():
    try:
        api_dict = {"business" : "https://newsapi.org/v2/top-headlines?country=in&category=business&apiKey=20397510eb91463fa02a11fd5115e19c",
                "entertainment" : "https://newsapi.org/v2/top-headlines?country=in&category=entertainment&apiKey=20397510eb91463fa02a11fd5115e19c",
                "health" : "https://newsapi.org/v2/top-headlines?country=in&category=health&apiKey=20397510eb91463fa02a11fd5115e19c",
                "science" :"https://newsapi.org/v2/top-headlines?country=in&category=science&apiKey=20397510eb91463fa02a11fd5115e19c",
                "sports" :"https://newsapi.org/v2/top-headlines?country=in&category=sports&apiKey=20397510eb91463fa02a11fd5115e19c",
                "technology" :"https://newsapi.org/v2/top-headlines?country=in&category=technology&apiKey=20397510eb91463fa02a11fd5115e19c"
        }

        content = None
        url = None
        speak("Which field news do you want, [business] , [health] , [technology], [sports] , [entertainment] , [science]")
        query = takecommand()
        
        if not query:
            speak("Sorry, I didn't catch that. Please try again.")
            eel.ShowHood()
            return
            
        for key ,value in api_dict.items():
            if key.lower() in query.lower():
                url = value
                print(url)
                print("url was found")
                break
            else:
                url = True
        if url is True:
            print("url not found")
            speak("Sorry, I couldn't find that news category. Please try again.")
            eel.ShowHood()
            return

        try:
            news = requests.get(url, timeout=10).text
            news = json.loads(news)
        except Exception as e:
            logger.error(f"News API error: {e}")
            speak("Sorry, I couldn't fetch the news right now. Please check your internet connection.")
            eel.ShowHood()
            return
            
        speak("Here is the news.")

        arts = news["articles"]
        counter = 0

        for articles in arts :
            article = articles["title"]
            print(article)
            eel.DisplayMessage(article)
            speak(article)
            counter += 1
            if counter == 3:
                break
            
            news_url = articles["url"]
            print(f"for more info visit: {news_url}")
            speak("here is the another one")
            eel.DisplayMessage("here is the another one")
            
        eel.DisplayMessage("that's all")
        speak("that's all")
        eel.ShowHood()
    except Exception as e:
        logger.error(f"NewsRead error: {e}")
        speak("Sorry, something went wrong while fetching news.")
        eel.ShowHood()
   