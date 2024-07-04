import cv2
import mediapipe as mp
import numpy as np
import requests

from games_file.python.alzheimer.cv2_utils import Hands, Camera

lower_color = np.array([35, 100, 100])
upper_color = np.array([85, 255, 255])

cap = Camera()
server_url = "http://127.0.0.1:8080"

mp_hands = mp.solutions.hands
hands_detector = mp_hands.Hands(max_num_hands=2,
                                min_detection_confidence=0.7,
                                min_tracking_confidence=0.7)

while True:
    img = cap.get_rgb_img()

    results = hands_detector.process(img)
    hands = Hands(results, img)
    hands.pinch_length = 190
    if hands.landmarks:
        hands.get_grab_pos()
        cx, cy = hands.get_center()
        for hand_landmarks in results.multi_hand_landmarks:
            if results.multi_handedness:
                for idx, classification in enumerate(results.multi_handedness):
                    if classification.classification[0].label == "Right":
                        handedness = "Right Hand"
                        data = {'x': cx, 'y': cy,
                                'hand': handedness.split(" ")[0],
                                'pinch': hands.is_pinching}
                        print(data)
                        try:
                            requests.post(server_url, json=data)
                            data = ""
                        except requests.exceptions.RequestException as e:
                            print(e)
                    elif classification.classification[0].label == "Left":
                        handedness = "Left Hand"
                        data = {'x': cx, 'y': cy,
                                'hand': handedness.split(" ")[0],
                                'pinch': hands.is_pinching}
                        print(data)
                        try:
                            requests.post(server_url, json=data)
                        except requests.exceptions.RequestException as e:
                            print(e)
                    mp.solutions.drawing_utils.draw_landmarks(img,
                                                              hand_landmarks,
                                                              mp_hands.HAND_CONNECTIONS)

    # cv2.imshow('Frame', img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.close()
cv2.destroyAllWindows()
