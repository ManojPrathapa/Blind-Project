import cv2

def list_webcams(max_tested=5):
    """Check local webcams and return available indices."""
    available = []
    for i in range(max_tested):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available.append(i)
        cap.release()
    return available

def select_camera():
    """Let user select between webcam(s) and IP webcam."""
    print("Detecting local webcams...")
    webcams = list_webcams()
    for idx, cam in enumerate(webcams):
        print(f"{idx+1}. Webcam {cam}")
    print(f"{len(webcams)+1}. Enter IP webcam URL")

    choice = input(f"Select camera [1-{len(webcams)+1}]: ")
    try:
        choice = int(choice)
    except ValueError:
        choice = 0

    if choice <= len(webcams) and choice > 0:
        print(f"Selected local webcam {webcams[choice-1]}")
        return webcams[choice-1]
    elif choice == len(webcams) + 1:
        url = input("Enter IP webcam URL (e.g., http://192.168.1.5:8080/video): ").strip()
        print(f"Selected IP camera: {url}")
        return url
    else:
        print("Invalid selection. Defaulting to webcam 0.")
        return 0
