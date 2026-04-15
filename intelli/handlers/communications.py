import sqlite3
import time
from urllib.parse import quote
from typing import Callable, Tuple
import platform
import subprocess
import pyautogui

from helper import remove_words
from intelli.core.platform import PlatformAdapter

class CommunicationsHandlers:
    def __init__(
        self,
        speak: Callable[[str], None],
        takecommand: Callable[[], str],
        permission_checker: Callable[[str], bool],
        platform_adapter: PlatformAdapter,
        assistant_name: str,
    ):
        self.speak = speak
        self.takecommand = takecommand
        self.permission_checker = permission_checker
        self.platform = platform_adapter
        self.assistant_name = assistant_name
        self.db_path = "INTELLI.db"

    def _find_contact(self, query: str) -> Tuple[str, str]:
        words_to_remove = [self.assistant_name, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'whatsapp', 'video']
        clean_query = remove_words(query, words_to_remove)
        
        try:
            clean_query = clean_query.strip().lower()
            with sqlite3.connect(self.db_path) as con:
                cursor = con.cursor()
                cursor.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + clean_query + '%', clean_query + '%'))
                results = cursor.fetchall()
                if not results:
                    self.speak('not exist in contacts')
                    return "", ""
                    
                mobile_number_str = str(results[0][0])
                if not mobile_number_str.startswith('+'):
                    # assuming +91 for now, this can be configured later
                    mobile_number_str = '+91' + mobile_number_str
                    
                return mobile_number_str, clean_query
        except Exception:
            self.speak('not exist in contacts')
            return "", ""

    def handle_communication(self, query: str) -> bool:
        if not self.permission_checker("send messages or place calls"):
            self.speak("Permission denied. Communication action cancelled.")
            return True

        contact_no, name = self._find_contact(query)
        if not contact_no:
            return True

        flag = ""
        user_message = ""
        if "message" in query:
            flag = "message"
            self.speak("what message to send")
            user_message = self.takecommand()
        elif "phone call" in query:
            flag = "call"
        else:
            flag = "video call"

        self._send_whatsapp(contact_no, user_message, flag, name)
        return True

    def _send_whatsapp(self, mobile_no: str, message: str, flag: str, name: str):
        if flag == 'message':
            target_tab = 12
            intelli_message = "message send successfully to " + name
        elif flag == 'call':
            target_tab = 7
            message = ''
            intelli_message = "calling to " + name
        else:
            target_tab = 6
            message = ''
            intelli_message = "starting video call with " + name

        encoded_message = quote(message)

        if self.platform.system == "linux":
            # Native WhatsDesk automation for Linux
            self.speak("Opening WhatsDesk.")
            subprocess.Popen(["whatsdesk"])
            time.sleep(5)
            # Basic pyautogui commands to navigate to search, find user, paste message
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(1)
            pyautogui.write(name)
            time.sleep(2)
            pyautogui.press('enter')
            time.sleep(1)
            if message:
                pyautogui.write(message)
                time.sleep(1)
                pyautogui.press('enter')
            self.speak(intelli_message)
            return

        # Fallback to web link
        if not self.platform.open_whatsapp_link(mobile_no, encoded_message):
            self.speak("Unable to open WhatsApp on this system.")
            return

        # Optional desktop automation for better UX on Windows
        if self.platform.system == "windows":
            time.sleep(5)
            pyautogui.hotkey('ctrl', 'f')
            for _ in range(1, target_tab):
                pyautogui.hotkey('tab')
            time.sleep(1)
            pyautogui.hotkey('enter')

        self.speak(intelli_message)
