#!/usr/bin/env python3
import random

import cv2
import mediapipe as mp


def setup_game(rows, cols):
    card_values = [i for i in range(1, (rows * cols) // 2 + 1)] * 2
    random.shuffle(card_values)
    return [card_values[i * cols:(i + 1) * cols] for i in range(rows)]


def launch_game(vid, card_val_grid, rows=4, cols=5):
    has_won = False
    has_to_draw = False
    is_pinched = False

    first_card = (-1, -1)
    second_card = (-1, -1)

    card_h = 200
    card_w = 150
    pos_x, pos_y = 0, 0

    grid = 200
    interval = 50

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7,
                           min_tracking_confidence=0.7)
    game_vid = cv2.VideoCapture(0)

    while True:
        success, r_img = vid.read()
        img = cv2.flip(r_img, 1)
        _, r_game_img = game_vid.read()
        game_img = cv2.flip(r_game_img, 1)
        RGB_img = cv2.cvtColor(game_img, cv2.COLOR_BGR2RGB)
        results = hands.process(RGB_img)

        cv2.rectangle(game_img, (0, 0),
                      (game_img.shape[1], game_img.shape[0]),
                      (255, 255, 255), -1),
        if all([card_val_grid[i][j] == -1 for i in range(rows) for j in
                range(cols)]):
            cv2.rectangle(game_img, (0, 0),
                          (game_img.shape[1], game_img.shape[0]),
                          (255, 255, 255), -1)
            cv2.putText(game_img, "Vous avez gagne !",
                        (500, 500),
                        cv2.FONT_HERSHEY_COMPLEX, 2, (0, 0, 0), 5)
            has_won = True
        cv2.putText(game_img, "Appuyez sur 'q' pour quitter",
                    (10, 30),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 3)
        if not has_won:
            for r in range(rows):
                for c in range(cols):
                    top_left_y = r * card_h
                    top_left_x = c * card_w
                    bottom_right_y = top_left_y + card_h
                    bottom_right_x = top_left_x + card_w

                    cv2.rectangle(game_img,
                                  (grid + top_left_x + interval,
                                   grid + top_left_y + interval),
                                  (grid + bottom_right_x,
                                   grid + bottom_right_y),
                                  card_val_grid[r][c] == -1 and (
                                      255, 255, 255) or (255, 255, 0),
                                  -1)
                    if card_val_grid[r][c] == -1:
                        text_origin = (
                            grid + top_left_x + interval // 2 + card_w // 2,
                            grid + top_left_y + interval // 2 + card_h // 2)
                        cv2.putText(game_img, "v",
                                    text_origin,
                                    cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0),
                                    3)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # mp_draw.draw_landmarks(game_img, hand_landmarks,
                #                        mp_hands.HAND_CONNECTIONS)
                for i, lm in enumerate(hand_landmarks.landmark):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    if i == 4:
                        Tx, Ty = cx, cy
                        cv2.circle(game_img, (Tx, Ty), 5, (0, 0, 255),
                                   cv2.FILLED)

                    if i == 8:
                        cv2.circle(game_img, (cx, cy), 5, (0, 0, 255),
                                   cv2.FILLED)
                        line = cv2.line(game_img, (cx, cy), (Tx, Ty),
                                        (0, 255, 0),
                                        1)
                        if line.shape[1] > 0:
                            length = ((cx - Tx) ** 2 + (cy - Ty) ** 2) ** 0.5
                            if length < 50 and not is_pinched:
                                print("Pinched")
                                print(cx, cy)
                                is_pinched = True
                                print("Pinched on card")
                                pos_x = ((cx - grid - interval) // 75) // 2
                                pos_y = ((cy - grid - interval) // 100) // 2
                                print(pos_x, pos_y)
                                has_to_draw = True
                            elif length > 100 and is_pinched:
                                is_pinched = False

        else:
            is_pinched = False

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if has_to_draw:
            if pos_y > rows - 1 or pos_x > cols - 1:
                has_to_draw = False
                continue
            elif pos_y < 0 or pos_x < 0:
                has_to_draw = False
                continue
            else:
                if second_card == (-1, -1):
                    print("first_card != (pos_y, pos_x): ", first_card,
                          (pos_y, pos_x))
                    second_card = (pos_y, pos_x)
                    has_to_draw = False
                    continue
                elif first_card == (-1, -1) and second_card != (pos_y, pos_x):
                    first_card = (pos_y, pos_x)
                    has_to_draw = False

        if first_card != (-1, -1):
            top_left_y = first_card[0] * card_h
            top_left_x = first_card[1] * card_w
            centerX = card_w // 2
            centerY = card_h // 2
            if card_val_grid[first_card[0]][first_card[1]] == -1:
                cv2.putText(game_img, f"{card_val_grid[pos_y][pos_x]}",
                            (
                                grid + top_left_x + interval // 2 + centerX,
                                grid + top_left_y + interval // 2 + centerY),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 3)
            else:
                cv2.putText(game_img,
                            f"{card_val_grid[first_card[0]][first_card[1]]}",
                            (
                                grid + top_left_x + interval // 2 + centerX,
                                grid + top_left_y + interval // 2 + centerY),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 3)

        if second_card != (-1, -1):
            centerX = card_w // 2
            centerY = card_h // 2
            top_left_y = second_card[0] * card_h
            top_left_x = second_card[1] * card_w
            if card_val_grid[second_card[0]][second_card[1]] == -1:
                cv2.putText(game_img, "",
                            (
                                grid + top_left_x + interval // 2 + centerX,
                                grid + top_left_y + interval // 2 + centerY),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 3)
            else:
                cv2.putText(game_img,
                            f"{card_val_grid[second_card[0]][second_card[1]]}",
                            (
                                grid + top_left_x + interval // 2 + centerX,
                                grid + top_left_y + interval // 2 + centerY),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 3)

        if first_card != (-1, -1) and second_card != (-1, -1):
            print(f"First card DIFF: {first_card}")
            print(f"Second card DIFF: {second_card}")
            if card_val_grid[first_card[0]][first_card[1]] == \
                    card_val_grid[second_card[0]][second_card[1]]:
                print(
                    f"Matched {card_val_grid[first_card[0]][first_card[1]]} ")
                print(f"and {card_val_grid[second_card[0]][second_card[1]]}")
                card_val_grid[first_card[0]][first_card[1]] = -1
                card_val_grid[second_card[0]][second_card[1]] = -1
                first_card = (-1, -1)
                second_card = (-1, -1)
            else:
                print("Not matched")
                first_card = (-1, -1)
                second_card = (-1, -1)

        cv2.waitKey(1)
        cv2.imshow("Memo", game_img)
        # cv2.imshow("Memo", img)

    destroy_all_windows(vid)


def destroy_all_windows(video):
    cv2.destroyAllWindows()
    video.release()


def how_to_play(vid):
    is_in_how_to_play = True
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7,
                           min_tracking_confidence=0.7)
    draw = mp.solutions.drawing_utils

    while is_in_how_to_play:
        success, r_img = vid.read()
        img = cv2.flip(r_img, 1)
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_img)
        cv2.putText(img, "Le but du jeu est de trouver les paires de cartes",
                    (10, 90),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 3)
        cv2.putText(img, "en les retournant deux par deux",
                    (10, 120),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 3)
        cv2.putText(img, "Appuyez sur 's' pour commencer le jeu",
                    (10, 180),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 3)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                draw.draw_landmarks(img, hand_landmarks,
                                    mp_hands.HAND_CONNECTIONS)

        cv2.imshow("How to play", img)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            is_in_how_to_play = False
        elif cv2.waitKey(1) & 0xFF == ord('q'):
            is_in_how_to_play = False
            destroy_all_windows(vid)


def menu(vid):
    is_in_menu = True
    is_pinched = False
    has_to_quit = False
    go_to_how_to_play = False

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7,
                           min_tracking_confidence=0.7)
    draw = mp.solutions.drawing_utils

    while is_in_menu:
        success, r_img = vid.read()
        img = cv2.flip(r_img, 1)
        first_rect = (img.shape[1] // 2 - 100, img.shape[0] // 2 - 200)
        second_rect = (img.shape[1] // 2 - 100, img.shape[0] // 2 + 200)
        third_rect = (img.shape[1] // 2 - 100, img.shape[0] // 2)
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_img)
        cv2.putText(img, "Appuyez sur 's' pour commencer le jeu",
                    (10, 30),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 3)
        cv2.putText(img, "Appuyez sur 'q' pour quitter",
                    (10, 60),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 3)

        cv2.rectangle(img, first_rect,
                      (first_rect[0] + 200, first_rect[1] + 100),
                      (255, 255, 255), -1)
        cv2.putText(img, "Jouer", (first_rect[0] + 50, first_rect[1] + 50),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 3)
        cv2.rectangle(img, second_rect,
                      (second_rect[0] + 200, second_rect[1] + 100),
                      (255, 255, 255), -1)
        cv2.putText(img, "Quitter", (second_rect[0] + 50, second_rect[1] + 50),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0),
                    3)
        cv2.rectangle(img, third_rect,
                      (third_rect[0] + 200, third_rect[1] + 100),
                      (255, 255, 255), -1)
        cv2.putText(img, "Comment", (third_rect[0] + 25, third_rect[1] + 50),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 3)
        cv2.putText(img, "jouer", (third_rect[0] + 50, third_rect[1] + 75),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 3)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                draw.draw_landmarks(img, hand_landmarks,
                                    mp_hands.HAND_CONNECTIONS)
                for i, lm in enumerate(hand_landmarks.landmark):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    if i == 4:
                        Tx, Ty = cx, cy
                        cv2.circle(img, (Tx, Ty), 5, (0, 0, 255), cv2.FILLED)

                    if i == 8:
                        cv2.circle(img, (cx, cy), 5, (0, 0, 255), cv2.FILLED)
                        line = cv2.line(img, (cx, cy), (Tx, Ty), (0, 255, 0),
                                        1)
                        if line.shape[1] > 0:
                            length = ((cx - Tx) ** 2 + (cy - Ty) ** 2) ** 0.5
                            if length < 50 and not is_pinched:
                                if (first_rect[0] < cx < first_rect[0] + 200
                                        and first_rect[1] < cy < first_rect[
                                            1] + 100):
                                    is_in_menu = False
                                elif second_rect[0] < cx < second_rect[
                                    0] + 200 and second_rect[1] < cy < \
                                        second_rect[
                                            1] + 100:
                                    has_to_quit = True
                                    is_in_menu = False
                                elif third_rect[0] < cx < third_rect[
                                    0] + 200 and third_rect[1] < cy < \
                                        third_rect[
                                            1] + 100:
                                    go_to_how_to_play = True
                                    is_in_menu = False

        cv2.imshow("Menu", img)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            is_in_menu = False
        elif cv2.waitKey(1) & 0xFF == ord('q'):
            is_in_menu = False
            has_to_quit = True

    if has_to_quit:
        destroy_all_windows(vid)
        return
    if go_to_how_to_play:
        how_to_play(vid)
        is_in_menu = True
    rows = 4
    cols = 5

    print("Test")
    launch_game(vid, setup_game(rows, cols), rows, cols)


def main():
    cap = cv2.VideoCapture(0)
    cap.set(3, 940)
    menu(cap)


if __name__ == '__main__':
    main()
