from PIL import Image
import os

KNOWN_FACES_DIR = "known_faces"

for filename in os.listdir(KNOWN_FACES_DIR):
    if filename.lower().endswith((".jpg", ".jpeg", ".png")):
        path = os.path.join(KNOWN_FACES_DIR, filename)
        try:
            img = Image.open(path)
            rgb_img = img.convert("RGB")  # Force 8-bit RGB
            rgb_img.save(os.path.join(KNOWN_FACES_DIR, filename), format="JPEG")
            print(f"[INFO] {filename} converted to standard 8-bit RGB JPG")
        except Exception as e:
            print(f"[ERROR] Could not process {filename}: {e}")
