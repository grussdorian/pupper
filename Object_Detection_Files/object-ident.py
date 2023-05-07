import cv2

classNames = []
classFile = "./coco.names"
with open(classFile, "rt") as f:
    classNames = f.read().rstrip("\n").split("\n")

configPath = "./ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
weightsPath = "./frozen_inference_graph.pb"

net = cv2.dnn_DetectionModel(weightsPath, configPath)
net.setInputSize(320, 320)
net.setInputScale(1.0 / 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

frame_height = 640
frame_width = 480


def getObjects(n_objects, img, thres, nms, draw=True, objects=['person']):
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
                    center_x = x1 + (width // 2)
                    center_y = y1 + (height // 2)
                    cv2.arrowedLine(img, (center_x, center_y), (frame_height//2, frame_width//2), (0, 255, 0),
                                    thickness=2, tipLength=0.5)
                    cv2.rectangle(img, box, color=(0, 255, 255), thickness=2)
                    # cv2.circle(img, (center_x, center_y), radius=5,
                    #            color=(0, 0, 255), thickness=-1)
                    cv2.putText(img, classNames[classId-1].upper(), (box[0]+10, box[1]+30),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                    cv2.putText(img, str(round(confidence*100, 2)), (box[0]+200, box[1]+30),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                    # print(n_objects)

    return img, objectInfo


if __name__ == "__main__":
    thresh = 0.7  # Threshold to detect object
    nms = 0.8
    cap = cv2.VideoCapture(0)
    # simulate delay, change fps
    fps = 120
    delay_time = int(1000/fps)
    # cap = cv2.VideoCapture('/Users/hardik/Downloads/cv-demo-test.mp4')
    frame_height = 640
    frame_width = 480
    cap.set(3, 640)
    cap.set(4, 480)
    # cap.set(10,70)

    while True:
        n_objects = 1
        success, img = cap.read()
        result, objectInfo = getObjects(n_objects, img, thresh, nms)
        # print(objectInfo)
        # print(result)
        cv2.imshow("Output", img)
        cv2.waitKey(delay_time)
