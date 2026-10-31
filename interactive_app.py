
import cv2
import mediapipe as mp
import pygame
import math
import os
import sys
import traceback

pygame.init()

# ---------------- SCREEN ----------------
WIDTH, HEIGHT = 1100, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("GestureX - Hand Tracking Application")
clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 25, bold=True)
small = pygame.font.SysFont("arial", 17)
tiny = pygame.font.SysFont("arial", 14)

WHITE = (255, 255, 255)
CYAN = (0, 220, 255)
GREEN = (70, 230, 140)
PINK = (255, 90, 160)
YELLOW = (255, 220, 60)
RED = (255, 80, 90)
BLUE = (70, 120, 255)
DARK = (15, 20, 40)
GRAY = (170, 180, 195)

MODEL_PATH = "hand_landmarker.task"

# Webcam preview position
CAM_X, CAM_Y = 25, 145
CAM_W, CAM_H = 430, 325

# Object workspace
WORK_X1, WORK_X2 = 490, 1070
WORK_Y1, WORK_Y2 = 150, 495

COLORS = [CYAN, PINK, GREEN, YELLOW, BLUE]
SHAPES = ["SQUARE", "TRIANGLE", "HEXAGON"]

original_objects = [
    {"x": 610, "y": 330, "size": 42, "color": CYAN},
    {"x": 780, "y": 330, "size": 42, "color": PINK},
    {"x": 950, "y": 330, "size": 42, "color": GREEN}
]

objects = []

for i, item in enumerate(original_objects):
    obj = item.copy()
    obj.update({
        "scale": 1.0,
        "angle": 0.0,
        "shape_index": 0,
        "color_index": i
    })
    objects.append(obj)

active_object = objects[0]
selected_object = None

camera = None
hand_detected = False
hand_count = 0
show_help = False
paused = False

status_message = "Show your hand to the webcam"
status_color = YELLOW

frame_timestamp = 0

# Smoothing values
MOVE_SMOOTH = 0.28
ZOOM_SMOOTH = 0.18
ROTATE_SMOOTH = 0.20

smooth_x = None
smooth_y = None

# Two-hand transform
two_hand_active = False
start_distance = 1.0
start_angle = 0.0
start_scale = 1.0
start_object_angle = 0.0

gesture_latches = {
    "PEACE": False,
    "FIST": False,
    "THUMBS UP": False,
    "OPEN PALM": False
}

RESET_BUTTON = pygame.Rect(950, 25, 120, 42)

# Hand skeleton connections
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17)
]


# ---------------- HELPERS ----------------

def draw_text(text, x, y, color=WHITE, selected_font=small):
    image = selected_font.render(str(text), True, color)
    screen.blit(image, (x, y))


def draw_panel(rect, color):
    pygame.draw.rect(
        screen, color, rect,
        border_radius=12
    )


def smooth_value(current, target, factor):
    return current + (target - current) * factor


def smooth_angle(current, target, factor):
    difference = (target - current + math.pi) % (2 * math.pi) - math.pi
    return current + difference * factor


def reset_all_objects():
    global active_object, selected_object, two_hand_active
    global smooth_x, smooth_y

    for i, obj in enumerate(objects):
        obj["x"] = original_objects[i]["x"]
        obj["y"] = original_objects[i]["y"]
        obj["size"] = original_objects[i]["size"]
        obj["scale"] = 1.0
        obj["angle"] = 0.0
        obj["shape_index"] = 0
        obj["color_index"] = i
        obj["color"] = COLORS[i]

    active_object = objects[0]
    selected_object = None
    two_hand_active = False
    smooth_x = None
    smooth_y = None


def reset_active_object():
    global selected_object, two_hand_active
    global smooth_x, smooth_y

    if active_object is None:
        return

    active_object["x"] = (WORK_X1 + WORK_X2) // 2
    active_object["y"] = (WORK_Y1 + WORK_Y2) // 2
    active_object["scale"] = 1.0
    active_object["angle"] = 0.0

    selected_object = None
    two_hand_active = False
    smooth_x = None
    smooth_y = None


def draw_object(obj, selected=False):
    x = int(obj["x"])
    y = int(obj["y"])
    radius = max(12, int(obj["size"] * obj["scale"]))

    sides = [4, 3, 6][obj["shape_index"]]
    points = []

    for i in range(sides):
        angle = (
            obj["angle"]
            + (2 * math.pi * i / sides)
            - math.pi / 2
        )

        px = x + math.cos(angle) * radius
        py = y + math.sin(angle) * radius
        points.append((int(px), int(py)))

    outline = GREEN if selected else WHITE

    pygame.draw.polygon(screen, obj["color"], points)
    pygame.draw.polygon(screen, outline, points, 3)

    if selected:
        pygame.draw.circle(
            screen, GREEN, (x, y), radius + 12, 2
        )


def find_object_near(point):
    px, py = point

    for obj in objects:
        distance = math.hypot(
            px - obj["x"],
            py - obj["y"]
        )

        if distance < obj["size"] * obj["scale"] + 45:
            return obj

    return None


def get_hand_point(hand):
    index = hand[8]

    x = WORK_X1 + index.x * (WORK_X2 - WORK_X1)
    y = WORK_Y1 + index.y * (WORK_Y2 - WORK_Y1)

    return int(x), int(y)


def get_pinch_center(hand):
    thumb = hand[4]
    index = hand[8]

    return (
        (thumb.x + index.x) / 2,
        (thumb.y + index.y) / 2
    )


# ---------------- GESTURE DETECTION ----------------

def finger_up(hand, tip, pip):
    return hand[tip].y < hand[pip].y


def classify_hand(hand):
    index_up = finger_up(hand, 8, 6)
    middle_up = finger_up(hand, 12, 10)
    ring_up = finger_up(hand, 16, 14)
    pinky_up = finger_up(hand, 20, 18)

    pinch_distance = math.hypot(
        hand[4].x - hand[8].x,
        hand[4].y - hand[8].y
    )

    if pinch_distance < 0.065:
        return "PINCH"

    thumb_extended = (
        abs(hand[4].x - hand[0].x)
        >
        abs(hand[2].x - hand[0].x) * 1.2
    )

    if index_up and middle_up and not ring_up and not pinky_up:
        return "PEACE"

    if not index_up and not middle_up and not ring_up and not pinky_up:
        if thumb_extended:
            return "THUMBS UP"
        return "FIST"

    if index_up and middle_up and ring_up and pinky_up:
        return "OPEN PALM"

    return "UNKNOWN"


def apply_gesture(gesture):
    global paused, status_message, status_color

    if gesture == "PEACE" and not gesture_latches["PEACE"]:
        active_object["color_index"] = (
            active_object["color_index"] + 1
        ) % len(COLORS)

        active_object["color"] = COLORS[
            active_object["color_index"]
        ]

        status_message = "PEACE - Color changed"
        status_color = CYAN

    elif gesture == "FIST" and not gesture_latches["FIST"]:
        active_object["shape_index"] = (
            active_object["shape_index"] + 1
        ) % len(SHAPES)

        status_message = (
            "FIST - Shape: " + SHAPES[active_object["shape_index"]]
        )

        status_color = YELLOW

    elif gesture == "THUMBS UP" and not gesture_latches["THUMBS UP"]:
        reset_active_object()
        status_message = "THUMBS UP - Object reset"
        status_color = GREEN

    elif gesture == "OPEN PALM" and not gesture_latches["OPEN PALM"]:
        paused = not paused

        status_message = (
            "APPLICATION PAUSED"
            if paused else "APPLICATION RESUMED"
        )

        status_color = YELLOW if paused else GREEN

    for name in gesture_latches:
        gesture_latches[name] = (name == gesture)


# ---------------- CAMERA TRACKING DISPLAY ----------------

def draw_camera_preview(frame, detected_hands):
    preview = cv2.resize(frame, (CAM_W, CAM_H))

    for hand in detected_hands:
        points = []

        for landmark in hand:
            px = int(landmark.x * CAM_W)
            py = int(landmark.y * CAM_H)
            points.append((px, py))

        for start, end in HAND_CONNECTIONS:
            cv2.line(
                preview,
                points[start],
                points[end],
                (0, 255, 100),
                2
            )

        for point in points:
            cv2.circle(
                preview, point, 4, (255, 255, 0), -1
            )

        for tip in [4, 8, 12, 16, 20]:
            cv2.circle(
                preview, points[tip], 7, (0, 0, 255), -1
            )

    rgb = cv2.cvtColor(preview, cv2.COLOR_BGR2RGB)

    camera_surface = pygame.image.frombuffer(
        rgb.tobytes(),
        (CAM_W, CAM_H),
        "RGB"
    )

    screen.blit(camera_surface, (CAM_X, CAM_Y))

    pygame.draw.rect(
        screen, CYAN,
        (CAM_X, CAM_Y, CAM_W, CAM_H),
        3
    )


# ---------------- INTERFACE ----------------

def draw_interface(camera_frame, detected_hands):
    screen.fill(DARK)

    draw_panel((15, 15, 1070, 85), (25, 45, 80))

    draw_text(
        "GESTUREX - LIVE HAND TRACKING",
        270, 38, CYAN, font
    )

    pygame.draw.rect(
        screen, BLUE, RESET_BUTTON,
        border_radius=9
    )

    draw_text(
        "RESET",
        RESET_BUTTON.x + 28,
        RESET_BUTTON.y + 10
    )

    # Webcam panel
    draw_panel((15, 110, 450, 390), (25, 45, 80))

    draw_text(
        "LIVE WEBCAM + HAND LANDMARKS",
        45, 117, YELLOW
    )

    if camera_frame is not None:
        draw_camera_preview(camera_frame, detected_hands)
    else:
        draw_text(
            "Waiting for webcam...",
            130, 270, RED
        )

    draw_text(
        f"Hands detected: {len(detected_hands)}",
        35, 480, GREEN
    )

    # Object workspace
    draw_panel(
        (475, 110, 610, 390),
        (25, 40, 70)
    )

    draw_text(
        "INTERACTIVE OBJECTS",
        620, 120, YELLOW, font
    )

    pygame.draw.rect(
        screen, GRAY,
        (WORK_X1, WORK_Y1, WORK_X2 - WORK_X1, WORK_Y2 - WORK_Y1),
        1
    )

    for obj in objects:
        draw_object(
            obj,
            selected=(obj is selected_object)
        )

    # Separate instructions panel
    draw_panel(
        (475, 510, 610, 75),
        (25, 40, 70)
    )

    draw_text(
        "PINCH = Move | Two-hand PINCH = Zoom + Rotate",
        490, 518, CYAN, tiny
    )

    draw_text(
        "PEACE = Color | FIST = Shape | THUMBS UP = Reset",
        490, 540, WHITE, tiny
    )

    draw_text(
        "OPEN PALM = Pause / Resume",
        490, 562, WHITE, tiny
    )

    # Status panel
    draw_panel((15, 595, 1070, 85), (25, 45, 80))

    draw_text(
        "SYSTEM STATUS:",
        35, 605, YELLOW
    )

    draw_text(
        status_message,
        35, 640, status_color
    )

    if active_object is not None:
        info = (
            f"Shape: {SHAPES[active_object['shape_index']]} | "
            f"Scale: {active_object['scale']:.2f} | "
            f"Angle: {math.degrees(active_object['angle']):.0f}"
        )

        draw_text(info, 650, 640, GREEN, tiny)

    if paused:
        draw_panel((600, 270, 300, 70), (110, 35, 35))
        draw_text("PAUSED", 695, 290, YELLOW, font)

    if show_help:
        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )
        overlay.fill((0, 0, 0, 210))
        screen.blit(overlay, (0, 0))

        draw_panel((180, 150, 740, 400), (25, 45, 80))

        draw_text("GESTUREX HELP", 430, 175, CYAN, font)

        instructions = [
            "One hand PINCH: Move object",
            "Two hand PINCH: Hands apart = Zoom In",
            "Two hand PINCH: Hands closer = Zoom Out",
            "Rotate hands: Rotate object",
            "PEACE: Change color",
            "FIST: Change shape",
            "THUMBS UP: Reset object",
            "OPEN PALM: Pause / Resume",
            "Q: Quit application | H: Close help"
        ]

        y = 230

        for line in instructions:
            draw_text(line, 250, y, WHITE)
            y += 32


# ---------------- ERROR SCREEN ----------------

def show_error(message):
    screen.fill(DARK)

    draw_text("GESTUREX ERROR", 390, 180, RED, font)
    draw_text(str(message)[:100], 100, 270, WHITE, small)
    draw_text("Press Q or ESC to close", 360, 400, CYAN)

    pygame.display.flip()

    waiting = True

    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_q, pygame.K_ESCAPE):
                    waiting = False

        clock.tick(30)


# ---------------- MAIN APPLICATION ----------------

def run_application():
    global camera, active_object, selected_object
    global hand_detected, show_help, paused
    global frame_timestamp, status_message, status_color
    global two_hand_active
    global start_distance, start_angle
    global start_scale, start_object_angle
    global smooth_x, smooth_y

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            "hand_landmarker.task file is missing from GestureX folder."
        )

    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not camera.isOpened():
        camera.release()
        camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        raise RuntimeError(
            "Webcam could not open. Close other apps using the camera."
        )

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    camera.set(cv2.CAP_PROP_FPS, 30)

    BaseOptions = mp.tasks.BaseOptions
    HandLandmarker = mp.tasks.vision.HandLandmarker
    Options = mp.tasks.vision.HandLandmarkerOptions
    RunningMode = mp.tasks.vision.RunningMode

    options = Options(
        base_options=BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=RunningMode.VIDEO,
        num_hands=2,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5
    )

    with HandLandmarker.create_from_options(options) as landmarker:
        running = True

        while running:
            clock.tick(30)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_q, pygame.K_ESCAPE):
                        running = False

                    elif event.key == pygame.K_h:
                        show_help = not show_help

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1 and RESET_BUTTON.collidepoint(event.pos):
                        reset_all_objects()
                        status_message = "All objects reset"
                        status_color = GREEN

            if not running:
                break

            success, frame = camera.read()

            if not success:
                status_message = "Cannot read webcam frame"
                status_color = RED
                draw_interface(None, [])
                pygame.display.flip()
                continue

            frame = cv2.flip(frame, 1)

            rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb
            )

            frame_timestamp += 33

            results = landmarker.detect_for_video(
                mp_image,
                frame_timestamp
            )

            hands = results.hand_landmarks or []
            hand_detected = len(hands) > 0

            # Two-hand pinch
            if len(hands) >= 2:
                g1 = classify_hand(hands[0])
                g2 = classify_hand(hands[1])

                if g1 == "PINCH" and g2 == "PINCH":

                    if not paused:
                        c1 = get_pinch_center(hands[0])
                        c2 = get_pinch_center(hands[1])

                        dx = c2[0] - c1[0]
                        dy = c2[1] - c1[1]

                        distance = max(
                            0.001,
                            math.hypot(dx, dy)
                        )

                        angle = math.atan2(dy, dx)

                        if not two_hand_active:
                            selected_object = active_object
                            start_distance = distance
                            start_angle = angle
                            start_scale = active_object["scale"]
                            start_object_angle = active_object["angle"]
                            two_hand_active = True

                        ratio = distance / start_distance

                        target_scale = max(
                            0.5,
                            min(2.5, start_scale * ratio)
                        )

                        active_object["scale"] = smooth_value(
                            active_object["scale"],
                            target_scale,
                            ZOOM_SMOOTH
                        )

                        angle_difference = (
                            angle - start_angle + math.pi
                        ) % (2 * math.pi) - math.pi

                        target_angle = (
                            start_object_angle + angle_difference
                        )

                        active_object["angle"] = smooth_angle(
                            active_object["angle"],
                            target_angle,
                            ROTATE_SMOOTH
                        )

                        status_message = "Two-hand PINCH: Zoom + Rotate"
                        status_color = GREEN

                    else:
                        status_message = "PAUSED - Open Palm to resume"
                        status_color = YELLOW

                else:
                    two_hand_active = False
                    status_message = "Two hands detected - Pinch with both"
                    status_color = CYAN

            # One-hand gestures
            elif len(hands) == 1:
                two_hand_active = False

                hand = hands[0]
                gesture = classify_hand(hand)

                if gesture == "PINCH":

                    if not paused:
                        point = get_hand_point(hand)

                        if selected_object is None:
                            selected_object = find_object_near(point)

                            if selected_object is not None:
                                active_object = selected_object

                        if selected_object is not None:
                            target_x, target_y = point

                            if smooth_x is None:
                                smooth_x = selected_object["x"]
                                smooth_y = selected_object["y"]

                            smooth_x = smooth_value(
                                smooth_x,
                                target_x,
                                MOVE_SMOOTH
                            )

                            smooth_y = smooth_value(
                                smooth_y,
                                target_y,
                                MOVE_SMOOTH
                            )

                            selected_object["x"] = smooth_x
                            selected_object["y"] = smooth_y

                            status_message = "One-hand PINCH: Moving object"
                            status_color = GREEN

                        else:
                            status_message = "Pinch near an object to select"
                            status_color = CYAN

                    else:
                        status_message = "PAUSED - Open Palm to resume"
                        status_color = YELLOW

                else:
                    selected_object = None
                    smooth_x = None
                    smooth_y = None

                    apply_gesture(gesture)

                    if gesture == "UNKNOWN":
                        for name in gesture_latches:
                            gesture_latches[name] = False

                        status_message = "Hand detected - Make a gesture"
                        status_color = WHITE

            else:
                selected_object = None
                two_hand_active = False
                smooth_x = None
                smooth_y = None

                for name in gesture_latches:
                    gesture_latches[name] = False

                status_message = "Show your hand to the webcam"
                status_color = RED

            draw_interface(frame, hands)
            pygame.display.flip()

    camera.release()


# ---------------- START ----------------

try:
    run_application()

except Exception as error:
    print("GestureX Error:", error)
    traceback.print_exc()

    try:
        show_error(error)
    except Exception:
        pass

finally:
    if camera is not None:
        camera.release()

    pygame.quit()
    sys.exit()
