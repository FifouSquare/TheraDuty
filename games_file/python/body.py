# # import cv2
# # from cvzone.PoseModule import PoseDetector
# #
# # # Constants
# # detector = PoseDetector()
# # cap = cv2.VideoCapture(0)
# #
# # while True:
# #     success, img = cap.read()
# #     img = detector.findPose(img)
# #     lmList, bboxInfo = detector.findPosition(img, bboxWithHands=True)
# #     if bboxInfo:
# #         center = bboxInfo["center"]
# #         cv2.circle(img, center, 5, (255, 0, 255), cv2.FILLED)
# #
# #     cv2.imshow("Body", img)
# #     if cv2.waitKey(1) & 0xFF == ord('q'):
# #         break
# #
# # cap.release()
# # cv2.destroyAllWindows()
#
# from cvzone.PoseModule import PoseDetector
# import cv2
#
#
# def draw_lines(img, lms):
#     cv2.line(img, lms[28][0:2], lms[26][0:2], (0, 255, 0), 3)
#     cv2.line(img, lms[26][0:2], lms[24][0:2], (0, 255, 0), 3)
#     cv2.line(img, lms[24][0:2], lms[12][0:2], (0, 255, 0), 3)
#     cv2.line(img, lms[12][0:2], lms[14][0:2], (0, 255, 0), 3)
#     cv2.line(img, lms[14][0:2], lms[16][0:2], (0, 255, 0), 3)
#     cv2.line(img, lms[16][0:2], lms[20][0:2], (0, 255, 0), 3)
#     cv2.line(img, lms[12][0:2], lms[8][0:2], (0, 255, 0), 3)
#     cv2.line(img, lms[8][0:2], lms[6][0:2], (0, 255, 0), 3)
#     cv2.line(img, lms[6][0:2], lms[4][0:2], (0, 255, 0), 3)
#     cv2.line(img, lms[4][0:2], lms[1][0:2], (0, 255, 0), 3)
#     cv2.line(img, lms[1][0:2], lms[3][0:2], (0, 255, 0), 3)
#     cv2.line(img, lms[3][0:2], lms[7][0:2], (0, 255, 0), 3)
#     cv2.line(img, lms[7][0:2], lms[11][0:2], (0, 255, 0), 3)
#     cv2.line(img, lms[11][0:2], lms[13][0:2], (0, 255, 0), 3)
#     cv2.line(img, lms[13][0:2], lms[15][0:2], (0, 255, 0), 3)
#     cv2.line(img, lms[15][0:2], lms[17][0:2], (0, 255, 0), 3)
#     cv2.line(img, lms[11][0:2], lms[23][0:2], (0, 255, 0), 3)
#     cv2.line(img, lms[23][0:2], lms[25][0:2], (0, 255, 0), 3)
#     cv2.line(img, lms[25][0:2], lms[27][0:2], (0, 255, 0), 3)
#
#
# # Initialize the webcam to the default camera (index 0)
# cap = cv2.VideoCapture(0)
#
# # Initialize the PoseDetector class. Here, we're using default parameters.
# # For a deep dive into what each parameter signifies, consider checking the
# # documentation.
# detector = PoseDetector(staticMode=False,
#                         modelComplexity=1,
#                         smoothLandmarks=True,
#                         enableSegmentation=False,
#                         smoothSegmentation=True,
#                         detectionCon=0.5,
#                         trackCon=0.5)
#
# x, y = 100, 100
# leg_is_open = True
# s_cap = cv2.VideoCapture(0)
#
# # Loop to continuously get frames from the webcam
# while True:
#     # Capture each frame from the webcam
#     success, r_img = cap.read()
#     d_img = cv2.flip(r_img, 1)
#     s, r_s = s_cap.read()
#     s_img = cv2.flip(r_s, 1)
#
#     # Detect human pose in the frame
#     s_img = detector.findPose(s_img, draw=False)
#
#     # Extract body landmarks and possibly a bounding box
#     # Set draw=True to visualize landmarks and bounding box on the image
#     lmList, bboxInfo = detector.findPosition(s_img, draw=False)
#     cv2.rectangle(d_img, (0, 0), (d_img.shape[1], d_img.shape[0]), (0, 0, 0),
#                   -1)
#     # If body landmarks are detected
#     if lmList:
#         # Extract the center of the bounding box around the detected pose
#         center = bboxInfo["center"]
#         draw_lines(d_img, lmList)
#
#         # Visualize the center of the bounding box
#         # cv2.circle(s_img, center, 5, (255, 0, 255), cv2.FILLED)
#
#         # Calculate the distance between landmarks 11 and 15 and visualize it
#         # length, img, info = detector.findDistance(lmList[24][0:2],
#         #                                           lmList[26][0:2],
#         #                                           img=s_img,
#         #                                           color=(255, 0, 0),
#         #                                           scale=10)
#         #
#         # # Display the distance value on the image
#         # cv2.putText(s_img, str(int(length)), (info[0], info[1]),
#         #             cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)
#         # if length < 50 and leg_is_open:
#         #     y += 10
#         #     leg_is_open = False
#         #     cv2.putText(s_img, "Close", (info[0], info[1] + 30),
#         #                 cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)
#         #
#         # elif length > 100 and not leg_is_open:
#         #     leg_is_open = True
#         #     y += 10
#
#         # Display the rectangle around the detected pose
#         cv2.rectangle(d_img, (x, y), (x + 100, y + 100), (255, 0, 255), -1)
#
#     # Display the processed frame
#     cv2.imshow("Image", d_img)
#
#     # Introduce a brief pause of 1 millisecond between frames
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#
# cap.release()
# cv2.destroyAllWindows()
