
import cv2
import mediapipe as mp

# MediaPipe Hand Landmarker
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Webcam start
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Camera open nahi ho raha!")
    raise SystemExit

# Hand detection model setup
options = HandLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path="hand_landmarker.task"
    ),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=2
)

with HandLandmarker.create_from_options(options) as landmarker:

    timestamp = 0

    while True:
        success, frame = cap.read()

        if not success:
            break

        frame = cv2.flip(frame, 1)

        # OpenCV BGR se RGB conversion
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # MediaPipe image
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        # Hand detection
        result = landmarker.detect_for_video(
            mp_image,
            timestamp
        )

        # Hand landmarks draw
        if result.hand_landmarks:
            for hand in result.hand_landmarks:
                for landmark in hand:
                    h, w, _ = frame.shape
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)

                    cv2.circle(
                        frame,
                        (x, y),
                        5,
                        (0, 255, 0),
                        -1
                    )

            cv2.putText(
                frame,
                "Hand Detected!",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

        cv2.imshow("GestureX - Hand Tracking", frame)

        timestamp += 33

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

cap.release()
cv2.destroyAllWindows()
