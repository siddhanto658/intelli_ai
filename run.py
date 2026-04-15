  
import multiprocessing
import threading
import platform
import subprocess
import os
from pathlib import Path

# Get the directory where run.py is located
BASE_DIR = Path(__file__).parent.absolute()
ENV_FILE = BASE_DIR / ".env"

# Load environment BEFORE spawning processes
def _load_env():
    try:
        from dotenv import load_dotenv
        if ENV_FILE.exists():
            load_dotenv(dotenv_path=ENV_FILE)
            print(f"[ENV] Loaded .env from: {ENV_FILE}")
            gemini = os.getenv("GEMINI_API_KEY", "")
            groq = os.getenv("GROQ_API_KEY", "")
            news = os.getenv("NEWS_API_KEY", "")
            print(f"[ENV] GEMINI_API_KEY: {'OK' if gemini else 'MISSING'}")
            print(f"[ENV] GROQ_API_KEY: {'OK' if groq else 'MISSING'}")
            print(f"[ENV] NEWS_API_KEY: {'OK' if news else 'MISSING'}")
        else:
            print(f"[ENV] Warning: .env file not found at {ENV_FILE}")
    except ImportError:
        print("[ENV] python-dotenv not installed, using system environment")

_load_env()

from db import init_database
from intelli.core.capabilities import detect_capabilities
from intelli.core.config import load_environment
from intelli.core.platform import PlatformAdapter

# To run INTELLI
def startINTELLI():
        print("Process 1 is running.")
        _load_env()
        from main import start
        start()

# To run hotword - as a thread within main process
def startHotwordThread():
    print("Hotword thread starting in main process...")
    import sys
    sys.stdout.flush()
    from features import hotword 
    hotword()


    # Start both processes
if __name__ == '__main__':
        init_database()
        capabilities = detect_capabilities(PlatformAdapter())
        print(f"Detected OS: {capabilities.os_name}")
        
        p1 = multiprocessing.Process(target=startINTELLI)
        p1.start()
        
        if platform.system().lower() == "windows":
            subprocess.call([r'device.bat'])
        
        # Start hotword in a thread instead of process (shares eel instance)
        hotword_thread = threading.Thread(target=startHotwordThread, daemon=True)
        hotword_thread.start()
        
        p1.join()

        print("system stop")