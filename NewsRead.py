import eel
import requests
import json
from command import takecommand, speak
from intelli.core.config import get_settings

@eel.expose
def latestnews():
    api_key = get_settings().news_api_key
    if not api_key:
        speak("News API key is missing. Please set NEWS_API_KEY in .env file.")
        eel.DisplayMessage("Missing NEWS_API_KEY")
        eel.ShowHood()
        return

    categories = {
        "business": "business",
        "entertainment": "entertainment",
        "health": "health",
        "science": "science",
        "sports": "sports",
        "technology": "technology",
        "politics": "politics",
    }

    speak("Which field news do you want? You can say: business, health, technology, sports, entertainment, science, or politics.")
    query = takecommand().lower()

    category = None
    for key in categories:
        if key in query:
            category = categories[key]
            break

    if not category:
        category = "top"  # Default to top news

    try:
        params = {
            "api-key": api_key,
            "language": "en",
            "source-country": "in",
            "page-size": 5,
        }

        if category != "top":
            params["category"] = category

        url = "https://api.worldnewsapi.com/top-news"
        response = requests.get(url, params=params, timeout=15)
        data = response.json()

        if response.status_code != 200:
            speak(f"Sorry, I couldn't fetch the news. Error: {data.get('message', 'Unknown error')}")
            eel.DisplayMessage(f"News API Error: {data.get('message', 'Unknown')}")
            eel.ShowHood()
            return

        # World News API returns: {"top_news": [{"news": [...]}]}
        top_news = data.get("top_news", [])
        articles = []
        if top_news and len(top_news) > 0:
            articles = top_news[0].get("news", [])

        if not articles:
            speak("No news found for this category.")
            eel.DisplayMessage("No news found")
            eel.ShowHood()
            return

        speak("Here are the latest news headlines.")

        for i, article in enumerate(articles[:5]):
            title = article.get("title", "No title")
            source = article.get("source_country", "").upper()
            sentiment = article.get("sentiment", 0)

            sentiment_emoji = ""
            if sentiment > 0.2:
                sentiment_emoji = " (Positive)"
            elif sentiment < -0.2:
                sentiment_emoji = " (Negative)"

            display_text = f"{title}{sentiment_emoji}"
            print(f"{i+1}. {title}")
            print(f"   Source: {source} | Sentiment: {sentiment}")
            eel.DisplayMessage(display_text)
            speak(f"{title}{sentiment_emoji}")

            if i < len(articles) - 1 and i < 4:
                speak("Here is the next one.")

        speak("That's all the news I have for you.")
        eel.DisplayMessage("That's all!")
        eel.ShowHood()

    except requests.exceptions.Timeout:
        speak("The news service is taking too long to respond. Please try again.")
        eel.DisplayMessage("Connection timeout")
        eel.ShowHood()

    except Exception as e:
        speak(f"Sorry, I encountered an error while fetching news: {str(e)}")
        eel.DisplayMessage(f"Error: {str(e)}")
        eel.ShowHood()
