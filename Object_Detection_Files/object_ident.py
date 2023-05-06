import cv2
import platform
# x dimension corresponds to height and y dimension corresponds to width, just like 2D array


classNames = []

# Change path based on OS and directory

if platform.system() == "Windows":
    classFile = "C:\\Users\\hardik\\pupper-master-github\\pupper\\Object_Detection_Files\\coco.names"
    configPath = "C:\\Users\\hardik\\pupper-master-github\\pupper\\Object_Detection_Files\\ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
    weightsPath = "C:\\Users\\hardik\\pupper-master-github\\pupper\\Object_Detection_Files\\frozen_inference_graph.pb"
else:
    classFile = "./coco.names"
    configPath = "./ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
    weightsPath = "./frozen_inference_graph.pb"

with open(classFile, "rt") as f:
    classNames = f.read().rstrip("\n").split("\n")


net = cv2.dnn_DetectionModel(weightsPath, configPath)
net.setInputSize(320, 320)
net.setInputScale(1.0 / 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)


def getObjects(n_objects, img, thres, nms, draw=True, objects=[], frame_height=320, frame_width=320):
    # print(frame_width, frame_height)
    if frame_width < frame_height:
        frame_center = (frame_height//2, frame_width//2)
    elif frame_width > frame_height:
        frame_center = (frame_width//2, frame_height//2)
    else:
        frame_center = (frame_width//2, frame_width//2)

    classIds, confs, bbox = net.detect(
        img, confThreshold=thres, nmsThreshold=nms)
    # print(classIds,bbox)
    if len(objects) == 0:
        objects = classNames
    objectInfo = []
    if len(classIds) != 0:
        for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
            className = classNames[classId - 1]
            if className in objects:
                objectInfo.append([box, className])
                if (draw and n_objects > 0):
                    x1, y1, height, width = box[0], box[1], box[2], box[3]
                    n_objects -= 1
                    center_x = x1 + (height // 2)
                    center_y = y1 + (width // 2)
                    object_center = (center_x, center_y)
                    cv2.arrowedLine(img, object_center, frame_center, (0, 255, 0),
                                    thickness=2, tipLength=0.5)
                    cv2.arrowedLine(img, object_center, (frame_center[0], object_center[1]), (255, 0, 0),
                                    thickness=2, tipLength=0.5)
                    cv2.rectangle(img, box, color=(0, 255, 255), thickness=2)

                    # cv2.circle(img, frame_center, radius=5,
                    #            color=(0, 0, 255), thickness=-1)
                    cv2.circle(img, object_center, radius=5,
                               color=(255, 255, 255), thickness=-1)
                    cv2.circle(img, frame_center, radius=5,
                               color=(255, 255, 255), thickness=-1)
                    # cv2.circle(img, (x1+height//2,y1+width//2), radius=5,
                    #            color=(0, 255, 255), thickness=-1)

                    cv2.putText(img, classNames[classId-1].upper(), (box[0]+10, box[1]+30),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(img, str(round(confidence*100, 2)), (box[0]+200, box[1]+30),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                    # print(n_objects)
                elif (n_objects > 0):
                    x1, y1, height, width = box[0], box[1], box[2], box[3]
                    n_objects -= 1
                    center_x = x1 + (height // 2)
                    center_y = y1 + (width // 2)
                    A = height*width
                    object_data = ((center_x, center_y), A, box)
                    objectInfo.append(object_data)
    return img, objectInfo


if __name__ == "__main__":
    import sys
    frame_h = 0
    frame_w = 0
    try:
        frame_w = int(sys.argv[1])
        frame_h = int(sys.argv[2])
    except:
        print("default frame height is 480 and width is 640")
        frame_h = 480
        frame_w = 640
    # frame_height = 720
    # frame_width = 1280
    thresh = 0.7  # Threshold to detect object
    nms = 0.8
    # For the pi's camera, camera id is 2
    cap = cv2.VideoCapture(2)
    # simulate delay, change fps
    fps = 120
    delay_time = int(1000/fps)
    # cap = cv2.VideoCapture('/Users/hardik/Downloads/cv-demo-test.mp4')

    cap.set(3, frame_h)
    cap.set(4, frame_w)
    # cap.set(10,70)

    while True:
        n_objects = 1
        success, img = cap.read()
        result, objectInfo = getObjects(
            n_objects, img, thresh, nms, frame_height=frame_h, frame_width=frame_w)
        # print(objectInfo)
        # print(result)
        cv2.imshow("Output", img)
        cv2.waitKey(delay_time)
