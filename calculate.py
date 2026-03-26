import eel
import wolframalpha
import pyttsx3
import speech_recognition
from command import speech_rate, logger

engine = pyttsx3.init("sapi5")
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[1].id)
rate = engine.setProperty("rate", speech_rate)

def speak(audio):
    try:
        engine.say(audio)
        engine.runAndWait()
    except Exception as e:
        logger.error(f"TTS error in calculate: {e}")


def WolfRamAlpha(query):
    try:
        apikey = "VHJK66YX43"
        requester = wolframalpha.Client(apikey)
        requested = requester.query(query)

        try:
            answer = next(requested.results).text
            return answer
        except StopIteration:
            speak("The value is not answerable")
            return None
        except Exception as e:
            logger.error(f"WolframAlpha query error: {e}")
            speak("The value is not answerable")
            return None
    except Exception as e:
        logger.error(f"WolframAlpha error: {e}")
        speak("Calculation service is unavailable")
        return None

@eel.expose
def Calc(query):
        try:
            Term = str(query)
            Term = Term.replace("intelli","")
            Term = Term.replace("multiply","*")
            Term = Term.replace("plus","+")
            Term = Term.replace("minus","-")
            Term = Term.replace("divide","/")

            Final = str(Term)
            logger.info(f"Calculating: {Final}")
            try:
                result = WolfRamAlpha(Final)
                if result:
                    print(f"{result}")
                    eel.DisplayMessage(result)
                    speak(result)
                else:
                    speak("Could not calculate the result")
                    eel.DisplayMessage("Could not calculate")
            
            except Exception as e:
                logger.error(f"Calculation error: {e}")
                speak("The value is not answerable")
                eel.DisplayMessage("The value is not answerable")
            eel.ShowHood()
        except Exception as e:
            logger.error(f"Calc function error: {e}")
            eel.ShowHood()
