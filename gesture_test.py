
import cv2
import mediapipe as mp
import time

from gesture_recognition import recognize_gesture

# -----------------------------
# MediaPipe Hand Detection Setup
# -----------------------------

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

MODEL_PATH = "hand_landmarker.task"

options = HandLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path=MODEL_PATH
    ),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=2,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
)

# -----------------------------
# Camera Setup
# -----------------------------

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print("ERROR: Camera open nahi hua!")
    print("Camera permission aur camera connection check karo.")
    raise SystemExit

print("GestureX camera successfully opened!")
print("Q press karke application close karo.")

# -----------------------------
# Hand Connections
# -----------------------------

connections = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17)
]

# -----------------------------
# Start Hand Detection
# -----------------------------

try:
    with HandLandmarker.create_from_options(options) as landmarker:

        start_time = time.monotonic()
        previous_time = start_time

        while True:

            success, frame = cap.read()

            if not success:
                print("ERROR: Camera frame read nahi ho raha!")
                break

            # Mirror camera
            frame = cv2.flip(frame, 1)

            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb_frame
            )

            # Timestamp in milliseconds
            timestamp = int(
                (time.monotonic() - start_time) * 1000
            )

            # Hand detection
            result = landmarker.detect_for_video(
                mp_image,
                timestamp
            )

            gesture = "NO HAND DETECTED"

            # -----------------------------
            # Draw Hand Landmarks
            # -----------------------------

            if result.hand_landmarks:

                for hand in result.hand_landmarks:

                    gesture = recognize_gesture(hand)

                    h, w, _ = frame.shape

                    points = []

                    for landmark in hand:

                        x = int(landmark.x * w)
                        y = int(landmark.y * h)

                        points.append((x, y))

                    # Draw connecting lines
                    for start, end in connections:

                        cv2.line(
                            frame,
                            points[start],
                            points[end],
                            (255, 0, 0),
                            2
                        )

                    # Draw green dots
                    for x, y in points:

                        cv2.circle(
                            frame,
                            (x, y),
                            6,
                            (0, 255, 0),
                            -1
                        )

            # -----------------------------
            # Display Gesture Name
            # -----------------------------

            color = (
                (0, 0, 255)
                if gesture == "NO HAND DETECTED"
                else (0, 255, 0)
            )

            cv2.rectangle(
                frame,
                (0, 0),
                (640, 75),
                (30, 30, 30),
                -1
            )

            cv2.putText(
                frame,
                "GestureX: " + gesture,
                (15, 48),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                color,
                2
            )

            # FPS display
            current_time = time.monotonic()
            fps = 1 / max(current_time - previous_time, 0.001)
            previous_time = current_time

            cv2.putText(
                frame,
                f"FPS: {int(fps)}",
                (520, 110),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

            # Show webcam window
            cv2.imshow(
                "GestureX - Live Gesture Recognition",
                frame
            )

            # Q press to exit
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

finally:
    cap.release()
    cv2.destroyAllWindows()
    print("GestureX closed successfully!")
