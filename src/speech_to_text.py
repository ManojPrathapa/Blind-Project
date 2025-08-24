import speech_recognition as sr

def listen():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print("🎙️ Listening... Speak now!")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio)
        print(f"✅ You said: {command}")
        return command.lower()
    except sr.UnknownValueError:
        print("❌ Sorry, I could not understand.")
        return None
    except sr.RequestError as e:
        print(f"❌ Could not request results; {e}")
        return None
