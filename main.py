
import cv2

# Webcam start karo
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Camera open nahi ho raha. Camera permission ya device check karo.")
    raise SystemExit

print("Webcam successfully started!")
print("Webcam band karne ke liye Q press karo.")

while True:
    success, frame = cap.read()

    if not success:
        print("Camera se frame read nahi ho raha.")
        break

    # Webcam image ko mirror karo
    frame = cv2.flip(frame, 1)

    cv2.imshow("GestureX - Webcam Test", frame)

    # Q press karne par webcam close hoga
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
