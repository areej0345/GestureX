# GestureX – Hand Gesture Controlled Interactive Application

## 📌 Project Overview

GestureX is a Python-based hand gesture recognition application that allows users to interact with objects using real-time hand movements and gestures.

The application uses a webcam to detect hand landmarks and recognize different gestures. Users can move, resize, rotate, and modify interactive shapes without using a mouse.

## ✨ Features

- **Live Webcam Tracking:** Displays the webcam feed in real time.
- **Hand Landmark Detection:** Detects and displays hand landmarks and connecting lines.
- **Object Movement:** Move objects using one-hand PINCH gesture.
- **Object Zoom:** Resize objects using two-hand PINCH gestures.
- **Object Rotation:** Rotate objects by changing the angle between both hands.
- **Color Changing:** Change object colors using the PEACE gesture.
- **Shape Changing:** Switch between different shapes using the FIST gesture.
- **Object Reset:** Reset the active object using THUMBS UP.
- **Pause and Resume:** Pause or resume the application using OPEN PALM.
- **Smooth Interaction:** Uses smoothing techniques to make object movement and transformations more stable.
- **Reset Button:** Reset all objects using the on-screen RESET button.
- **Help Panel:** Press H to view gesture instructions.

## 🖐️ Gesture Controls

| Gesture | Action |
|---|---|
| One-hand PINCH | Move an object |
| Two-hand PINCH | Zoom in and zoom out |
| Rotate both hands | Rotate an object |
| PEACE ✌️ | Change object color |
| FIST ✊ | Change object shape |
| THUMBS UP 👍 | Reset active object |
| OPEN PALM ✋ | Pause / Resume |

### Keyboard Controls

| Key | Action |
|---|---|
| H | Open / Close Help Panel |
| Q | Quit Application |
| ESC | Exit Application |

## 🛠️ Technologies Used

- Python
- OpenCV
- MediaPipe
- Pygame
- NumPy
- Math
- VS Code

## 📂 Project Structure

```text
GestureX/
│
├── venv312/
│
├── main.py
├── hand_tracking.py
├── gesture_recognition.py
├── gesture_test.py
├── application.py
├── interactive_app.py
│
├── hand_landmarker.task
├── highscore.txt
│
└── README.md
```

**Note:** `highscore.txt` is created automatically when a new high score is saved by the game.

## ⚙️ Installation

### 1. Install Python

Install Python 3.12 and make sure Python is added to PATH.

### 2. Open the Project Folder

Open the GestureX folder in Visual Studio Code.

### 3. Create a Virtual Environment

Open the VS Code terminal and run:

```bash
python -m venv venv312
```

### 4. Activate the Virtual Environment

For Windows PowerShell:

```powershell
.\venv312\Scripts\Activate.ps1
```

### 5. Install Required Libraries

```bash
python -m pip install opencv-python mediapipe pygame numpy
```

### 6. Download the Hand Landmark Model

Download the MediaPipe Hand Landmarker model file named:

```text
hand_landmarker.task
```

Place this file inside the main GestureX project folder.

The application requires this model for hand detection.

## ▶️ How to Run

Make sure the virtual environment is activated and the webcam is connected.

Run the interactive application:

```bash
python interactive_app.py
```

The application will open a window containing:

- Live webcam preview
- Hand landmark visualization
- Interactive object workspace
- Gesture instructions
- System status information

## 🎮 How to Use

1. Start the application.
2. Allow webcam access.
3. Show your hand in front of the webcam.
4. Use PINCH to select and move an object.
5. Use two-hand PINCH to zoom and rotate.
6. Use PEACE to change color.
7. Use FIST to change shape.
8. Use THUMBS UP to reset the active object.
9. Use OPEN PALM to pause or resume.
10. Press Q to close the application.

## 🔧 Troubleshooting

**Webcam not opening**
- Check whether the webcam is connected.
- Close other applications using the webcam.
- Check camera permissions in Windows settings.

**Hand landmarks not appearing**
- Make sure your hand is visible.
- Ensure there is enough lighting.
- Check that `hand_landmarker.task` is in the project folder.

**Module not found error**
- Activate the virtual environment.
- Install the required Python libraries.

## 🚀 Future Improvements

- Add more hand gestures.
- Improve gesture recognition accuracy.
- Add more interactive shapes.
- Improve movement and rotation smoothness.
- Add customizable object controls.
- Develop additional gesture-controlled games.

## 👩‍💻 Project Information

**Project Name:** GestureX

**Project Type:** Hand Gesture Recognition and Interactive Application

**Programming Language:** Python

**Development Environment:** Visual Studio Code

**Main Purpose:** To provide a touch-free interactive experience using real-time hand tracking and gesture recognition.

---

**GestureX – Control Objects with Your Hands!**