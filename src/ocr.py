import cv2
import easyocr
import pyttsx3
import threading
import time

from src.navigation import NavigationManager  # use unified navigation

# =====================
# Voice Engine
# =====================
class Voice:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 150)

    def speak(self, text: str):
        print(f"[VOICE]: {text}")
        self.engine.say(text)
        self.engine.runAndWait()


# =====================
# OCR Reader
# =====================
class OCRReader:
    def __init__(self):
        self.reader = easyocr.Reader(["en"], gpu=False)

    def run_loop(self, source=0, on_text=None):
        cap = cv2.VideoCapture(source)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            results = self.reader.readtext(frame)
            for (bbox, text, prob) in results:
                if prob > 0.5:
                    if on_text:
                        on_text(text)

                    pts = cv2.boxPoints(cv2.minAreaRect(bbox))
                    pts = cv2.convexHull(pts.astype(int))
                    cv2.polylines(frame, [pts], True, (0, 255, 0), 2)
                    cv2.putText(frame, text, tuple(pts[0]), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            cv2.imshow("OCR", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()


# =====================
# Object Detection Stub
# (replace with real YOLO/SSD later)
# =====================
class ObjectDetector:
    def __init__(self, voice: Voice):
        self.voice = voice
        self.object_classes = ["person", "car", "dog", "chair"]

    def detect_objects(self, frame):
        # Mock detection
        h, w, _ = frame.shape
        bbox = [w // 4, h // 4, w // 2, h // 2]
        detected_object = "person"
        distance = self.estimate_distance(bbox, w, h)

        # Speak result
        self.voice.speak(f"{detected_object} detected {distance} meters away")

        # Draw rectangle
        cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 0, 255), 2)
        cv2.putText(frame, f"{detected_object} {distance}m", (bbox[0], bbox[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        return [(detected_object, bbox, distance)]

    def estimate_distance(self, bbox, frame_w, frame_h):
        box_w = bbox[2] - bbox[0]
        scale = frame_w / box_w
        distance_m = round(scale * 0.5, 1)
        return distance_m


# =====================
# Main Runner for Nav + Objects
# =====================
def run_navigation_with_objects():
    voice = Voice()
    detector = ObjectDetector(voice)
    navigator = NavigationManager(voice.speak, travel_mode="walking")

    start = input("Enter starting location: ")
    destination = input("Enter destination: ")

    # Start navigation (runs in background, API or fallback browser)
    navigator.start_navigation(start, destination, use_api_guidance=True)

    # Start camera loop
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        detector.detect_objects(frame)
        cv2.imshow("Navigation + Object Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    navigator.stop()


# =====================
# Entry Point
# =====================
if __name__ == "__main__":
    run_navigation_with_objects()
