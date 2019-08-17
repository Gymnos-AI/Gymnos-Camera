# Continuously capture frames and perform object detection on them
import cv2
import numpy as np
from timeit import default_timer as timer


class Predictors:
    def __init__(self, model_type, model_path: str):
        print("This: "+ str(model_type))
        if model_type == 'HOG':
            print("Using CV2 Hog Detector")
            self.model = cv2.HOGDescriptor()
            self.model.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        elif model_type == "YOLOV3":
            print("Using Yolo V3")
            import gymnoscamera.yolo_network.yolo_v3 as yolo
            self.model = yolo.YOLO(model_path=model_path)
        elif model_type == "YOLOV3RT":
            print("Using Yolo V3 RT")
            import gymnoscamera.yolo_network_rt.yolo_v3_rt as yolort
            self.model = yolort.Yolo_v3_rt()

    def hog_detector(self, to_predict):
        """
        Takes in a frame, runs it through the HOG Detector  and returns the results

        :param to_predict: The frame passed into the model
        :return: frame after it is processed
        """
        start = timer()
        (rects, weights) = self.model.detectMultiScale(to_predict, winStride=(4, 4), padding=(8, 8), scale=1.05)
        for (x, y, w, h) in rects:
            cv2.rectangle(to_predict, (x, y), (x + w, y + h), (0, 0, 255), 2)
        end = timer()
        print(end - start)

        return to_predict

    def yolo_v3_detector(self, to_predict):
        """
        Before you run the YOLO Detector, download the models from:
        https://drive.google.com/drive/folders/1fibgr4c2CUMItWOngjTxwhqSzsHXBXvT
        and place it in a location that you will provide as an argument to run_camera.py

        :param to_predict: The frame we would like to run prediction on
        :return:
        """
        return np.asarray(self.model.detect_image(to_predict))

    def yolo_v3_rt(self, to_predict):
        """

        :param to_predict:
        :return:
        """
        return np.asarray(self.model.detect_image(to_predict))