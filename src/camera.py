import cv2

def list_webcams(max_index: int = 5):
    found = []
    for i in range(max_index):
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if cap is not None and cap.read()[0]:
            found.append(i)
        if cap is not None:
            cap.release()
    return found

def select_camera():
    print("Detecting local webcams...")
    cams = list_webcams(5)
    for idx, c in enumerate(cams, start=1):
        print(f"{idx}. Webcam {c}")
    print(f"{len(cams) + 1}. Enter IP webcam URL")

    while True:
        try:
            sel = int(input(f"Select camera [1-{len(cams)+1}]: ").strip())
        except Exception:
            sel = -1
        if 1 <= sel <= len(cams):
            cam_index = cams[sel - 1]
            print(f"Selected local webcam {cam_index}")
            return cam_index
        elif sel == len(cams) + 1:
            url = input("Enter IP camera URL (e.g., http://<phone-ip>:8080/video): ").strip()
            print(f"Selected IP stream: {url}")
            return url
        else:
            print("Invalid choice. Try again.")
