import random
import webbrowser
from typing import Callable

import requests
import speedtest_cli
import re
from intelli.core.platform import PlatformAdapter


class MediaInfoHandlers:
    def __init__(
        self,
        speak: Callable[[str], None],
        takecommand: Callable[[], str],
        eel_module,
        pyautogui_module,
        handgesture_func: Callable[[], None],
        platform_adapter: PlatformAdapter,
        permission_checker: Callable[[str], bool],
    ):
        self.speak = speak
        self.takecommand = takecommand
        self.eel = eel_module
        self.pyautogui = pyautogui_module
        self.handgesture = handgesture_func
        self.platform = platform_adapter
        self.permission_checker = permission_checker

    def handle_launch(self, query: str) -> bool:
        launch_query = query.replace("launch", "").replace("intelli", "").strip()
        self.speak("Launching " + launch_query)
        self.pyautogui.press(self.platform.launcher_key())
        self.pyautogui.typewrite(launch_query)
        self.pyautogui.sleep(2)
        self.pyautogui.press("enter")
        return True

    def handle_youtube(self, query: str) -> bool:
        from features import PlayYoutube

        PlayYoutube(query)
        return True

    def handle_greetings(self, query: str) -> bool:
        if "hello" in query or "hii" in query or "good morning" in query or "good afternoon" in query or "good evening" in query:
            from features import greetuser

            greetuser()
            return True

        if "your name" in query:
            text = "My name is INTELLI, How can I help you today!"
            self.speak(text)
            self.eel.DisplayMessage(text)
            return True

        if "how are you" in query or "how r u" in query:
            text = "I'm Doing great!, Just hanging out in the cloud, eagerly awaiting the next question or conversation. Hows your day going so far?!"
            self.speak(text)
            self.eel.DisplayMessage(text)
            return True

        if "introduce yourself" in query:
            text = (
                "Sure!! Hey there, everyone! My name is INTELLI, and I am an AI designed to be a friendly and helpful conversation partner. "
                "You can think of me as a digital assistant that you can chat with about pretty much anything. I am here to help!"
            )
            self.speak(text)
            self.eel.DisplayMessage(text)
            return True

        if "your birthday" in query or "you born" in query:
            text = (
                "I do not really have a birthday since I was not born in the traditional sense. "
                "I was created by a group of 5 engineering students. But I can help you do your tasks better!"
            )
            self.speak(text)
            self.eel.DisplayMessage(text)
            return True

        return False

    def handle_google(self, query: str) -> bool:
        from features import searchGoogle

        searchGoogle(query)
        return True

    def handle_weather_temperature(self, query: str) -> bool:
        try:
            from intelli.handlers.weather import get_weather
            response = get_weather(query)
            self.eel.DisplayMessage(response)
            self.speak(response)
        except Exception as e:
            print(f"Weather error: {e}")
            self.speak("Sorry, I could not fetch the weather right now.")
        return True

    def handle_speedtest(self, query: str) -> bool:
        try:
            self.speak("Running internet speed test. This may take a moment.")
            wifi = speedtest_cli.Speedtest()
            upload_net = int(wifi.upload() / 1048576)
            download_net = int(wifi.download() / 1048576)
            self.speak(f"Your download speed is {download_net} MB per second")
            self.speak(f"Your upload speed is {upload_net} MB per second")
        except Exception as e:
            print(f"Speedtest error: {e}")
            self.speak("Sorry, I could not complete the speed test. Please check your internet connection.")
        return True

    def handle_handsfree(self, query: str) -> bool:
        if self.handgesture is None:
            self.speak("Sorry, hand gesture control is not available on this system. The mediapipe library needs to be updated.")
            return True
        if not self.permission_checker("activate handsfree control"):
            self.speak("Permission denied. Handsfree mode cancelled.")
            return True
        self.speak("Activating Hands free mode!")
        try:
            self.handgesture()
        except Exception as e:
            print(f"Handgesture error: {e}")
            self.speak("Hand gesture control encountered an error.")
        return True

    def handle_tired(self, query: str) -> bool:
        self.speak("I have got some great ideas! What would you like! watching a movie, music video, comedy video or informational video")
        relax = self.takecommand().lower()
        if "music" in relax or "songs" in relax:
            self.speak("Playing your favourite songs,")
            playlist = (
                "https://www.youtube.com/watch?v=w_EbL-rkNgs&list=PLJ0ixiQcQtGKcczK9dSNjIy2kUh5xkyiu",
                "https://www.youtube.com/watch?v=_GWKkqNoyEA&list=PLJ0ixiQcQtGKcczK9dSNjIy2kUh5xkyiu&index=3",
                "https://www.youtube.com/watch?v=Hq5rXS0iIPU&list=PLJ0ixiQcQtGKcczK9dSNjIy2kUh5xkyiu&index=8",
                "https://www.youtube.com/watch?v=vTMAa6zZ7jY&list=PLJ0ixiQcQtGKcczK9dSNjIy2kUh5xkyiu&index=40",
                "https://www.youtube.com/watch?v=K1FlAphL2p8&list=PLJ0ixiQcQtGKcczK9dSNjIy2kUh5xkyiu&index=62",
            )
            webbrowser.open(random.choice(playlist))
            return True

        from features import PlayYoutube
        import pywhatkit as kit

        if "comedy" in relax or "funny" in relax:
            self.speak("Playing a funny video on YouTube! I hope you would like it")
            kit.playonyt("stand up comedy")
            PlayYoutube(query)
            return True
        if "movie" in relax or "movies" in relax:
            self.speak("Playing a movie trailer on YouTube! I hope you would like it")
            kit.playonyt("latest movie trailers")
            PlayYoutube(query)
            return True
        if "information" in relax or "informational" in relax:
            self.speak("Playing an informational video on youtube! I hope it helps")
            kit.playonyt("current affairs long video")
            PlayYoutube(query)
            return True

        self.speak("Sorry! I did not recognize that. Please try again")
        return True

    def handle_camera(self, query: str) -> bool:
        if not self.permission_checker("open camera and click photo"):
            self.speak("Permission denied. Camera action cancelled.")
            return True
        self.speak("ok sir, clicking your photo")
        self.pyautogui.press(self.platform.launcher_key())
        self.pyautogui.typewrite("camera")
        self.pyautogui.press("enter")
        self.pyautogui.sleep(2)
        self.speak("SMILE please")
        self.pyautogui.press("enter")
        return True

    def handle_play_song(self, query: str) -> bool:
        import pywhatkit as kit
        song_name = query
        for word in ["play", "song", "music", "play song", "play music", "bajao", "song bajao", "intelli"]:
            song_name = song_name.replace(word, "").strip()
        if not song_name:
            song_name = "popular songs"
        self.speak(f"Playing {song_name} on YouTube")
        kit.playonyt(song_name)
        return True

    def handle_open_app(self, query: str) -> bool:
        app_mapping = {
            "chrome": "chrome",
            "browser": "chrome",
            "edge": "msedge",
            "firefox": "firefox",
            "notepad": "notepad",
            "calculator": "calc",
            "vscode": "code",
            "code": "code",
        }
        for app_key, app_exe in app_mapping.items():
            if app_key in query.lower():
                self.speak(f"Opening {app_key}")
                import subprocess
                try:
                    subprocess.Popen(app_exe)
                except:
                    self.pyautogui.press(self.platform.launcher_key())
                    self.pyautogui.typewrite(app_key)
                    self.pyautogui.press("enter")
                return True
        return False

