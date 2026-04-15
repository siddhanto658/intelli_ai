import eel
import socket

from features import *
from command import *

def start():
    eel.init("www")
    playAssistantSound()
    
    # Try different ports if 8000 is in use
    ports = [8000, 8001, 8080, 8888]
    for port in ports:
        try:
            eel.start('index.html', host='localhost', port=port, size=(720, 540), block=True)
            break
        except OSError as e:
            if "port" in str(e).lower() or "address" in str(e).lower():
                print(f"Port {port} in use, trying next...")
                continue
            raise