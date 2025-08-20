# src/utils.py
from typing import Tuple

def box_center(box: Tuple[int, int, int, int]) -> Tuple[int, int]:
    x1, y1, x2, y2 = box
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2
    return (cx, cy)

def box_area(box: Tuple[int, int, int, int]) -> int:
    x1, y1, x2, y2 = box
    w = max(0, x2 - x1)
    h = max(0, y2 - y1)
    return w * h

def direction_from_center(cx: int, frame_w: int) -> str:
    # thirds: left, center, right
    if cx < frame_w / 3:
        return "on the left"
    elif cx > (2 * frame_w) / 3:
        return "on the right"
    else:
        return "ahead"
