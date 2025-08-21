# main.py
from __future__ import annotations

import os
import time
import threading
from pathlib import Path

from src.detector import Detector
from src.voice import Voice
from src.utils import box_center, box_area, direction_from_center
from src.camera import select_camera
from src.ocr import OCRReader
from src.navigation import NavigationManager
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

MODEL_PATH = Path("models/yolov5s.pt")
CONF_THRESHOLD = 0.35
ANNOUNCE_COOLDOWN = 2.5
DISTANCE_SCALING = 1500.0


def approximate_distance(area):
    if area <= 0:
        return None
    return (DISTANCE_SCALING / (area ** 0.5))


def run_detection(voice: Voice, source=None):
    if not MODEL_PATH.exists():
        print(f"Model not found at {MODEL_PATH}. Put yolov5s.pt in models/.")
        voice.speak("Model file missing.")
        return

    if source is None:
        source = select_camera()

    detector = Detector(model_path=str(MODEL_PATH), conf=CONF_THRESHOLD, device="cpu")
    tracked = {}

    try:
        for frame, results in detector.stream(source=source):
            now = time.time()
            frame_h, frame_w = frame.shape[:2]

            detections = []
            for r in results:
                boxes = getattr(r, "boxes", None)
                if boxes is None or len(boxes) == 0:
                    continue
                for box in boxes:
                    # ultralytics Results boxes
                    xyxy = box.xyxy
                    if hasattr(xyxy, "cpu"):
                        xyxy = xyxy.cpu().numpy()
                    xyxy = getattr(xyxy, "flatten", lambda: xyxy)().tolist()
                    if len(xyxy) < 4:
                        continue
                    x1, y1, x2, y2 = map(int, xyxy[:4])
                    conf = float(getattr(box.conf, "item", lambda: box.conf)())
                    cls_id = int(getattr(box.cls, "item", lambda: box.cls)())
                    label = detector.names[cls_id] if cls_id < len(detector.names) else str(cls_id)

                    cx, cy = box_center((x1, y1, x2, y2))
                    area = box_area((x1, y1, x2, y2))

                    detections.append({
                        "label": label,
                        "conf": conf,
                        "box": (x1, y1, x2, y2),
                        "center": (cx, cy),
                        "area": area
                    })

            for det in detections:
                label = det["label"]
                center = det["center"]
                area = det["area"]
                direction = direction_from_center(center[0], frame_w)
                dist_est = approximate_distance(area)
                if dist_est is None:
                    continue

                key = f"{label}_{round(center[0]/50)}_{round(center[1]/50)}"
                matched_key = None
                for k, info in tracked.items():
                    if not k.startswith(label + "_"):
                        continue
                    prev_cx, prev_cy = info["last_center"]
                    if abs(prev_cx - center[0]) < 80 and abs(prev_cy - center[1]) < 80:
                        matched_key = k
                        break
                if matched_key is None:
                    matched_key = key

                info = tracked.get(matched_key)
                announce = False
                if info is None or (time.time() - info["last_time"] >= ANNOUNCE_COOLDOWN):
                    announce = True
                    tracked[matched_key] = {"last_time": time.time(), "last_center": center}

                tracked[matched_key]["last_center"] = center

                if announce:
                    phrase = f"{label} {direction}, approximately {dist_est:.1f} meters away"
                    print("ANNOUNCE:", phrase)
                    voice.speak(phrase)

            # Cleanup
            to_delete = [k for k, info in tracked.items() if now - info["last_time"] > 6.0]
            for k in to_delete:
                del tracked[k]

    finally:
        detector.close()


def run_ocr(voice: Voice, source=None, languages=None):
    if source is None:
        source = select_camera()
    reader = OCRReader(languages=languages or ["en"], gpu=False, min_confidence=0.45, speak_cooldown=2.0)
    reader.run_loop(source=source, on_text=lambda s: voice.speak(s))


def run_navigation_with_detection(voice: Voice):
    print("Enter origin address (or 'current location' if you plan to start where you are):")
    origin = input("> ").strip()
    print("Enter destination address:")
    destination = input("> ").strip()

    # Start navigation (opens Google Maps + optional API voice guidance)
    nav = NavigationManager(voice_say=voice.speak, travel_mode="walking")
    nav.start_navigation(
        origin=origin,
        destination=destination,
        use_api_guidance=True,          # set False to force browser-only mode
        location_supplier=None,         # provide a callback returning (lat, lon) if you have GPS feed
        announce_interval=12.0,
    )

    # Start object detection concurrently
    cam_source = select_camera()
    det_thread = threading.Thread(target=run_detection, args=(voice, cam_source), daemon=True)
    det_thread.start()

    voice.speak("Navigation started. Object detection running.")
    print("Press Ctrl+C to stop navigation + detection.")
    try:
        while det_thread.is_alive():
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        nav.stop()


def main():
    voice = Voice()
    try:
        print("\nStarting BlindAssist…\n")
        while True:
            print("=== BlindAssist – Feature Menu ===")
            print("1. Object detection with spoken distance/direction")
            print("2. Read text (OCR) from camera")
            print("3. Voice-guided navigation to a destination (opens Google Maps) + live object detection")
            print("4. Quit")
            choice = input("Select [1-4]: ").strip()

            if choice == "1":
                run_detection(voice)
            elif choice == "2":
                # Example: OCR in English + Hindi -> ["en","hi"]
                run_ocr(voice, languages=["en"])
            elif choice == "3":
                run_navigation_with_detection(voice)
            elif choice == "4":
                break
            else:
                print("Invalid option.\n")
    finally:
        voice.stop()
        print("Exited cleanly.")


if __name__ == "__main__":
    main()
