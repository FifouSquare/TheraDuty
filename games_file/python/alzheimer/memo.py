import cv2
import mediapipe as mp
import numpy as np
import requests


def overlay_image_alpha(img, img_overlay, x, y, alpha_mask):
    """Overlay `img_overlay` onto `img` at (x, y) and blend using `alpha_mask`.

    Args:
        img (np.ndarray): Background image.
        img_overlay (np.ndarray): Image to overlay.
        x (int): X position to place the top-left corner of `img_overlay` on `img`.
        y (int): Y position to place the top-left corner of `img_overlay` on `img`.
        alpha_mask (np.ndarray): Alpha mask of `img_overlay`.

    Returns:
        np.ndarray: Resulting image with overlay.
    """
    # Image ranges
    y1, y2 = y, y + img_overlay.shape[0]
    x1, x2 = x, x + img_overlay.shape[1]

    # Check if the overlay is out of bounds of the background image
    if y1 < 0 or y2 > img.shape[0] or x1 < 0 or x2 > img.shape[1]:
        print("Error: Overlay image is out of bounds.")
        return img

    # Blend overlay within the determined ranges
    alpha = alpha_mask / 255.0
    for c in range(0, 3):
        img[y1:y2, x1:x2, c] = ((1. - alpha) * img[y1:y2, x1:x2, c]
                                + alpha * img_overlay[:, :, c])

    return img


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


def get_coords(server_url="http://127.0.0.1:8080"):
    var = requests.get(server_url)
    data = var.json()
    if data:
        return data["x"], data["y"], data["pinch"]


def get_rgb_img(camera):
    _, frame = camera.read()
    frame = cv2.flip(frame, 1)
    return frame


def destroy_all_windows(cam):
    cam.release()
    cv2.destroyAllWindows()


def game():
    pass


def draw_menu(img, play_button_pos, tuto_button_pos, quit_button_pos,
              button_size):
    play_button = cv2.imread("./play_button.png", cv2.IMREAD_UNCHANGED)
    tuto_button = cv2.imread("./tuto_button.png", cv2.IMREAD_UNCHANGED)
    quit_button = cv2.imread("./quit_button.png", cv2.IMREAD_UNCHANGED)

    # Resize buttons if needed

    play_button_rgb = cv2.resize(play_button[:, :, :3], button_size)
    play_button_alpha = cv2.resize(play_button[:, :, 3], button_size)

    tuto_button_rgb = cv2.resize(tuto_button[:, :, :3], button_size)
    tuto_button_alpha = cv2.resize(tuto_button[:, :, 3], button_size)

    quit_button_rgb = cv2.resize(quit_button[:, :, :3], button_size)
    quit_button_alpha = cv2.resize(quit_button[:, :, 3], button_size)

    # Button positions

    img = overlay_image_alpha(img, play_button_rgb,
                              x=play_button_pos[0],
                              y=play_button_pos[1],
                              alpha_mask=play_button_alpha)
    img = overlay_image_alpha(img, tuto_button_rgb,
                              x=tuto_button_pos[0],
                              y=tuto_button_pos[1],
                              alpha_mask=tuto_button_alpha)
    img = overlay_image_alpha(img, quit_button_rgb,
                              x=quit_button_pos[0],
                              y=quit_button_pos[1],
                              alpha_mask=quit_button_alpha)


def menu():
    cursor = "./cursor.png"
    cursor_pinched = "./cursor_pinched.png"

    is_in_menu = True
    has_to_quit = False
    go_to_play = False
    go_to_how_to_play = False

    cam = cv2.VideoCapture(0)
    img = get_rgb_img(cam)
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
    button_size = (320, 80)
    play_button_pos = (img.shape[1] // 2 - button_size[0] // 2,
                       img.shape[0] // 2 - 200)
    tuto_button_pos = (img.shape[1] // 2 - button_size[0] // 2,
                       img.shape[0] // 2 - 50)
    quit_button_pos = (img.shape[1] // 2 - button_size[0] // 2,
                       img.shape[0] // 2 + 100)
    overlay_img = cv2.imread(cursor, cv2.IMREAD_UNCHANGED)
    while is_in_menu:
        img = get_rgb_img(cam)
        # hands = Hands(results, img)
        #
        if overlay_img.shape[2] == 4:
            overlay_img_rgb = overlay_img[:, :, :3]
            overlay_alpha = overlay_img[:, :, 3]
        else:
            overlay_img_rgb = overlay_img
            overlay_alpha = np.ones(
                (overlay_img.shape[0], overlay_img.shape[1]),
                dtype=overlay_img.dtype) * 255
        cursor_size = 100
        overlay_img_rgb = cv2.resize(overlay_img_rgb,
                                     (cursor_size,
                                      cursor_size))
        overlay_alpha = cv2.resize(overlay_alpha,
                                   (cursor_size,
                                    cursor_size))
        background.draw(img)
        coord = get_coords()
        draw_menu(img, play_button_pos, tuto_button_pos, quit_button_pos,
                  button_size)
        if coord:
            x = coord[0]
            y = coord[1]
            if coord[2]:
                overlay_img = cv2.imread(cursor_pinched, cv2.IMREAD_UNCHANGED)
                if play_button_pos[0] < x < play_button_pos[0] + button_size[
                    0] and play_button_pos[1] < y < play_button_pos[1] + \
                        button_size[1]:
                    is_in_menu = False
                    go_to_play = True
                if tuto_button_pos[0] < x < tuto_button_pos[0] + button_size[
                    0] and tuto_button_pos[1] < y < tuto_button_pos[1] + \
                        button_size[1]:
                    is_in_menu = False
                    go_to_how_to_play = True
                if quit_button_pos[0] < x < quit_button_pos[0] + button_size[
                    0] and quit_button_pos[1] < y < quit_button_pos[1] + \
                        button_size[1]:
                    is_in_menu = False
                    has_to_quit = True
            else:
                overlay_img = cv2.imread(cursor, cv2.IMREAD_UNCHANGED)
            img = overlay_image_alpha(img, overlay_img_rgb, x=x,
                                      y=y,
                                      alpha_mask=overlay_alpha)

        cv2.imshow("Menu", img)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            is_in_menu = False
        if cv2.waitKey(1) & 0xFF == ord('q'):
            is_in_menu = False
            has_to_quit = True

    if has_to_quit:
        destroy_all_windows(cam)
        return
    if go_to_how_to_play:
        destroy_all_windows(cam)
        how_to_play()
    if go_to_play:
        destroy_all_windows(cam)
        game()


def win():
    is_running = True
    has_to_replay = True

    mp_hands = mp.solutions.hands
    hands_detector = mp_hands.Hands(max_num_hands=1,
                                    min_detection_confidence=0.7,
                                    min_tracking_confidence=0.7)

    cam = cv2.VideoCapture(0)
    img = get_rgb_img(cam)
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
        img = get_rgb_img(cam)
        results = hands_detector.process(img)
        # hands = Hands(results, img)

        background.draw(img)
        cv2.putText(img, "Victoire !", (img.shape[1] // 2 - 100, 100),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 3)
        replay.draw(img)
        quit_button.draw(img)

        # if hands.landmarks:
        #     hands.get_pinch_pos()
        #
        # if hands.is_pinched_inside(quit_button):
        #     is_running = False
        #     has_to_replay = False
        # if hands.is_pinched_inside(replay):
        #     is_running = False
        #     has_to_replay = True

        cv2.imshow("Win", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            is_running = False
            has_to_replay = False

    destroy_all_windows(cam)
    if has_to_replay:
        game()


def how_to_play():
    is_in_how_to_play = True
    mp_hands = mp.solutions.hands
    hands_detector = mp_hands.Hands(max_num_hands=1,
                                    min_detection_confidence=0.7,
                                    min_tracking_confidence=0.7)
    cam = cv2.VideoCapture(0)
    img = get_rgb_img(cam)
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
        img = get_rgb_img(cam)
        results = hands_detector.process(img)
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


def main():
    menu()


if __name__ == "__main__":
    main()
