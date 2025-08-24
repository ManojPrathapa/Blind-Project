from PIL import Image
import os

KNOWN_FACES_DIR = "known_faces"

for filename in os.listdir(KNOWN_FACES_DIR):
    if filename.lower().endswith((".jpg", ".jpeg", ".png")):
        path = os.path.join(KNOWN_FACES_DIR, filename)
        try:
            img = Image.open(path).convert("RGB")  # Convert to RGB
            img.save(path)  # Overwrite the file
            print(f"[INFO] Converted {filename} to RGB.")
        except Exception as e:
            print(f"[Warning] Could not convert {filename}: {e}")
