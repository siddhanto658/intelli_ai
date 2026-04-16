from intelli.core.router import IntentRouter
from intelli.handlers.basic import BasicHandlers
from intelli.handlers.media_info import MediaInfoHandlers
from intelli.handlers.social import SocialHandlers
from intelli.handlers.communications import CommunicationsHandlers
from intelli.handlers.utility import UtilityHandlers
from intelli.handlers.generation import GenerationHandlers
from intelli.handlers.dictionary import DictionaryAPI
from intelli.handlers.openweather import OpenMeteoWeather


# Quick handlers for new APIs
_dictionary_handler = DictionaryAPI._static_method
_weather_handler = OpenMeteoWeather


def build_router(
    router: IntentRouter,
    basic_handlers: BasicHandlers,
    utility_handlers: UtilityHandlers,
    social_handlers: SocialHandlers,
    media_info_handlers: MediaInfoHandlers,
    generation_handlers: GenerationHandlers,
    communications_handlers: CommunicationsHandlers,
) -> IntentRouter:
    router.register(["open"], basic_handlers.handle_open)
    router.register(["news"], basic_handlers.handle_news)
    router.register(["calculate"], basic_handlers.handle_calculate)
    router.register(["shutdown the system"], basic_handlers.handle_shutdown)
    router.register(["screenshot"], basic_handlers.handle_screenshot)

    router.register(
        ["add my task", "view my task", "update my task", "delete my task"],
        utility_handlers.handle_tasks,
    )
    router.register(["my routine"], utility_handlers.handle_routine)
    router.register(["time", "date"], utility_handlers.handle_time_date)
    router.register(
        ["remember that", "what do you remember"],
        utility_handlers.handle_memory,
    )
    router.register(
        ["change voice", "switch voice", "male voice", "female voice", "sweet voice"],
        utility_handlers.handle_voice_change,
    )

    router.register(
        ["message", "phone call", "video call"],
        communications_handlers.handle_communication,
    )

    router.register(["launch"], media_info_handlers.handle_launch)
    router.register(["on youtube", "open youtube", "play youtube"], media_info_handlers.handle_youtube)
    router.register(["play song", "play music", "play a song", "bajao song", "song bajao"], media_info_handlers.handle_play_song)
    router.register(["open chrome", "open browser", "open edge", "open firefox", "open notepad", "open calculator", "open vscode", "open code"], media_info_handlers.handle_open_app)
    router.register(
        [
            "hello",
            "hii",
            "good morning",
            "good afternoon",
            "good evening",
            "your name",
            "how are you",
            "how r u",
            "introduce yourself",
            "your birthday",
            "you born",
        ],
        media_info_handlers.handle_greetings,
    )
    router.register(["google"], media_info_handlers.handle_google)
    router.register(
        ["temperature", "weather", "rain", "sunny", "cloudy", "forecast", "astronomy", "stargazing", "will it"],
        media_info_handlers.handle_weather_temperature,
    )
    router.register(
        ["speed test", "internet speed"],
        media_info_handlers.handle_speedtest,
    )
    router.register(
        ["handsfree", "hands free", "hand free"],
        media_info_handlers.handle_handsfree,
    )
    router.register(["tired"], media_info_handlers.handle_tired)
    router.register(["click my photo"], media_info_handlers.handle_camera)

    router.register(["generate image", "create image", "draw an image"], generation_handlers.handle_image_generation)
    router.register(["generate document", "create doc", "write a report"], generation_handlers.handle_docx_generation)
    router.register(["generate presentation", "create ppt", "make slides"], generation_handlers.handle_pptx_generation)
    router.register(["generate video", "create video"], generation_handlers.handle_video_generation)

    # New: Dictionary lookup
    router.register(
        ["define", "meaning of", "what does", "dictionary"],
        _handle_dictionary,
    )

    # New: Wikipedia lookup
    router.register(
        ["who is", "what is", "tell me about", "wikipedia"],
        _handle_wikipedia,
    )

    return router


def _handle_dictionary(query: str) -> bool:
    """Handle dictionary lookups."""
    import re
    from command import speak
    
    # Extract word to define
    patterns = [
        r"define\s+(\w+)",
        r"meaning of\s+(\w+)",
        r"what does\s+(\w+)\s+mean",
        r"dictionary\s+(\w+)",
    ]
    
    word = None
    for pattern in patterns:
        match = re.search(pattern, query.lower())
        if match:
            word = match.group(1)
            break
    
    if not word:
        # Try to get last word
        words = query.lower().split()
        word = words[-1] if words else None
    
    if word:
        definition = DictionaryAPI.define(word)
        if definition:
            speak(definition)
            return True
    
    return False


def _handle_wikipedia(query: str) -> bool:
    """Handle Wikipedia lookups."""
    from command import speak
    
    # Remove common prefixes
    query = query.lower()
    query = query.replace("who is", "").replace("what is", "")
    query = query.replace("tell me about", "").replace("wikipedia", "")
    query = query.replace("intelli", "").strip()
    
    if not query:
        return False
    
    try:
        import requests
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            extract = data.get("extract", "")
            if extract:
                speak(extract)
                return True
    except:
        pass
    
    return False

