# src/voice.py
import pyttsx3
import threading
import queue
import time

class Voice:
    def __init__(self):
        self.engine = pyttsx3.init()
        # tuning
        try:
            self.engine.setProperty("rate", 155)
            self.engine.setProperty("volume", 1.0)
        except Exception:
            pass

        self.q = queue.Queue()
        self._running = True
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def _worker(self):
        while self._running:
            try:
                text = self.q.get(timeout=0.5)
            except queue.Empty:
                continue
            try:
                # speak (pyttsx3 is blocking so this thread will block until speak done)
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print("Voice error:", e)

    def speak(self, text: str):
        """Queue text to be spoken (non-blocking)."""
        if not text:
            return
        # Avoid stacking identical messages sequentially: if last item equals text, skip
        # But simplest: always enqueue
        self.q.put(text)

    def stop(self):
        # wait for queue to empty then shutdown
        timeout = time.time() + 2.0
        while not self.q.empty() and time.time() < timeout:
            time.sleep(0.1)
        self._running = False
        try:
            if self._thread.is_alive():
                self._thread.join(timeout=1.0)
        except Exception:
            pass
        try:
            self.engine.stop()
        except Exception:
            pass
