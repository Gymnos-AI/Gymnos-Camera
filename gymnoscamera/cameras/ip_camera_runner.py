import cv2
import time
from threading import Thread, Lock

from gymnoscamera.cameras.camera import Camera


mutex = Lock()


class IpCameraRunner(Camera):
    """
    An implementation of a Camera runner which sources its camera from a USB camera
    """
    def __init__(self, db, model_type: str, model_path: str, headless_mode):
        super().__init__(db, model_type, model_path, headless_mode)

        user = 'admin'
        password = 'MZEJUT'
        ip_address = '192.168.1.77'
        port = '554'
        stream = 'h264_stream'

        # connect to the stream
        url = 'rtsp://{}:{}@{}:{}/{}'.format(user, password, ip_address, port, stream)
        self.camera = cv2.VideoCapture(url)
        time.sleep(0.5)
        self.point = 0

        self.waiting_to_aquire = False

        worker = Thread(target=self.update_stream, args=())
        worker.setDaemon(True)
        worker.start()

    def update_stream(self):
        while True:
            if self.waiting_to_aquire:
                time.sleep(0.75)
            mutex.acquire()
            self.camera.read()
            mutex.release()

    def get_frame(self):
        """
        Retrieves a frames from the camera and returns it
        """
        self.waiting_to_aquire = True
        mutex.acquire()
        ret, image = self.camera.read()
        frame_time = time.time()
        mutex.release()
        self.waiting_to_aquire = False

        image = cv2.resize(image, (self.camera_height, self.camera_width))

        return image, frame_time
