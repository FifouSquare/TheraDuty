#!/usr/bin/env python3
import random
import sys

import cv2
import mediapipe as mp


def draw_rounded_rectangle(img, top_left, bottom_right, color, thickness,
                           radius):
    x1, y1 = top_left
    x2, y2 = bottom_right

    # Ensure radius is not greater than half of the width or height
    radius = min(radius, (x2 - x1) // 2, (y2 - y1) // 2)

    # Draw four rounded corners
    cv2.ellipse(img, (x1 + radius, y1 + radius), (radius, radius), 180, 0, 90,
                color, thickness)
    cv2.ellipse(img, (x2 - radius, y1 + radius), (radius, radius), 270, 0, 90,
                color, thickness)
    cv2.ellipse(img, (x1 + radius, y2 - radius), (radius, radius), 90, 0, 90,
                color, thickness)
    cv2.ellipse(img, (x2 - radius, y2 - radius), (radius, radius), 0, 0, 90,
                color, thickness)

    # Draw four lines
    cv2.line(img, (x1 + radius, y1), (x2 - radius, y1), color, thickness)
    cv2.line(img, (x1 + radius, y2), (x2 - radius, y2), color, thickness)
    cv2.line(img, (x1, y1 + radius), (x1, y2 - radius), color, thickness)
    cv2.line(img, (x2, y1 + radius), (x2, y2 - radius), color, thickness)


def draw_filled_rounded_rectangle(img, top_left, bottom_right, color, radius):
    x1, y1 = top_left
    x2, y2 = bottom_right

    # Ensure radius is not greater than half of the width or height
    radius = min(radius, (x2 - x1) // 2, (y2 - y1) // 2)

    # Draw four rounded corners
    cv2.ellipse(img, (x1 + radius, y1 + radius), (radius, radius), 180, 0, 90,
                color, -1)
    cv2.ellipse(img, (x2 - radius, y1 + radius), (radius, radius), 270, 0, 90,
                color, -1)
    cv2.ellipse(img, (x1 + radius, y2 - radius), (radius, radius), 90, 0, 90,
                color, -1)
    cv2.ellipse(img, (x2 - radius, y2 - radius), (radius, radius), 0, 0, 90,
                color, -1)

    # Draw four rectangles
    cv2.rectangle(img, (x1 + radius, y1), (x2 - radius, y2), color, -1)
    cv2.rectangle(img, (x1, y1 + radius), (x1 + radius, y2 - radius), color,
                  -1)
    cv2.rectangle(img, (x2 - radius, y1 + radius), (x2, y2 - radius), color,
                  -1)
    cv2.rectangle(img, (x1 + radius, y1), (x2 - radius, y1 + radius), color,
                  -1)
    cv2.rectangle(img, (x1 + radius, y2 - radius), (x2 - radius, y2), color,
                  -1)


def draw_rounded_shadow_rectangle(img, top_left, bottom_right, color, radius,
                                  shadow_offset,
                                  shadow_color, highlight_color):
    shadow_top_left = (
        top_left[0] + shadow_offset, top_left[1] + shadow_offset)
    shadow_bottom_right = (
        bottom_right[0] + shadow_offset, bottom_right[1] + shadow_offset)

    highlight_top_left = (
        top_left[0] - shadow_offset, top_left[1] - shadow_offset)
    highlight_bottom_right = (
        bottom_right[0] - shadow_offset, bottom_right[1] - shadow_offset)

    # Draw the shadow
    draw_filled_rounded_rectangle(img, shadow_top_left, shadow_bottom_right,
                                  shadow_color, radius)

    draw_filled_rounded_rectangle(img, highlight_top_left,
                                  highlight_bottom_right,
                                  highlight_color, radius)

    # Draw the main filled rounded rectangle on top of the shadow
    draw_filled_rounded_rectangle(img, top_left, bottom_right, color, radius)


def draw_line(lm, i, w, h):
    start = (int(lm.landmark[i].x * w),
             int(lm.landmark[i].y * h))
    end = (int(lm.landmark[i + 1].x * w),
           int(lm.landmark[i + 1].y * h))
    return start, end


class Camera:
    def __init__(self):
        self.camera = cv2.VideoCapture(0)
        self.resolution = (800, 600)
        self.framerate = 24
        self.camera.set(3, 940)

    def __del__(self):
        self.close()

    def close(self):
        self.camera.release()

    def get_rgb_img(self):
        ret, frame = self.camera.read()
        frame = cv2.flip(frame, 1)
        return frame


class Rectangle:
    def __init__(self, x, y, width, height, color=(200, 200, 200),
                 thickness=-1,
                 text="",
                 corner_radius=24):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.thickness = thickness
        self.text = text
        self.text_color = (0, 0, 0)
        self.highlight_color = (255, 255, 255)
        self.shadow_color = (96, 96, 96)
        self.corner_radius = corner_radius
        self.is_clicked = False

    def draw(self, img):
        if self.thickness == -1:
            draw_rounded_shadow_rectangle(img, (self.x, self.y),
                                          (self.x + self.width,
                                           self.y + self.height),
                                          self.color, self.corner_radius, 5,
                                          self.shadow_color,
                                          self.highlight_color)
        else:
            draw_rounded_rectangle(img, (self.x, self.y),
                                   (self.x + self.width, self.y + self.height),
                                   radius=self.corner_radius, color=self.color,
                                   thickness=self.thickness)
        if self.text != "" and self.is_clicked:
            cv2.putText(img, self.text,
                        (
                            self.x + self.width // 2 - len(self.text) * 10,
                            self.y + self.height // 2),
                        cv2.FONT_HERSHEY_COMPLEX, 1, self.text_color, 3)


class Hands:
    def __init__(self, result, img):
        self.landmarks = result.multi_hand_landmarks
        self.is_pinching = False
        self.img = img
        self.pinch_pos = (0, 0)
        self.pinch_length = 50
        self.pinch_length_open = 100

    def draw(self, thickness=20, color=(0, 255, 0)):
        lm = self.landmarks[0]
        h, w, c = self.img.shape
        for i in range(21):
            if i < 4:
                start, end = draw_line(lm, i, w, h)
                cv2.line(self.img, start, end, color, thickness)
            if i == 4:
                start = (int(lm.landmark[1].x * w),
                         int(lm.landmark[1].y * h))
                end = (int(lm.landmark[5].x * w),
                       int(lm.landmark[5].y * h))
                cv2.line(self.img, start, end, color, thickness)
            if 4 < i < 8:
                start, end = draw_line(lm, i, w, h)
                cv2.line(self.img, start, end, color, thickness)

            if i == 8:
                start = (int(lm.landmark[5].x * w),
                         int(lm.landmark[5].y * h))
                end = (int(lm.landmark[9].x * w),
                       int(lm.landmark[9].y * h))
                cv2.line(self.img, start, end, color, thickness)

            if 8 < i < 12:
                start, end = draw_line(lm, i, w, h)
                cv2.line(self.img, start, end, color, thickness)

            if i == 12:
                start = (int(lm.landmark[9].x * w),
                         int(lm.landmark[9].y * h))
                end = (int(lm.landmark[13].x * w),
                       int(lm.landmark[13].y * h))
                cv2.line(self.img, start, end, color, thickness)

            if 12 < i < 16:
                start, end = draw_line(lm, i, w, h)
                cv2.line(self.img, start, end, color, thickness)

            if i == 16:
                start = (int(lm.landmark[13].x * w),
                         int(lm.landmark[13].y * h))
                end = (int(lm.landmark[17].x * w),
                       int(lm.landmark[17].y * h))
                cv2.line(self.img, start, end, color, thickness)

            if 16 < i < 20:
                start, end = draw_line(lm, i, w, h)
                cv2.line(self.img, start, end, color, thickness)
            if i == 17:
                start = (int(lm.landmark[17].x * w),
                         int(lm.landmark[17].y * h))
                end = (int(lm.landmark[0].x * w),
                       int(lm.landmark[0].y * h))
                cv2.line(self.img, start, end, color, thickness)

    def draw_on_img(self, img, thickness=20, color=(0, 255, 0)):
        lm = self.landmarks[0]
        h, w, c = self.img.shape
        for i in range(21):
            if i < 4:
                start, end = draw_line(lm, i, w, h)
                cv2.line(img, start, end, color, thickness)
            if i == 4:
                start = (int(lm.landmark[1].x * w),
                         int(lm.landmark[1].y * h))
                end = (int(lm.landmark[5].x * w),
                       int(lm.landmark[5].y * h))
                cv2.line(img, start, end, color, thickness)
            if 4 < i < 8:
                start, end = draw_line(lm, i, w, h)
                cv2.line(img, start, end, color, thickness)

            if i == 8:
                start = (int(lm.landmark[5].x * w),
                         int(lm.landmark[5].y * h))
                end = (int(lm.landmark[9].x * w),
                       int(lm.landmark[9].y * h))
                cv2.line(img, start, end, color, thickness)

            if 8 < i < 12:
                start, end = draw_line(lm, i, w, h)
                cv2.line(img, start, end, color, thickness)

            if i == 12:
                start = (int(lm.landmark[9].x * w),
                         int(lm.landmark[9].y * h))
                end = (int(lm.landmark[13].x * w),
                       int(lm.landmark[13].y * h))
                cv2.line(img, start, end, color, thickness)

            if 12 < i < 16:
                start, end = draw_line(lm, i, w, h)
                cv2.line(img, start, end, color, thickness)

            if i == 16:
                start = (int(lm.landmark[13].x * w),
                         int(lm.landmark[13].y * h))
                end = (int(lm.landmark[17].x * w),
                       int(lm.landmark[17].y * h))
                cv2.line(img, start, end, color, thickness)

            if 16 < i < 20:
                start, end = draw_line(lm, i, w, h)
                cv2.line(img, start, end, color, thickness)
            if i == 17:
                start = (int(lm.landmark[17].x * w),
                         int(lm.landmark[17].y * h))
                end = (int(lm.landmark[0].x * w),
                       int(lm.landmark[0].y * h))
                cv2.line(img, start, end, color, thickness)

    def get_pinch_pos(self):
        tx, ty = 0, 0
        for hand_landmarks in self.landmarks:
            self.draw()
            for i, lm in enumerate(hand_landmarks.landmark):
                h, w, c = self.img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                if i == 4:
                    tx, ty = cx, cy

                if i == 8:
                    length = ((cx - tx) ** 2 + (cy - ty) ** 2) ** 0.5
                    if length < self.pinch_length and not self.is_pinching:
                        self.is_pinching = True
                        self.pinch_pos = (cx, cy)
                        return cx, cy
                    elif length > self.pinch_length_open and self.is_pinching:
                        self.is_pinching = False

    def is_pinched_inside(self, r):
        x, y = self.pinch_pos
        if r.x < x < r.x + r.width and r.y < y < r.y + r.height:
            return True
        return False


def setup_game(rows=4, cols=5):
    card_values = [i for i in range(1, (rows * cols) // 2 + 1)] * 2
    random.shuffle(card_values)
    shuffled_cards = [card_values[i * cols:(i + 1) * cols] for i in
                      range(rows)]
    cards = []
    interval = 50
    for i in range(rows):
        for j in range(cols):
            cards.append(
                Rectangle(j * 150 + j * interval, i * 200 + i * interval,
                          150, 200, text=str(shuffled_cards[i][j])))
    return cards


def win():
    is_running = True
    has_to_replay = True

    mp_hands = mp.solutions.hands
    hands_detector = mp_hands.Hands(max_num_hands=1,
                                    min_detection_confidence=0.7,
                                    min_tracking_confidence=0.7)

    cam = Camera()
    img = cam.get_rgb_img()
    background = Rectangle(0, 0, img.shape[1], img.shape[0],
                           (0, 0, 0), corner_radius=0)
    replay = Rectangle(int(img.shape[1] * 0.3), int(img.shape[0] * 0.5), 200,
                       100, (0, 200, 0))
    replay.text = "Rejouer"
    replay.is_clicked = True
    replay.shadow_color = (0, 155, 0)
    replay.highlight_color = (0, 255, 0)

    quit_button = Rectangle(int(img.shape[1] * 0.6), int(img.shape[0] * 0.5),
                            200, 100, (0, 0, 200))
    quit_button.text = "Quitter"
    quit_button.is_clicked = True
    quit_button.shadow_color = (0, 0, 155)
    quit_button.highlight_color = (0, 0, 255)

    while is_running:
        img = cam.get_rgb_img()
        results = hands_detector.process(img)
        hands = Hands(results, img)

        background.draw(img)
        cv2.putText(img, "Victoire !", (img.shape[1] // 2 - 100, 100),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 3)
        replay.draw(img)
        quit_button.draw(img)

        if hands.landmarks:
            hands.get_pinch_pos()

        if hands.is_pinched_inside(quit_button):
            is_running = False
            has_to_replay = False
        if hands.is_pinched_inside(replay):
            is_running = False
            has_to_replay = True

        cv2.imshow("Win", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            is_running = False
            has_to_replay = False

    destroy_all_windows(cam.camera)
    if has_to_replay:
        launch_game()


def launch_game():
    first_card = None
    second_card = None
    is_not_matched = False
    go_to_menu = False
    is_running = True

    cam = Camera()

    cv2.namedWindow("Memo", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Memo", 1280, 720)
    card_val_grid = setup_game()

    mp_hands = mp.solutions.hands
    hands_detector = mp_hands.Hands(max_num_hands=1,
                                    min_detection_confidence=0.7,
                                    min_tracking_confidence=0.7)

    game_img = cam.get_rgb_img()
    background = Rectangle(0, 0, game_img.shape[1], game_img.shape[0],
                           (0, 0, 0), corner_radius=0)

    menu_button = Rectangle(100, int(game_img.shape[0] * 0.8), 200, 100,
                            text="Menu")
    menu_button.is_clicked = True

    for card in card_val_grid:
        card.x += game_img.shape[0] // 2
        card.y += 100

    while is_running:
        img = cam.get_rgb_img()
        game_img = cam.get_rgb_img()
        results = hands_detector.process(img)
        hands = Hands(results, img)

        background.draw(game_img)
        menu_button.draw(game_img)
        for card in card_val_grid:
            card.draw(game_img)
        if hands.landmarks:
            hands.draw_on_img(game_img)
            hands.get_pinch_pos()

        if hands.is_pinched_inside(menu_button):
            is_running = False
            go_to_menu = True

        for card in card_val_grid:
            if hands.is_pinched_inside(card) and card.color != (
                    0, 200, 0):
                if is_not_matched:
                    first_card.is_clicked = False
                    second_card.is_clicked = False
                    first_card.text_color = (0, 0, 0)
                    second_card.text_color = (0, 0, 0)
                    first_card = None
                    second_card = None
                    is_not_matched = False
                if first_card is None:
                    card.is_clicked = True
                    first_card = card
                elif second_card is None and first_card != card:
                    second_card = card
                    second_card.is_clicked = True
                break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if first_card is not None and second_card is not None:
            if first_card.text == second_card.text:
                first_card.color = (0, 200, 0)
                first_card.text_color = (0, 255, 0)
                first_card.shadow_color = (0, 155, 0)
                first_card.highlight_color = (0, 255, 0)

                second_card.color = (0, 200, 0)
                second_card.text_color = (0, 255, 0)
                second_card.shadow_color = (0, 155, 0)
                second_card.highlight_color = (0, 255, 0)
                first_card = None
                second_card = None
            else:
                first_card.text_color = (0, 0, 200)
                second_card.text_color = (0, 0, 200)
                is_not_matched = True

        cv2.waitKey(1)
        cv2.imshow("Memo", game_img)

        for card in card_val_grid:
            if card.color != (0, 200, 0):
                break
            is_running = False

    if go_to_menu:
        destroy_all_windows(cam.camera)
        menu()
    else:
        destroy_all_windows(cam.camera)
        win()


def destroy_all_windows(cam):
    cam.release()
    cv2.destroyAllWindows()


def how_to_play():
    is_in_how_to_play = True
    mp_hands = mp.solutions.hands
    hands_detector = mp_hands.Hands(max_num_hands=1,
                                    min_detection_confidence=0.7,
                                    min_tracking_confidence=0.7)
    cam = Camera()
    img = cam.get_rgb_img()
    card_example = Rectangle(int(img.shape[1] * 0.6), int(img.shape[0] * 0.1),
                             150, 200, text="1")
    card_example_2 = Rectangle(int(img.shape[1] * 0.8),
                               int(img.shape[0] * 0.1), 150, 200,
                               text="1")

    play_button = Rectangle(int(img.shape[1] * 0.7), int(img.shape[0] * 0.7),
                            200, 100, text="Jouer")
    play_button.is_clicked = True

    quit_button = Rectangle(int(img.shape[1] * 0.2), int(img.shape[0] * 0.7),
                            200, 100, text="Quitter")
    quit_button.is_clicked = True

    background = Rectangle(0, 0, img.shape[1], img.shape[0], (0, 0, 0),
                           -1, corner_radius=0)

    while is_in_how_to_play:
        img = cam.get_rgb_img()
        results = hands_detector.process(img)
        hands = Hands(results, img)
        background.draw(img)
        cv2.putText(img, "Le but du jeu est de trouver les paires de cartes",
                    (10, 90),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 3)
        cv2.putText(img, "en les retournant deux par deux",
                    (10, 120),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 3)
        cv2.putText(img, "Testez avec ces cartes pour jouer au jeu",
                    (10, 180),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 3)

        card_example.draw(img)
        card_example_2.draw(img)
        quit_button.draw(img)

        if card_example.is_clicked and card_example_2.is_clicked:
            card_example.color = (0, 200, 0)
            card_example.text_color = (0, 255, 0)
            card_example.shadow_color = (0, 155, 0)
            card_example.highlight_color = (0, 255, 0)

            card_example_2.color = (0, 200, 0)
            card_example_2.text_color = (0, 255, 0)
            card_example_2.shadow_color = (0, 155, 0)
            card_example_2.highlight_color = (0, 255, 0)
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
            destroy_all_windows(cam.camera)
            launch_game()

        if hands.is_pinched_inside(quit_button):
            destroy_all_windows(cam.camera)
            sys.exit(0)

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


def menu():
    is_in_menu = True
    has_to_quit = False
    go_to_play = False
    go_to_how_to_play = False

    mp_hands = mp.solutions.hands
    hands_detector = mp_hands.Hands(max_num_hands=1,
                                    min_detection_confidence=0.7,
                                    min_tracking_confidence=0.7)

    cam = Camera()
    img = cam.get_rgb_img()
    rectangle_width = 300
    play_button = Rectangle(img.shape[1] // 2 - 100,
                            img.shape[0] // 2 - 200,
                            rectangle_width, 100, text="Jouer",
                            corner_radius=24)
    quit_button = Rectangle(img.shape[1] // 2 - 100,
                            img.shape[0] // 2 + 200,
                            rectangle_width, 100, text="Quitter",
                            corner_radius=24)
    htp_button = Rectangle(img.shape[1] // 2 - 100, img.shape[0] // 2,
                           rectangle_width, 100, text="Comment jouer",
                           corner_radius=24)
    background = Rectangle(0, 0, img.shape[1], img.shape[0], (0, 0, 0),
                           -1, corner_radius=0)

    play_button.is_clicked = True
    htp_button.is_clicked = True
    quit_button.is_clicked = True

    while is_in_menu:
        img = cam.get_rgb_img()
        results = hands_detector.process(img)
        hands = Hands(results, img)

        background.draw(img)

        draw_menu(img, play_button, htp_button, quit_button)

        if hands.landmarks:
            hands.get_pinch_pos()

        if hands.is_pinched_inside(play_button):
            is_in_menu = False
            go_to_play = True
        if hands.is_pinched_inside(htp_button):
            is_in_menu = False
            go_to_how_to_play = True
        if hands.is_pinched_inside(quit_button):
            is_in_menu = False
            has_to_quit = True

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
        destroy_all_windows(cam.camera)
        how_to_play()
    if go_to_play:
        destroy_all_windows(cam.camera)
        launch_game()


def main():
    menu()


if __name__ == '__main__':
    main()
