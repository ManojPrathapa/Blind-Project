import os
import cv2
import time
import threading
import pyttsx3
import face_recognition
import pytesseract
import speech_recognition as sr
import webbrowser
from ultralytics import YOLO

# -------------------
# Text-to-Speech Setup
# -------------------
_engine = pyttsx3.init()
_engine.setProperty('rate', 170)

def speak(text):
    try:
        _engine.say(text)
        _engine.runAndWait()
    except RuntimeError:
        pass  # engine already running

# -------------------
# Voice Command Setup
# -------------------
recognizer = sr.Recognizer()
last_command = None

def listen_command(timeout=5, phrase_time_limit=5):
    global last_command
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            print("[Voice] Listening for command...")
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            command = recognizer.recognize_google(audio).lower()
            last_command = command
            return command
    except (sr.WaitTimeoutError, sr.UnknownValueError, sr.RequestError):
        return None

def async_listen():
    """Run voice recognition in a separate thread."""
    while True:
        listen_command(timeout=5, phrase_time_limit=5)

# -------------------
# Face Recognition
# -------------------
class FaceRecognition:
    def __init__(self, known_faces_dir="known_faces"):
        self.known_encodings = []
        self.known_names = []
        self.load_known_faces(known_faces_dir)

    def load_known_faces(self, known_faces_dir):
        if not os.path.exists(known_faces_dir):
            print(f"[WARNING] Known faces directory '{known_faces_dir}' does not exist.")
            return
        for filename in os.listdir(known_faces_dir):
            if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                path = os.path.join(known_faces_dir, filename)
                image = cv2.imread(path)
                if image is None:
                    print(f"[WARNING] Could not read image: {filename}")
                    continue
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                encodings = face_recognition.face_encodings(rgb_image)
                if encodings:
                    self.known_encodings.append(encodings[0])
                    self.known_names.append(os.path.splitext(filename)[0])
                else:
                    print(f"[INFO] No face found in {filename}")

    def recognize_face(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        locations = face_recognition.face_locations(rgb_frame)
        encodings = face_recognition.face_encodings(rgb_frame, locations)
        for encoding, location in zip(encodings, locations):
            matches = face_recognition.compare_faces(self.known_encodings, encoding)
            name = "Unknown"
            if True in matches:
                name = self.known_names[matches.index(True)]
            top, right, bottom, left = location
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            speak(f"This is {name}")
        return frame

# -------------------
# OCR Function
# -------------------
def perform_ocr(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
    text = " ".join([word for word in data['text'] if word.strip() != ""])
    if text:
        speak(f"OCR detected: {text}")
    else:
        speak("No text detected.")

# -------------------
# Navigation Manager
# -------------------
class NavigationManager:
    def start_navigation(self, destination):
        # Automatically use current location
        speak(f"Navigation started to {destination}")
        url = f"https://www.google.com/maps/dir/?api=1&origin=Current+Location&destination={destination}"
        webbrowser.open(url)
        print(f"[INFO] Navigation to: {destination}")

# -------------------
# YOLO Object Detection
# -------------------
class YOLODetector:
    def __init__(self, model_path="yolov5s.pt"):
        self.model = YOLO(model_path)

    def detect_objects(self, frame):
        results = self.model(frame)[0]  # take first result
        for result in results.boxes:
            x1, y1, x2, y2 = map(int, result.xyxy[0])
            conf = float(result.conf[0])
            cls = int(result.cls[0])
            label = self.model.names[cls] if hasattr(self.model, "names") else str(cls)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(frame, f"{label} {conf:.2f}", (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        return frame

# -------------------
# Main Loop
# -------------------
def main():
    speak("System ready. Listening for commands.")
    face_recognizer = FaceRecognition()
    navigator = NavigationManager()
    yolo_detector = YOLODetector()

    # Start async voice listener
    listener_thread = threading.Thread(target=async_listen, daemon=True)
    listener_thread.start()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        speak("Warning: Camera not detected!")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # Run YOLO only after destination is given
        global last_command
        command = last_command
        last_command = None

        if command:
            print(f"[Command heard]: {command}")

            if "exit" in command:
                speak("Exiting system.")
                break

            elif "who is this" in command:
                face_recognizer.recognize_face(frame)

            elif "navigate to" in command:
                speak("Please tell me the destination.")
                destination = None
                while not destination:
                    time.sleep(0.5)
                    destination = last_command
                    last_command = None
                navigator.start_navigation(destination)
                speak(f"Starting object detection now.")
                # Continue YOLO detection after navigation
                frame = yolo_detector.detect_objects(frame)

            elif "read text" in command or "ocr" in command:
                perform_ocr(frame)

        # Show camera for debugging
        cv2.imshow("Camera", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
