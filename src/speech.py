import json
import queue
import threading
import sounddevice as sd
from vosk import Model, KaldiRecognizer

class SpeechListener:
    """
    Offline voice command listener (English).
    Download a Vosk model and set model_path to its folder.
    e.g., 'vosk-model-small-en-us-0.15'
    """
    def __init__(self, model_path: str = None, samplerate: int = 16000, device=None):
        self.model = Model(model_path) if model_path else None
        self.rec = KaldiRecognizer(self.model, samplerate) if self.model else None
        self.rec.SetWords(True) if self.rec else None
        self.q = queue.Queue()
        self.samplerate = samplerate
        self.device = device
        self._stream = None
        self._thread = None
        self._running = False

    def _callback(self, indata, frames, time, status):
        if status:
            return
        self.q.put(bytes(indata))

    def start(self):
        if not self.model:
            raise RuntimeError("Vosk model not loaded. Provide model_path to SpeechListener.")
        self._running = True
        self._stream = sd.RawInputStream(samplerate=self.samplerate, blocksize = 8000,
                                         device=self.device, dtype='int16',
                                         channels=1, callback=self._callback)
        self._stream.start()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _loop(self):
        while self._running:
            data = self.q.get()
            if self.rec.AcceptWaveform(data):
                result = json.loads(self.rec.Result())
                text = result.get("text", "").strip()
                if text:
                    self.on_command(text)

    def on_command(self, text: str):
        """Override in user code or assign a function: listener.on_command = func"""
        print("[Command]", text)

    def stop(self):
        self._running = False
        try:
            if self._stream:
                self._stream.stop()
                self._stream.close()
        except Exception:
            pass
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
