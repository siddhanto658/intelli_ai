import eel
import requests
import json
from command import speak
from intelli.core.config import get_settings
from intelli.core.thread_safe import stop_listening, is_speaking
from intelli.core.logger import log_info, log_warning, log_error

MAX_NEWS_ITEMS = 5

def should_continue():
    """Check if we should continue or stop."""
    return not stop_listening.is_set

def latestnews():
    api_key = get_settings().news_api_key
    if not api_key:
        try:
            eel.DisplayMessage("Missing NEWS_API_KEY")
            eel.ShowHood()
        except:
            pass
        return

    try:
        speak("Which field news do you want? You can say: business, health, technology, sports, entertainment, science, or politics.")
        
        if not should_continue():
            return
            
        query = ""

    except:
        pass

    categories = {
        "business": "business",
        "entertainment": "entertainment",
        "health": "health",
        "science": "science",
        "sports": "sports",
        "technology": "technology",
        "politics": "politics",
    }

    category = None
    for key in categories:
        if key in query:
            category = categories[key]
            break

    if not category:
        category = "top"

    if not should_continue():
        return

    try:
        params = {
            "api-key": api_key,
            "language": "en",
            "source-country": "in",
            "page-size": MAX_NEWS_ITEMS,
        }

        if category != "top":
            params["category"] = category

        url = "https://api.worldnewsapi.com/top-news"
        response = requests.get(url, params=params, timeout=15)
        data = response.json()

        if response.status_code != 200:
            speak(f"Sorry, I couldn't fetch the news. Error: {data.get('message', 'Unknown error')}")
            return

        top_news = data.get("top_news", [])
        articles = []
        if top_news and len(top_news) > 0:
            articles = top_news[0].get("news", [])

        if not articles:
            speak("No news found for this category.")
            return

        speak("Here are the latest news headlines.")

        news_count = 0
        for i, article in enumerate(articles[:MAX_NEWS_ITEMS]):
            if not should_continue():
                log_info("News reading interrupted by user")
                break

            title = article.get("title", "No title")
            source = article.get("source_country", "").upper()
            sentiment = article.get("sentiment", 0)

            sentiment_text = ""
            if sentiment > 0.2:
                sentiment_text = " (Positive)"
            elif sentiment < -0.2:
                sentiment_text = " (Negative)"

            display_text = f"{title}{sentiment_text}"
            print(f"{i+1}. {title}")
            print(f"   Source: {source} | Sentiment: {sentiment}")
            
            try:
                eel.DisplayMessage(display_text)
            except:
                pass
            
            speak(f"{title}{sentiment_text}")

            if not should_continue():
                break

            news_count += 1

            if i < len(articles) - 1 and i < MAX_NEWS_ITEMS - 1:
                speak("Here is the next one.")
                
                if not should_continue():
                    break

        if news_count > 0 and should_continue():
            speak(f"That's {news_count} news items for you.")

        try:
            eel.DisplayMessage(f"Read {news_count} news items")
            eel.ShowHood()
        except:
            pass

    except requests.exceptions.Timeout:
        speak("The news service is taking too long to respond. Please try again.")

    except Exception as e:
        log_error(f"News fetch error: {e}")
        speak("Sorry, I encountered an error while fetching news.")
