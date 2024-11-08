import time

import cv2
import mediapipe as mp
import requests


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
        _, frame = self.camera.read()
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


class HandDetector:
    def __init__(self, static_image_mode=False, max_num_hands=2,
                 min_detection_confidence=0.5, min_tracking_confidence=0.5):
        self.mp_hands = mp.solutions.hands
        self.hands_detector = self.mp_hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence)

    def find_hands(self, img, draw=False):
        results = self.hands_detector.process(img)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                if draw:
                    mp.solutions.drawing_utils.draw_landmarks(img,
                                                              hand_landmarks,
                                                              self.mp_hands.HAND_CONNECTIONS)
        return results

    def get_landmarks(self, img, draw=False):
        results = self.find_hands(img, draw)
        return results.multi_hand_landmarks


class Hands:
    def __init__(self, detector: HandDetector, img):
        self.landmarks = detector.get_landmarks(img)
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

    def get_pinch_pos(self, send_data=True, server_url="http://127.0.0.1:8080",
                      data=None):
        tx, ty = 0, 0
        cx, cy = 0, 0
        if self.landmarks:
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
                            print(
                                f"DEBUG | {time.time()} | x: {cx}, y: {cy}")
                            print(
                                f"pinch: {self.is_pinching}, length: {length}")
                        elif length > self.pinch_length_open and self.is_pinching:
                            self.is_pinching = False
                if send_data:
                    if data is None:
                        data = {'x': cx, 'y': cy, 'pinch': self.is_pinching}
                    print("DATA:", data)
                    try:
                        requests.post(server_url, json=data)
                    except requests.exceptions.RequestException as e:
                        print(e)

    def get_grab_pos(self, send_data=True, server_url="http://127.0.0.1:8080",
                     data=None):
        tx, ty = 0, 0
        cx, cy = 0, 0
        if self.landmarks:
            for hand_landmarks in self.landmarks:
                self.draw()
                for i, lm in enumerate(hand_landmarks.landmark):
                    h, w, c = self.img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    if i == 0:
                        tx, ty = cx, cy

                    if i == 12:
                        length = ((cx - tx) ** 2 + (cy - ty) ** 2) ** 0.5
                        if length < self.pinch_length and not self.is_pinching:
                            self.is_pinching = True
                            self.pinch_pos = (cx, cy)
                        elif length > self.pinch_length_open and self.is_pinching:
                            self.is_pinching = False
                if send_data:
                    if data is None:
                        data = {'x': cx, 'y': cy, 'pinch': self.is_pinching}
                    print("DATA:", data)
                    try:
                        requests.post(server_url, json=data)
                    except requests.exceptions.RequestException as e:
                        print(e)

    def is_pinched_inside(self, r):
        x, y = self.pinch_pos
        if r.x < x < r.x + r.width and r.y < y < r.y + r.height:
            return True
        return False

    def get_all_positions(self):
        pass

    def get_center(self):
        cx, cy = 0, 0
        for hand_landmarks in self.landmarks:
            for i, lm in enumerate(hand_landmarks.landmark):
                h, w, c = self.img.shape
                cx += int(lm.x * w)
                cy += int(lm.y * h)
        return cx // 21, cy // 21

    def get_top_left(self):
        top_left = (0, 0)
        for hand_landmarks in self.landmarks:
            for i, lm in enumerate(hand_landmarks.landmark):
                h, w, c = self.img.shape
                top_left = (int(lm.x * w), int(lm.y * h))
        return top_left
