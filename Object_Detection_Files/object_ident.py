import cv2
import os
# os.system("chdir \\\\Mac\\Home\\Desktop\\pupper-master-github\\pupper")
# x dimension corresponds to height and y dimension corresponds to width, just like 2D array


classNames = []

# Change path based on OS and directory
classFile = "C:\\Users\\hardik\\pupper-master-github\\pupper\\Object_Detection_Files\\coco.names"
configPath = "C:\\Users\\hardik\\pupper-master-github\\pupper\\Object_Detection_Files\\ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
weightsPath = "C:\\Users\\hardik\\pupper-master-github\\pupper\\Object_Detection_Files\\frozen_inference_graph.pb"

with open(classFile, "rt") as f:
    classNames = f.read().rstrip("\n").split("\n")


net = cv2.dnn_DetectionModel(weightsPath, configPath)
net.setInputSize(320, 320)
net.setInputScale(1.0 / 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)


def getObjects(n_objects, img, thres, nms,  frame_height, frame_width, draw=True, objects=['person']):
    frame_center = (frame_width//2, frame_height//2)
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
                    object_center = (center_x,center_y)
                    cv2.arrowedLine(img, object_center, frame_center, (0, 255, 0),
                                    thickness=2, tipLength=0.5)
                    cv2.arrowedLine(img, object_center, (frame_center[0], object_center[1]), (255, 0, 0),
                                    thickness=2, tipLength=0.5)
                    cv2.rectangle(img, box, color=(0, 255, 255), thickness=2)

                    # cv2.circle(img, frame_center, radius=5,
                    #            color=(0, 0, 255), thickness=-1)
                    cv2.circle(img, object_center, radius=5,
                               color=(255, 255, 255), thickness=-1)
                    # cv2.circle(img, (x1+height//2,y1+width//2), radius=5,
                    #            color=(0, 255, 255), thickness=-1)

                    cv2.putText(img, classNames[classId-1].upper(), (box[0]+10, box[1]+30),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(img, str(round(confidence*100, 2)), (box[0]+200, box[1]+30),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                    # print(n_objects)
                elif (n_objects>0):
                    x1, y1, height, width = box[0], box[1], box[2], box[3]
                    n_objects -= 1
                    center_x = x1 + (height // 2)
                    center_y = y1 + (width // 2)
                    object_center = (center_x,center_y)
                    area = height*width
                    objectInfo.append(area)
                    objectInfo.append(object_center)
    return img, objectInfo


if __name__ == "__main__":
    frame_height = 720
    frame_width = 1280
    thresh = 0.7  # Threshold to detect object
    nms = 0.8
    cap = cv2.VideoCapture(0)
    # simulate delay, change fps
    fps = 120
    delay_time = int(1000/fps)
    # cap = cv2.VideoCapture('/Users/hardik/Downloads/cv-demo-test.mp4')

    cap.set(3, frame_height)
    cap.set(4, frame_width)
    # cap.set(10,70)

    while True:
        n_objects = 1
        success, img = cap.read()
        result, objectInfo = getObjects(n_objects, img, thresh, nms, frame_height, frame_width)
        # print(objectInfo)
        # print(result)
        cv2.imshow("Output", img)
        cv2.waitKey(delay_time)
