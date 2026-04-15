import eel
import wolframalpha
from command import speak
from intelli.core.config import get_settings

def WolfRamAlpha(query):
    apikey = get_settings().wolfram_alpha_api_key
    if not apikey:
        speak("Wolfram Alpha API key is missing.")
        return None
    requester = wolframalpha.Client(apikey)
    requested = requester.query(query)

    try:
        answer = next(requested.results).text
        return answer
    except StopIteration:  # Specify the exception type
        speak("The value is not answerable")

@eel.expose
def Calc(query):
        Term = str(query)
        Term = Term.replace("intelli","")
        Term = Term.replace("multiply","*")
        Term = Term.replace("plus","+")
        Term = Term.replace("minus","-")
        Term = Term.replace("divide","/")

        Final = str(Term)
        try:
            result = WolfRamAlpha(Final)
            if not result:
                raise ValueError("No result")
            print(f"{result}")
            eel.DisplayMessage(result)
            speak(result)
        
        except Exception:  # Catch all other exceptions
            speak("The value is not answerable")
            eel.DisplayMessage("The value is not answerable")
        eel.ShowHood()
# Calc()
