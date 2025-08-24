import pyttsx3

def speak(text: str):
    """Convert text to speech and speak it aloud."""
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Test
if __name__ == "__main__":
    speak("Hello! I can talk now. This is text to speech working.")
