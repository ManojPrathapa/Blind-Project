import os
import datetime
from text_to_speech import speak

def handle_command(command: str):
    """
    Handle voice commands and return an action string.
    """

    if not command:
        return "No command"

    command = command.lower()

    # Simple greetings
    if "hello" in command:
        speak("Hello! How can I help you?")
        return "Greeted"

    # Tell time
    elif "time" in command:
        now = datetime.datetime.now().strftime("%H:%M")
        speak(f"The time is {now}")
        return "Told Time"

    # Open notepad (Windows)
    elif "open notepad" in command:
        speak("Opening Notepad")
        os.system("notepad")
        return "Opened Notepad"

    # Exit program
    elif "exit" in command or "quit" in command:
        speak("Exiting the program. Goodbye!")
        return "Exit"

    # Fallback
    else:
        speak("Sorry, I did not understand that command.")
        return "Unknown"

