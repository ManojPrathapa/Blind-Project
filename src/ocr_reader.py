import cv2
import easyocr

# Initialize the EasyOCR reader (English only for now, can add more languages)
reader = easyocr.Reader(['en'])

def perform_ocr(frame):
    try:
        # Convert frame (BGR from OpenCV) to RGB
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Run EasyOCR
        results = reader.readtext(rgb)

        if results:
            print("[OCR Result]:")
            for (bbox, text, prob) in results:
                print(f"  - {text} (conf: {prob:.2f})")
        else:
            print("[OCR Result]: No text detected.")

    except Exception as e:
        print("[OCR Error]:", e)

