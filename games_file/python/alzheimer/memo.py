#!/usr/bin/env python3
import random

import cv2
import mediapipe as mp

from games_file.python.cv2_utils import Camera, Rectangle, Hands


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

        background = Rectangle(0, 0, game_img.shape[1], game_img.shape[0],
                               (255, 255, 255), -1)
        background.draw(game_img)
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
            tx, ty = 0, 0
            for hand_landmarks in results.multi_hand_landmarks:
                # mp_draw.draw_landmarks(game_img, hand_landmarks,
                #                        mp_hands.HAND_CONNECTIONS)
                for i, lm in enumerate(hand_landmarks.landmark):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    if i == 4:
                        tx, ty = cx, cy
                        cv2.circle(game_img, (tx, ty), 5, (0, 0, 255),
                                   cv2.FILLED)

                    if i == 8:
                        cv2.circle(game_img, (cx, cy), 5, (0, 0, 255),
                                   cv2.FILLED)
                        line = cv2.line(game_img, (cx, cy), (tx, ty),
                                        (0, 255, 0),
                                        1)
                        if line.shape[1] > 0:
                            length = ((cx - tx) ** 2 + (cy - ty) ** 2) ** 0.5
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


def destroy_all_windows(cam):
    cam.release()
    cv2.destroyAllWindows()


def how_to_play(cam: Camera):
    is_in_how_to_play = True
    mp_hands = mp.solutions.hands
    hands_detector = mp_hands.Hands(max_num_hands=1,
                                    min_detection_confidence=0.7,
                                    min_tracking_confidence=0.7)
    img = cam.get_rgb_img()
    card_example = Rectangle(int(img.shape[1] * 0.6), int(img.shape[0] * 0.1), 150, 200,
                             (255, 255, 255), -1, "1")
    card_example_2 = Rectangle(int(img.shape[1] * 0.8), int(img.shape[0] * 0.1), 150, 200,
                               (255, 255, 255), -1,
                               "1")

    play_button = Rectangle(int(img.shape[1] * 0.7), int(img.shape[0] * 0.7),
                            200, 100, (255, 255, 255), -1, "Jouer")
    play_button.is_clicked = True

    quit_button = Rectangle(int(img.shape[1] * 0.2), int(img.shape[0] * 0.7),
                            200, 100, (255, 255, 255), -1, "Quitter")
    quit_button.is_clicked = True

    while is_in_how_to_play:
        img = cam.get_rgb_img()
        results = hands_detector.process(img)
        hands = Hands(results, img)
        background = Rectangle(0, 0, img.shape[1], img.shape[0], (0, 0, 0),
                               -1)
        background.draw(img)
        cv2.putText(img, "Le but du jeu est de trouver les paires de cartes",
                    (10, 90),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 3)
        cv2.putText(img, "en les retournant deux par deux",
                    (10, 120),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 3)
        cv2.putText(img, "Appuyez sur 's' pour commencer le jeu",
                    (10, 180),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 3)

        card_example.draw(img)
        card_example_2.draw(img)
        quit_button.draw(img)

        if card_example.is_clicked and card_example_2.is_clicked:
            card_example.color = (0, 200, 0)
            card_example_2.color = (0, 200, 0)
            play_button.draw(img)

        if hands.landmarks:
            hands.draw()
            hands.get_pinch_pos()

        if hands.is_pinched_inside(card_example):
            card_example.is_clicked = True

        if hands.is_pinched_inside(card_example_2):
            card_example_2.is_clicked = True

        if hands.is_pinched_inside(play_button):
            is_in_how_to_play = False

        if hands.is_pinched_inside(quit_button):
            is_in_how_to_play = False
            destroy_all_windows(cam.camera)

        cv2.imshow("How to play", img)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            is_in_how_to_play = False
        elif cv2.waitKey(1) & 0xFF == ord('q'):
            is_in_how_to_play = False
            destroy_all_windows(cam.camera)


def draw_menu(img, first_rect: Rectangle, second_rect: Rectangle,
              third_rect: Rectangle):
    cv2.putText(img, "Appuyez sur 's' pour commencer le jeu",
                (10, 30),
                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 3)
    cv2.putText(img, "Appuyez sur 'q' pour quitter",
                (10, 60),
                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 3)

    first_rect.draw(img)
    second_rect.draw(img)
    third_rect.draw(img)


def menu(cam: Camera):
    is_in_menu = True
    has_to_quit = False
    go_to_how_to_play = False

    mp_hands = mp.solutions.hands
    hands_detector = mp_hands.Hands(max_num_hands=1,
                                    min_detection_confidence=0.7,
                                    min_tracking_confidence=0.7)

    img = cam.get_rgb_img()
    rectangle_width = 300
    first_rect = Rectangle(img.shape[1] // 2 - 100,
                           img.shape[0] // 2 - 200,
                           rectangle_width, 100, text="Jouer",
                           corner_radius=24)
    second_rect = Rectangle(img.shape[1] // 2 - 100,
                            img.shape[0] // 2 + 200,
                            rectangle_width, 100, text="Quitter",
                            corner_radius=24)
    third_rect = Rectangle(img.shape[1] // 2 - 100, img.shape[0] // 2,
                           rectangle_width, 100, text="Comment jouer",
                           corner_radius=24)
    background = Rectangle(0, 0, img.shape[1], img.shape[0], (0, 0, 0),
                           -1)

    first_rect.is_clicked = True
    second_rect.is_clicked = True
    third_rect.is_clicked = True

    while is_in_menu:
        img = cam.get_rgb_img()
        results = hands_detector.process(img)
        hands = Hands(results, img)

        background.draw(img)

        draw_menu(img, first_rect, second_rect, third_rect)

        if hands.landmarks:
            hands.get_pinch_pos()

        if hands.is_pinched_inside(first_rect):
            is_in_menu = False
        if hands.is_pinched_inside(second_rect):
            is_in_menu = False
            has_to_quit = True
        if hands.is_pinched_inside(third_rect):
            is_in_menu = False
            go_to_how_to_play = True

        cv2.imshow("Menu", img)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            is_in_menu = False
        if cv2.waitKey(1) & 0xFF == ord('q'):
            is_in_menu = False
            has_to_quit = True

    if has_to_quit:
        destroy_all_windows(cam.camera)
        return
    if go_to_how_to_play:
        how_to_play(cam)
        is_in_menu = True
    rows = 4
    cols = 5

    print("Test")
    launch_game(cam.camera, setup_game(rows, cols), rows, cols)


def main():
    camera = Camera()
    menu(camera)


if __name__ == '__main__':
    main()
