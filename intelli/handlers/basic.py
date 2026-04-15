from typing import Callable

from intelli.core.platform import PlatformAdapter


class BasicHandlers:
    def __init__(
        self,
        speak: Callable[[str], None],
        takecommand: Callable[[], str],
        platform_adapter: PlatformAdapter,
        pyautogui_module,
        permission_checker: Callable[[str], bool],
    ):
        self.speak = speak
        self.takecommand = takecommand
        self.platform = platform_adapter
        self.pyautogui = pyautogui_module
        self.permission_checker = permission_checker

    def handle_open(self, query: str) -> bool:
        from features import openCommand

        openCommand(query)
        return True

    def handle_news(self, query: str) -> bool:
        from NewsRead import latestnews

        latestnews()
        return True

    def handle_calculate(self, query: str) -> bool:
        from calculate import Calc

        calc_query = query.replace("calculate", "").replace("intelli", "").strip()
        Calc(calc_query)
        return True

    def handle_shutdown(self, query: str) -> bool:
        if not self.permission_checker("shutdown the system"):
            self.speak("Permission denied. Shutdown cancelled.")
            return True
        self.speak("Are You sure you want to shutdown, Say Yes or No!")
        shutdown = self.takecommand()
        if shutdown == "yes":
            self.speak("ok sir, I am shutting down the system")
            if not self.platform.shutdown():
                self.speak("I could not shutdown this system.")
        elif shutdown == "no":
            self.speak("ok sir, I am not shutting down the system")
        return True

    def handle_screenshot(self, query: str) -> bool:
        if not self.permission_checker("take a screenshot"):
            self.speak("Permission denied. Screenshot cancelled.")
            return True
        self.speak("ok sir, taking screenshot")
        if not self.platform.screenshot("screenshot by AI.jpg", self.pyautogui):
            self.speak("Unable to take screenshot right now.")
        return True

