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

        user = 'admin'
        password = 'MZEJUT'
        ip_address = '192.168.1.90'
        port = '554'
        stream = 'h264_stream'

        # connect to the stream
        url = 'rtsp://{}:{}@{}:{}/{}'.format(user, password, ip_address, port, stream)
        self.camera = cv2.VideoCapture(url)
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
