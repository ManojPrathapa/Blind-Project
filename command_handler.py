import os
import datetime
from text_to_speech import speak
from ocr_reader import read_text_from_image
from person_recognizer import recognize_person

def handle_command(command: str):
    if not command:
        return "No command"

    command = command.lower()

    if "hello" in command:
        speak("Hello! How can I help you?")
        return "Greeted"

    elif "time" in command:
        now = datetime.datetime.now().strftime("%H:%M")
        speak(f"The time is {now}")
        return "Told Time"

    elif "open notepad" in command:
        speak("Opening Notepad")
        os.system("notepad")
        return "Opened Notepad"

    elif "read image" in command or "ocr" in command:
        speak("Reading text from sample image")
        text = read_text_from_image("sample.jpg")  # put an image here
        return f"OCR: {text}"

    elif "who is this" in command or "recognize person" in command:
        speak("Checking person in image")
        name = recognize_person("person.jpg")  # put an image here
        return f"Person: {name}"

    elif "exit" in command or "quit" in command:
        speak("Exiting the program. Goodbye!")
        return "Exit"

    else:
        speak("Sorry, I did not understand that command.")
        return "Unknown"
