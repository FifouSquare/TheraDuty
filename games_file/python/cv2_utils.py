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
                                  shadow_color):
    shadow_top_left = (
        top_left[0] + shadow_offset, top_left[1] + shadow_offset)
    shadow_bottom_right = (
        bottom_right[0] + shadow_offset, bottom_right[1] + shadow_offset)

    # Draw the shadow
    draw_filled_rounded_rectangle(img, shadow_top_left, shadow_bottom_right,
                                  shadow_color, radius)

    # Draw the main filled rounded rectangle on top of the shadow
    draw_filled_rounded_rectangle(img, top_left, bottom_right, color, radius)


class Camera:
    def __init__(self):
        self.camera = cv2.VideoCapture(0)
        self.resolution = (640, 480)
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
    def __init__(self, x, y, width, height, color=(255, 255, 255),
                 thickness=-1,
                 text="",
                 corner_radius=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.thickness = thickness
        self.text = text
        self.corner_radius = corner_radius

    def draw(self, img):
        if self.thickness == -1:
            draw_rounded_shadow_rectangle(img, (self.x, self.y),
                                          (self.x + self.width,
                                           self.y + self.height),
                                          self.color, self.corner_radius, 5,
                                          (96, 96, 96))
        else:
            draw_rounded_rectangle(img, (self.x, self.y),
                                   (self.x + self.width, self.y + self.height),
                                   radius=self.corner_radius, color=self.color,
                                   thickness=self.thickness)
        if self.text != "":
            cv2.putText(img, self.text,
                        (
                            self.x + self.width // 2 - len(self.text) * 10,
                            self.y + self.height // 2),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 3)


class Hands:
    def __init__(self, result, img):
        self.landmarks = result.multi_hand_landmarks
        self.is_pinching = False
        self.img = img
        self.pinch_pos = (0, 0)
        self.pinch_length = 50
        self.pinch_length_open = 100

    def get_pinch_pos(self):
        tx, ty = 0, 0
        utils = mp.solutions.drawing_utils
        for hand_landmarks in self.landmarks:
            utils.draw_landmarks(self.img, hand_landmarks,
                                 mp.solutions.hands.HAND_CONNECTIONS)
            for i, lm in enumerate(hand_landmarks.landmark):
                h, w, c = self.img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                if i == 4:
                    tx, ty = cx, cy

                if i == 8:
                    length = ((cx - tx) ** 2 + (cy - ty) ** 2) ** 0.5
                    if length < self.pinch_length and not self.is_pinching:
                        print("Pinched")
                        print(cx, cy)
                        self.is_pinching = True
                        self.pinch_pos = (cx, cy)
                        return cx, cy
                    elif length > self.pinch_length_open and self.is_pinching:
                        self.is_pinching = False

    def is_pinched_inside(self, rect):
        x, y = self.pinch_pos
        if rect.x < x < rect.x + rect.width and rect.y < y < rect.y + rect.height:
            return True
        return False
