  
import multiprocessing
import threading
import platform
import subprocess
import os
import sys
import signal
from pathlib import Path

# Get the directory where run.py is located
BASE_DIR = Path(__file__).parent.absolute()
ENV_FILE = BASE_DIR / ".env"

# Global process references for cleanup
_main_process = None
_hotword_flag = None

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
    sys.stdout.flush()
    from features import hotword
    from intelli.core.thread_safe import hotword_active
    global _hotword_flag
    _hotword_flag = hotword_active
    hotword()

def stopINTELLI():
    """Stop INTELLI gracefully."""
    global _main_process, _hotword_flag
    print("\n[SHUTDOWN] Stopping INTELLI...")
    
    # Stop hotword listener
    if _hotword_flag is not None:
        _hotword_flag.clear()
        print("[SHUTDOWN] Hotword listener stopped")
    
    # Terminate main process
    if _main_process and _main_process.is_alive():
        _main_process.terminate()
        _main_process.join(timeout=2)
        if _main_process.is_alive():
            _main_process.kill()
        print("[SHUTDOWN] Main process terminated")
    
    print("[SHUTDOWN] INTELLI stopped successfully")
    sys.exit(0)

def signal_handler(signum, frame):
    """Handle Ctrl+C and termination signals."""
    print("\n[RECEIVED] Termination signal")
    stopINTELLI()

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Start both processes
if __name__ == '__main__':
    print("=" * 50)
    print("  INTELLI AI - Voice Assistant")
    print("=" * 50)
    print("  Commands:")
    print("    Ctrl+C     - Stop INTELLI gracefully")
    print("    close btn  - End session from UI")
    print("=" * 50)
    print()
    
    init_database()
    capabilities = detect_capabilities(PlatformAdapter())
    print(f"Detected OS: {capabilities.os_name}")
    
    _main_process = multiprocessing.Process(target=startINTELLI)
    _main_process.start()
    
    if platform.system().lower() == "windows":
        subprocess.call([r'device.bat'])
    
    # Start hotword in a thread instead of process (shares eel instance)
    hotword_thread = threading.Thread(target=startHotwordThread, daemon=True)
    hotword_thread.start()
    
    try:
        _main_process.join()
    except KeyboardInterrupt:
        stopINTELLI()

    print("system stop")