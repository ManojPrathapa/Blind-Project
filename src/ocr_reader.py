import cv2
import pytesseract

def perform_ocr(frame):
    """
    Performs OCR on a given frame and prints/speaks the detected text.
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    data = pytesseract.image_to_string(gray)
    if data.strip():
        print(f"[OCR] Detected text: {data}")
    else:
        print("[OCR] No text detected.")
    return data

