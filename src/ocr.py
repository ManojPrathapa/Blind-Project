import pytesseract
import pyttsx3
import cv2
from typing import Optional, List
import easyocr

class OCR:
    def __init__(self, languages: str = 'eng', use_easyocr: bool = True):
        """
        languages: Tesseract language codes, e.g., 'eng+fra+hin'
        use_easyocr: if True, use EasyOCR as fallback for better recognition
        """
        self.languages = languages
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 180)  # speech rate
        self.engine.setProperty('volume', 1.0)
        self.use_easyocr = use_easyocr
        if use_easyocr:
            self.reader = easyocr.Reader([lang.split('+')[0] for lang in languages.split('+')])

    def speak(self, text: str):
        if not text.strip():
            return
        self.engine.say(text)
        self.engine.runAndWait()

    def detect_text(self, frame) -> List[str]:
        """
        Detect text in a given image frame.
        Returns a list of detected text strings.
        """
        text_results = []

        # Tesseract detection
        config = '--psm 6'  # assume a single uniform block of text
        try:
            text = pytesseract.image_to_string(frame, lang=self.languages, config=config)
            if text.strip():
                text_results.append(text.strip())
        except Exception as e:
            print("Tesseract OCR error:", e)

        # EasyOCR fallback
        if self.use_easyocr:
            try:
                easy_results = self.reader.readtext(frame, detail=0)
                for t in easy_results:
                    if t.strip() not in text_results:
                        text_results.append(t.strip())
            except Exception as e:
                print("EasyOCR error:", e)

        return text_results

    def speak_text_from_frame(self, frame):
        """
        Detects text and speaks it immediately.
        """
        texts = self.detect_text(frame)
        for t in texts:
            print("OCR DETECTED:", t)
            self.speak(t)
