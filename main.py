import os
import eel
import traceback
import warnings
import sys
warnings.filterwarnings("ignore", category=UserWarning)

from logger import logger
from features import *
from command import *

def start():
    try:
        logger.info("Starting INTELLI AI Assistant...")
        
        eel.init("www")
        logger.info("Eel initialized")
        
        playAssistantSound()
        logger.info("Assistant sound played")

        try:
            os.system('start msedge.exe --app="http://localhost:8000/index.html"')
            logger.info("Browser opened")
        except Exception as e:
            logger.warning(f"Could not open browser: {e}")

        eel.start('index.html', mode=None, host='localhost', block=True)
    except Exception as e:
        logger.error(f"Fatal error during startup: {e}")
        traceback.print_exc()
        input("Press Enter to exit...")

start()