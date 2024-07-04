from hand_tracking_lib.cv2_utils import *


def main():
    debug = False
    # Initialize the camera
    camera = Camera()

    is_running = True
    detector = HandDetector()

    while is_running:
        img = camera.get_rgb_img()
        hand = Hands(detector, img)
        hand.pinch_length = 190
        hand.get_pinch_pos()

        if debug:
            cv2.imshow('Game DEBUG', img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            is_running = False

    camera.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
