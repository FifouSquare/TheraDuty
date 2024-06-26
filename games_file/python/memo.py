#!/usr/bin/env python3
import random

import cv2
import mediapipe as mp


def setup_game(rows, cols):
    card_values = [i for i in range(1, (rows * cols) // 2 + 1)] * 2
    random.shuffle(card_values)
    return [card_values[i * cols:(i + 1) * cols] for i in range(rows)]


def launch_game(card_val_grid, rows=4, cols=5):
    has_won = False
    has_to_draw = False
    is_pinched = False

    first_card = (-1, -1)
    second_card = (-1, -1)

    CARD_HEIGHT = 200
    CARD_WIDTH = 150
    posX, posY = 0, 0

    GRID_BASE = 200
    GRID_INTERVAL = 50
    while True:
        success, r_img = vid.read()
        img = cv2.flip(r_img, 1)
        if all([card_val_grid[i][j] == -1 for i in range(rows) for j in range(cols)]):
            cv2.rectangle(img, (0, 0), (img.shape[1], img.shape[0]), (255, 255, 255), -1)
            cv2.putText(img, "Vous avez gagne !",
                        (500, 500),
                        cv2.FONT_HERSHEY_COMPLEX, 2, (0, 0, 0), 5)
            has_won = True
        cv2.putText(img, "Appuyez sur 'q' pour quitter",
                    (10, 30),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 3)
        RGB_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(RGB_img)
        if not has_won:
            for r in range(rows):
                for c in range(cols):
                    top_left_y = r * CARD_HEIGHT
                    top_left_x = c * CARD_WIDTH
                    bottom_right_y = top_left_y + CARD_HEIGHT
                    bottom_right_x = top_left_x + CARD_WIDTH

                    cv2.rectangle(img, (GRID_BASE + top_left_x + GRID_INTERVAL, GRID_BASE + top_left_y + GRID_INTERVAL),
                                  (GRID_BASE + bottom_right_x, GRID_BASE + bottom_right_y),
                                  card_val_grid[r][c] == -1 and (255, 255, 255) or (255, 255, 0),
                                  -1)
                    if card_val_grid[r][c] == -1:
                        cv2.putText(img, "v",
                                    (GRID_BASE + top_left_x + GRID_INTERVAL // 2 + CARD_WIDTH // 2,
                                     GRID_BASE + top_left_y + GRID_INTERVAL // 2 + CARD_HEIGHT // 2),
                                    cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                for i, lm in enumerate(hand_landmarks.landmark):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    if i == 4:
                        Tx, Ty = cx, cy
                        cv2.circle(img, (Tx, Ty), 5, (0, 0, 255), cv2.FILLED)

                    if i == 8:
                        cv2.circle(img, (cx, cy), 5, (0, 0, 255), cv2.FILLED)
                        line = cv2.line(img, (cx, cy), (Tx, Ty), (0, 255, 0), 1)
                        if line.shape[1] > 0:
                            length = ((cx - Tx) ** 2 + (cy - Ty) ** 2) ** 0.5
                            if length < 50 and not is_pinched:
                                print("Pinched")
                                print(cx, cy)
                                is_pinched = True
                                print("Pinched on card")
                                posX = ((cx - GRID_BASE - GRID_INTERVAL) // 75) // 2
                                posY = ((cy - GRID_BASE - GRID_INTERVAL) // 100) // 2
                                print(posX, posY)
                                has_to_draw = True
                            elif length > 100 and is_pinched:
                                is_pinched = False

                            prev_cx, prev_cy = cx, cy
        else:
            is_pinched = False

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if has_to_draw:
            if posY > rows - 1 or posX > cols - 1:
                has_to_draw = False
                continue
            elif posY < 0 or posX < 0:
                has_to_draw = False
                continue
            else:
                if second_card == (-1, -1):
                    print("First card == -1")
                    second_card = (posY, posX)
                    has_to_draw = False
                    continue
                elif first_card == (-1, -1):
                    first_card = (posY, posX)
                    has_to_draw = False

        if first_card != (-1, -1):
            top_left_y = first_card[0] * CARD_HEIGHT
            top_left_x = first_card[1] * CARD_WIDTH
            centerX = CARD_WIDTH // 2
            centerY = CARD_HEIGHT // 2
            if card_val_grid[first_card[0]][first_card[1]] == -1:
                cv2.putText(img, f"{card_val_grid[posY][posX]}",
                            (GRID_BASE + top_left_x + GRID_INTERVAL // 2 + centerX,
                             GRID_BASE + top_left_y + GRID_INTERVAL // 2 + centerY),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 3)
            else:
                cv2.putText(img, f"{card_val_grid[first_card[0]][first_card[1]]}",
                            (GRID_BASE + top_left_x + GRID_INTERVAL // 2 + centerX,
                             GRID_BASE + top_left_y + GRID_INTERVAL // 2 + centerY),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 3)

        if second_card != (-1, -1):
            centerX = CARD_WIDTH // 2
            centerY = CARD_HEIGHT // 2
            top_left_y = second_card[0] * CARD_HEIGHT
            top_left_x = second_card[1] * CARD_WIDTH
            if card_val_grid[second_card[0]][second_card[1]] == -1:
                cv2.putText(img, "",
                            (GRID_BASE + top_left_x + GRID_INTERVAL // 2 + centerX,
                             GRID_BASE + top_left_y + GRID_INTERVAL // 2 + centerY),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 3)
            else:
                cv2.putText(img, f"{card_val_grid[second_card[0]][second_card[1]]}",
                            (GRID_BASE + top_left_x + GRID_INTERVAL // 2 + centerX,
                             GRID_BASE + top_left_y + GRID_INTERVAL // 2 + centerY),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 3)

        if first_card != (-1, -1) and second_card != (-1, -1):
            print(f"First card DIFF: {first_card}")
            print(f"Second card DIFF: {second_card}")
            if card_val_grid[first_card[0]][first_card[1]] == card_val_grid[second_card[0]][second_card[1]]:
                print(
                    f"Matched {card_val_grid[first_card[0]][first_card[1]]} and {card_val_grid[second_card[0]][second_card[1]]}")
                card_val_grid[first_card[0]][first_card[1]] = -1
                card_val_grid[second_card[0]][second_card[1]] = -1
                first_card = (-1, -1)
                second_card = (-1, -1)
            else:
                print("Not matched")
                first_card = (-1, -1)
                second_card = (-1, -1)

        cv2.waitKey(1)
        cv2.imshow("Memo", img)


def menu():
    is_in_menu = True
    is_pinched = False
    has_to_quit = False

    while is_in_menu:
        success, r_img = vid.read()
        img = cv2.flip(r_img, 1)
        first_rect = (img.shape[1] // 2 - 100, img.shape[0] // 2 - 200)
        second_rect = (img.shape[1] // 2 - 100, img.shape[0] // 2 + 200)
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_img)
        cv2.putText(img, "Appuyez sur 's' pour commencer le jeu",
                    (10, 30),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 3)
        cv2.putText(img, "Appuyez sur 'q' pour quitter",
                    (10, 60),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 3)

        cv2.rectangle(img, first_rect, (first_rect[0] + 200, first_rect[1] + 100), (255, 255, 255), -1)
        cv2.putText(img, "Jouer", (first_rect[0] + 50, first_rect[1] + 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 3)
        cv2.rectangle(img, second_rect, (second_rect[0] + 200, second_rect[1] + 100), (255, 255, 255), -1)
        cv2.putText(img, "Quitter", (second_rect[0] + 50, second_rect[1] + 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0),
                    3)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                for i, lm in enumerate(hand_landmarks.landmark):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    if i == 4:
                        Tx, Ty = cx, cy
                        cv2.circle(img, (Tx, Ty), 5, (0, 0, 255), cv2.FILLED)

                    if i == 8:
                        cv2.circle(img, (cx, cy), 5, (0, 0, 255), cv2.FILLED)
                        line = cv2.line(img, (cx, cy), (Tx, Ty), (0, 255, 0), 1)
                        if line.shape[1] > 0:
                            length = ((cx - Tx) ** 2 + (cy - Ty) ** 2) ** 0.5
                            if length < 50 and not is_pinched:
                                if first_rect[0] < cx < first_rect[0] + 200 and first_rect[1] < cy < first_rect[1] + 100:
                                    is_in_menu = False
                                elif second_rect[0] < cx < second_rect[0] + 200 and second_rect[1] < cy < second_rect[1] + 100:
                                    has_to_quit = True
                                    is_in_menu = False

        cv2.imshow("Menu", img)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            is_in_menu = False
        elif cv2.waitKey(1) & 0xFF == ord('q'):
            break

    if has_to_quit:
        return
    rows = 4
    cols = 5

    launch_game(setup_game(rows, cols), rows, cols)


if __name__ == '__main__':
    vid = cv2.VideoCapture(0)
    vid.set(3, 940)
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
    mp_draw = mp.solutions.drawing_utils

    menu()
