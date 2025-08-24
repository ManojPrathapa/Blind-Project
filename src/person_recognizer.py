import os
import cv2
import face_recognition

class FaceRecognition:
    def __init__(self, voice_module, known_faces_dir="known_faces"):
        self.voice = voice_module
        self.known_encodings = []
        self.known_names = []
        self.load_known_faces(known_faces_dir)

    def load_known_faces(self, known_faces_dir):
        if not os.path.exists(known_faces_dir):
            print(f"[WARNING] Known faces directory '{known_faces_dir}' does not exist.")
            return

        for filename in os.listdir(known_faces_dir):
            if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                path = os.path.join(known_faces_dir, filename)
                image = cv2.imread(path)  # OpenCV reads in BGR

                if image is None:
                    print(f"[WARNING] Could not read image: {filename}")
                    continue

                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                encodings = face_recognition.face_encodings(rgb_image)

                if encodings:
                    self.known_encodings.append(encodings[0])
                    self.known_names.append(os.path.splitext(filename)[0])
                else:
                    print(f"[INFO] No face found in {filename}")

    def recognize_face(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        locations = face_recognition.face_locations(rgb_frame)
        encodings = face_recognition.face_encodings(rgb_frame, locations)

        for encoding, location in zip(encodings, locations):
            matches = face_recognition.compare_faces(self.known_encodings, encoding)
            name = "Unknown"
            if True in matches:
                match_index = matches.index(True)
                name = self.known_names[match_index]

            # Draw rectangle around face
            top, right, bottom, left = location
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            # Speak name
            self.voice.speak(f"This is {name}")

        return frame
