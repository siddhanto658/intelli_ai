import eel
import requests
import json
from command import takecommand, speak
from intelli.core.config import get_settings
@eel.expose
def latestnews():
    api_key = get_settings().news_api_key
    if not api_key:
        speak("News API key is missing. Please set NEWS_API_KEY.")
        eel.DisplayMessage("Missing NEWS_API_KEY")
        eel.ShowHood()
        return

    api_dict = {
        "business": f"https://newsapi.org/v2/top-headlines?country=in&category=business&apiKey={api_key}",
        "entertainment": f"https://newsapi.org/v2/top-headlines?country=in&category=entertainment&apiKey={api_key}",
        "health": f"https://newsapi.org/v2/top-headlines?country=in&category=health&apiKey={api_key}",
        "science": f"https://newsapi.org/v2/top-headlines?country=in&category=science&apiKey={api_key}",
        "sports": f"https://newsapi.org/v2/top-headlines?country=in&category=sports&apiKey={api_key}",
        "technology": f"https://newsapi.org/v2/top-headlines?country=in&category=technology&apiKey={api_key}",
    }

    url = None
    speak("Which field news do you want, [business] , [health] , [technology], [sports] , [entertainment] , [science]")
    query = takecommand()
    for key, value in api_dict.items():
        if key.lower() in query.lower():
            url = value
            print(url)
            print("url was found")
            break
    if not url:
        speak("I could not find that news category.")
        eel.DisplayMessage("Unsupported news category.")
        eel.ShowHood()
        return

    news = requests.get(url, timeout=10).text
    news = json.loads(news)
    speak("Here is the news.")

    arts = news["articles"]
    counter = 0

    for articles in arts:
        article = articles["title"]
        print(article)
        eel.DisplayMessage(article)
        speak(article)
        
        news_url = articles["url"]
        print(f"for more info visit: {news_url}")

        counter += 1
        if counter == 3:
            break

        speak("here is the another one")
        eel.DisplayMessage("here is the another one")
        
    eel.DisplayMessage("that's all")
    speak("that's all")
    eel.ShowHood()