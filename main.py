import eel

from features import *
from command import *

def start():
    
    eel.init("www")

    playAssistantSound()

    eel.start('index.html', host='localhost', size=(720, 540), block=True)