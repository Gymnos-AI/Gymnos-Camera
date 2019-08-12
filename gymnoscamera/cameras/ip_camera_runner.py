import cv2
import time
from threading import Thread, Lock

from gymnoscamera.cameras.camera import Camera


mutex = Lock()


class IpCameraRunner(Camera):
    """
    An implementation of a Camera runner which sources its camera from a USB camera
    """
    def __init__(self, db, model_path: str):
        super().__init__(db, model_path)

        # initialize the camera
        self.camera = cv2.VideoCapture('rtsp://admin:MZEJUT@192.168.1.90:554/h264_stream')
        self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        time.sleep(0.5)
        self.point = 0

        worker = Thread(target=self.update_stream, args=())
        worker.setDaemon(True)
        worker.start()

    def update_stream(self):
        while True:
            mutex.acquire()
            self.camera.read()
            mutex.release()

    def get_frame(self):
        """
        Retrieves a frames from the camera and returns it
        """
        mutex.acquire()
        ret, image = self.camera.read()
        frame_time = time.time()
        mutex.release()

        image = cv2.resize(image, (self.camera_height, self.camera_width))

        return image, frame_time
