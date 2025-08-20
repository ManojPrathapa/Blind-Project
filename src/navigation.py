import pyttsx3

def navigate(detections):
    engine = pyttsx3.init()
    if not detections:
        engine.say("No objects detected.")
    else:
        for obj in detections:
            engine.say(f"{obj} ahead.")
    engine.runAndWait()
