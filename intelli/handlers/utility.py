import datetime
import re
from typing import Callable


class UtilityHandlers:
    def __init__(
        self,
        speak: Callable[[str], None],
        takecommand: Callable[[], str],
        spoken_number_to_int: Callable[[str], int],
        eel_module,
        remove_words: Callable[[str, list], str],
        assistant_name: str,
    ):
        self.speak = speak
        self.takecommand = takecommand
        self._to_int = spoken_number_to_int
        self.eel = eel_module
        self.remove_words = remove_words
        self.assistant_name = assistant_name

    def handle_tasks(self, query: str) -> bool:
        if "add my task" in query:
            from task import add_task

            add_task()
            return True
        if "view my task" in query:
            from task import view_task

            view_task()
            return True
        if "update my task" in query:
            from task import update_task

            update_task()
            return True
        if "delete my task" in query:
            from task import delete_task

            delete_task()
            return True
        return False

    def handle_routine(self, query: str) -> bool:
        tasks = []
        self.speak("Do you want to clear old tasks (Plz speak YES or NO)")
        user_choice = self.takecommand().lower()

        mode = "a"
        if "yes" in user_choice:
            mode = "w"

        with open("tasks.txt", mode, encoding="utf-8") as file:
            self.speak("How many tasks do you want to add?")
            no_tasks = self._to_int(self.takecommand())
            if no_tasks is None:
                self.speak("I could not understand the number of tasks.")
                return True
            for i in range(no_tasks):
                self.speak(f"Tell me task number {i+1}")
                task_item = self.takecommand()
                tasks.append(task_item)
                file.write(f"{i}. {tasks[i]}\n")
        return True

    def handle_time_date(self, query: str) -> bool:
        if "time" in query:
            str_time = datetime.datetime.now().strftime("%I:%M %p")
            self.speak(f"The time is {str_time}")
            self.eel.DisplayMessage(f"The time is {str_time}")
            return True
        if "date" in query:
            str_date = datetime.datetime.now().strftime("%B %d, %Y")
            self.speak(f"The date is {str_date}")
            self.eel.DisplayMessage(f"The date is {str_date}")
            return True
        return False

    def handle_memory(self, query: str) -> bool:
        if "remember that" in query:
            remove_words_list = [self.assistant_name, "remember", "that"]
            message = self.remove_words(query, remove_words_list)
            # Use whole word replacement to fix the 'coding' -> 'codyoung' bug
            message = re.sub(r'\bi\b', 'you', message, flags=re.IGNORECASE)
            message = re.sub(r'\bmy\b', 'your', message, flags=re.IGNORECASE)
            self.speak("ok I remember that " + message)
            with open("Remember.txt", "a", encoding="utf-8") as remember:
                remember.write(message + " \n")
            return True
        if "what do you remember" in query:
            try:
                with open("Remember.txt", "r", encoding="utf-8") as remember:
                    lines = remember.readlines()
                    if not lines:
                        self.speak("I don't remember anything right now.")
                        self.eel.DisplayMessage("I don't remember anything right now.")
                        return True
                    
                    self.speak("You told me to remember these things:")
                    self.eel.DisplayMessage("You told me to remember these things:")
                    
                    for line in lines:
                        line = line.strip()
                        if line:
                            self.eel.DisplayMessage(line)
                            self.speak(line)
                    
                    self.speak("That's all.")
                    self.eel.DisplayMessage("That's all.")
            except FileNotFoundError:
                self.speak("I don't remember anything right now.")
                self.eel.DisplayMessage("I don't remember anything right now.")
            return True
        return False

    def handle_voice_change(self, query: str) -> bool:
        from intelli.core.speech import set_voice_preference
        if "female" in query:
            set_voice_preference('female')
            self.speak("Switching to my sweet female voice!")
        elif "male" in query or "boy" in query:
            set_voice_preference('male')
            self.speak("Switching to my default male voice!")
        return True

