# Blind Assistance System

A Python-based real-time object detection and navigation assistant designed for visually impaired users. The system utilizes a camera feed (either from a webcam or an IP camera) to detect objects, estimate their distance, and provide directional cues. These cues are then announced via voice, with repeated announcements until the object leaves the frame.

## Features

- **Real-time Object Detection**  
  Uses YOLOv5/YOLOv8 for detecting objects in a live video feed.

- **Voice Navigation Assistance**  
  Announces object type, approximate distance, and direction (left, right, or ahead).

- **Dynamic Camera Selection**  
  - Automatically detects all connected webcams.  
  - Option to enter an IP webcam URL (e.g., using the Android app “IP Webcam”).

- **Distance Estimation**  
  Estimates distance based on the size of the object’s bounding box.

- **Object Tracking & Re-announcement**  
  - Repeats announcements for the same object after a cooldown period.  
  - Stops announcing when the object leaves the frame.

- **Lightweight & Python-Only**  
  Works without Conda and is compatible with Python 3.11.

## Project Structure

```bash
Blind-Assist/
│
├── main.py # Entry point for the application
├── requirements.txt # Python dependencies
├── models/
│ └── yolov5s.pt # YOLO model weights
├── src/
│ ├── detector.py # Object detection module
│ ├── voice.py # Voice assistance module (using pyttsx3)
│ ├── utils.py # Helper functions (box_center, box_area, direction)
│ └── camera.py # Camera selection module
└── README.md # Project documentation
```
## Dependencies

- **Python 3.11**

Required libraries:

- `torch>=2.1.0`
- `ultralytics>=8.0.20`
- `opencv-python>=4.7.0`
- `numpy>=1.25`
- `pyttsx3>=2.90`

Install dependencies using:

```bash
python -m venv venv
venv\Scripts\activate   # (Windows)
pip install -r requirements.txt

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install opencv-python opencv-contrib-python
pip install opencv-python
```
4. Configure IP Webcam (Optional)

Install the "IP Webcam" app on your Android device.

Start the camera server.

Copy the video URL (e.g., http://192.168.1.5:8080/video) to use in the program.

## Running the Program

**To run the application, execute:**
```bash
python main.py
```

This will trigger the camera selection menu:

It will list all connected local webcams.You can also enter an IP webcam URL.

A detection window will open showing the live video feed with bounding boxes. The system will begin making voice announcements:

Example: "Person ahead, approximately 3.5 meters away"
Example: "Chair on the left, approximately 2.1 meters away."

Press 'q' to exit the program.

## Project Features Explained
| Feature                      | Details                                                                |
| ---------------------------- | ---------------------------------------------------------------------- |
| **Object Detection**         | Detects objects in real-time using YOLOv5.                             |
| **Distance Estimation**      | Estimates distance based on the size of the bounding box.              |
| **Navigation Direction**     | Announces the relative position of the object (left, ahead, right).    |
| **Repeated Announcements**   | Announces the same object every few seconds until it leaves the frame. |
| **Dynamic Camera Selection** | Works with both USB webcams and IP cameras over Wi-Fi.                 |
