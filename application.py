
import cv2
import mediapipe as mp
import pygame
import sys
import time
import random
import math

from gesture_recognition import recognize_gesture

pygame.init()

WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("GestureX - Catch the Target")

clock = pygame.time.Clock()

title_font = pygame.font.SysFont("Arial", 65, bold=True)
font = pygame.font.SysFont("Arial", 30)
small_font = pygame.font.SysFont("Arial", 21)
button_font = pygame.font.SysFont("Arial", 28, bold=True)

WHITE = (255, 255, 255)
BLACK = (15, 20, 40)
BLUE = (50, 150, 255)
GREEN = (0, 220, 100)
RED = (255, 60, 60)
YELLOW = (255, 220, 0)

WELCOME = "WELCOME"
PLAYING = "PLAYING"
GAME_OVER = "GAME_OVER"

game_state = WELCOME

play_button = pygame.Rect(330, 390, 240, 65)
restart_button = pygame.Rect(330, 420, 240, 60)

ball_colors = [
    (50, 150, 255),
    (255, 220, 0),
    (255, 0, 0),
    (0, 255, 0),
    (255, 105, 180)
]

color_index = 0
ball_color = ball_colors[color_index]

ball_radius = 25
target_radius = 22

ball_x = WIDTH // 2
ball_y = HEIGHT // 2

target_x = random.randint(100, WIDTH - 100)
target_y = random.randint(130, HEIGHT - 100)

score = 0
game_duration = 60
start_time = 0

# Load saved high score
try:
    with open("highscore.txt", "r") as file:
        high_score = int(file.read())
except (FileNotFoundError, ValueError):
    high_score = 0

paused = False
last_peace_time = 0
previous_gesture = "NO HAND"

timestamp_start = time.monotonic()

# MediaPipe setup
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path="hand_landmarker.task"
    ),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=1
)


def draw_background():
    screen.fill(BLACK)

    for i in range(0, WIDTH, 60):
        pygame.draw.line(
            screen, (30, 40, 65),
            (i, 0), (i, HEIGHT), 1
        )

    for i in range(0, HEIGHT, 60):
        pygame.draw.line(
            screen, (30, 40, 65),
            (0, i), (WIDTH, i), 1
        )


def draw_welcome_screen():
    draw_background()

    title = title_font.render("GESTUREX", True, BLUE)
    subtitle = font.render(
        "Hand Gesture Controlled Game", True, WHITE
    )

    screen.blit(
        title,
        title.get_rect(center=(WIDTH // 2, 145))
    )

    screen.blit(
        subtitle,
        subtitle.get_rect(center=(WIDTH // 2, 215))
    )

    instructions = [
        "INDEX FINGER  -  Move the Ball",
        "PEACE GESTURE  -  Change Ball Color",
        "OPEN PALM  -  Pause Game",
        "FIST  -  Resume Game",
        "Catch the red target to earn points!"
    ]

    y = 265

    for item in instructions:
        text = small_font.render(item, True, WHITE)
        screen.blit(
            text,
            text.get_rect(center=(WIDTH // 2, y))
        )
        y += 30

    mouse_pos = pygame.mouse.get_pos()

    button_color = (
        GREEN if play_button.collidepoint(mouse_pos)
        else BLUE
    )

    pygame.draw.rect(
        screen, button_color,
        play_button, border_radius=15
    )

    play_text = button_font.render(
        "PLAY GAME", True, WHITE
    )

    screen.blit(
        play_text,
        play_text.get_rect(center=play_button.center)
    )

    high_text = small_font.render(
        f"Best Score: {high_score}", True, YELLOW
    )

    screen.blit(
        high_text,
        high_text.get_rect(center=(WIDTH // 2, 485))
    )


def draw_game_over():
    draw_background()

    title = title_font.render(
        "GAME OVER", True, RED
    )

    score_text = font.render(
        f"Your Score: {score}", True, WHITE
    )

    high_text = font.render(
        f"High Score: {high_score}", True, YELLOW
    )

    screen.blit(
        title,
        title.get_rect(center=(WIDTH // 2, 180))
    )

    screen.blit(
        score_text,
        score_text.get_rect(center=(WIDTH // 2, 270))
    )

    screen.blit(
        high_text,
        high_text.get_rect(center=(WIDTH // 2, 325))
    )

    pygame.draw.rect(
        screen, BLUE,
        restart_button, border_radius=12
    )

    restart_text = button_font.render(
        "PLAY AGAIN", True, WHITE
    )

    screen.blit(
        restart_text,
        restart_text.get_rect(center=restart_button.center)
    )


def reset_game():
    global score, start_time, ball_x, ball_y
    global target_x, target_y, paused, game_state
    global previous_gesture

    score = 0
    start_time = time.monotonic()

    ball_x = WIDTH // 2
    ball_y = HEIGHT // 2

    target_x = random.randint(100, WIDTH - 100)
    target_y = random.randint(130, HEIGHT - 100)

    paused = False
    previous_gesture = "NO HAND"
    game_state = PLAYING


# Open camera
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
cap.set(cv2.CAP_PROP_FPS, 30)

camera_available = cap.isOpened()

print("GestureX Started!")

try:
    with HandLandmarker.create_from_options(options) as landmarker:

        running = True

        while running:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:

                        if (
                            game_state == WELCOME
                            and play_button.collidepoint(event.pos)
                        ):
                            if camera_available:
                                reset_game()
                            else:
                                print("Camera open nahi hua!")

                        elif (
                            game_state == GAME_OVER
                            and restart_button.collidepoint(event.pos)
                        ):
                            reset_game()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    if (
                        event.key == pygame.K_r
                        and game_state == GAME_OVER
                    ):
                        reset_game()

            if not running:
                break

            # Welcome screen
            if game_state == WELCOME:

                draw_welcome_screen()

                if not camera_available:
                    warning = small_font.render(
                        "Camera not available!",
                        True, RED
                    )

                    screen.blit(
                        warning,
                        warning.get_rect(
                            center=(WIDTH // 2, 520)
                        )
                    )

            # Playing screen
            elif game_state == PLAYING:

                success, frame = cap.read()

                if not success:
                    print("Camera frame read nahi hua!")
                    break

                frame = cv2.flip(frame, 1)
                rgb = cv2.cvtColor(
                    frame, cv2.COLOR_BGR2RGB
                )

                mp_image = mp.Image(
                    image_format=mp.ImageFormat.SRGB,
                    data=rgb
                )

                timestamp = int(
                    (time.monotonic() - timestamp_start) * 1000
                )

                result = landmarker.detect_for_video(
                    mp_image, timestamp
                )

                gesture = "NO HAND"

                if result.hand_landmarks:

                    hand = result.hand_landmarks[0]
                    gesture = recognize_gesture(hand)

                    index_tip = hand[8]

                    target_ball_x = int(
                        index_tip.x * WIDTH
                    )

                    target_ball_y = int(
                        index_tip.y * HEIGHT
                    )

                    if (
                        gesture == "INDEX FINGER"
                        and not paused
                    ):
                        ball_x += (
                            target_ball_x - ball_x
                        ) * 0.40

                        ball_y += (
                            target_ball_y - ball_y
                        ) * 0.40

                    if gesture == "PEACE":

                        current_time = time.monotonic()

                        if (
                            previous_gesture != "PEACE"
                            and current_time - last_peace_time > 0.5
                        ):
                            color_index = (
                                color_index + 1
                            ) % len(ball_colors)

                            ball_color = ball_colors[color_index]
                            last_peace_time = current_time

                    if gesture == "OPEN PALM":
                        paused = True

                    if gesture == "FIST":
                        paused = False

                else:
                    paused = False

                previous_gesture = gesture

                elapsed = time.monotonic() - start_time
                remaining = max(
                    0, int(game_duration - elapsed)
                )

                # Save high score when game ends
                if remaining == 0:

                    if score > high_score:
                        high_score = score

                        with open("highscore.txt", "w") as file:
                            file.write(str(high_score))

                    game_state = GAME_OVER

                camera_surface = pygame.image.frombuffer(
                    rgb.tobytes(),
                    (rgb.shape[1], rgb.shape[0]),
                    "RGB"
                )

                camera_surface = pygame.transform.scale(
                    camera_surface, (WIDTH, HEIGHT)
                )

                screen.blit(camera_surface, (0, 0))

                if not paused and remaining > 0:

                    distance = math.sqrt(
                        (ball_x - target_x) ** 2
                        + (ball_y - target_y) ** 2
                    )

                    if distance < ball_radius + target_radius:

                        score += 1

                        target_x = random.randint(
                            100, WIDTH - 100
                        )

                        target_y = random.randint(
                            130, HEIGHT - 100
                        )

                pygame.draw.circle(
                    screen, RED,
                    (target_x, target_y),
                    target_radius
                )

                pygame.draw.circle(
                    screen, ball_color,
                    (int(ball_x), int(ball_y)),
                    ball_radius
                )

                pygame.draw.circle(
                    screen, WHITE,
                    (int(ball_x), int(ball_y)),
                    ball_radius, 3
                )

                pygame.draw.rect(
                    screen, BLACK,
                    (0, 0, WIDTH, 85)
                )

                score_text = font.render(
                    f"Score: {score}", True, WHITE
                )

                time_text = font.render(
                    f"Time: {remaining}", True, WHITE
                )

                gesture_text = small_font.render(
                    "Gesture: " + gesture, True, GREEN
                )

                screen.blit(score_text, (20, 10))
                screen.blit(time_text, (250, 10))
                screen.blit(gesture_text, (20, 52))

                if paused:

                    pause_text = title_font.render(
                        "PAUSED", True, RED
                    )

                    screen.blit(
                        pause_text,
                        pause_text.get_rect(
                            center=(WIDTH // 2, HEIGHT // 2)
                        )
                    )

                instruction = small_font.render(
                    "Index: Move | Peace: Color | Open Palm: Pause | Fist: Resume",
                    True, WHITE
                )

                screen.blit(
                    instruction,
                    (20, HEIGHT - 35)
                )

            # Game over screen
            elif game_state == GAME_OVER:
                draw_game_over()

            pygame.display.flip()
            clock.tick(30)

finally:
    cap.release()
    pygame.quit()
    cv2.destroyAllWindows()
    print("GestureX Closed!")
