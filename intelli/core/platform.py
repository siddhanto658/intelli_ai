import os
import platform
import shutil
import subprocess
import webbrowser
from pathlib import Path
from typing import Optional
import threading
import time
import numpy as np
import cv2
import mss


class PlatformAdapter:
    def __init__(self):
        self.system = platform.system().lower()
        self._is_recording = False
        self._is_paused = False
        self._recording_thread = None
        self._video_writer = None

    def open_url(self, url: str) -> bool:
        try:
            webbrowser.open(url)
            return True
        except Exception:
            return False

    def open_app(self, app_or_path: str) -> bool:
        target = app_or_path.strip()
        if not target:
            return False

        try:
            if self.system == "windows":
                os.startfile(target)  # type: ignore[attr-defined]
                return True
            if self.system == "darwin":
                subprocess.Popen(["open", target])
                return True
            # linux and other unix
            if Path(target).exists():
                subprocess.Popen(["xdg-open", target])
                return True
            executable = shutil.which(target)
            if executable:
                subprocess.Popen([executable])
                return True
            subprocess.Popen(["xdg-open", target])
            return True
        except Exception:
            return False

    def shutdown(self) -> bool:
        try:
            if self.system == "windows":
                subprocess.Popen(["shutdown", "/s", "/t", "1"])
            elif self.system == "darwin":
                subprocess.Popen(["osascript", "-e", 'tell app "System Events" to shut down'])
            else:
                subprocess.Popen(["shutdown", "-h", "now"])
            return True
        except Exception:
            return False

    def screenshot(self, output_path: str, pyautogui_module: Optional[object] = None) -> bool:
        if not pyautogui_module:
            return False
        try:
            image = pyautogui_module.screenshot()
            image.save(output_path)
            return True
        except Exception:
            return False

    def launcher_key(self) -> str:
        if self.system == "windows":
            return "win"
        if self.system == "darwin":
            return "command"
        return "super"

    def open_whatsapp_link(self, mobile_no: str, text: str = "") -> bool:
        encoded_text = text.replace(" ", "%20")
        web_url = f"https://wa.me/{mobile_no}?text={encoded_text}"
        return self.open_url(web_url)

    def _record_screen_loop(self, output_path: str):
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # primary monitor
            width = monitor["width"]
            height = monitor["height"]
            
            fourcc = cv2.VideoWriter_fourcc(*"XVID")
            self._video_writer = cv2.VideoWriter(output_path, fourcc, 20.0, (width, height))
            
            while self._is_recording:
                if not self._is_paused:
                    img = np.array(sct.grab(monitor))
                    # Convert BGRA to BGR
                    frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                    self._video_writer.write(frame)
                time.sleep(1/20) # 20 fps approx
            
            self._video_writer.release()
            self._video_writer = None

    def start_screen_recording(self, output_path: str) -> bool:
        if self._is_recording:
            return False
        
        self._is_recording = True
        self._is_paused = False
        self._recording_thread = threading.Thread(target=self._record_screen_loop, args=(output_path,))
        self._recording_thread.start()
        return True

    def pause_screen_recording(self) -> bool:
        if not self._is_recording:
            return False
        self._is_paused = True
        return True

    def resume_screen_recording(self) -> bool:
        if not self._is_recording:
            return False
        self._is_paused = False
        return True

    def stop_screen_recording(self) -> bool:
        if not self._is_recording:
            return False
        self._is_recording = False
        if self._recording_thread:
            self._recording_thread.join()
        return True


