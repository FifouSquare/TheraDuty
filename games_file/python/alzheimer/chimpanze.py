import random
import time

import cv2
import mediapipe as mp

width, height = 1280, 720

num_numbers = 10
display_time = 5

positions = [(random.randint(50, width - 50), random.randint(50, height - 50))
             for _ in range(num_numbers)]
numbers = list(range(1, num_numbers + 1))
random.shuffle(numbers)

selected_numbers = []
correct_order = sorted(numbers)
game_over = False

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.5,
                       min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils


def draw_numbers(img, positions, numbers, show):
    for pos, num in zip(positions, numbers):
        if show:
            cv2.putText(img, str(num), pos, cv2.FONT_HERSHEY_SIMPLEX, 2,
                        (255, 255, 255), 3)
        else:
            cv2.circle(img, pos, 20, (255, 255, 255), -1)


def check_pinch(hand_landmarks, img):
    global selected_numbers, game_over
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]

    ix, iy = int(index_tip.x * width), int(index_tip.y * height)
    tx, ty = int(thumb_tip.x * width), int(thumb_tip.y * height)

    if abs(ix - tx) < 20 and abs(iy - ty) < 20:
        for i, pos in enumerate(positions):
            if abs(ix - pos[0]) < 20 and abs(iy - pos[1]) < 20:
                if numbers[i] not in selected_numbers:
                    selected_numbers.append(numbers[i])
                    if len(selected_numbers) == num_numbers:
                        game_over = True


start_time = time.time()

cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, image = cap.read()
    if not success:
        break

    image = cv2.flip(image, 1)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)

    img = image.copy()

    elapsed_time = time.time() - start_time

    if elapsed_time < display_time:
        draw_numbers(img, positions, numbers, show=True)
    else:
        draw_numbers(img, positions, numbers, show=False)
        if not game_over:
            cv2.putText(img, "Select the numbers in order", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            for i, num in enumerate(selected_numbers):
                cv2.putText(img, str(num), (50, 100 + i * 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        else:
            if sorted(selected_numbers) == correct_order:
                cv2.putText(img, "You win!", (width // 2 - 100, height // 2),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
            else:
                cv2.putText(img, "Game over!", (width // 2 - 100, height // 2),
                            cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(img, hand_landmarks,
                                      mp_hands.HAND_CONNECTIONS)
            check_pinch(hand_landmarks, img)

    cv2.imshow('Game', img)

    if cv2.waitKey(1) & 0xFF == 27:
        break

hands.close()
cap.release()
cv2.destroyAllWindows()
