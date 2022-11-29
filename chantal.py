import speech_recognition
import time
from subprocess import call
import pyttsx3

trigger = "chantal"
engine = pyttsx3.init()
recognizer = speech_recognition.Recognizer()

print("Beginning to listen...")

def recognize(audio):
    try:
        return recognizer.recognize_google(audio, language="fr-FR")
    except LookupError:
        print("error")
        return ''

def listen():
        with speech_recognition.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)
                words = recognize(audio)
        try:
                print("user : ", words)
                return words
        except speech_recognition.UnknownValueError:
                print("Could not understand audio")
        return ""

# print("Trying to always listen...\n")
# words = " "
flag = True
while flag:
        if trigger in listen().lower():
                engine.setProperty('rate', 180)
                engine.say("oui ?")
                engine.runAndWait()

        if "agenda" in listen().lower():
                engine.setProperty('rate', 180)
                engine.say("je vous écoute")
                engine.runAndWait()
                date_input = listen().lower()
                flag = False
        time.sleep(0.1) 

    

# engine.setProperty('rate', 200)
# engine.say("mode repos activé")
# engine.runAndWait()

print("\ncommande vocale détectée avant filtrage : ", date_input)