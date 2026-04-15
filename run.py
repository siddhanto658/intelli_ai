 
import multiprocessing
import platform
import subprocess

from db import init_database
from intelli.core.capabilities import detect_capabilities
from intelli.core.config import load_environment
from intelli.core.platform import PlatformAdapter

# To run INTELLI
def startINTELLI():
        # Code for process 1
        print("Process 1 is running.")
        load_environment(".env")
        from main import start
        start()

# To run hotword
def listenHotword():
        # Code for process 2
        print("Process 2 is running.")
        load_environment(".env")
        from features import hotword 
        hotword()


    # Start both processes
if __name__ == '__main__':
        load_environment(".env")
        init_database()
        capabilities = detect_capabilities(PlatformAdapter())
        print(f"Detected OS: {capabilities.os_name}")
        p1 = multiprocessing.Process(target=startINTELLI)
        p2 = multiprocessing.Process(target=listenHotword)
        p1.start()
        if platform.system().lower() == "windows":
            subprocess.call([r'device.bat'])
        p2.start()
        p1.join()

        if p2.is_alive():
            p2.terminate()
            p2.join()

        print("system stop")