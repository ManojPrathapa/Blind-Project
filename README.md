# BlindAssist — YOLO-based Blind Assistance (Python, v3.11)

Features:
- Real-time object detection using Ultralytics YOLO
- Spoken alerts with object name, estimated distance, and navigation hint (left/center/right)
- Repeats alert for an object while it remains in view

## Requirements
- Python 3.11
- Create a virtualenv and install requirements:
  ```bash
  python -m venv .venv
  .venv\Scripts\activate        # Windows
  source .venv/bin/activate     # macOS / Linux
  pip install --upgrade pip
  pip install -r requirements.txt

Run using:
python main.py