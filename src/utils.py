import os
import platform

def box_center(box):
    x1, y1, x2, y2 = box
    return ((x1 + x2)//2, (y1 + y2)//2)

def box_area(box):
    x1, y1, x2, y2 = box
    return max(0, x2 - x1) * max(0, y2 - y1)

def direction_from_center(cx: int, frame_w: int) -> str:
    if cx < frame_w / 3:
        return "on the left"
    elif cx > (2 * frame_w) / 3:
        return "on the right"
    else:
        return "ahead"

def clear_console():
    if platform.system().lower().startswith("win"):
        os.system("cls")
    else:
        os.system("clear")
