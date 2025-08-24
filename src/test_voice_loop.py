from speech_to_text import listen_command
from text_to_speech import speak

if __name__ == "__main__":
    speak("Hello! Say something.")
    command = listen_command()
    speak(f"You said: {command}")
