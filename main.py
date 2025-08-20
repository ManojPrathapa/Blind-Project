import time
from pathlib import Path
from src.detector import Detector
from src.voice import Voice
from src.utils import box_center, box_area, direction_from_center
from src.camera import select_camera

MODEL_PATH = Path("models/yolov5s.pt")
CONF_THRESHOLD = 0.35
ANNOUNCE_COOLDOWN = 2.5
DISTANCE_SCALING = 1500.0

def approximate_distance(area):
    if area <= 0:
        return None
    return (DISTANCE_SCALING / (area ** 0.5))

def main():
    print("Starting BlindAssist...")

    if not MODEL_PATH.exists():
        print(f"Model not found at {MODEL_PATH}. Please download yolov5s.pt and put it in models/ folder.")
        return

    # Select camera
    VIDEO_SOURCE = select_camera()

    detector = Detector(model_path=str(MODEL_PATH), conf=CONF_THRESHOLD, device="cpu")
    voice = Voice()
    tracked = {}

    try:
        for frame, results in detector.stream(source=VIDEO_SOURCE):
            now = time.time()
            frame_h, frame_w = frame.shape[:2]

            detections = []
            for r in results:
                boxes = r.boxes
                if boxes is None or len(boxes) == 0:
                    continue
                for box in boxes:
                    xyxy = box.xyxy.cpu().numpy().flatten().tolist()
                    conf = float(box.conf.cpu().numpy()) if hasattr(box, "conf") else float(box.conf)
                    cls_id = int(box.cls.cpu().numpy()) if hasattr(box, "cls") else int(box.cls)
                    label = detector.names[cls_id] if cls_id < len(detector.names) else str(cls_id)

                    x1, y1, x2, y2 = map(int, xyxy[:4])
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
                    if k.startswith(label + "_"):
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

            # Remove objects not seen for 6s
            to_delete = [k for k, info in tracked.items() if now - info["last_time"] > 6.0]
            for k in to_delete:
                del tracked[k]

    except KeyboardInterrupt:
        print("Interrupted by user.")
    finally:
        voice.stop()
        detector.close()
        print("Exited cleanly.")

if __name__ == "__main__":
    main()
