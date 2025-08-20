import cv2
from ultralytics import YOLO

class Detector:
    def __init__(self, model_path="models/yolov5s.pt", conf=0.35, device="cpu"):
        self.model = YOLO(model_path)
        self.conf = conf
        self.device = device
        try:
            self.model.predict_kwargs = {"conf": self.conf}
        except Exception:
            pass
        self.names = self.model.names

    def stream(self, source=0, show=True, imgsz=640):
        cap = cv2.VideoCapture(source)
        if not cap.isOpened():
            raise RuntimeError(f"Cannot open video source {source}")

        while True:
            ret, frame = cap.read()
            if not ret:
                continue  # keep trying for IP webcam

            results = self.model.predict(source=[frame], imgsz=imgsz, conf=self.conf, device=self.device, verbose=False)

            if show:
                annotated = results[0].plot()
                annotated_bgr = cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR)
                cv2.imshow("BlindAssist - Detected", annotated_bgr)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            yield frame, results

        cap.release()
        cv2.destroyAllWindows()

    def close(self):
        pass
