# import cv2
# from cvzone.PoseModule import PoseDetector
#
# # Constants
# detector = PoseDetector()
# cap = cv2.VideoCapture(0)
#
# while True:
#     success, img = cap.read()
#     img = detector.findPose(img)
#     lmList, bboxInfo = detector.findPosition(img, bboxWithHands=True)
#     if bboxInfo:
#         center = bboxInfo["center"]
#         cv2.circle(img, center, 5, (255, 0, 255), cv2.FILLED)
#
#     cv2.imshow("Body", img)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#
# cap.release()
# cv2.destroyAllWindows()

from cvzone.PoseModule import PoseDetector
import cv2

# Initialize the webcam to the default camera (index 0)
cap = cv2.VideoCapture(0)

# Initialize the PoseDetector class. Here, we're using default parameters. For a deep dive into what each parameter signifies, consider checking the documentation.
detector = PoseDetector(staticMode=False,
                        modelComplexity=1,
                        smoothLandmarks=True,
                        enableSegmentation=False,
                        smoothSegmentation=True,
                        detectionCon=0.5,
                        trackCon=0.5)

x, y = 100, 100
leg_is_open = True

# Loop to continuously get frames from the webcam
while True:
    # Capture each frame from the webcam
    success, r_img = cap.read()
    img = cv2.flip(r_img, 1)

    # Detect human pose in the frame
    img = detector.findPose(img)

    # Extract body landmarks and possibly a bounding box
    # Set draw=True to visualize landmarks and bounding box on the image
    lmList, bboxInfo = detector.findPosition(img, draw=True, bboxWithHands=False)

    # If body landmarks are detected
    if lmList:
        # Extract the center of the bounding box around the detected pose
        center = bboxInfo["center"]

        # Visualize the center of the bounding box
        cv2.circle(img, center, 5, (255, 0, 255), cv2.FILLED)

        # Calculate the distance between landmarks 11 and 15 and visualize it
        length, img, info = detector.findDistance(lmList[24][0:2],
                                                  lmList[26][0:2],
                                                  img=img,
                                                  color=(255, 0, 0),
                                                  scale=10)

        # Display the distance value on the image
        cv2.putText(img, str(int(length)), (info[0], info[1]), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)
        if length < 50 and leg_is_open:
            y += 10
            leg_is_open = False
            cv2.putText(img, "Close", (info[0], info[1] + 30), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)

        elif length > 100 and not leg_is_open:
            leg_is_open = True
            y += 10

        # Display the rectangle around the detected pose
        cv2.rectangle(img, (x, y), (x + 100, y + 100), (255, 0, 255), -1)

    # Display the processed frame
    cv2.imshow("Image", img)

    # Introduce a brief pause of 1 millisecond between frames
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
