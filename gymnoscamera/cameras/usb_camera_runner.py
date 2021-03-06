import cv2
import time
import logging
import numpy as np

from gymnoscamera.cameras.camera import Camera

iou_threshold = 0.01
time_threshold = 2  # how many seconds until machine is sure you are in or out


class UsbCameraRunner(Camera):
    """
    An implementation of a Camera runner which sources its camera from a USB camera
    """
    def __init__(self, model_type: str, model_path: str):
        super().__init__(model_type, model_path)

        # initialize the camera
        self.camera = cv2.VideoCapture(0)
        time.sleep(0.1)  # allow the camera to warm up

    def get_frame(self):
        """
        Retrieves a frames from the camera and returns it
        """
        ret, image = self.camera.read()
        try:
            image = cv2.resize(image, (self.camera_height, self.camera_width))
        except cv2.error as e:
            image = np.zeros([self.camera_height, self.camera_width, 3])
            logging.info("Error getting frame: " + e)
            time.sleep(0.5)
            # connect to the stream
            self.camera = cv2.VideoCapture(0)

        return image, time.time()
