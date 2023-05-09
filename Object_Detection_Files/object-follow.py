from Object_Detection_Files.object_ident import getObjects
import cv2 

frame_height = 720
frame_width = 1280
frame_center = (frame_width//2, frame_height//2)


def detection_loop():
    thresh = 0.7  # Threshold to detect object
    nms = 0.8
    cap = cv2.VideoCapture(0)
    # simulate delay, change fps
    fps = 1000
    delay_time = int(1000/fps)

    cap.set(3, frame_height)
    cap.set(4, frame_width)
    # cap.set(10,70)

    while True:
        n_objects = 1
        success, img = cap.read()
        result, objectInfo = getObjects(n_objects, img, thresh, nms, draw=False)
        ## Check iff one objected is detected. If number of objects detected != 1 then continue in the loop
        if len(objectInfo) != 2:
            continue
        # print(objectInfo[1])
        # print(result)
        object_center = objectInfo[-1]
        print(type(object_center[0]), type(object_center[1]))

        ## Vector v denotes the magnitude and direction of Yaw control
        v = (object_center, (frame_center[0], object_center[1]))
        v_mod = frame_center[0] - object_center[0]

        # Only try to draw stuff that are well defined otherwise opencv will crash
        if v_mod < 0:
            print(f"direction is left to right, magnitude is {v_mod}")
        if v_mod > 0:
            print(f"direction is right to left, magnitude is {v_mod}")
        
        cv2.arrowedLine(img, object_center, (frame_center[0], object_center[1]), (255, 0, 0),
                                    thickness=2, tipLength=0.5)
        

        cv2.imshow("Output", img)
        cv2.waitKey(delay_time)

if __name__ == "__main__":
    detection_loop()