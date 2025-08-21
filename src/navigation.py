from __future__ import annotations
import os, threading, time, webbrowser, urllib.parse, requests, cv2, torch, pyttsx3
from typing import Optional, Callable, Dict, Any

# --- TTS engine (offline, no API needed) ---
_engine = pyttsx3.init()
_engine.setProperty('rate', 170)
_engine.setProperty('volume', 1.0)

def speak(text: str):
    """Speak + print."""
    print(f"ANNOUNCE: {text}")
    _engine.say(text)
    _engine.runAndWait()

# --- Google Maps helpers ---
def open_gmaps_in_browser(origin: str, destination: str, travel_mode: str = "walking") -> None:
    base = "https://www.google.com/maps/dir/?api=1"
    params = {"origin": origin, "destination": destination, "travelmode": travel_mode}
    url = f"{base}&{urllib.parse.urlencode(params)}"
    webbrowser.open(url, new=2)

def _gmaps_geocode(addr: str, api_key: str) -> Optional[Dict[str, float]]:
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    r = requests.get(url, params={"address": addr, "key": api_key}, timeout=15)
    data = r.json()
    if data.get("status") == "OK" and data.get("results"):
        loc = data["results"][0]["geometry"]["location"]
        return {"lat": loc["lat"], "lng": loc["lng"]}
    return None

def _gmaps_directions(origin: str, destination: str, api_key: str, mode: str = "walking") -> Optional[Dict[str, Any]]:
    url = "https://maps.googleapis.com/maps/api/directions/json"
    r = requests.get(url, params={
        "origin": origin, "destination": destination, "mode": mode,
        "key": api_key, "units": "metric", "alternatives": "false",
    }, timeout=20)
    return r.json()

def _strip_html(html: str) -> str:
    import re
    return re.sub("<.*?>", "", html or "").replace("&nbsp;", " ").replace("&amp;", "&")

# --- Object detection helpers ---
def estimate_distance(bbox, frame_width):
    x1, y1, x2, y2 = bbox
    obj_width = x2 - x1
    if obj_width <= 0:
        return None
    focal_length = 500
    real_width = 0.5
    distance = (real_width * focal_length) / obj_width
    return round(distance, 1)

def get_direction(bbox, frame_width):
    x1, y1, x2, y2 = bbox
    center_x = (x1 + x2) / 2
    if center_x < frame_width / 3:
        return "on the left"
    elif center_x > 2 * frame_width / 3:
        return "on the right"
    else:
        return "ahead"

# --- Main Navigation Manager ---
class NavigationManager:
    def __init__(self, voice_say: Callable[[str], None] = speak, travel_mode: str = "walking"):
        self.voice_say = voice_say
        self.travel_mode = travel_mode
        self._nav_thread: Optional[threading.Thread] = None
        self._detect_thread: Optional[threading.Thread] = None
        self._running = False
        self._last_announcements: dict[str, float] = {}  # throttle announcements

    def start_navigation(
        self, origin: str, destination: str,
        use_api_guidance: bool = True,
        location_supplier: Optional[Callable[[], Optional[tuple[float, float]]]] = None,
        announce_interval: float = 10.0,
        camera_index: int = 0,
    ):
        open_gmaps_in_browser(origin, destination, self.travel_mode)
        api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        self._running = True

        # Start spoken turn-by-turn (if API available)
        if use_api_guidance and api_key:
            self._nav_thread = threading.Thread(
                target=self._run_guidance,
                args=(origin, destination, api_key, location_supplier, announce_interval),
                daemon=True,
            )
            self._nav_thread.start()
        else:
            self.voice_say("Google Maps opened. API guidance not enabled.")
            if use_api_guidance and not api_key:
                self.voice_say("Tip: set GOOGLE_MAPS_API_KEY for turn-by-turn directions.")

        # Start object detection in parallel
        self._detect_thread = threading.Thread(
            target=self._run_detection, args=(camera_index,), daemon=True
        )
        self._detect_thread.start()

    def stop(self):
        self._running = False
        if self._nav_thread and self._nav_thread.is_alive():
            self._nav_thread.join(timeout=2.0)
        if self._detect_thread and self._detect_thread.is_alive():
            self._detect_thread.join(timeout=2.0)

    def _run_guidance(
        self, origin: str, destination: str, api_key: str,
        location_supplier: Optional[Callable[[], Optional[tuple[float, float]]]],
        announce_interval: float,
    ):
        try:
            o = _gmaps_geocode(origin, api_key) or {}
            d = _gmaps_geocode(destination, api_key) or {}
            o_str = f"{o.get('lat','')},{o.get('lng','')}" if o else origin
            d_str = f"{d.get('lat','')},{d.get('lng','')}" if d else destination

            route = _gmaps_directions(o_str, d_str, api_key, mode=self.travel_mode)
            if not route or not route.get("routes"):
                self.voice_say("Sorry, I could not find a route.")
                return

            leg = route["routes"][0]["legs"][0]
            steps = leg.get("steps", [])
            if not steps:
                self.voice_say("No navigation steps found.")
                return

            self.voice_say(f"Starting navigation. Distance {leg['distance']['text']}, ETA {leg['duration']['text']}.")

            for step in steps:
                if not self._running: break
                instr = _strip_html(step.get("html_instructions", ""))
                dist_txt = (step.get("distance") or {}).get("text", "")
                phrase = instr + (f". For {dist_txt}" if dist_txt else "")
                self.voice_say(phrase)
                time.sleep((step.get("duration") or {}).get("value", 20) / 3)

            self.voice_say("You have arrived at your destination.")
        except Exception as e:
            self.voice_say(f"Navigation error: {e}")

    def _run_detection(self, camera_index: int = 0):
        try:
            model = torch.hub.load("ultralytics/yolov5", "yolov5s")
            cap = cv2.VideoCapture(camera_index,cv2.CAP_DSHOW)
            self.voice_say("Object detection started.")

            while self._running:
                ret, frame = cap.read()

                if not ret:
                    time.sleep(0.5)
                    continue

                results = model(frame)
                detections = results.xyxy[0].cpu().numpy()

                for *bbox, conf, cls in detections:
                    label = results.names[int(cls)]
                    distance = estimate_distance(bbox, frame.shape[1])
                    direction = get_direction(bbox, frame.shape[1])

                    if distance:
                        key = f"{label}_{direction}"
                        now = time.time()
                        last = self._last_announcements.get(key, 0)
                        if now - last >= 3:  # throttle to every 3s
                            self.voice_say(f"{label} {direction}, about {distance} meters away")
                            self._last_announcements[key] = now

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

            cap.release()
            cv2.destroyAllWindows()
        except Exception as e:
            self.voice_say(f"Detection error: {e}")
