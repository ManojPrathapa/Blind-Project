import pyttsx3

class VoiceModule:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 150)

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

