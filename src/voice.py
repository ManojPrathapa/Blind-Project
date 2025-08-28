import pyttsx3
import threading
import queue
import time

class Voice:
    def __init__(self):
        self.engine = pyttsx3.init()
        try:
            self.engine.setProperty("rate", 160)
            self.engine.setProperty("volume", 1.0)
        except Exception:
            pass
        self.q = queue.Queue()
        self.running = True
        self.th = threading.Thread(target=self._worker, daemon=True)
        self.th.start()

    def _worker(self):
        while self.running:
            try:
                text = self.q.get(timeout=0.5)
            except queue.Empty:
                continue
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print("TTS error:", e)

    def speak(self, text: str):
        if text:
            self.q.put(text)

    def stop(self):
        deadline = time.time() + 2.0
        while not self.q.empty() and time.time() < deadline:
            time.sleep(0.1)
        self.running = False
        try:
            self.engine.stop()
        except Exception:
            pass
        try:
            if self.th.is_alive():
                self.th.join(timeout=1.0)
        except Exception:
            pass