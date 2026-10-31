
import math

def recognize_gesture(hand_landmarks):
    """
    Hand landmarks se basic gestures identify karta hai.
    """

    fingers = {
        "index": (8, 6),
        "middle": (12, 10),
        "ring": (16, 14),
        "pinky": (20, 18)
    }

    finger_status = {}

    for finger, (tip, pip) in fingers.items():
        finger_status[finger] = (
            hand_landmarks[tip].y < hand_landmarks[pip].y
        )

    index = finger_status["index"]
    middle = finger_status["middle"]
    ring = finger_status["ring"]
    pinky = finger_status["pinky"]

    # Thumb aur index finger ke darmiyan distance
    thumb_tip = hand_landmarks[4]
    index_tip = hand_landmarks[8]

    distance = math.sqrt(
        (thumb_tip.x - index_tip.x) ** 2 +
        (thumb_tip.y - index_tip.y) ** 2
    )

    # PINCH gesture
    if distance < 0.05:
        return "PINCH"

    elif index and middle and ring and pinky:
        return "OPEN PALM"

    elif not index and not middle and not ring and not pinky:
        return "FIST"

    elif index and middle and not ring and not pinky:
        return "PEACE"

    elif index and not middle and not ring and not pinky:
        return "INDEX FINGER"

    else:
        return "UNKNOWN"
